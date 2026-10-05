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
