package driver

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// DockerDriver manages ephemeral runners running as Docker containers.
type DockerDriver struct {
	executor      CmdExecutor
	store         *InstanceStore
	defaultImage  string
	defaultNet    string
}

// NewDockerDriver creates a Docker runner driver.
func NewDockerDriver(executor CmdExecutor, store *InstanceStore, defaultImage, defaultNet string) *DockerDriver {
	if executor == nil {
		executor = &OSExecutor{}
	}
	if defaultImage == "" {
		defaultImage = "ghcr.io/actions/actions-runner:latest"
	}
	return &DockerDriver{
		executor:     executor,
		store:        store,
		defaultImage: defaultImage,
		defaultNet:   defaultNet,
	}
}

// Backend returns "docker".
func (d *DockerDriver) Backend() string {
	return "docker"
}

// SpawnRunner creates and starts an ephemeral runner container.
func (d *DockerDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	name := spec.Name
	if name == "" {
		name = fmt.Sprintf("runzero-%s", spec.ID)
	}

	image := spec.ImageName
	if image == "" {
		image = d.defaultImage
	}

	args := []string{"run", "-d", "--name", name, "--label", "runzero=true"}
	args = append(args, "--label", fmt.Sprintf("runzero.id=%s", spec.ID))
	args = append(args, "--label", fmt.Sprintf("runzero.repo=%s", spec.Repo))

	if spec.CPUs > 0 {
		args = append(args, fmt.Sprintf("--cpus=%d", spec.CPUs))
	}
	if spec.MemoryMB > 0 {
		args = append(args, fmt.Sprintf("-m=%dm", spec.MemoryMB))
	}

	net := spec.Network
	if net == "" {
		net = d.defaultNet
	}
	if net != "" {
		args = append(args, "--network", net)
	}

	if spec.CacheDir != "" {
		args = append(args, "-v", fmt.Sprintf("%s:/cache:rw", spec.CacheDir))
	}

	for k, v := range spec.Env {
		args = append(args, "-e", fmt.Sprintf("%s=%s", k, v))
	}

	args = append(args, image)

	out, err := d.executor.Run(ctx, "docker", args...)
	if err != nil {
		return nil, fmt.Errorf("docker run failed (%w): %s", err, strings.TrimSpace(string(out)))
	}

	now := time.Now().UTC().Format(time.RFC3339)
	info := state.RunnerInfo{
		ID:         spec.ID,
		Name:       name,
		Status:     "running",
		State:      "running",
		TargetRepo: spec.Repo,
		TargetArch: spec.Arch,
		Backend:    "docker",
		CreatedAt:  &now,
	}

	if d.store != nil {
		d.store.Register(info)
	}

	return &info, nil
}
