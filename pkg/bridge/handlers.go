package bridge

import (
	"encoding/json"
	"net/http"
	"runtime"
	"strings"

	"github.com/el-j/run-zero/pkg/driver"
)

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	resp := HealthResponse{
		Status:             "ok",
		Service:            "runzero-vm-bridge",
		Version:            s.version,
		Platform:           runtime.GOOS,
		AvailableVMDrivers: []string{"orbstack"},
		AllDrivers:         []string{"orbstack", "docker"},
		GitSHA:             s.gitSHA,
	}
	s.writeJSON(w, http.StatusOK, resp)
}

func (s *Server) handleStatus(w http.ResponseWriter, r *http.Request) {
	resp := StatusResponse{
		Status:           "ok",
		AvailableDrivers: []string{"orbstack", "docker"},
		Platform:         runtime.GOOS,
	}
	s.writeJSON(w, http.StatusOK, resp)
}

func (s *Server) handleGetDriverRunners(w http.ResponseWriter, r *http.Request, driverName string) {
	d := s.resolveDriver(driverName)
	if d == nil {
		s.writeJSON(w, http.StatusBadRequest, map[string]string{"error": "Unknown driver: " + driverName})
		return
	}
	runners, err := d.ListRunners(r.Context())
	if err != nil {
		s.writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error(), "driver": driverName})
		return
	}
	s.writeJSON(w, http.StatusOK, RunnersResponse{Driver: driverName, Runners: runners})
}

func (s *Server) handlePostDriverSpawn(w http.ResponseWriter, r *http.Request, driverName string) {
	d := s.resolveDriver(driverName)
	if d == nil {
		s.writeJSON(w, http.StatusBadRequest, SpawnResponse{Status: "error", Error: "Unknown driver: " + driverName})
		return
	}

	var req SpawnRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil && err.Error() != "EOF" {
		s.writeJSON(w, http.StatusBadRequest, SpawnResponse{Status: "error", Error: "Invalid JSON: " + err.Error()})
		return
	}

	var labels []string
	if req.Labels != "" {
		for _, l := range strings.Split(req.Labels, ",") {
			if trimmed := strings.TrimSpace(l); trimmed != "" {
				labels = append(labels, trimmed)
			}
		}
	}

	spec := driver.RunnerSpec{
		Name:    req.Name,
		Repo:    req.Repo,
		Arch:    req.Arch,
		Backend: driverName,
		Labels:  labels,
		Token:   req.RunnerToken,
		Env:     req.ExtraEnv,
	}

	info, err := d.SpawnRunner(r.Context(), spec)
	if err != nil {
		s.writeJSON(w, http.StatusInternalServerError, SpawnResponse{Status: "error", Driver: driverName, Error: err.Error()})
		return
	}

	s.writeJSON(w, http.StatusOK, SpawnResponse{
		Status:   "success",
		Driver:   driverName,
		RunnerID: info.ID,
	})
}

func (s *Server) handlePostDriverStop(w http.ResponseWriter, r *http.Request, driverName string) {
	d := s.resolveDriver(driverName)
	if d == nil {
		s.writeJSON(w, http.StatusBadRequest, ActionResponse{Status: "error", Error: "Unknown driver: " + driverName})
		return
	}

	var body struct {
		RunnerID string `json:"runner_id"`
		ID       string `json:"id"`
	}
	_ = json.NewDecoder(r.Body).Decode(&body)

	targetID := body.RunnerID
	if targetID == "" {
		targetID = body.ID
	}

	if err := d.StopRunner(r.Context(), targetID); err != nil {
		s.writeJSON(w, http.StatusInternalServerError, ActionResponse{Status: "error", Error: err.Error()})
		return
	}

	s.writeJSON(w, http.StatusOK, ActionResponse{Status: "success", Destroyed: true})
}

func (s *Server) handlePostDriverPrune(w http.ResponseWriter, r *http.Request, driverName string) {
	s.writeJSON(w, http.StatusOK, ActionResponse{Status: "success", Pruned: 0})
}

func (s *Server) handlePostDriverCleanup(w http.ResponseWriter, r *http.Request, driverName string) {
	d := s.resolveDriver(driverName)
	if d != nil {
		_ = d.CleanupAll(r.Context())
	}
	s.writeJSON(w, http.StatusOK, ActionResponse{Status: "success"})
}
