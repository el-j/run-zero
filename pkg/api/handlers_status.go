package api

import (
	"net/http"

	"github.com/el-j/run-zero/pkg/state"
)

func handleStatusAndFleet(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}
		writeJSON(w, http.StatusOK, st.GetSnapshot())
	}
}

func handleLogs(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"logs": st.GetLogs(),
		})
	}
}

// handleRunnerLog returns the log tail captured from a runner before its
// container/VM was removed (GET /api/runner-log?name=<runner name>), so a runner
// that died mid-job stays diagnosable after cleanup.
func handleRunnerLog(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}
		name := r.URL.Query().Get("name")
		if name == "" {
			writeError(w, http.StatusBadRequest, "name is required")
			return
		}
		log, ok := st.GetRunnerLog(name)
		if !ok {
			writeError(w, http.StatusNotFound, "no retained log for runner")
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"name": name,
			"log":  log,
		})
	}
}
