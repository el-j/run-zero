package driver

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// multipassHome is the default user's home in Multipass' Ubuntu images.
const multipassHome = "/home/ubuntu"

// MultipassDriver runs each job in a fresh Canonical Multipass Ubuntu VM
// (macOS, Linux, Windows). The guest installs and registers an ephemeral runner,
// runs one job and powers itself off; the prune pass then deletes it.
// Multipass only runs guests of the host's architecture.
type MultipassDriver struct {
	executor CmdExecutor
	store    *InstanceStore
	image    string
	hostArch string
}

// NewMultipassDriver creates a Multipass driver launching image (default
// "24.04"); a nil executor runs the real multipass CLI.
func NewMultipassDriver(executor CmdExecutor, store *InstanceStore, image string) *MultipassDriver {
	if executor == nil {
		executor = &OSExecutor{}
	}
	if image == "" {
		image = "24.04"
	}
	return &MultipassDriver{executor: executor, store: store, image: image, hostArch: hostArch()}
}

// Backend returns "multipass".
func (m *MultipassDriver) Backend() string { return KindMultipass }

// SpawnRunner launches a VM, mounts the host caches and starts the detached
// guest bootstrap. It returns once the VM is up.
func (m *MultipassDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	arch := m.hostArch
	if spec.Arch != "" && spec.Arch != "both" {
		arch = normalizeArch(spec.Arch)
	}
	if arch != m.hostArch {
		return nil, fmt.Errorf("multipass only runs %s guests on this host, not %s", m.hostArch, arch)
	}
	name := orbstackMachineName(spec.Name)

	// Multipass needs explicit sizes; unlimited sizing (0) gets 2 CPU / 2 GiB.
	cpus, mem := spec.CPUs, spec.MemoryMB
	if cpus <= 0 {
		cpus = 2
	}
	if mem <= 0 {
		mem = 2048
	}
	args := []string{"launch", m.image, "--name", name, "--cpus", fmt.Sprintf("%d", cpus), "--memory", fmt.Sprintf("%dM", mem)}
	if out, err := m.executor.Run(ctx, "multipass", args...); err != nil {
		return nil, fmt.Errorf("multipass launch failed (%w): %s", err, strings.TrimSpace(string(out)))
	}
	m.mountCaches(ctx, name, spec.Mounts)

	spec.Arch = arch
	g := guestScript{
		Name:      name,
		Home:      multipassHome,
		Spec:      spec,
		Finish:    "sudo systemctl poweroff || sudo poweroff || true",
		HostIPCmd: `ip route | awk '/default/ { print $3 }'`,
	}
	if out, err := m.executor.Run(ctx, "multipass", "exec", name, "--", "bash", "-c", g.detached()); err != nil {
		_, _ = m.executor.Run(ctx, "multipass", "delete", "--purge", name)
		return nil, fmt.Errorf("runner bootstrap failed in VM %s (%w): %s", name, err, strings.TrimSpace(string(out)))
	}

	now := time.Now().UTC().Format(time.RFC3339)
	info := state.RunnerInfo{
		ID: name, Name: name, Status: "running", State: "running",
		TargetRepo: spec.Repo, TargetArch: arch, Backend: KindMultipass, CreatedAt: &now,
	}
	if m.store != nil {
		m.store.Register(info)
	}
	return &info, nil
}

// mountCaches mounts each host cache dir into the guest, translating the
// runner container's /home/runner paths to the guest's home. A failed mount
// only costs the cache, so it is not fatal.
func (m *MultipassDriver) mountCaches(ctx context.Context, name string, mounts map[string]string) {
	for hostPath, guestPath := range mounts {
		if rest, ok := strings.CutPrefix(guestPath, "/home/runner"); ok {
			guestPath = multipassHome + rest
		}
		prep := fmt.Sprintf("sudo mkdir -p %[1]s && sudo chown -R ubuntu:ubuntu %[1]s", shellQuote(guestPath))
		if _, err := m.executor.Run(ctx, "multipass", "exec", name, "--", "bash", "-c", prep); err != nil {
			continue
		}
		_, _ = m.executor.Run(ctx, "multipass", "mount", hostPath, name+":"+guestPath)
	}
}

// ListRunners lists RunZero VMs from `multipass list --format json`, with the
// repo/arch recorded at spawn time.
func (m *MultipassDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	out, err := m.executor.Run(ctx, "multipass", "list", "--format", "json")
	if err != nil {
		return nil, fmt.Errorf("multipass list failed (%w): %s", err, strings.TrimSpace(string(out)))
	}
	var listing struct {
		List []struct {
			Name  string `json:"name"`
			State string `json:"state"`
		} `json:"list"`
	}
	if err := json.Unmarshal(out, &listing); err != nil {
		return nil, fmt.Errorf("failed parsing multipass list: %w", err)
	}

	known := storeByName(m.store)
	var runners []state.RunnerInfo
	for _, vm := range listing.List {
		if !strings.HasPrefix(vm.Name, "runzero-") {
			continue
		}
		status := multipassStatus(vm.State)
		r := orbstackRunnerFromName(vm.Name)
		r.Backend, r.Status, r.State = KindMultipass, status, status
		applyKnown(&r, known)
		runners = append(runners, r)
	}
	return runners, nil
}

// multipassStatus maps a Multipass instance state to a runner status: running,
// starting (still covering its job), or stopped (finished, to be pruned).
func multipassStatus(s string) string {
	switch strings.ToLower(s) {
	case "running":
		return "running"
	case "starting", "restarting":
		return "starting"
	}
	return "stopped"
}

// StopRunner deletes and purges a runner VM.
func (m *MultipassDriver) StopRunner(ctx context.Context, runnerID string) error {
	name := resolveMachineName(m.store, runnerID)
	if out, err := m.executor.Run(ctx, "multipass", "delete", "--purge", name); err != nil {
		return fmt.Errorf("multipass delete failed (%w): %s", err, strings.TrimSpace(string(out)))
	}
	if m.store != nil {
		m.store.Unregister(name)
	}
	return nil
}

// CleanupAll deletes every RunZero VM.
func (m *MultipassDriver) CleanupAll(ctx context.Context) error {
	return cleanupAll(ctx, m)
}

// storeByName indexes the store's runners by name.
func storeByName(store *InstanceStore) map[string]state.RunnerInfo {
	known := map[string]state.RunnerInfo{}
	if store == nil {
		return known
	}
	for _, r := range store.List() {
		if r.Name != "" {
			known[r.Name] = r
		}
	}
	return known
}

// applyKnown overrides the lossy values parsed from a machine name with those
// recorded at spawn time.
func applyKnown(r *state.RunnerInfo, known map[string]state.RunnerInfo) {
	k, ok := known[r.Name]
	if !ok {
		return
	}
	r.ID = k.ID
	if k.TargetRepo != "" {
		r.TargetRepo = k.TargetRepo
	}
	if k.TargetArch != "" {
		r.TargetArch = k.TargetArch
	}
	r.CreatedAt = k.CreatedAt
}

// resolveMachineName maps a runner ID (as listed, or an entropy suffix) to its
// machine name via the store; unknown IDs are used as the name.
func resolveMachineName(store *InstanceStore, runnerID string) string {
	if store != nil {
		for _, r := range store.List() {
			if r.ID == runnerID || r.Name == runnerID || strings.HasSuffix(r.Name, "-"+runnerID) {
				return r.Name
			}
		}
	}
	return runnerID
}

// cleanupAll stops every runner d lists, returning the first error.
func cleanupAll(ctx context.Context, d RunnerDriver) error {
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
