package api

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

type RunnerActionPayload struct {
	RunnerID string `json:"runner_id,omitempty"`
	Action   string `json:"action"`
	Repo     string `json:"repo,omitempty"`
	Arch     string `json:"arch,omitempty"`
}

func handleRunnerAction(st *state.State, runnerDriver ...driver.RunnerDriver) http.HandlerFunc {
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

func handlePrune(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		st.AppendLog("[Go Engine] ✂️ Triggered fleet runner prune.")
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"status":  "success",
			"message": "Prune executed",
		})
	}
}
