package driver

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// ListRunners queries Docker for containers with label runzero=true.
func (d *DockerDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	format := "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.State}}\t{{.Label \"runzero.repo\"}}\t{{.Label \"runzero.id\"}}"
	out, err := d.executor.Run(ctx, "docker", "ps", "-a", "--filter", "label=runzero=true", "--format", format)
	if err != nil {
		return nil, fmt.Errorf("docker ps failed: %w", err)
	}

	return parseDockerPS(string(out)), nil
}

// resolveTargets returns docker container references for a runner ID as reported by
// ListRunners (the runzero.id label value, or a raw container ID/name).
func (d *DockerDriver) resolveTargets(ctx context.Context, runnerID string) []string {
	var targets []string
	seen := make(map[string]bool)
	add := func(t string) {
		if t != "" && !seen[t] {
			seen[t] = true
			targets = append(targets, t)
		}
	}

	out, err := d.executor.Run(ctx, "docker", "ps", "-aq", "--filter", "label=runzero.id="+runnerID)
	if err == nil {
		for _, id := range strings.Fields(string(out)) {
			add(id)
		}
	}

	if d.store != nil {
		if r, ok := d.store.Get(runnerID); ok {
			add(r.Name)
		}
	}
	add(runnerID)
	if !strings.HasPrefix(runnerID, "runzero-") {
		add(fmt.Sprintf("runzero-%s", runnerID))
	}
	return targets
}

// StopRunner stops and removes a runner container.
func (d *DockerDriver) StopRunner(ctx context.Context, runnerID string) error {
	var lastOut string
	var lastErr error
	removed := false

	for _, target := range d.resolveTargets(ctx, runnerID) {
		_, _ = d.executor.Run(ctx, "docker", "stop", "-t", "5", target)
		out, err := d.executor.Run(ctx, "docker", "rm", "-f", target)
		if err == nil {
			removed = true
			break
		}
		lastOut, lastErr = strings.TrimSpace(string(out)), err
	}

	if !removed {
		return fmt.Errorf("docker rm failed (%w): %s", lastErr, lastOut)
	}

	if d.store != nil {
		d.store.Unregister(runnerID)
	}
	return nil
}

// RunnerLogs returns the last tail lines of a runner container's output.
func (d *DockerDriver) RunnerLogs(ctx context.Context, runnerID string, tail int) (string, error) {
	if tail <= 0 {
		tail = 100
	}
	var lastErr error
	for _, target := range d.resolveTargets(ctx, runnerID) {
		out, err := d.executor.Run(ctx, "docker", "logs", "--tail", fmt.Sprintf("%d", tail), target)
		if err == nil {
			return strings.TrimSpace(string(out)), nil
		}
		lastErr = err
	}
	return "", fmt.Errorf("docker logs failed: %w", lastErr)
}

// CleanupAll stops and terminates all RunZero managed containers.
func (d *DockerDriver) CleanupAll(ctx context.Context) error {
	runners, err := d.ListRunners(ctx)
	if err != nil {
		return err
	}

	var firstErr error
	for _, r := range runners {
		if err := d.StopRunner(ctx, r.ID); err != nil && firstErr == nil {
			firstErr = err
		}
	}
	return firstErr
}

func parseDockerPS(output string) []state.RunnerInfo {
	lines := strings.Split(strings.TrimSpace(output), "\n")
	var runners []state.RunnerInfo

	for _, line := range lines {
		parts := strings.Split(strings.TrimSpace(line), "\t")
		if len(parts) < 4 || parts[0] == "" {
			continue
		}
		repo := ""
		if len(parts) >= 5 {
			repo = parts[4]
		}
		id := parts[0]
		if len(parts) >= 6 && parts[5] != "" {
			id = parts[5]
		}

		runners = append(runners, state.RunnerInfo{
			ID:         id,
			Name:       parts[1],
			Status:     parts[2],
			State:      parts[3],
			TargetRepo: repo,
			Backend:    "docker",
		})
	}
	return runners
}
