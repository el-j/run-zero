package driver

import (
	"context"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// Router delegates runner provisioning to Docker or OrbStack VM driver.
type Router struct {
	dockerDriver  RunnerDriver
	vmDriver      RunnerDriver
	defaultMode   string
	autoRouteVM   bool
	store         *InstanceStore
}

// NewRouter creates a hybrid backend driver router.
func NewRouter(dockerDriver, vmDriver RunnerDriver, defaultMode string, autoRouteVM bool, store *InstanceStore) *Router {
	if defaultMode == "" {
		defaultMode = "auto"
	}
	return &Router{
		dockerDriver: dockerDriver,
		vmDriver:     vmDriver,
		defaultMode:  strings.ToLower(defaultMode),
		autoRouteVM:  autoRouteVM,
		store:        store,
	}
}

// Backend returns the router mode.
func (r *Router) Backend() string {
	return r.defaultMode
}

// SelectDriver chooses the appropriate driver for a given runner spec.
func (r *Router) SelectDriver(spec RunnerSpec) RunnerDriver {
	reqBackend := strings.ToLower(strings.TrimSpace(spec.Backend))
	if reqBackend == "orbstack" || reqBackend == "vm" {
		if r.vmDriver != nil {
			return r.vmDriver
		}
	}
	if reqBackend == "docker" || reqBackend == "container" {
		if r.dockerDriver != nil {
			return r.dockerDriver
		}
	}

	if r.autoRouteVM && r.vmDriver != nil {
		for _, lbl := range spec.Labels {
			l := strings.ToLower(strings.TrimSpace(lbl))
			if l == "vm" || l == "orb" || l == "orbstack" || l == "linux-vm" {
				return r.vmDriver
			}
		}
	}

	if (r.defaultMode == "orbstack" || r.defaultMode == "vm") && r.vmDriver != nil {
		return r.vmDriver
	}

	if r.dockerDriver != nil {
		return r.dockerDriver
	}
	return r.vmDriver
}

// SpawnRunner delegates execution to the selected driver.
func (r *Router) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	driver := r.SelectDriver(spec)
	return driver.SpawnRunner(ctx, spec)
}

// ListRunners combines runners discovered across both drivers.
func (r *Router) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	var results []state.RunnerInfo

	if r.dockerDriver != nil {
		dRunners, err := r.dockerDriver.ListRunners(ctx)
		if err == nil {
			results = append(results, dRunners...)
		}
	}
	if r.vmDriver != nil {
		vRunners, err := r.vmDriver.ListRunners(ctx)
		if err == nil {
			results = append(results, vRunners...)
		}
	}

	return results, nil
}

// StopRunner attempts stopping the runner in the corresponding driver.
func (r *Router) StopRunner(ctx context.Context, runnerID string) error {
	if r.store != nil {
		if info, ok := r.store.Get(runnerID); ok {
			if info.Backend == "orbstack" && r.vmDriver != nil {
				return r.vmDriver.StopRunner(ctx, runnerID)
			}
			if info.Backend == "docker" && r.dockerDriver != nil {
				return r.dockerDriver.StopRunner(ctx, runnerID)
			}
		}
	}

	if r.dockerDriver != nil {
		if err := r.dockerDriver.StopRunner(ctx, runnerID); err == nil {
			return nil
		}
	}
	if r.vmDriver != nil {
		return r.vmDriver.StopRunner(ctx, runnerID)
	}
	return nil
}

// CleanupAll cleans up runners in both Docker and VM drivers.
func (r *Router) CleanupAll(ctx context.Context) error {
	var firstErr error
	if r.dockerDriver != nil {
		if err := r.dockerDriver.CleanupAll(ctx); err != nil && firstErr == nil {
			firstErr = err
		}
	}
	if r.vmDriver != nil {
		if err := r.vmDriver.CleanupAll(ctx); err != nil && firstErr == nil {
			firstErr = err
		}
	}
	return firstErr
}
