package builder

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
)

// IsStagingProvisioned tests if the staging VM completed its provisioning sequence.
func (b *GoldenBuilder) IsStagingProvisioned(ctx context.Context, stagingName string) bool {
	checkCmd := "test -f /home/runner/actions-runner/run.sh || grep -q 'Base image provisioning complete' /home/runner/provision.log 2>/dev/null"
	_, err := b.exec.Run(ctx, "orb", "-m", stagingName, "-u", "runner", "bash", "-c", checkCmd)
	return err == nil
}

// StopVM shuts down a running VM.
func (b *GoldenBuilder) StopVM(ctx context.Context, vmName string) error {
	_, err := b.exec.Run(ctx, "orbctl", "stop", vmName)
	return err
}

// PromoteStaging atomically promotes a completed staging VM to the base image.
func (b *GoldenBuilder) PromoteStaging(ctx context.Context, stagingName, baseName string) error {
	_ = b.StopVM(ctx, stagingName)

	// If destination exists, delete it first to prevent rename collisions
	names, _ := b.ListVMs(ctx)
	for _, n := range names {
		if n == baseName {
			_, _ = b.exec.Run(ctx, "orbctl", "delete", "-f", baseName)
			break
		}
	}

	// Attempt rename
	if _, err := b.exec.Run(ctx, "orbctl", "rename", stagingName, baseName); err == nil {
		return nil
	}

	// Fallback to clone + delete
	if _, err := b.exec.Run(ctx, "orbctl", "clone", stagingName, baseName); err != nil {
		return fmt.Errorf("failed promoting staging VM %s to %s: %w", stagingName, baseName, err)
	}
	_, _ = b.exec.Run(ctx, "orbctl", "delete", "-f", stagingName)
	return nil
}

// EnsureBaseImagesStopped halts any golden base images currently running.
func (b *GoldenBuilder) EnsureBaseImagesStopped(ctx context.Context) ([]string, error) {
	out, err := b.exec.Run(ctx, "orbctl", "list", "--format", "json")
	if err != nil {
		return nil, err
	}
	var vms []struct {
		Name  string `json:"name"`
		State string `json:"state"`
	}
	if err := json.Unmarshal(out, &vms); err != nil {
		return nil, err
	}

	var stopped []string
	for _, vm := range vms {
		if strings.HasPrefix(vm.Name, BaseImagePrefix) && vm.State == "running" {
			if err := b.StopVM(ctx, vm.Name); err == nil {
				stopped = append(stopped, vm.Name)
			}
		}
	}
	return stopped, nil
}
