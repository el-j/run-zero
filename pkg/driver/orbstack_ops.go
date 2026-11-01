package driver

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// ListRunners queries OrbStack for running machines prefixed with runzero-.
func (o *OrbStackDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	out, err := o.executor.Run(ctx, "orbctl", "list")
	if err != nil {
		return nil, fmt.Errorf("orbctl list failed: %w", err)
	}

	runners := parseOrbctlList(string(out))
	o.enrichFromStore(runners)
	return runners, nil
}

// enrichFromStore fills in TargetRepo/TargetArch for machines whose names no longer
// carry the repo (OrbStack machine names must be valid hostnames, so the repo's
// "owner__repo" token is lossy there). The instance store records the exact values
// at spawn time.
func (o *OrbStackDriver) enrichFromStore(runners []state.RunnerInfo) {
	if o.store == nil {
		return
	}
	byName := make(map[string]state.RunnerInfo)
	for _, known := range o.store.List() {
		if known.Name != "" {
			byName[known.Name] = known
		}
	}
	for i := range runners {
		known, ok := byName[runners[i].Name]
		if !ok {
			if runners[i].CreatedAt == nil {
				now := time.Now().UTC().Format(time.RFC3339)
				runners[i].CreatedAt = &now
				if o.store != nil {
					o.store.Register(runners[i])
				}
			}
			continue
		}
		// The store holds the exact spawn-time values; the ones parsed from the
		// machine name are lossy, so the store wins whenever it has a value.
		if known.TargetRepo != "" {
			runners[i].TargetRepo = known.TargetRepo
		}
		if known.TargetArch != "" {
			runners[i].TargetArch = known.TargetArch
		}
		if runners[i].CreatedAt == nil {
			runners[i].CreatedAt = known.CreatedAt
		}
	}
}

// StopRunner stops and deletes an OrbStack runner machine.
func (o *OrbStackDriver) StopRunner(ctx context.Context, runnerID string) error {
	name := runnerID
	if !strings.HasPrefix(name, "runzero-") && !strings.HasPrefix(name, "local-runner-") {
		if o.store != nil {
			if r, ok := o.store.Get(runnerID); ok && r.Name != "" {
				name = r.Name
			}
		}
		if !strings.HasPrefix(name, "runzero-") && !strings.HasPrefix(name, "local-runner-") {
			if listed, err := o.ListRunners(ctx); err == nil {
				for _, r := range listed {
					if r.ID == runnerID {
						name = r.Name
						break
					}
				}
			}
		}
		if !strings.HasPrefix(name, "runzero-") && !strings.HasPrefix(name, "local-runner-") {
			name = fmt.Sprintf("runzero-%s", runnerID)
		}
	}

	log.Printf("[orbstack] StopRunner: deleting VM %q (requested id %q)", name, runnerID)
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
	var runners []state.RunnerInfo
	for _, line := range strings.Split(strings.TrimSpace(output), "\n") {
		fields := strings.Fields(strings.TrimSpace(line))
		if len(fields) == 0 || !isRunnerMachine(fields[0]) {
			continue
		}
		status := "running"
		if len(fields) >= 2 {
			status = fields[1]
		}
		r := orbstackRunnerFromName(fields[0])
		r.Status = status
		r.State = status
		runners = append(runners, r)
	}
	return runners
}

// isRunnerMachine reports whether an OrbStack machine is a runner. Golden base
// images (and their build-time staging VMs) are templates, not runners: listing
// them would get them pruned as "finished" runners.
func isRunnerMachine(name string) bool {
	if strings.HasPrefix(name, goldenVMBasePrefix) {
		return false
	}
	return strings.HasPrefix(name, "runzero-") || strings.HasPrefix(name, "local-runner-")
}

// orbstackRunnerFromName decodes the ID, repo, arch and job/run IDs carried in a
// runner machine name.
func orbstackRunnerFromName(name string) state.RunnerInfo {
	r := state.RunnerInfo{ID: name, Name: name, Backend: "orbstack"}
	if n, ok := parseJobScopedName(name); ok {
		// Expected format: runzero-j<jobID>-r<runID>-<arch>-<owner__repo>-<id>
		// Example: runzero-j202-r101-amd64-el-j__herbful-063160
		r.ID, r.TargetRepo, r.TargetArch, r.JobID, r.RunID = n.id, n.repo, n.arch, n.jobID, n.runID
		return r
	}
	if trimmed, ok := strings.CutPrefix(name, "runzero-"); ok {
		parts := strings.Split(trimmed, "-")
		r.ID = trimmed
		if len(parts) >= 4 && parts[0] == "manual" {
			// Expected format: runzero-manual-<arch>-<owner__repo>-<id>
			r.TargetArch = parts[1]
			r.ID = parts[len(parts)-1]
			r.TargetRepo = parseRepoToken(strings.Join(parts[2:len(parts)-1], "-"))
		}
		return r
	}
	// Expected format: local-runner-[arch]-[owner]-[repo]-[id]
	// e.g. local-runner-amd64-el-j-herbful-063160
	parts := strings.Split(strings.TrimPrefix(name, "local-runner-"), "-")
	if len(parts) >= 3 {
		r.TargetArch = parts[0]
		r.ID = parts[len(parts)-1]
		r.TargetRepo = legacyRepoFromName(strings.Join(parts[1:len(parts)-1], "-"))
	}
	return r
}

// legacyRepoFromName guesses owner/repo from a dash-joined legacy name token.
func legacyRepoFromName(repoPart string) string {
	if strings.HasPrefix(repoPart, "el-j-") {
		return "el-j/" + strings.TrimPrefix(repoPart, "el-j-")
	}
	if idx := strings.Index(repoPart, "-"); idx != -1 {
		return repoPart[:idx] + "/" + repoPart[idx+1:]
	}
	return repoPart
}
