package builder

import (
	"time"
)

const (
	// DefaultRunnerVersion is the pinned GitHub Actions runner release.
	DefaultRunnerVersion = "2.337.0"
	// BaseImagePrefix is the prefix used for OrbStack golden base VMs.
	BaseImagePrefix = "runzero-vm-base-"
)

// ImageStatus represents the build status of a golden VM image.
type ImageStatus string

const (
	StatusReady    ImageStatus = "ready"
	StatusBuilding ImageStatus = "building"
	StatusStale    ImageStatus = "stale"
	StatusFailed   ImageStatus = "failed"
)

// ImageEvent records image lifecycle progress for operator dashboards.
type ImageEvent struct {
	Status ImageStatus `json:"status"`
	Arch   string      `json:"arch"`
	Detail string      `json:"detail"`
	Time   time.Time   `json:"time"`
}

// Config holds options for the golden image builder.
type Config struct {
	Distro              string
	RunnerVersion       string
	StateDir            string
	CPUs                string
	Memory              string
	ProvisionScriptPath string
}

// InfrastructureImageStatus represents readiness of a VM base or container runner image.
type InfrastructureImageStatus struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Kind      string `json:"kind"` // "orbstack-vm" | "docker-container"
	Arch      string `json:"arch"` // "arm64" | "amd64"
	Exists    bool   `json:"exists"`
	IsStale   bool   `json:"is_stale"`
	Version   string `json:"version,omitempty"`
	SizeBytes int64  `json:"size_bytes,omitempty"`
	SizeHuman string `json:"size_human,omitempty"`
	CreatedAt string `json:"created_at,omitempty"`
	Status    string `json:"status"` // "ready" | "missing" | "stale" | "building" | "failed"
}

// ImageBuildProgress records active asynchronous build status.
type ImageBuildProgress struct {
	BuildID     string   `json:"build_id"`
	Target      string   `json:"target"` // "all" | "vm" | "container"
	Arch        string   `json:"arch"`   // "all" | "arm64" | "amd64"
	Status      string   `json:"status"` // "idle" | "building" | "success" | "failed"
	ProgressPct int      `json:"progress_pct"`
	CurrentStep string   `json:"current_step"`
	StartedAt   string   `json:"started_at"`
	CompletedAt string   `json:"completed_at,omitempty"`
	Error       string   `json:"error,omitempty"`
	LogLines    []string `json:"log_lines,omitempty"`
}

// ImagesStatusResponse holds the collective state of all golden images and containers.
type ImagesStatusResponse struct {
	VMImages        []InfrastructureImageStatus `json:"vm_images"`
	ContainerImages []InfrastructureImageStatus `json:"container_images"`
	AllReady        bool                        `json:"all_ready"`
	ActiveBuild     *ImageBuildProgress         `json:"active_build,omitempty"`
}

// ImageBuildRequest represents a trigger build request.
type ImageBuildRequest struct {
	Target string `json:"target"` // "all" | "vm" | "container"
	Arch   string `json:"arch"`   // "all" | "arm64" | "amd64"
	Force  bool   `json:"force"`
}
