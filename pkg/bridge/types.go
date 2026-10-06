package bridge

import (
	"github.com/el-j/run-zero/pkg/state"
)

// HealthResponse represents the payload returned by /health.
type HealthResponse struct {
	Status             string   `json:"status"`
	Service            string   `json:"service"`
	Version            string   `json:"version"`
	Platform           string   `json:"platform"`
	AvailableVMDrivers []string `json:"available_vm_drivers"`
	AllDrivers         []string `json:"all_drivers"`
	GitSHA             string   `json:"git_sha,omitempty"`
}

// StatusResponse represents driver readiness returned by /api/status.
type StatusResponse struct {
	Status           string   `json:"status"`
	AvailableDrivers []string `json:"available_drivers"`
	Platform         string   `json:"platform"`
}

// RunnersResponse represents the list of active runners for a driver.
type RunnersResponse struct {
	Driver  string             `json:"driver"`
	Runners []state.RunnerInfo `json:"runners"`
}

// SpawnRequest models parameters received to provision a runner.
type SpawnRequest struct {
	Repo        string            `json:"repo,omitempty"`
	Org         string            `json:"org,omitempty"`
	Arch        string            `json:"arch,omitempty"`
	Labels      string            `json:"labels,omitempty"`
	RunnerToken string            `json:"runner_token,omitempty"`
	Name        string            `json:"name,omitempty"`
	ExtraEnv    map[string]string `json:"extra_env,omitempty"`
}

// SpawnResponse returns the identifier of the spawned runner.
type SpawnResponse struct {
	Status   string `json:"status"`
	Driver   string `json:"driver,omitempty"`
	RunnerID string `json:"runner_id,omitempty"`
	Error    string `json:"error,omitempty"`
}

// ActionResponse communicates completion of destructive or lifecycle tasks.
type ActionResponse struct {
	Status    string `json:"status"`
	Destroyed bool   `json:"destroyed,omitempty"`
	Pruned    int    `json:"pruned,omitempty"`
	Built     bool   `json:"built,omitempty"`
	Error     string `json:"error,omitempty"`
}
