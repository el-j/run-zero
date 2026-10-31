package api

import (
	"context"
	"encoding/json"
	"net/http"
	"strings"

	"github.com/el-j/run-zero/pkg/builder"
)

// imageInspector reports the state of runner images; satisfied by *builder.ImageInspector.
type imageInspector interface {
	Inspect(ctx context.Context) builder.ImagesStatusResponse
}

// buildController drives image builds; satisfied by *builder.BuildManager.
type buildController interface {
	GetActiveBuild() *builder.ImageBuildProgress
	GetBuildByID(id string) (*builder.ImageBuildProgress, bool)
	TriggerBuild(ctx context.Context, req builder.ImageBuildRequest) (*builder.ImageBuildProgress, error)
	CancelBuild() error
}

func handleGetImages(inspector imageInspector, buildMgr buildController) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		resp := inspector.Inspect(r.Context())
		if buildMgr != nil {
			resp.ActiveBuild = buildMgr.GetActiveBuild()
		}
		writeJSON(w, http.StatusOK, resp)
	}
}

func handleTriggerBuild(buildMgr buildController) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		var req builder.ImageBuildRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil && err.Error() != "EOF" {
			writeError(w, http.StatusBadRequest, "Invalid JSON: "+err.Error())
			return
		}

		progress, err := buildMgr.TriggerBuild(r.Context(), req)
		if err != nil {
			writeError(w, http.StatusConflict, err.Error())
			return
		}

		writeJSON(w, http.StatusAccepted, progress)
	}
}

func handleCancelBuild(buildMgr buildController) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		if err := buildMgr.CancelBuild(); err != nil {
			writeError(w, http.StatusInternalServerError, err.Error())
			return
		}

		writeJSON(w, http.StatusOK, map[string]interface{}{
			"ok":      true,
			"message": "Build cancel requested",
		})
	}
}

func handleGetBuildProgress(buildMgr buildController) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}

		path := r.URL.Path
		id := strings.TrimPrefix(path, "/api/images/build/")
		if id == "" || id == path {
			active := buildMgr.GetActiveBuild()
			if active == nil {
				writeError(w, http.StatusNotFound, "No active build")
				return
			}
			writeJSON(w, http.StatusOK, active)
			return
		}

		progress, found := buildMgr.GetBuildByID(id)
		if !found {
			writeError(w, http.StatusNotFound, "Build not found")
			return
		}

		writeJSON(w, http.StatusOK, progress)
	}
}
