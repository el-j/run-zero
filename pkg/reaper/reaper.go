package reaper

import (
	"context"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

// Reaper enforces idle timeouts, zombie runner pruning, and unregistered runner teardown.
type Reaper struct {
	driver   driver.RunnerDriver
	ghClient *github.Client
	timeouts Timeouts
}

// NewReaper creates a self-healing reaper instance.
func NewReaper(driver driver.RunnerDriver, ghClient *github.Client, timeouts Timeouts) *Reaper {
	if timeouts.IdleSeconds <= 0 {
		timeouts = DefaultTimeouts()
	}
	return &Reaper{
		driver:   driver,
		ghClient: ghClient,
		timeouts: timeouts,
	}
}

// Reconcile executes a full reap pass across local active runners.
// It queries GitHub runner registrations for repos that have active runners,
// classifies each runner against registration and age timeouts, tears down
// orphaned/idle/stale runners via driver.StopRunner, and cleans up registrations from GitHub.
func (r *Reaper) Reconcile(
	ctx context.Context,
	localRunners []state.RunnerInfo,
	standbyCount int,
) []string {
	if len(localRunners) == 0 {
		return nil
	}

	repoMap := make(map[string]bool)
	for _, runner := range localRunners {
		if runner.TargetRepo != "" {
			repoMap[runner.TargetRepo] = true
		}
	}

	registrations := make(map[string]Registration)
	registryConclusive := false

	if r.ghClient != nil {
		for repo := range repoMap {
			regs, err := r.ghClient.ListRunners(ctx, repo, "")
			if err == nil {
				registryConclusive = true
				for _, reg := range regs {
					registrations[reg.Name] = Registration{
						ID:     reg.ID,
						Name:   reg.Name,
						Status: reg.Status,
						Busy:   reg.Busy,
						Scope:  reg.Scope,
					}
					// Auto-clean dead offline runzero runners from GitHub
					if reg.Status == "offline" && strings.HasPrefix(reg.Name, "runzero-") {
						_ = r.ghClient.DeleteRunner(ctx, repo, "", reg.ID)
					}
				}
			}
		}
	}

	nowUnix := float64(time.Now().Unix())
	reaped := r.ReconcileLocalRunners(ctx, localRunners, registrations, registryConclusive, nowUnix, standbyCount)

	// Clean up GitHub registration for any runner that was reaped
	if r.ghClient != nil && len(reaped) > 0 {
		reapedMap := make(map[string]bool)
		for _, id := range reaped {
			reapedMap[id] = true
		}
		for _, runner := range localRunners {
			if reapedMap[runner.ID] || reapedMap[runner.Name] {
				if reg, ok := registrations[runner.Name]; ok {
					_ = r.ghClient.DeleteRunner(ctx, runner.TargetRepo, "", reg.ID)
				}
			}
		}
	}

	return reaped
}

// ReconcileLocalRunners evaluates local runners against GitHub registrations and reaps dead/idle runners.
func (r *Reaper) ReconcileLocalRunners(
	ctx context.Context,
	localRunners []state.RunnerInfo,
	registrations map[string]Registration,
	registryConclusive bool,
	nowUnix float64,
	standbyCount int,
) []string {
	standbyLeft := standbyCount
	var reapedIDs []string

	for _, runner := range localRunners {
		var age float64
		if runner.CreatedAt != nil {
			t, err := time.Parse(time.RFC3339, *runner.CreatedAt)
			if err == nil {
				age = nowUnix - float64(t.Unix())
			}
		}

		var regPtr *Registration
		if reg, ok := registrations[runner.Name]; ok {
			regPtr = &reg
		}

		action := Classify(age, regPtr, registryConclusive, r.timeouts)

		if action == ActionReapIdle && standbyLeft > 0 {
			standbyLeft--
			continue
		}

		if action == ActionReapUnregistered || action == ActionReapIdle || action == ActionCheckStaleBusy {
			if r.driver != nil {
				_ = r.driver.StopRunner(ctx, runner.ID)
			}
			reapedIDs = append(reapedIDs, runner.ID)
		}
	}

	return reapedIDs
}
