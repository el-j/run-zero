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
	driver    driver.RunnerDriver
	ghClient  *github.Client
	timeouts  Timeouts
	firstSeen map[string]float64
	// Logf, when set, receives notable actions such as cancelled zombie jobs.
	Logf func(format string, args ...any)
}

// NewReaper creates a self-healing reaper instance.
func NewReaper(driver driver.RunnerDriver, ghClient *github.Client, timeouts Timeouts) *Reaper {
	if timeouts.IdleSeconds <= 0 {
		timeouts = DefaultTimeouts()
	}
	return &Reaper{
		driver:    driver,
		ghClient:  ghClient,
		timeouts:  timeouts,
		firstSeen: make(map[string]float64),
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

	registrations, conclusiveRepos := r.fetchRegistrations(ctx, localRunners)
	nowUnix := float64(time.Now().Unix())
	reaped := r.ReconcileLocalRunners(ctx, localRunners, registrations, conclusiveRepos, nowUnix, standbyCount)
	r.deleteReapedRegistrations(ctx, localRunners, registrations, reaped)
	return reaped
}

// fetchRegistrations lists GitHub runner registrations (by runner name) for
// every repo with a local runner, deleting dead offline runzero registrations on
// the way. conclusiveRepos records the repos whose listing succeeded: a runner
// may only be judged "unregistered" against its own repo's listing.
func (r *Reaper) fetchRegistrations(
	ctx context.Context,
	localRunners []state.RunnerInfo,
) (registrations map[string]Registration, conclusiveRepos map[string]bool) {
	registrations = make(map[string]Registration)
	conclusiveRepos = make(map[string]bool)
	if r.ghClient == nil {
		return registrations, conclusiveRepos
	}

	repoMap := make(map[string]bool)
	for _, runner := range localRunners {
		if runner.TargetRepo != "" {
			repoMap[runner.TargetRepo] = true
		}
	}
	for repo := range repoMap {
		regs, err := r.ghClient.ListRunners(ctx, repo, "")
		if err != nil {
			continue
		}
		conclusiveRepos[repo] = true
		for _, reg := range regs {
			registrations[reg.Name] = Registration{
				ID:     reg.ID,
				Name:   reg.Name,
				Status: reg.Status,
				Busy:   reg.Busy,
				Scope:  reg.Scope,
			}
			// Auto-clean dead offline runzero runners from GitHub. A zombie (offline
			// but still busy) holds an orphaned job, and GitHub refuses to delete a
			// busy runner, so its job is cancelled first.
			if reg.Status == "offline" && strings.HasPrefix(reg.Name, "runzero-") {
				if reg.Busy {
					r.cancelOrphanedJobs(ctx, repo, reg.Name)
				}
				_ = r.ghClient.DeleteRunner(ctx, repo, "", reg.ID)
			}
		}
	}
	return registrations, conclusiveRepos
}

// cancelOrphanedJobs cancels the workflow runs whose in-progress jobs are held
// by runnerName, a runner GitHub reports offline but still busy.
func (r *Reaper) cancelOrphanedJobs(ctx context.Context, repo, runnerName string) {
	jobs, err := r.ghClient.ListActiveJobs(ctx, repo)
	if err != nil {
		return
	}
	cancelled := map[int64]bool{}
	for _, j := range jobs {
		if j.Status != "in_progress" || j.RunnerName == nil || *j.RunnerName != runnerName || cancelled[j.RunID] {
			continue
		}
		cancelled[j.RunID] = true
		if err := r.ghClient.TriggerWorkflowAction(ctx, repo, j.RunID, "cancel"); err != nil {
			r.logf("[Reaper] ⚠️ Could not cancel run #%d orphaned on dead runner %s (%s): %v", j.RunID, runnerName, repo, err)
			continue
		}
		r.logf("[Reaper] 🧟 Cancelled run #%d: job %q was orphaned on dead runner %s (%s)", j.RunID, j.Name, runnerName, repo)
	}
}

func (r *Reaper) logf(format string, args ...any) {
	if r.Logf != nil {
		r.Logf(format, args...)
	}
}

// deleteReapedRegistrations removes the GitHub registration of every reaped runner.
func (r *Reaper) deleteReapedRegistrations(
	ctx context.Context,
	localRunners []state.RunnerInfo,
	registrations map[string]Registration,
	reaped []string,
) {
	if r.ghClient == nil || len(reaped) == 0 {
		return
	}
	reapedMap := make(map[string]bool)
	for _, id := range reaped {
		reapedMap[id] = true
	}
	for _, runner := range localRunners {
		if !reapedMap[runner.ID] && !reapedMap[runner.Name] {
			continue
		}
		if reg, ok := registrations[runner.Name]; ok {
			_ = r.ghClient.DeleteRunner(ctx, runner.TargetRepo, "", reg.ID)
		}
	}
}

// ReconcileLocalRunners evaluates local runners against GitHub registrations and reaps dead/idle runners.
// conclusiveRepos lists the repos whose registrations were fetched successfully.
func (r *Reaper) ReconcileLocalRunners(
	ctx context.Context,
	localRunners []state.RunnerInfo,
	registrations map[string]Registration,
	conclusiveRepos map[string]bool,
	nowUnix float64,
	standbyCount int,
) []string {
	standbyLeft := standbyCount
	var reapedIDs []string

	for _, runner := range localRunners {
		var regPtr *Registration
		if reg, ok := registrations[runner.Name]; ok {
			regPtr = &reg
		}

		action := Classify(r.runnerAge(runner, nowUnix), regPtr, conclusiveRepos[runner.TargetRepo], r.timeouts)

		if action == ActionReapIdle && standbyLeft > 0 {
			standbyLeft--
			continue
		}

		if action == ActionReapUnregistered || action == ActionReapIdle || action == ActionCheckStaleBusy {
			if r.driver != nil {
				if err := r.driver.StopRunner(ctx, runner.ID); err != nil && runner.Name != "" && runner.Name != runner.ID {
					_ = r.driver.StopRunner(ctx, runner.Name)
				}
			}
			reapedIDs = append(reapedIDs, runner.ID)
		}
	}

	r.forgetGoneRunners(localRunners)
	return reapedIDs
}

// runnerAge returns seconds since the runner was created, or since this reaper
// first saw it when the creation time is unknown.
func (r *Reaper) runnerAge(runner state.RunnerInfo, nowUnix float64) float64 {
	if runner.CreatedAt != nil {
		// A creation time in the future (clock skew) is not trusted.
		if t, err := time.Parse(time.RFC3339, *runner.CreatedAt); err == nil && float64(t.Unix()) <= nowUnix {
			return nowUnix - float64(t.Unix())
		}
	}
	if r.firstSeen == nil {
		r.firstSeen = make(map[string]float64)
	}
	key := runnerKey(runner)
	seen, ok := r.firstSeen[key]
	if !ok {
		seen = nowUnix
		r.firstSeen[key] = seen
	}
	return nowUnix - seen
}

// forgetGoneRunners drops first-seen times of runners that no longer exist.
func (r *Reaper) forgetGoneRunners(localRunners []state.RunnerInfo) {
	liveKeys := make(map[string]bool, len(localRunners))
	for _, runner := range localRunners {
		liveKeys[runnerKey(runner)] = true
	}
	for k := range r.firstSeen {
		if !liveKeys[k] {
			delete(r.firstSeen, k)
		}
	}
}

func runnerKey(runner state.RunnerInfo) string {
	if runner.ID == "" {
		return runner.Name
	}
	return runner.ID
}
