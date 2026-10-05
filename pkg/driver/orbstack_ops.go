package driver

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// ListRunners queries OrbStack for running machines prefixed with runzero-.
func (o *OrbStackDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	out, err := o.executor.Run(ctx, "orbctl", "list")
	if err != nil {
		return nil, fmt.Errorf("orbctl list failed: %w", err)
	}

	return parseOrbctlList(string(out)), nil
}

// StopRunner stops and deletes an OrbStack runner machine.
func (o *OrbStackDriver) StopRunner(ctx context.Context, runnerID string) error {
	name := runnerID
	if !strings.HasPrefix(name, "runzero-") {
		name = fmt.Sprintf("runzero-%s", runnerID)
	}

	_, _ = o.executor.Run(ctx, "orbctl", "stop", name)
	out, err := o.executor.Run(ctx, "orbctl", "delete", "-f", name)
	if err != nil {
		return fmt.Errorf("orbctl delete failed (%w): %s", err, strings.TrimSpace(string(out)))
	}

	if o.store != nil {
		o.store.Unregister(runnerID)
	}
	return nil
}

// CleanupAll stops and removes all OrbStack runner machines.
func (o *OrbStackDriver) CleanupAll(ctx context.Context) error {
	runners, err := o.ListRunners(ctx)
	if err != nil {
		return err
	}

	var firstErr error
	for _, r := range runners {
		if err := o.StopRunner(ctx, r.ID); err != nil && firstErr == nil {
			firstErr = err
		}
	}
	return firstErr
}

func parseOrbctlList(output string) []state.RunnerInfo {
	lines := strings.Split(strings.TrimSpace(output), "\n")
	var runners []state.RunnerInfo

	for _, line := range lines {
		fields := strings.Fields(strings.TrimSpace(line))
		if len(fields) == 0 {
			continue
		}
		name := fields[0]
		if !strings.HasPrefix(name, "runzero-") {
			continue
		}

		status := "running"
		if len(fields) >= 2 {
			status = fields[1]
		}

		id := strings.TrimPrefix(name, "runzero-")
		runners = append(runners, state.RunnerInfo{
			ID:      id,
			Name:    name,
			Status:  status,
			State:   status,
			Backend: "orbstack",
		})
	}
	return runners
}
