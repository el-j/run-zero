package api

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

// randRead is a seam over crypto/rand so the fallback path is testable.
var randRead = rand.Read

func randomHex(bytesLen int) string {
	b := make([]byte, bytesLen)
	if _, err := randRead(b); err != nil {
		return fmt.Sprintf("%06x", time.Now().UnixNano()%0xFFFFFF)
	}
	return hex.EncodeToString(b)
}

// RunnerActionPayload is the JSON body accepted by POST /api/actions/runner.
type RunnerActionPayload struct {
	RunnerID string `json:"runner_id,omitempty"`
	Action   string `json:"action"`
	Repo     string `json:"repo,omitempty"`
	Arch     string `json:"arch,omitempty"`
	Backend  string `json:"backend,omitempty"`
}

var validRunnerActions = map[string]bool{
	"start": true, "stop": true, "drain": true, "pause": true, "resume": true, "open-terminal": true,
}

// firstDriver returns the optional driver passed variadically, or nil.
func firstDriver(runnerDriver []driver.RunnerDriver) driver.RunnerDriver {
	if len(runnerDriver) > 0 {
		return runnerDriver[0]
	}
	return nil
}

// decodeRunnerAction parses and validates the request, writing the error response itself.
func decodeRunnerAction(w http.ResponseWriter, r *http.Request) (RunnerActionPayload, bool) {
	var payload RunnerActionPayload
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return payload, false
	}
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON payload")
		return payload, false
	}
	if !validRunnerActions[payload.Action] {
		writeError(w, http.StatusBadRequest, "Invalid runner action. Must be one of: start, stop, drain, pause, resume, open-terminal")
		return payload, false
	}
	return payload, true
}

func handleRunnerActionWithDeps(st *state.State, cfg *config.Config, ghClient *github.Client, runnerDriver ...driver.RunnerDriver) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		payload, ok := decodeRunnerAction(w, r)
		if !ok {
			return
		}
		rd := firstDriver(runnerDriver)

		switch {
		case payload.Action == "pause":
			st.SetAutoscalerStatus("paused")
		case payload.Action == "resume":
			st.SetAutoscalerStatus("running")
		case payload.Action == "open-terminal":
			respondOpenTerminal(st, w, r, payload)
			return
		case payload.Action == "start" && rd != nil && ghClient != nil:
			respondManualStart(st, cfg, ghClient, rd, w, r, payload)
			return
		case payload.Action == "stop" && rd != nil && payload.RunnerID != "":
			if err := rd.StopRunner(r.Context(), payload.RunnerID); err != nil {
				st.AppendLog(fmt.Sprintf("[Go Engine] ❌ Failed to stop runner %s: %v", payload.RunnerID, err))
				writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to stop runner: %v", err))
				return
			}
		}

		st.AppendLog(fmt.Sprintf("[Go Engine] 🏃 Runner control action: %s", payload.Action))
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"ok":      true,
			"message": fmt.Sprintf("Runner action '%s' executed", payload.Action),
		})
	}
}

// resolveTerminalTarget finds the runner name and backend for an open-terminal request.
func resolveTerminalTarget(st *state.State, payload RunnerActionPayload) (name, backend string) {
	if payload.RunnerID != "" {
		for _, rInfo := range st.GetSnapshot().Runners {
			if rInfo.ID == payload.RunnerID || rInfo.Name == payload.RunnerID {
				name = rInfo.Name
				backend = rInfo.Backend
				break
			}
		}
	}
	if name == "" {
		name = payload.RunnerID
	}
	if backend == "" {
		backend = payload.Backend
	}
	if backend == "" {
		if strings.HasPrefix(name, "runzero-j") || strings.HasPrefix(name, "runzero-vm") {
			backend = "orbstack"
		} else {
			backend = "docker"
		}
	}
	return name, backend
}

func terminalCommand(backend, name string) string {
	if backend == "orbstack" {
		return fmt.Sprintf("orb -m %s -u runner bash", name)
	}
	return fmt.Sprintf("docker exec -it %s bash", name)
}

// launchBridgeTerminal asks the host VM bridge to open a terminal; false when unavailable or failed.
func launchBridgeTerminal(r *http.Request, payload RunnerActionPayload, name, backend string) bool {
	bridgeURL := os.Getenv("HOST_VM_BRIDGE_URL")
	if bridgeURL == "" || bridgeURL == "none" {
		return false
	}
	reqBody, _ := json.Marshal(map[string]string{
		"runner_id":   payload.RunnerID,
		"runner_name": name,
		"backend":     backend,
	})
	httpReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, strings.TrimRight(bridgeURL, "/")+"/api/actions/open-terminal", bytes.NewReader(reqBody))
	if err != nil {
		return false
	}
	httpReq.Header.Set("Content-Type", "application/json")
	if token := os.Getenv("RUNZERO_BRIDGE_TOKEN"); token != "" {
		httpReq.Header.Set("Authorization", "Bearer "+token)
	}
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(httpReq)
	if err != nil {
		return false
	}
	defer func() { _ = resp.Body.Close() }()
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return false
	}
	var bridgeResp struct {
		TerminalLaunched bool `json:"terminal_launched"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&bridgeResp); err != nil {
		return false
	}
	return bridgeResp.TerminalLaunched
}

func respondOpenTerminal(st *state.State, w http.ResponseWriter, r *http.Request, payload RunnerActionPayload) {
	name, backend := resolveTerminalTarget(st, payload)
	cmdStr := terminalCommand(backend, name)
	launched := launchBridgeTerminal(r, payload, name, backend)

	msg := fmt.Sprintf("Terminal opened for %s", name)
	if !launched {
		msg = fmt.Sprintf("Command copied: %s", cmdStr)
	}
	st.AppendLog(fmt.Sprintf("[Go Engine] 💻 Terminal connection for runner %s: %s", name, cmdStr))
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"ok":                true,
		"command":           cmdStr,
		"terminal_launched": launched,
		"message":           msg,
	})
}

// buildManualSpec assembles the RunnerSpec for a manually started runner.
func buildManualSpec(cfg *config.Config, payload RunnerActionPayload, repo, arch, token string) driver.RunnerSpec {
	id := randomHex(3)
	backend := "docker"
	if payload.Backend != "" {
		backend = payload.Backend
	} else if cfg != nil && cfg.RunnerBackend != "" && cfg.RunnerBackend != "auto" {
		backend = cfg.RunnerBackend
	}
	spec := driver.RunnerSpec{
		ID:       id,
		Name:     driver.ManualRunnerName(repo, arch, id),
		Repo:     repo,
		Arch:     arch,
		Backend:  backend,
		Labels:   []string{"self-hosted", "local", arch},
		Token:    token,
		CPUs:     3,
		MemoryMB: 4096,
		Network:  "host",
	}
	if cfg != nil {
		if cfg.RunnerCPUs > 0 {
			spec.CPUs = cfg.RunnerCPUs
		}
		spec.CacheDir = cfg.HostCacheDir
	}
	return spec
}

func respondManualStart(st *state.State, cfg *config.Config, ghClient *github.Client, rd driver.RunnerDriver, w http.ResponseWriter, r *http.Request, payload RunnerActionPayload) {
	targetRepo := payload.Repo
	if targetRepo == "" {
		if snap := st.GetSnapshot(); len(snap.RepoPriority) > 0 {
			targetRepo = snap.RepoPriority[0]
		}
	}
	if targetRepo == "" {
		writeError(w, http.StatusBadRequest, "No repository specified for runner start")
		return
	}
	targetArch := payload.Arch
	if targetArch == "" {
		targetArch = "amd64"
	}

	token, err := ghClient.CreateRegistrationToken(r.Context(), targetRepo, "")
	if err != nil {
		st.AppendLog(fmt.Sprintf("[Go Engine] ❌ Failed to get registration token for %s: %v", targetRepo, err))
		writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to get registration token: %v", err))
		return
	}

	spec := buildManualSpec(cfg, payload, targetRepo, targetArch, token)
	info, err := rd.SpawnRunner(r.Context(), spec)
	if err != nil {
		st.AppendLog(fmt.Sprintf("[Go Engine] ❌ Failed to manually spawn runner: %v", err))
		writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to spawn runner: %v", err))
		return
	}
	st.AppendLog(fmt.Sprintf("[Go Engine] 🚀 Manually spawned runner %s for %s (%s)", spec.Name, targetRepo, targetArch))
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"ok":        true,
		"runner_id": info.ID,
		"name":      info.Name,
		"message":   fmt.Sprintf("Runner '%s' spawned for %s", spec.Name, targetRepo),
	})
}

func handlePrune(st *state.State, runnerDriver ...driver.RunnerDriver) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		pruned := 0
		if len(runnerDriver) > 0 && runnerDriver[0] != nil {
			removed, err := driver.PruneFinished(r.Context(), runnerDriver[0], func(r state.RunnerInfo, logTail string) {
				if r.Name != "" && logTail != "" {
					st.SetRunnerLog(r.Name, logTail)
				}
			})
			if err != nil {
				st.AppendLog(fmt.Sprintf("[Go Engine] ❌ Fleet prune failed: %v", err))
				writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to prune runners: %v", err))
				return
			}
			pruned = len(removed)
		}

		st.AppendLog(fmt.Sprintf("[Go Engine] ✂️ Triggered fleet runner prune. Removed %d finished runner(s).", pruned))
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"ok":      true,
			"message": fmt.Sprintf("Prune executed. Removed %d finished runner(s).", pruned),
			"pruned":  pruned,
		})
	}
}
