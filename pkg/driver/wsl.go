package driver

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// wslHome is the runner user's home inside WSL guests.
const wslHome = "/home/runner"

// WSLDriver runs ephemeral runners in WSL2 on a Windows host. With a base
// tarball (WSL_BASE_TARBALL) every runner gets its own distro, imported from
// the tarball and unregistered when its job is done; otherwise runners run in
// per-runner directories inside one shared distro (WSL_DISTRO_BASE), and a
// marker file tells the prune pass the job is done. WSL2 only runs guests of
// the host's architecture.
type WSLDriver struct {
	executor    CmdExecutor
	store       *InstanceStore
	distroBase  string
	baseTarball string
	installDir  string
	hostArch    string
}

// NewWSLDriver creates a WSL2 driver; a nil executor runs the real wsl.exe.
// distroBase defaults to "Ubuntu-24.04"; installDir holds imported distros.
func NewWSLDriver(executor CmdExecutor, store *InstanceStore, distroBase, baseTarball, installDir string) *WSLDriver {
	if executor == nil {
		executor = &OSExecutor{}
	}
	if distroBase == "" {
		distroBase = "Ubuntu-24.04"
	}
	return &WSLDriver{
		executor: executor, store: store, distroBase: distroBase,
		baseTarball: baseTarball, installDir: installDir, hostArch: hostArch(),
	}
}

// Backend returns "wsl2".
func (w *WSLDriver) Backend() string { return KindWSL2 }

// ownDistro reports whether each runner gets its own imported distro.
func (w *WSLDriver) ownDistro() bool { return w.baseTarball != "" }

// home is a runner's directory: the runner user's home in its own distro, or a
// per-runner directory in the shared distro.
func (w *WSLDriver) home(name string) string {
	if w.ownDistro() {
		return wslHome
	}
	return wslHome + "/" + name
}

func (w *WSLDriver) distro(name string) string {
	if w.ownDistro() {
		return name
	}
	return w.distroBase
}

// SpawnRunner imports a distro (tarball mode) and starts the detached guest
// bootstrap as the runner user.
func (w *WSLDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	arch := w.hostArch
	if spec.Arch != "" && spec.Arch != "both" {
		arch = normalizeArch(spec.Arch)
	}
	if arch != w.hostArch {
		return nil, fmt.Errorf("WSL2 only runs %s guests on this host, not %s", w.hostArch, arch)
	}
	name := orbstackMachineName(spec.Name)

	if w.ownDistro() {
		dir := filepath.Join(w.installDir, name)
		if out, err := w.executor.Run(ctx, "wsl.exe", "--import", name, dir, w.baseTarball, "--version", "2"); err != nil {
			return nil, fmt.Errorf("wsl --import failed (%w): %s", err, wslText(out))
		}
	}

	spec.Arch = arch
	spec.Labels = append(spec.Labels, "wsl", "windows-host")
	home := w.home(name)
	finish := ""
	if !w.ownDistro() {
		finish = fmt.Sprintf("touch %s", shellQuote(home+".done"))
	}
	g := guestScript{
		Name:      name,
		Home:      home,
		Spec:      spec,
		Finish:    finish,
		HostIPCmd: `ip route show default | awk '{ print $3 }'`,
	}
	if out, err := w.executor.Run(ctx, "wsl.exe", "-d", w.distro(name), "-u", "runner", "--", "bash", "-c", g.detached()); err != nil {
		_ = w.remove(ctx, name)
		return nil, fmt.Errorf("runner bootstrap failed in WSL distro %s (%w): %s", w.distro(name), err, wslText(out))
	}

	now := time.Now().UTC().Format(time.RFC3339)
	info := state.RunnerInfo{
		ID: name, Name: name, Status: "running", State: "running",
		TargetRepo: spec.Repo, TargetArch: arch, Backend: KindWSL2, CreatedAt: &now,
	}
	if w.store != nil {
		w.store.Register(info)
	}
	return &info, nil
}

// ListRunners lists RunZero runners: imported distros from `wsl --list
// --verbose` in tarball mode, else the runners recorded in the store, each
// reported stopped once its done marker exists.
func (w *WSLDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	known := storeByName(w.store)
	var runners []state.RunnerInfo
	add := func(name, status string) {
		r := orbstackRunnerFromName(name)
		r.Backend, r.Status, r.State = KindWSL2, status, status
		applyKnown(&r, known)
		runners = append(runners, r)
	}

	if !w.ownDistro() {
		for name, r := range known {
			if r.Backend != KindWSL2 {
				continue
			}
			status := "running"
			if _, err := w.executor.Run(ctx, "wsl.exe", "-d", w.distroBase, "--", "test", "-e", w.home(name)+".done"); err == nil {
				status = "stopped"
			}
			add(name, status)
		}
		return runners, nil
	}

	out, err := w.executor.Run(ctx, "wsl.exe", "--list", "--verbose")
	if err != nil {
		return nil, fmt.Errorf("wsl --list failed (%w): %s", err, wslText(out))
	}
	for name, st := range parseWSLList(wslText(out)) {
		if strings.HasPrefix(name, "runzero-") {
			add(name, st)
		}
	}
	return runners, nil
}

// parseWSLList reads `wsl --list --verbose` (NAME STATE VERSION columns, the
// default distro marked "*") into name -> runner status. A stopped distro has
// finished its job (it stops once its last process exits).
func parseWSLList(text string) map[string]string {
	distros := map[string]string{}
	for i, line := range strings.Split(text, "\n") {
		f := strings.Fields(strings.TrimPrefix(strings.TrimSpace(line), "*"))
		if i == 0 || len(f) < 2 {
			continue // header or blank
		}
		status := "stopped"
		switch strings.ToLower(f[1]) {
		case "running":
			status = "running"
		case "installing", "converting":
			status = "starting"
		}
		distros[f[0]] = status
	}
	return distros
}

// wslText decodes wsl.exe output, which Windows writes as UTF-16LE.
func wslText(out []byte) string {
	s := strings.ReplaceAll(string(out), "\x00", "")
	s = strings.TrimPrefix(s, "\ufeff")
	s = strings.TrimPrefix(s, "\xff\xfe")
	return strings.TrimSpace(strings.ReplaceAll(s, "\r", ""))
}

// StopRunner terminates and unregisters a runner's distro (tarball mode), or
// kills its runner and deletes its directory in the shared distro.
func (w *WSLDriver) StopRunner(ctx context.Context, runnerID string) error {
	name := resolveMachineName(w.store, runnerID)
	if err := w.remove(ctx, name); err != nil {
		return err
	}
	if w.store != nil {
		w.store.Unregister(name)
	}
	return nil
}

func (w *WSLDriver) remove(ctx context.Context, name string) error {
	if w.ownDistro() {
		_, _ = w.executor.Run(ctx, "wsl.exe", "--terminate", name)
		if out, err := w.executor.Run(ctx, "wsl.exe", "--unregister", name); err != nil {
			return fmt.Errorf("wsl --unregister failed (%w): %s", err, wslText(out))
		}
		return nil
	}
	home := shellQuote(w.home(name))
	script := fmt.Sprintf("pkill -f %[1]s/actions-runner || true; rm -rf %[1]s %[2]s", home, shellQuote(w.home(name)+".done"))
	if out, err := w.executor.Run(ctx, "wsl.exe", "-d", w.distroBase, "-u", "root", "--", "bash", "-c", script); err != nil {
		return fmt.Errorf("removing runner %s from %s failed (%w): %s", name, w.distroBase, err, wslText(out))
	}
	return nil
}

// CleanupAll removes every RunZero runner.
func (w *WSLDriver) CleanupAll(ctx context.Context) error {
	return cleanupAll(ctx, w)
}
