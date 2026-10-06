package daemon

import (
	"os"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/settings"
	"github.com/el-j/run-zero/pkg/state"
)

func initPriorityManager(cfg *config.Config) *github.PriorityManager {
	var prioList []string
	if cfg.RepoPriority != "" {
		for _, p := range strings.Split(cfg.RepoPriority, ",") {
			if strings.TrimSpace(p) != "" {
				prioList = append(prioList, strings.TrimSpace(p))
			}
		}
	}
	pm, _ := github.NewPriorityManager("repo_priority.json", prioList, nil)
	return pm
}

func initPoller(cfg *config.Config, pm *github.PriorityManager, st *state.State) *github.Poller {
	var repos []string
	if cfg.ReposConfig != "" {
		for _, r := range strings.Split(cfg.ReposConfig, ",") {
			if strings.TrimSpace(r) != "" {
				repos = append(repos, strings.TrimSpace(r))
			}
		}
	}
	ghClient := github.NewClient(cfg.AccessToken, "", nil)
	rec := github.NewReconciler(pm)
	return github.NewPoller(ghClient, rec, st, repos, time.Duration(cfg.PollInterval)*time.Second)
}

func initDriver(cfg *config.Config, store *driver.InstanceStore) driver.RunnerDriver {
	dockerDriver := driver.NewDockerDriver(nil, store, "", "")
	var orbDriver driver.RunnerDriver
	if bridgeURL := os.Getenv("HOST_VM_BRIDGE_URL"); bridgeURL != "" && bridgeURL != "none" {
		token := os.Getenv("RUNZERO_BRIDGE_TOKEN")
		orbDriver = driver.NewBridgeDriver(bridgeURL, "orbstack", token, nil)
	} else {
		orbDriver = driver.NewOrbStackDriver(nil, store, "")
	}
	return driver.NewRouter(dockerDriver, orbDriver, cfg.RunnerBackend, cfg.AutoRouteVM, store)
}

func initReaper(d driver.RunnerDriver, gh *github.Client) *reaper.Reaper {
	return reaper.NewReaper(d, gh, reaper.DefaultTimeouts())
}

func initSettings(cfg *config.Config) *settings.Manager {
	return settings.NewManager(cfg, ".env")
}
