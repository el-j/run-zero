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
	executor     CmdExecutor
	store        *InstanceStore
	defaultImage string
	defaultNet   string
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
		if spec.Arch != "" {
			image = fmt.Sprintf("local-github-runner:%s", spec.Arch)
		} else {
			image = d.defaultImage
		}
	}

	args := []string{"run", "-d", "--name", name}
	if spec.Arch != "" {
		args = append(args, "--platform", fmt.Sprintf("linux/%s", spec.Arch))
	}
	args = append(args, "--cap-add", "SYS_ADMIN")
	args = append(args, "-v", "/var/run/docker.sock:/var/run/docker.sock")
	args = append(args, "--label", "runzero=true")
	args = append(args, "--label", "managed-by=local-autoscaler")
	args = append(args, "--label", "backend=docker")
	args = append(args, "--label", fmt.Sprintf("runzero.id=%s", spec.ID))
	args = append(args, "--label", fmt.Sprintf("runzero.repo=%s", spec.Repo))
	args = append(args, "--label", fmt.Sprintf("target-repo=%s", spec.Repo))
	args = append(args, "--label", fmt.Sprintf("target-arch=%s", spec.Arch))

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
	for hostP, contP := range spec.Mounts {
		args = append(args, "-v", fmt.Sprintf("%s:%s:rw", hostP, contP))
	}

	envMap := make(map[string]string)
	for k, v := range spec.Env {
		envMap[k] = v
	}
	if spec.Token != "" && envMap["RUNNER_TOKEN"] == "" {
		envMap["RUNNER_TOKEN"] = spec.Token
	}
	if envMap["RUNNER_NAME"] == "" {
		envMap["RUNNER_NAME"] = name
	}
	if spec.Repo != "" && envMap["REPO"] == "" {
		envMap["REPO"] = spec.Repo
	}
	if len(spec.Labels) > 0 && envMap["RUNNER_LABELS"] == "" {
		envMap["RUNNER_LABELS"] = strings.Join(spec.Labels, ",")
	}
	if envMap["EPHEMERAL"] == "" {
		envMap["EPHEMERAL"] = "true"
	}
	if envMap["RUNNER_WORKDIR"] == "" {
		envMap["RUNNER_WORKDIR"] = "_work"
	}

	for k, v := range envMap {
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
