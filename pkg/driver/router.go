package driver

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// Router delegates runner provisioning to Docker or OrbStack VM driver.
type Router struct {
	dockerDriver RunnerDriver
	vmDriver     RunnerDriver
	defaultMode  string
	autoRouteVM  bool
	store        *InstanceStore
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

func isVMTriggerLabel(label string) bool {
	l := strings.ToLower(strings.TrimSpace(label))
	switch l {
	case "vm", "orb", "orbstack", "linux-vm", "e2e", "browser", "playwright", "cypress",
		"selenium", "lighthouse", "systemd", "gui", "unconfined", "postgres", "mysql",
		"redis", "db", "database", "integration", "service", "services", "dind":
		return true
	}
	return false
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
			if isVMTriggerLabel(lbl) {
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
	info, err := driver.SpawnRunner(ctx, spec)
	if err == nil && info != nil && r.store != nil {
		r.store.Register(*info)
	}
	return info, err
}

// ListRunners combines runners discovered across both drivers.
func (r *Router) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	var results []state.RunnerInfo

	if r.dockerDriver != nil {
		dRunners, err := r.dockerDriver.ListRunners(ctx)
		if err == nil {
			for _, dr := range dRunners {
				if r.store != nil {
					r.store.Register(dr)
				}
			}
			results = append(results, dRunners...)
		}
	}
	if r.vmDriver != nil {
		vRunners, err := r.vmDriver.ListRunners(ctx)
		if err == nil {
			for _, vr := range vRunners {
				if r.store != nil {
					r.store.Register(vr)
				}
			}
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
		for _, info := range r.store.List() {
			if info.Name == runnerID || info.ID == runnerID {
				if info.Backend == "orbstack" && r.vmDriver != nil {
					return r.vmDriver.StopRunner(ctx, runnerID)
				}
				if info.Backend == "docker" && r.dockerDriver != nil {
					return r.dockerDriver.StopRunner(ctx, runnerID)
				}
			}
		}
	}

	var dErr error
	if r.dockerDriver != nil {
		if dErr = r.dockerDriver.StopRunner(ctx, runnerID); dErr == nil {
			return nil
		}
	}
	if r.vmDriver != nil {
		if vErr := r.vmDriver.StopRunner(ctx, runnerID); vErr == nil {
			return nil
		} else if dErr != nil {
			return fmt.Errorf("docker stop failed (%w); vm stop failed: %v", dErr, vErr)
		} else {
			return vErr
		}
	}
	return dErr
}

// RunnerLogs returns a runner's recent output from whichever driver owns it, so
// PruneFinished can retain logs when the daemon runs through the Router. It
// tries the backend recorded in the store first, then every driver that can
// return logs.
func (r *Router) RunnerLogs(ctx context.Context, runnerID string, tail int) (string, error) {
	var ordered []RunnerDriver
	if r.store != nil {
		if info, ok := r.store.Get(runnerID); ok && info.Backend == "orbstack" {
			ordered = append(ordered, r.vmDriver, r.dockerDriver)
		}
	}
	if ordered == nil {
		ordered = []RunnerDriver{r.dockerDriver, r.vmDriver}
	}

	lastErr := fmt.Errorf("no driver can return logs for runner %s", runnerID)
	for _, d := range ordered {
		provider, ok := d.(LogProvider)
		if !ok || d == nil {
			continue
		}
		out, err := provider.RunnerLogs(ctx, runnerID, tail)
		if err == nil {
			return out, nil
		}
		lastErr = err
	}
	return "", lastErr
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
