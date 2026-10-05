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
