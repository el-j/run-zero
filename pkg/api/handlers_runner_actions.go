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

func randomHex(bytesLen int) string {
	b := make([]byte, bytesLen)
	if _, err := rand.Read(b); err != nil {
		return fmt.Sprintf("%06x", time.Now().UnixNano()%0xFFFFFF)
	}
	return hex.EncodeToString(b)
}

type RunnerActionPayload struct {
	RunnerID string `json:"runner_id,omitempty"`
	Action   string `json:"action"`
	Repo     string `json:"repo,omitempty"`
	Arch     string `json:"arch,omitempty"`
	Backend  string `json:"backend,omitempty"`
}

func handleRunnerAction(st *state.State, runnerDriver ...driver.RunnerDriver) http.HandlerFunc {
	return handleRunnerActionWithDeps(st, nil, nil, runnerDriver...)
}

func handleRunnerActionWithDeps(st *state.State, cfg *config.Config, ghClient *github.Client, runnerDriver ...driver.RunnerDriver) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var payload RunnerActionPayload
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
			writeError(w, http.StatusBadRequest, "Invalid JSON payload")
			return
		}

		validActions := map[string]bool{
			"start": true, "stop": true, "drain": true, "pause": true, "resume": true, "open-terminal": true,
		}
		if !validActions[payload.Action] {
			writeError(w, http.StatusBadRequest, "Invalid runner action. Must be one of: start, stop, drain, pause, resume, open-terminal")
			return
		}

		if payload.Action == "pause" {
			st.SetAutoscalerStatus("paused")
		} else if payload.Action == "resume" {
			st.SetAutoscalerStatus("running")
		} else if payload.Action == "open-terminal" {
			var runnerName, backend string
			if payload.RunnerID != "" {
				for _, rInfo := range st.GetSnapshot().Runners {
					if rInfo.ID == payload.RunnerID || rInfo.Name == payload.RunnerID {
						runnerName = rInfo.Name
						backend = rInfo.Backend
						break
					}
				}
			}
			if runnerName == "" {
				runnerName = payload.RunnerID
			}
			if backend == "" {
				backend = payload.Backend
				if backend == "" {
					if strings.HasPrefix(runnerName, "runzero-j") || strings.HasPrefix(runnerName, "runzero-vm") {
						backend = "orbstack"
					} else {
						backend = "docker"
					}
				}
			}

			var cmdStr string
			if backend == "orbstack" {
				cmdStr = fmt.Sprintf("orb -m %s -u runner bash", runnerName)
			} else {
				cmdStr = fmt.Sprintf("docker exec -it %s bash", runnerName)
			}

			terminalLaunched := false
			bridgeURL := os.Getenv("HOST_VM_BRIDGE_URL")
			if bridgeURL != "" && bridgeURL != "none" {
				reqBody, _ := json.Marshal(map[string]string{
					"runner_id":   payload.RunnerID,
					"runner_name": runnerName,
					"backend":     backend,
				})
				httpReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, strings.TrimRight(bridgeURL, "/")+"/api/actions/open-terminal", bytes.NewReader(reqBody))
				if err == nil {
					httpReq.Header.Set("Content-Type", "application/json")
					if token := os.Getenv("RUNZERO_BRIDGE_TOKEN"); token != "" {
						httpReq.Header.Set("Authorization", "Bearer "+token)
					}
					client := &http.Client{Timeout: 5 * time.Second}
					resp, err := client.Do(httpReq)
					if err == nil {
						defer resp.Body.Close()
						if resp.StatusCode >= 200 && resp.StatusCode < 300 {
							var bridgeResp struct {
								TerminalLaunched bool `json:"terminal_launched"`
							}
							if err := json.NewDecoder(resp.Body).Decode(&bridgeResp); err == nil {
								terminalLaunched = bridgeResp.TerminalLaunched
							}
						}
					}
				}
			}

			msg := fmt.Sprintf("Terminal opened for %s", runnerName)
			if !terminalLaunched {
				msg = fmt.Sprintf("Command copied: %s", cmdStr)
			}
			st.AppendLog(fmt.Sprintf("[Go Engine] 💻 Terminal connection for runner %s: %s", runnerName, cmdStr))
			writeJSON(w, http.StatusOK, map[string]interface{}{
				"ok":                true,
				"command":           cmdStr,
				"terminal_launched": terminalLaunched,
				"message":           msg,
			})
			return
		}

		if payload.Action == "start" && len(runnerDriver) > 0 && runnerDriver[0] != nil && ghClient != nil {
			targetRepo := payload.Repo
			if targetRepo == "" {
				snap := st.GetSnapshot()
				if len(snap.RepoPriority) > 0 {
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

			id := randomHex(3)
			name := driver.ManualRunnerName(targetRepo, targetArch, id)
			backend := "docker"
			if payload.Backend != "" {
				backend = payload.Backend
			} else if cfg != nil && cfg.RunnerBackend != "" && cfg.RunnerBackend != "auto" {
				backend = cfg.RunnerBackend
			}

			spec := driver.RunnerSpec{
				ID:       id,
				Name:     name,
				Repo:     targetRepo,
				Arch:     targetArch,
				Backend:  backend,
				Labels:   []string{"self-hosted", "local", targetArch},
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

			info, err := runnerDriver[0].SpawnRunner(r.Context(), spec)
			if err != nil {
				st.AppendLog(fmt.Sprintf("[Go Engine] ❌ Failed to manually spawn runner: %v", err))
				writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to spawn runner: %v", err))
				return
			}
			st.AppendLog(fmt.Sprintf("[Go Engine] 🚀 Manually spawned runner %s for %s (%s)", name, targetRepo, targetArch))
			writeJSON(w, http.StatusOK, map[string]interface{}{
				"ok":        true,
				"runner_id": info.ID,
				"name":      info.Name,
				"message":   fmt.Sprintf("Runner '%s' spawned for %s", name, targetRepo),
			})
			return
		}

		if payload.Action == "stop" && len(runnerDriver) > 0 && runnerDriver[0] != nil && payload.RunnerID != "" {
			if err := runnerDriver[0].StopRunner(r.Context(), payload.RunnerID); err != nil {
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
