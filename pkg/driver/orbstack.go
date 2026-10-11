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
	name = orbstackMachineName(name)

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
		// Golden base images are existing machines: they are cloned, not created
		// (`orbctl create` only accepts a distro and rejects a machine name).
		createArgs := []string{"create", source, name}
		if strings.HasPrefix(source, goldenVMBasePrefix) {
			createArgs = []string{"clone", source, name}
		} else if spec.Arch != "" && spec.Arch != "both" {
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

	if spec.Token != "" && spec.Repo != "" {
		if out, err := o.executor.Run(ctx, "orb", "-m", name, "-u", "runner", "bash", "-c", runnerRegistrationScript(name, spec)); err != nil {
			// Never leave an idle, unregistered VM behind (it would count as capacity
			// and never pick up the job).
			_, _ = o.executor.Run(ctx, "orbctl", "delete", "-f", name)
			return nil, fmt.Errorf("runner registration failed in VM %s (%w): %s", name, err, strings.TrimSpace(string(out)))
		}
	}

	now := time.Now().UTC().Format(time.RFC3339)
	id := spec.ID
	if id == "" {
		// The bridge builds specs without an ID; key by machine name so concurrent
		// VMs don't overwrite each other's repo/arch mapping in the store.
		id = name
	}
	info := state.RunnerInfo{
		ID:         id,
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

// orbstackMaxMachineName is the DNS-label limit OrbStack enforces on machine names.
const orbstackMaxMachineName = 63

// orbstackMachineName converts a runner name into a valid OrbStack machine name:
// lowercase letters, digits and single hyphens only, at most 63 characters. When
// shortening, the tail (which carries the per-runner entropy suffix) is kept so
// names stay unique.
func orbstackMachineName(name string) string {
	var b strings.Builder
	lastDash := false
	for _, r := range strings.ToLower(name) {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
			b.WriteRune(r)
			lastDash = false
			continue
		}
		if !lastDash {
			b.WriteByte('-')
			lastDash = true
		}
	}
	out := strings.Trim(b.String(), "-")
	if out == "" {
		return "runzero"
	}
	if len(out) > orbstackMaxMachineName {
		const tail = 12
		head := strings.Trim(out[:orbstackMaxMachineName-tail-1], "-")
		out = head + "-" + strings.Trim(out[len(out)-tail:], "-")
	}
	return out
}

// shellQuote single-quotes v for safe embedding in a bash script.
func shellQuote(v string) string {
	return "'" + strings.ReplaceAll(v, "'", `'\''`) + "'"
}

// runnerLabels returns the custom labels to register: the job's own labels (minus the
// ones GitHub adds itself) plus "local" and the arch label the router matched on.
func runnerLabels(spec RunnerSpec) string {
	builtin := map[string]bool{"self-hosted": true, "linux": true, "x64": true, "arm64": true}
	seen := map[string]bool{}
	var out []string
	add := func(l string) {
		l = strings.TrimSpace(l)
		key := strings.ToLower(l)
		if l == "" || seen[key] || (builtin[key] && key != "arm64") {
			return
		}
		seen[key] = true
		out = append(out, l)
	}
	for _, l := range spec.Labels {
		add(l)
	}
	add("local")
	if spec.Arch != "" && spec.Arch != "both" {
		add(spec.Arch)
	}
	return strings.Join(out, ",")
}

// runnerRegistrationScript configures and starts an ephemeral Actions runner inside a
// VM cloned from the golden base image (runner unpacked in /home/runner/actions-runner,
// Docker engine installed natively so bind mounts resolve inside the VM).
func runnerRegistrationScript(name string, spec RunnerSpec) string {
	return fmt.Sprintf(`set -e
# GitHub-hosted runners resolve "localhost" to IPv4 only. A stock Ubuntu VM lists
# ::1 first, so services bound to 127.0.0.1 (or that dial "localhost" internally,
# e.g. Zitadel's gRPC gateway) hit "connection refused" on [::1]. Drop "localhost"
# from the ::1 hosts entry; ip6-localhost/ip6-loopback stay.
sudo sed -i -E 's/^(::1[[:space:]]+)localhost[[:space:]]+/\1/' /etc/hosts || true
cd /home/runner/actions-runner
./config.sh --unattended --ephemeral --replace --url %s --token %s --name %s --labels %s --work _work
setsid nohup ./run.sh > /home/runner/runner.log 2>&1 < /dev/null &
sleep 1
`, shellQuote("https://github.com/"+spec.Repo), shellQuote(spec.Token), shellQuote(name), shellQuote(runnerLabels(spec)))
}
