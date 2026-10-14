package driver

import (
	"context"
	"fmt"
	"strconv"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// ListRunners queries Docker for containers with label runzero=true.
func (d *DockerDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	format := "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.State}}\t{{.Label \"runzero.repo\"}}\t{{.Label \"runzero.id\"}}\t{{.Label \"runzero.created_at\"}}\t{{.Label \"runzero.arch\"}}\t{{.Label \"runzero.job_id\"}}\t{{.Label \"runzero.run_id\"}}\t{{.Label \"runzero.job\"}}\t{{.Label \"runzero.workflow\"}}"
	out, err := d.executor.Run(ctx, "docker", "ps", "-a", "--filter", "label=runzero=true", "--format", format)
	if err != nil {
		return nil, fmt.Errorf("docker ps failed: %w", err)
	}

	runners := parseDockerPS(string(out))
	d.enrichFromStore(runners)
	return runners, nil
}

func (d *DockerDriver) enrichFromStore(runners []state.RunnerInfo) {
	if d.store == nil {
		return
	}
	byName := make(map[string]state.RunnerInfo)
	for _, known := range d.store.List() {
		if known.Name != "" {
			byName[known.Name] = known
		}
		if known.ID != "" {
			byName[known.ID] = known
		}
	}
	for i := range runners {
		known, ok := byName[runners[i].Name]
		if !ok {
			known, ok = byName[runners[i].ID]
		}
		if !ok {
			continue
		}
		if runners[i].TargetRepo == "" {
			runners[i].TargetRepo = known.TargetRepo
		}
		if runners[i].TargetArch == "" {
			runners[i].TargetArch = known.TargetArch
		}
		if runners[i].CreatedAt == nil {
			runners[i].CreatedAt = known.CreatedAt
		}
	}
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
		if _, inspectErr := d.executor.Run(ctx, "docker", "inspect", target); inspectErr != nil {
			lastErr = inspectErr
			lastOut = "no such container"
			continue
		}
		_, _ = d.executor.Run(ctx, "docker", "stop", "-t", "5", target)
		out, err := d.executor.Run(ctx, "docker", "rm", "-f", target)
		outStr := strings.TrimSpace(string(out))
		if err == nil && outStr != "" && !strings.Contains(strings.ToLower(outStr), "no such container") {
			removed = true
			break
		}
		lastOut, lastErr = outStr, err
	}

	if !removed {
		return fmt.Errorf("docker rm failed (%w): %s", lastErr, lastOut)
	}

	// Clean up any auxiliary sibling containers associated with this workflow run ID
	runIDToken := extractRunIDToken(runnerID)
	if d.store != nil {
		if info, ok := d.store.Get(runnerID); ok && info.RunID != nil && *info.RunID > 0 {
			runIDToken = fmt.Sprintf("%d", *info.RunID)
		}
	}
	if runIDToken != "" {
		auxOut, auxErr := d.executor.Run(ctx, "docker", "ps", "-aq", "--filter", "name="+runIDToken)
		if auxErr == nil {
			for _, auxID := range strings.Fields(string(auxOut)) {
				insp, _ := d.executor.Run(ctx, "docker", "inspect", auxID, "--format", "{{.Name}} {{index .Config.Labels \"runzero\"}}")
				inspStr := string(insp)
				if !strings.Contains(inspStr, "runzero") && !strings.Contains(inspStr, "local-runner-") {
					_, _ = d.executor.Run(ctx, "docker", "stop", "-t", "3", auxID)
					_, _ = d.executor.Run(ctx, "docker", "rm", "-f", auxID)
				}
			}
		}
	}

	if d.store != nil {
		d.store.Unregister(runnerID)
	}
	return nil
}

func extractRunIDToken(nameOrID string) string {
	parts := strings.Split(nameOrID, "-")
	for _, p := range parts {
		if strings.HasPrefix(p, "r") && len(p) > 2 {
			digits := p[1:]
			allDigits := true
			for _, r := range digits {
				if r < '0' || r > '9' {
					allDigits = false
					break
				}
			}
			if allDigits {
				return digits
			}
		}
	}
	return ""
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
		var createdPtr *string
		if len(parts) >= 7 && strings.TrimSpace(parts[6]) != "" {
			c := strings.TrimSpace(parts[6])
			createdPtr = &c
		}

		targetArch := ""
		if len(parts) >= 8 && strings.TrimSpace(parts[7]) != "" {
			targetArch = strings.TrimSpace(parts[7])
		}

		var jobIDPtr *int64
		if len(parts) >= 9 && strings.TrimSpace(parts[8]) != "" {
			if parsed, err := strconv.ParseInt(strings.TrimSpace(parts[8]), 10, 64); err == nil {
				jobIDPtr = &parsed
			}
		}

		var runIDPtr *int64
		if len(parts) >= 10 && strings.TrimSpace(parts[9]) != "" {
			if parsed, err := strconv.ParseInt(strings.TrimSpace(parts[9]), 10, 64); err == nil {
				runIDPtr = &parsed
			}
		}

		var jobNamePtr *string
		if len(parts) >= 11 && strings.TrimSpace(parts[10]) != "" {
			jName := strings.TrimSpace(parts[10])
			jobNamePtr = &jName
		}

		var workflowPtr *string
		if len(parts) >= 12 && strings.TrimSpace(parts[11]) != "" {
			wName := strings.TrimSpace(parts[11])
			workflowPtr = &wName
		}

		name := parts[1]
		// If metadata is missing from labels, parse from standard container name:
		// Format: runzero-j<jobID>-r<runID>-<arch>-<owner__repo>-<id>
		if strings.HasPrefix(name, "runzero-") {
			trimmed := strings.TrimPrefix(name, "runzero-")
			tokens := strings.Split(trimmed, "-")
			if len(tokens) >= 5 && strings.HasPrefix(tokens[0], "j") && strings.HasPrefix(tokens[1], "r") {
				if jobIDPtr == nil {
					if parsed, err := strconv.ParseInt(tokens[0][1:], 10, 64); err == nil {
						jobIDPtr = &parsed
					}
				}
				if runIDPtr == nil {
					if parsed, err := strconv.ParseInt(tokens[1][1:], 10, 64); err == nil {
						runIDPtr = &parsed
					}
				}
				if targetArch == "" {
					targetArch = tokens[2]
				}
				if repo == "" {
					repoPart := strings.Join(tokens[3:len(tokens)-1], "-")
					repo = parseRepoToken(repoPart)
				}
				if id == parts[0] {
					id = tokens[len(tokens)-1]
				}
			}
		}

		runners = append(runners, state.RunnerInfo{
			ID:           id,
			Name:         name,
			Status:       parts[2],
			State:        parts[3],
			TargetRepo:   repo,
			TargetArch:   targetArch,
			Backend:      "docker",
			CreatedAt:    createdPtr,
			JobID:        jobIDPtr,
			RunID:        runIDPtr,
			JobName:      jobNamePtr,
			WorkflowName: workflowPtr,
		})
	}
	return runners
}
