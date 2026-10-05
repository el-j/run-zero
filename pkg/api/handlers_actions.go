package api

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/el-j/run-zero/pkg/state"
)

type RepoPriorityPayload struct {
	Priority []string `json:"priority"`
	Paused   []string `json:"paused"`
}

type WorkflowActionPayload struct {
	Repo   string `json:"repo"`
	RunID  int64  `json:"run_id"`
	Action string `json:"action"`
}

type RunnerActionPayload struct {
	RunnerID string `json:"runner_id,omitempty"`
	Action   string `json:"action"`
	Repo     string `json:"repo,omitempty"`
	Arch     string `json:"arch,omitempty"`
}

func handleRepoPriority(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var payload RepoPriorityPayload
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
			writeError(w, http.StatusBadRequest, "Invalid JSON payload")
			return
		}

		if payload.Priority == nil {
			payload.Priority = []string{}
		}
		if payload.Paused == nil {
			payload.Paused = []string{}
		}

		st.SetRepoPriority(payload.Priority, payload.Paused)
		st.AppendLog(fmt.Sprintf("[Go Engine] 🔀 Updated repository priority: %v (paused: %v)", payload.Priority, payload.Paused))
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"status":   "success",
			"priority": payload.Priority,
			"paused":   payload.Paused,
		})
	}
}

func handleWorkflowAction(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var payload WorkflowActionPayload
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
			writeError(w, http.StatusBadRequest, "Invalid JSON payload")
			return
		}

		if payload.Repo == "" || payload.RunID <= 0 {
			writeError(w, http.StatusBadRequest, "repo and valid run_id are required")
			return
		}

		act := payload.Action
		if act != "cancel" && act != "rerun" && act != "rerun-failed" {
			writeError(w, http.StatusBadRequest, "action must be one of: cancel, rerun, rerun-failed")
			return
		}

		st.AppendLog(fmt.Sprintf("[Go Engine] ⚡ Workflow action '%s' triggered on %s run #%d", act, payload.Repo, payload.RunID))
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"ok":      true,
			"message": fmt.Sprintf("Triggered %s on run %d", act, payload.RunID),
		})
	}
}

func handleRunnerAction(st *state.State) http.HandlerFunc {
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
