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

// StopRunner stops and removes a runner container.
func (d *DockerDriver) StopRunner(ctx context.Context, runnerID string) error {
	name := runnerID
	if !strings.HasPrefix(name, "runzero-") {
		name = fmt.Sprintf("runzero-%s", runnerID)
	}

	_, _ = d.executor.Run(ctx, "docker", "stop", "-t", "5", name)
	out, err := d.executor.Run(ctx, "docker", "rm", "-f", name)
	if err != nil {
		return fmt.Errorf("docker rm failed (%w): %s", err, strings.TrimSpace(string(out)))
	}

	if d.store != nil {
		d.store.Unregister(runnerID)
	}
	return nil
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
