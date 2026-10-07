package api

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
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
			"start": true, "stop": true, "drain": true, "pause": true, "resume": true,
		}
		if !validActions[payload.Action] {
			writeError(w, http.StatusBadRequest, "Invalid runner action. Must be one of: start, stop, drain, pause, resume")
			return
		}

		if payload.Action == "pause" {
			st.SetAutoscalerStatus("paused")
		} else if payload.Action == "resume" {
			st.SetAutoscalerStatus("running")
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
			name := fmt.Sprintf("local-runner-%s-%s-%s", targetArch, strings.ReplaceAll(targetRepo, "/", "-"), id)
			spec := driver.RunnerSpec{
				ID:       id,
				Name:     name,
				Repo:     targetRepo,
				Arch:     targetArch,
				Backend:  "docker",
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
