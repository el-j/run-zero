package driver

import (
	"context"

	"github.com/el-j/run-zero/pkg/state"
)

// RunnerSpec defines configuration for launching an ephemeral runner instance.
type RunnerSpec struct {
	ID        string
	Name      string
	Repo      string
	Arch      string
	Backend   string
	CPUs      int
	MemoryMB  int
	Labels    []string
	Token     string
	CacheDir  string
	Env       map[string]string
	Network   string
	ImageName string
}

// RunnerDriver abstracts ephemeral runner lifecycle across container and hypervisor backends.
type RunnerDriver interface {
	Backend() string
	SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error)
	ListRunners(ctx context.Context) ([]state.RunnerInfo, error)
	StopRunner(ctx context.Context, runnerID string) error
	CleanupAll(ctx context.Context) error
}
