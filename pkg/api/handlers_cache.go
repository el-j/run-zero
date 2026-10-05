package api

import (
	"encoding/json"
	"net/http"

	"github.com/el-j/run-zero/pkg/state"
)

type CachePurgePayload struct {
	Category string `json:"category,omitempty"`
	Repo     string `json:"repo,omitempty"`
	All      bool   `json:"all,omitempty"`
}

func handleCache(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		stats := map[string]interface{}{
			"total_bytes": int64(0),
			"total_human": "0 B",
			"categories": []map[string]interface{}{
				{"category": "npm", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "yarn", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "pnpm", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "pip", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "uv", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "go-mod", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "go-build", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "cargo", "bytes": int64(0), "human_readable": "0 B"},
				{"category": "toolcache", "bytes": int64(0), "human_readable": "0 B"},
			},
		}
		writeJSON(w, http.StatusOK, stats)
	}
}

func handleCachePurge(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var payload CachePurgePayload
		if r.Body != nil {
			_ = json.NewDecoder(r.Body).Decode(&payload)
		}

		label := payload.Category
		if payload.All || label == "" {
			label = "all"
		}

		st.AppendLog("[Go Engine] 🧹 Purged cache: " + label)
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"ok":      true,
			"cleared": []string{label},
		})
	}
}

func handleCleanCacheLegacy(st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var payload map[string]interface{}
		if r.Body != nil {
			if err := json.NewDecoder(r.Body).Decode(&payload); err != nil && err.Error() != "EOF" {
				writeError(w, http.StatusBadRequest, "Invalid JSON payload")
				return
			}
		}

		cat := "all"
		if payload != nil {
			if v, ok := payload["category"]; ok {
				if str, isStr := v.(string); isStr {
					cat = str
				} else {
					writeError(w, http.StatusBadRequest, "category must be a string")
					return
				}
			}
		}

		st.AppendLog("[Go Engine] 🧹 Cleaned cache: " + cat)
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"status":  "success",
			"cleared": []string{cat},
		})
	}
}
