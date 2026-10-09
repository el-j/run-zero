package driver

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// OrbStackDriver manages ephemeral runners running inside OrbStack Linux hypervisor VMs.
type OrbStackDriver struct {
	executor      CmdExecutor
	store         *InstanceStore
	defaultDistro string
}

const goldenVMBasePrefix = "runzero-vm-base-"

// NewOrbStackDriver creates an OrbStack VM driver.
func NewOrbStackDriver(executor CmdExecutor, store *InstanceStore, defaultDistro string) *OrbStackDriver {
	if executor == nil {
		executor = &OSExecutor{}
	}
	if defaultDistro == "" {
		defaultDistro = "ubuntu:jammy"
	}
	return &OrbStackDriver{
		executor:      executor,
		store:         store,
		defaultDistro: defaultDistro,
	}
}

// Backend returns "orbstack".
func (o *OrbStackDriver) Backend() string {
	return "orbstack"
}

// SpawnRunner creates, configures, and boots a new OrbStack Linux VM runner.
func (o *OrbStackDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	name := spec.Name
	if name == "" {
		name = fmt.Sprintf("runzero-%s", spec.ID)
	}

	candidates := make([]string, 0, 2)
	if spec.ImageName != "" {
		candidates = append(candidates, spec.ImageName)
	} else {
		if spec.Arch != "" && spec.Arch != "both" {
			candidates = append(candidates, goldenVMBasePrefix+spec.Arch)
		}
		candidates = append(candidates, o.defaultDistro)
	}

	var (
		out []byte
		err error
	)
	createErrors := make([]string, 0, len(candidates))
	for _, source := range candidates {
		createArgs := []string{"create", source, name}
		if spec.Arch != "" && spec.Arch != "both" && !strings.HasPrefix(source, goldenVMBasePrefix) {
			createArgs = append(createArgs, "--arch", spec.Arch)
		}
		out, err = o.executor.Run(ctx, "orbctl", createArgs...)
		if err == nil {
			break
		}
		createErrors = append(createErrors, fmt.Sprintf("%s: %s", source, strings.TrimSpace(string(out))))
		if spec.ImageName != "" {
			break
		}
	}
	if err != nil {
		return nil, fmt.Errorf("orbctl create failed for %s (%w): %s", strings.Join(candidates, " -> "), err, strings.Join(createErrors, " | "))
	}

	if spec.CPUs > 0 {
		_, _ = o.executor.Run(ctx, "orbctl", "config", "set", name, "cpu", fmt.Sprintf("%d", spec.CPUs))
	}
	if spec.MemoryMB > 0 {
		_, _ = o.executor.Run(ctx, "orbctl", "config", "set", name, "memory", fmt.Sprintf("%dM", spec.MemoryMB))
	}

	out, err = o.executor.Run(ctx, "orbctl", "start", name)
	if err != nil {
		return nil, fmt.Errorf("orbctl start failed (%w): %s", err, strings.TrimSpace(string(out)))
	}

	now := time.Now().UTC().Format(time.RFC3339)
	info := state.RunnerInfo{
		ID:         spec.ID,
		Name:       name,
		Status:     "running",
		State:      "running",
		TargetRepo: spec.Repo,
		TargetArch: spec.Arch,
		Backend:    "orbstack",
		CreatedAt:  &now,
	}
	if o.store != nil {
		o.store.Register(info)
	}

	return &info, nil
}
