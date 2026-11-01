package driver

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// ErrImageMissing reports that the runner image is not present locally, so
// every spawn will fail until it is rebuilt.
var ErrImageMissing = errors.New("runner image missing")

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
	image := d.imageFor(spec)
	args := []string{"run", "-d", "--name", name}
	if spec.Arch != "" {
		args = append(args, "--platform", fmt.Sprintf("linux/%s", spec.Arch))
	}
	args = append(args, "--cap-add", "SYS_ADMIN", "-v", "/var/run/docker.sock:/var/run/docker.sock")
	args = append(args, runnerLabelArgs(spec, name)...)
	args = append(args, d.resourceArgs(spec)...)
	for k, v := range runnerEnv(spec, name) {
		args = append(args, "-e", fmt.Sprintf("%s=%s", k, v))
	}
	args = append(args, image)

	out, err := d.executor.Run(ctx, "docker", args...)
	if err != nil {
		msg := strings.TrimSpace(string(out))
		if strings.Contains(msg, "Unable to find image") || strings.Contains(msg, "No such image") {
			return nil, fmt.Errorf("%w: %s (docker run: %s)", ErrImageMissing, image, msg)
		}
		return nil, fmt.Errorf("docker run failed (%w): %s", err, msg)
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

// imageFor picks the runner image: the spec's, else the per-arch local image,
// else the driver default.
func (d *DockerDriver) imageFor(spec RunnerSpec) string {
	if spec.ImageName != "" {
		return spec.ImageName
	}
	if spec.Arch != "" {
		return fmt.Sprintf("local-github-runner:%s", spec.Arch)
	}
	return d.defaultImage
}

// runnerLabelArgs returns the --label flags that let ListRunners recover a
// container's metadata.
func runnerLabelArgs(spec RunnerSpec, name string) []string {
	labels := []string{
		"runzero=true",
		"managed-by=local-autoscaler",
		"backend=docker",
		fmt.Sprintf("runzero.id=%s", spec.ID),
		fmt.Sprintf("runzero.repo=%s", spec.Repo),
		fmt.Sprintf("target-repo=%s", spec.Repo),
		fmt.Sprintf("target-arch=%s", spec.Arch),
		fmt.Sprintf("runzero.arch=%s", spec.Arch),
		fmt.Sprintf("com.docker.compose.project=%s", "runzero-runners"),
		fmt.Sprintf("com.docker.compose.service=%s", name),
		fmt.Sprintf("runzero.created_at=%s", time.Now().UTC().Format(time.RFC3339)),
	}
	if spec.JobID != nil {
		labels = append(labels, fmt.Sprintf("runzero.job_id=%d", *spec.JobID))
	}
	if spec.RunID != nil {
		labels = append(labels, fmt.Sprintf("runzero.run_id=%d", *spec.RunID))
	}
	if spec.JobName != "" {
		labels = append(labels, fmt.Sprintf("runzero.job=%s", spec.JobName))
	}
	if spec.WorkflowName != nil && *spec.WorkflowName != "" {
		labels = append(labels, fmt.Sprintf("runzero.workflow=%s", *spec.WorkflowName))
	}
	args := make([]string, 0, 2*len(labels))
	for _, l := range labels {
		args = append(args, "--label", l)
	}
	return args
}

// resourceArgs returns the CPU, memory, network and volume flags for a runner.
func (d *DockerDriver) resourceArgs(spec RunnerSpec) []string {
	var args []string
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
	return args
}

// runnerEnv merges spec.Env with the defaults the runner entrypoint needs;
// values already present in spec.Env win.
func runnerEnv(spec RunnerSpec, name string) map[string]string {
	env := make(map[string]string, len(spec.Env)+6)
	for k, v := range spec.Env {
		env[k] = v
	}
	setDefault := func(k, v string) {
		if v != "" && env[k] == "" {
			env[k] = v
		}
	}
	setDefault("RUNNER_TOKEN", spec.Token)
	setDefault("RUNNER_NAME", name)
	setDefault("REPO", spec.Repo)
	setDefault("RUNNER_LABELS", strings.Join(spec.Labels, ","))
	setDefault("EPHEMERAL", "true")
	setDefault("RUNNER_WORKDIR", "_work")
	return env
}
