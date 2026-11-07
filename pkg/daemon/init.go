package daemon

import (
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/settings"
	"github.com/el-j/run-zero/pkg/state"
)

// splitList splits a comma-separated setting into its non-blank, trimmed items.
func splitList(s string) []string {
	var items []string
	for _, item := range strings.Split(s, ",") {
		if trimmed := strings.TrimSpace(item); trimmed != "" {
			items = append(items, trimmed)
		}
	}
	return items
}

func initPriorityManager(cfg *config.Config) *github.PriorityManager {
	pm, _ := github.NewPriorityManager("repo_priority.json", splitList(cfg.RepoPriority), nil)
	return pm
}

func initPoller(cfg *config.Config, pm *github.PriorityManager, st *state.State) *github.Poller {
	ghClient := github.NewClient(cfg.AccessToken, "", nil)
	rec := github.NewReconciler(pm)
	return github.NewPoller(ghClient, rec, st, splitList(cfg.ReposConfig), time.Duration(cfg.PollInterval)*time.Second)
}

func initDriver(cfg *config.Config, store *driver.InstanceStore) driver.RunnerDriver {
	dockerDriver := driver.NewDockerDriver(nil, store, "", "")
	return driver.NewRouter(dockerDriver, initVMDriver(cfg, store), cfg.RunnerBackend, cfg.AutoRouteVM, store)
}

// vmKind picks the VM engine: VM_BACKEND when set, else the engine
// RUNNER_BACKEND names when it is WSL2 or Multipass, else OrbStack.
func vmKind(cfg *config.Config) string {
	switch k := driver.BackendKind(cfg.VMBackend); k {
	case driver.KindOrbStack, driver.KindWSL2, driver.KindMultipass:
		return k
	}
	switch k := driver.BackendKind(cfg.RunnerBackend); k {
	case driver.KindWSL2, driver.KindMultipass:
		return k
	}
	return driver.KindOrbStack
}

// initVMDriver builds the driver for VM-routed jobs: through the host VM
// bridge when the daemon runs in a container (HOST_VM_BRIDGE_URL), else the
// engine's CLI directly.
func initVMDriver(cfg *config.Config, store *driver.InstanceStore) driver.RunnerDriver {
	kind := vmKind(cfg)
	if bridgeURL := os.Getenv("HOST_VM_BRIDGE_URL"); bridgeURL != "" && bridgeURL != "none" {
		return driver.NewBridgeDriver(bridgeURL, kind, os.Getenv("RUNZERO_BRIDGE_TOKEN"), nil, store)
	}
	switch kind {
	case driver.KindWSL2:
		return newWSLDriver(cfg, store)
	case driver.KindMultipass:
		return driver.NewMultipassDriver(nil, store, cfg.MultipassImage)
	}
	return driver.NewOrbStackDriver(nil, store, "")
}

// newWSLDriver builds the WSL2 driver, keeping imported distros in
// WSL_RUNNER_DIR or the state directory.
func newWSLDriver(cfg *config.Config, store *driver.InstanceStore) driver.RunnerDriver {
	return driver.NewWSLDriver(nil, store, cfg.WSLDistroBase, cfg.WSLBaseTarball, wslRunnerDir(cfg))
}

// wslRunnerDir is WSL_RUNNER_DIR, or <state dir>/wsl.
func wslRunnerDir(cfg *config.Config) string {
	if cfg.WSLRunnerDir != "" {
		return cfg.WSLRunnerDir
	}
	return filepath.Join(stateDir(), "wsl")
}

func initReaper(cfg *config.Config, d driver.RunnerDriver, gh *github.Client) *reaper.Reaper {
	return reaper.NewReaper(d, gh, reaperTimeouts(cfg))
}

// reaperTimeouts applies RUNNER_BUSY_TIMEOUT_SECONDS to the default reaper timeouts.
func reaperTimeouts(cfg *config.Config) reaper.Timeouts {
	t := reaper.DefaultTimeouts()
	if cfg.BusyTimeoutSeconds > 0 {
		t.BusySeconds = cfg.BusyTimeoutSeconds
	}
	return t
}

func initSettings(cfg *config.Config) *settings.Manager {
	return settings.NewManager(cfg, ".env")
}
