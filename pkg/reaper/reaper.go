package reaper

import (
	"context"
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
