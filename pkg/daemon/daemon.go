package daemon

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/api"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

// Daemon coordinates the RunZero background engine, autoscaler loops, and HTTP control plane.
type Daemon struct {
	cfg         *config.Config
	state       *state.State
	server      *api.Server
	version     string
	priorityMgr *github.PriorityManager
	poller      *github.Poller
}

// NewDaemon initializes a new daemon instance.
func NewDaemon(cfg *config.Config, version string, distDir, staticDir string) *Daemon {
	st := state.NewState(cfg.MaxRunners, version, nil)

	var prioList []string
	if cfg.RepoPriority != "" {
		for _, p := range strings.Split(cfg.RepoPriority, ",") {
			if strings.TrimSpace(p) != "" {
				prioList = append(prioList, strings.TrimSpace(p))
			}
		}
	}
	pm, _ := github.NewPriorityManager("repo_priority.json", prioList, nil)
	prio, paused := pm.GetState()
	st.SetRepoPriority(prio, paused)

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
	poller := github.NewPoller(ghClient, rec, st, repos, time.Duration(cfg.PollInterval)*time.Second)

	var srv *api.Server
	if cfg.DashboardEnabled {
		allowedHosts := []string{cfg.DashboardHost, "localhost", "127.0.0.1"}
		srv = api.NewServer(cfg, st, distDir, staticDir, allowedHosts, 5*time.Second)
	}

	return &Daemon{
		cfg:         cfg,
		state:       st,
		server:      srv,
		version:     version,
		priorityMgr: pm,
		poller:      poller,
	}
}

// Config returns the active daemon configuration.
func (d *Daemon) Config() *config.Config {
	return d.cfg
}

// State returns the live daemon runtime state.
func (d *Daemon) State() *state.State {
	return d.state
}

// Server returns the control plane HTTP server, if enabled.
func (d *Daemon) Server() *api.Server {
	return d.server
}

// PriorityManager returns the priority manager instance.
func (d *Daemon) PriorityManager() *github.PriorityManager {
	return d.priorityMgr
}

// Poller returns the GitHub actions poller instance.
func (d *Daemon) Poller() *github.Poller {
	return d.poller
}

// Start boots the control plane server and daemon components.
func (d *Daemon) Start() error {
	d.state.AppendLog(fmt.Sprintf("[Go Engine] 🚀 RunZero daemon v%s starting...", d.version))
	if d.server != nil {
		if err := d.server.Start(); err != nil {
			return fmt.Errorf("failed to start control plane: %w", err)
		}
		d.state.AppendLog(fmt.Sprintf("[Go Engine] 📊 Real-Time Web UI running at http://%s", d.server.Addr()))
	}
	return nil
}

// Run executes the daemon blocking until ctx is cancelled, then initiates graceful shutdown.
func (d *Daemon) Run(ctx context.Context) error {
	if err := d.Start(); err != nil {
		return err
	}

	if d.poller != nil {
		go d.poller.Start(ctx)
	}

	<-ctx.Done()
	return d.Stop()
}

// Stop gracefully terminates the daemon and its control plane server.
func (d *Daemon) Stop() error {
	d.state.AppendLog("[Go Engine] 🛑 Stopping RunZero daemon...")
	d.state.SetAutoscalerStatus("stopped")

	if d.server != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()
		if err := d.server.Shutdown(ctx); err != nil {
			return err
		}
	}
	d.state.AppendLog("[Go Engine] Daemon stopped cleanly.")
	return nil
}
