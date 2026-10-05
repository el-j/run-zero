package builder

import (
	"context"
	"fmt"
	"os"
)

// BuildBaseImage provisions a new golden base VM with zero downtime for existing jobs.
func (b *GoldenBuilder) BuildBaseImage(ctx context.Context, arch string) (bool, error) {
	var customScript string
	if b.cfg.ProvisionScriptPath != "" {
		if data, err := os.ReadFile(b.cfg.ProvisionScriptPath); err == nil {
			customScript = string(data)
		}
	}
	fullScript := FullProvisionScript(arch, b.cfg.RunnerVersion, customScript)

	baseName := b.BaseImageName(arch)
	if b.BaseImageExists(ctx, arch) {
		if !b.IsStale(arch) {
			b.EmitEvent(StatusReady, arch, "Already built -- skipping.")
			return false, nil
		}
		b.EmitEvent(StatusStale, arch, fmt.Sprintf("Stale runner version, updating to %s", b.cfg.RunnerVersion))
	}

	stagingName := b.StagingImageName(arch)
	b.EmitEvent(StatusBuilding, arch, fmt.Sprintf("Building %s (%s)...", baseName, b.cfg.Distro))

	_, _ = b.exec.Run(ctx, "orbctl", "delete", "-f", stagingName)

	createArgs := []string{"create", "-a", arch, "-u", "runner"}
	if b.cfg.CPUs != "" {
		createArgs = append(createArgs, "--cpus", b.cfg.CPUs)
	}
	if b.cfg.Memory != "" {
		createArgs = append(createArgs, "--memory", b.cfg.Memory)
	}
	createArgs = append(createArgs, b.cfg.Distro, stagingName)

	if _, err := b.exec.Run(ctx, "orbctl", createArgs...); err != nil {
		b.EmitEvent(StatusFailed, arch, fmt.Sprintf("Failed creating VM %s: %v", stagingName, err))
		return false, fmt.Errorf("failed creating staging VM %s: %w", stagingName, err)
	}

	if _, err := b.exec.Run(ctx, "orb", "-m", stagingName, "-u", "runner", "bash", "-c", fullScript); err != nil {
		b.EmitEvent(StatusFailed, arch, fmt.Sprintf("Provisioning failed on %s: %v", stagingName, err))
		return false, fmt.Errorf("provisioning failed on %s: %w", stagingName, err)
	}

	if err := b.PromoteStaging(ctx, stagingName, baseName); err != nil {
		b.EmitEvent(StatusFailed, arch, fmt.Sprintf("Promotion failed for %s: %v", baseName, err))
		return false, err
	}

	_ = b.WriteStamp(arch)
	b.EmitEvent(StatusReady, arch, "Build succeeded.")
	return true, nil
}
