package driver

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

// recordingExec records every command line and answers by the first matching
// prefix in replies (a nil error answer means success).
type recordingExec struct {
	calls   []string
	replies []reply
}

type reply struct {
	prefix string
	out    string
	err    error
}

func (r *recordingExec) Run(_ context.Context, name string, args ...string) ([]byte, error) {
	line := name + " " + strings.Join(args, " ")
	r.calls = append(r.calls, line)
	for _, rep := range r.replies {
		if strings.HasPrefix(line, rep.prefix) {
			return []byte(rep.out), rep.err
		}
	}
	return nil, nil
}

func (r *recordingExec) LookPath(file string) (string, error) { return file, nil }

func (r *recordingExec) called(prefix string) bool {
	for _, c := range r.calls {
		if strings.HasPrefix(c, prefix) {
			return true
		}
	}
	return false
}

var errBoom = errors.New("boom")

func vmSpec() RunnerSpec {
	return RunnerSpec{
		ID: "abc123", Name: "runzero-j1-r2-amd64-el-j__repo.x-abc123", Repo: "el-j/repo.x", Arch: "amd64",
		CPUs: 2, MemoryMB: 4096, Labels: []string{"self-hosted", "e2e"}, Token: "tok'en",
	}
}

func TestBackendKind(t *testing.T) {
	for name, want := range map[string]string{
		"": "", "auto": "", "hybrid": "", "docker": KindDocker, "container": KindDocker,
		"orb": KindOrbStack, "orbstack-vm": KindOrbStack, "vm-orb": KindOrbStack, "OrbStack": KindOrbStack,
		"wsl": KindWSL2, "wsl2": KindWSL2, "windows": KindWSL2,
		"multipass": KindMultipass, "canonical-multipass": KindMultipass, "vm": "vm", "bogus": "",
	} {
		if got := BackendKind(name); got != want {
			t.Errorf("BackendKind(%q) = %q, want %q", name, got, want)
		}
	}
	if !IsVMBackend("wsl2") || !IsVMBackend("vm") || IsVMBackend("docker") || IsVMBackend("auto") {
		t.Error("IsVMBackend misclassifies")
	}
	if normalizeArch("x86_64") != "amd64" || normalizeArch("aarch64") != "arm64" || hostArch() == "" {
		t.Error("arch normalisation broken")
	}
}

func TestGuestScript(t *testing.T) {
	spec := vmSpec()
	spec.Env = map[string]string{"B_VAR": "two", "A_VAR": "o'ne", "bad-key": "x"}
	g := guestScript{Name: "vm-1", Home: "/home/ubuntu", Spec: spec, Finish: "echo done", HostIPCmd: "echo 10.0.0.1"}

	s := g.script()
	for _, want := range []string{
		"actions-runner-linux-x64-" + RunnerVersion + ".tar.gz",
		"--token 'tok'\\''en'",
		"--name 'vm-1'",
		"--url 'https://github.com/el-j/repo.x'",
		"--labels 'e2e,local,vm,amd64'",
		"export A_VAR='o'\\''ne'\nexport B_VAR='two'\n",
		"timeout 6h ./run.sh || true\necho done\n",
	} {
		if !strings.Contains(s, want) {
			t.Errorf("script missing %q:\n%s", want, s)
		}
	}
	if strings.Contains(s, "bad-key") || strings.Contains(s, "HOST_IP") {
		t.Error("invalid env names and (disabled) proxies must not appear")
	}

	g.Spec.Proxies = true
	g.Spec.Arch = "arm64"
	s = g.script()
	if !strings.Contains(s, "HOST_IP=$(echo 10.0.0.1)") || !strings.Contains(s, "GOPROXY=") || !strings.Contains(s, "linux-arm64-") {
		t.Errorf("expected proxy env and arm64 runner:\n%s", s)
	}
	if d := g.detached(); !strings.HasPrefix(d, "mkdir -p '/home/ubuntu' && setsid nohup bash -c ") || !strings.HasSuffix(d, "> '/home/ubuntu'/runzero-setup.log 2>&1 < /dev/null &") {
		t.Errorf("unexpected detached wrapper: %s", d)
	}
}

func newTestMultipass(exec *recordingExec) *MultipassDriver {
	d := NewMultipassDriver(exec, NewInstanceStore(""), "")
	d.hostArch = "amd64"
	return d
}

func TestMultipass_SpawnRunner(t *testing.T) {
	exec := &recordingExec{replies: []reply{{prefix: "multipass exec runzero-j1-r2-amd64-el-j-repo-x-abc123 -- bash -c sudo mkdir -p '/home/ubuntu/.cache/fail'", err: errBoom}}}
	d := newTestMultipass(exec)
	spec := vmSpec()
	spec.Mounts = map[string]string{"/host/npm": "/home/runner/.npm", "/host/fail": "/home/runner/.cache/fail"}

	info, err := d.SpawnRunner(context.Background(), spec)
	if err != nil {
		t.Fatalf("spawn: %v", err)
	}
	name := "runzero-j1-r2-amd64-el-j-repo-x-abc123"
	if info.Name != name || info.TargetRepo != "el-j/repo.x" || info.Backend != KindMultipass {
		t.Fatalf("unexpected info %+v", info)
	}
	if !exec.called("multipass launch 24.04 --name " + name + " --cpus 2 --memory 4096M") {
		t.Errorf("launch missing: %v", exec.calls)
	}
	if !exec.called("multipass mount /host/npm " + name + ":/home/ubuntu/.npm") {
		t.Errorf("cache mount (with /home/runner -> /home/ubuntu) missing: %v", exec.calls)
	}
	if exec.called("multipass mount /host/fail") {
		t.Error("a mount whose preparation failed must be skipped")
	}
	if !exec.called("multipass exec " + name + " -- bash -c mkdir -p '/home/ubuntu' && setsid nohup") {
		t.Errorf("detached bootstrap missing: %v", exec.calls)
	}
	if _, ok := d.store.Get(name); !ok {
		t.Error("runner not recorded in the store")
	}
}

func TestMultipass_SpawnRunnerFailures(t *testing.T) {
	ctx := context.Background()

	exec := &recordingExec{}
	d := newTestMultipass(exec)
	spec := vmSpec()
	spec.Arch = "arm64"
	if _, err := d.SpawnRunner(ctx, spec); err == nil || len(exec.calls) != 0 {
		t.Fatalf("other-arch spawn must be refused without commands: %v %v", err, exec.calls)
	}

	exec = &recordingExec{replies: []reply{{prefix: "multipass launch", out: "no space", err: errBoom}}}
	if _, err := newTestMultipass(exec).SpawnRunner(ctx, vmSpec()); err == nil || !strings.Contains(err.Error(), "no space") {
		t.Fatalf("launch failure: %v", err)
	}

	exec = &recordingExec{replies: []reply{{prefix: "multipass exec", err: errBoom}}}
	spec = vmSpec()
	spec.Arch, spec.CPUs, spec.MemoryMB = "", 0, 0
	if _, err := newTestMultipass(exec).SpawnRunner(ctx, spec); err == nil {
		t.Fatal("bootstrap failure must fail the spawn")
	}
	if !exec.called("multipass delete --purge") || !exec.called("multipass launch 24.04 --name runzero-j1-r2-amd64-el-j-repo-x-abc123 --cpus 2 --memory 2048M") {
		t.Errorf("expected cleanup and the 2 CPU / 2 GiB fallback for unlimited sizing: %v", exec.calls)
	}
}

func TestMultipass_ListStopCleanup(t *testing.T) {
	ctx := context.Background()
	listing := `{"list":[
		{"name":"runzero-j1-r2-amd64-el-j-repo-x-abc123","state":"Running"},
		{"name":"runzero-manual-amd64-o-r-def456","state":"Starting"},
		{"name":"runzero-j3-r4-amd64-o-r-ghi789","state":"Stopped"},
		{"name":"someone-else","state":"Running"}]}`
	exec := &recordingExec{replies: []reply{{prefix: "multipass list", out: listing}}}
	d := newTestMultipass(exec)
	d.store.Register(state.RunnerInfo{ID: "runzero-j1-r2-amd64-el-j-repo-x-abc123", Name: "runzero-j1-r2-amd64-el-j-repo-x-abc123", TargetRepo: "el-j/repo.x", TargetArch: "amd64"})

	runners, err := d.ListRunners(ctx)
	if err != nil || len(runners) != 3 {
		t.Fatalf("list: %v %+v", err, runners)
	}
	if r := runners[0]; r.TargetRepo != "el-j/repo.x" || r.Status != "running" || r.Backend != KindMultipass || r.JobID == nil || *r.JobID != 1 {
		t.Errorf("store values must win over the lossy name: %+v", r)
	}
	if runners[1].Status != "starting" || runners[2].Status != "stopped" {
		t.Errorf("unexpected statuses: %+v", runners)
	}

	if err := d.StopRunner(ctx, "abc123"); err != nil || !exec.called("multipass delete --purge runzero-j1-r2-amd64-el-j-repo-x-abc123") {
		t.Fatalf("stop by entropy id: %v %v", err, exec.calls)
	}
	if _, ok := d.store.Get("runzero-j1-r2-amd64-el-j-repo-x-abc123"); ok {
		t.Error("stopped runner must leave the store")
	}
	if err := d.CleanupAll(ctx); err != nil {
		t.Fatalf("cleanup: %v", err)
	}

	bad := &recordingExec{replies: []reply{{prefix: "multipass list", out: "{"}}}
	if _, err := newTestMultipass(bad).ListRunners(ctx); err == nil {
		t.Error("bad JSON must fail")
	}
	failing := &recordingExec{replies: []reply{{prefix: "multipass", err: errBoom}}}
	fd := newTestMultipass(failing)
	if _, err := fd.ListRunners(ctx); err == nil {
		t.Error("list failure must fail")
	}
	if err := fd.CleanupAll(ctx); err == nil {
		t.Error("cleanup must report a list failure")
	}
	if err := fd.StopRunner(ctx, "x"); err == nil {
		t.Error("delete failure must fail")
	}
	stopFails := &recordingExec{replies: []reply{{prefix: "multipass list", out: listing}, {prefix: "multipass delete", err: errBoom}}}
	if err := newTestMultipass(stopFails).CleanupAll(ctx); err == nil {
		t.Error("cleanup must report a stop failure")
	}

	nd := NewMultipassDriver(nil, nil, "22.04")
	if _, ok := nd.executor.(*OSExecutor); !ok || nd.image != "22.04" || nd.Backend() != KindMultipass {
		t.Error("unexpected defaults")
	}
	if len(storeByName(nil)) != 0 || resolveMachineName(nil, "x") != "x" {
		t.Error("nil store helpers")
	}
}

func newTestWSL(exec *recordingExec, tarball string) *WSLDriver {
	d := NewWSLDriver(exec, NewInstanceStore(""), "", tarball, `C:\runzero\wsl`)
	d.hostArch = "amd64"
	return d
}

func TestWSL_SpawnRunner(t *testing.T) {
	ctx := context.Background()
	name := "runzero-j1-r2-amd64-el-j-repo-x-abc123"

	exec := &recordingExec{}
	d := newTestWSL(exec, `C:\base.tar`)
	info, err := d.SpawnRunner(ctx, vmSpec())
	if err != nil || info.Backend != KindWSL2 || info.Name != name {
		t.Fatalf("spawn: %v %+v", err, info)
	}
	if !exec.called("wsl.exe --import "+name+" ") || !exec.called("wsl.exe -d "+name+" -u runner -- bash -c mkdir -p '/home/runner' &&") {
		t.Errorf("tarball mode commands missing: %v", exec.calls)
	}

	exec = &recordingExec{}
	shared := newTestWSL(exec, "")
	if _, err := shared.SpawnRunner(ctx, vmSpec()); err != nil {
		t.Fatal(err)
	}
	last := exec.calls[len(exec.calls)-1]
	if !strings.HasPrefix(last, "wsl.exe -d Ubuntu-24.04 -u runner -- bash -c mkdir -p '/home/runner/"+name+"'") ||
		!strings.Contains(last, "touch") || !strings.Contains(last, ".done") {
		t.Errorf("shared mode bootstrap: %s", last)
	}

	spec := vmSpec()
	spec.Arch = "arm64"
	if _, err := newTestWSL(&recordingExec{}, "").SpawnRunner(ctx, spec); err == nil {
		t.Error("other-arch spawn must be refused")
	}
	failImport := &recordingExec{replies: []reply{{prefix: "wsl.exe --import", out: "b\x00a\x00d\x00", err: errBoom}}}
	if _, err := newTestWSL(failImport, `C:\base.tar`).SpawnRunner(ctx, vmSpec()); err == nil || !strings.Contains(err.Error(), "bad") {
		t.Errorf("import failure (UTF-16 output decoded): %v", err)
	}
	failBoot := &recordingExec{replies: []reply{{prefix: "wsl.exe -d", err: errBoom}}}
	spec = vmSpec()
	spec.Arch = "both"
	if _, err := newTestWSL(failBoot, `C:\base.tar`).SpawnRunner(ctx, spec); err == nil || !failBoot.called("wsl.exe --unregister") {
		t.Errorf("bootstrap failure must unregister the distro: %v %v", err, failBoot.calls)
	}
}

func TestWSL_ListStopCleanup(t *testing.T) {
	ctx := context.Background()
	utf16 := func(s string) string {
		var b strings.Builder
		b.WriteString("\xff\xfe")
		for _, r := range s {
			b.WriteRune(r)
			b.WriteByte(0)
		}
		return b.String()
	}
	listing := utf16("  NAME                                      STATE           VERSION\r\n" +
		"* Ubuntu-24.04                              Running         2\r\n" +
		"  runzero-j1-r2-amd64-el-j-repo-x-abc123    Running         2\r\n" +
		"  runzero-j3-r4-amd64-o-r-def456            Stopped         2\r\n" +
		"  runzero-j5-r6-amd64-o-r-ghi789            Installing      2\r\n\r\n")
	exec := &recordingExec{replies: []reply{{prefix: "wsl.exe --list --verbose", out: listing}}}
	d := newTestWSL(exec, `C:\base.tar`)
	runners, err := d.ListRunners(ctx)
	if err != nil || len(runners) != 3 {
		t.Fatalf("list: %v %+v", err, runners)
	}
	status := map[string]string{}
	for _, r := range runners {
		status[r.Name] = r.Status
	}
	if status["runzero-j1-r2-amd64-el-j-repo-x-abc123"] != "running" || status["runzero-j3-r4-amd64-o-r-def456"] != "stopped" || status["runzero-j5-r6-amd64-o-r-ghi789"] != "starting" {
		t.Errorf("statuses: %v", status)
	}
	if err := d.StopRunner(ctx, "runzero-j3-r4-amd64-o-r-def456"); err != nil || !exec.called("wsl.exe --terminate runzero-j3-r4-amd64-o-r-def456") || !exec.called("wsl.exe --unregister runzero-j3-r4-amd64-o-r-def456") {
		t.Fatalf("tarball stop: %v %v", err, exec.calls)
	}
	if err := d.CleanupAll(ctx); err != nil {
		t.Fatal(err)
	}

	failing := &recordingExec{replies: []reply{{prefix: "wsl.exe", err: errBoom}}}
	fd := newTestWSL(failing, `C:\base.tar`)
	if _, err := fd.ListRunners(ctx); err == nil {
		t.Error("list failure must fail")
	}
	if err := fd.StopRunner(ctx, "x"); err == nil {
		t.Error("unregister failure must fail")
	}

	// Shared mode: runners come from the store; the done marker means stopped.
	exec = &recordingExec{replies: []reply{{prefix: "wsl.exe -d Ubuntu-24.04 -- test -e /home/runner/runzero-done", out: ""}, {prefix: "wsl.exe -d Ubuntu-24.04 -- test -e", err: errBoom}}}
	shared := newTestWSL(exec, "")
	shared.store.Register(state.RunnerInfo{ID: "runzero-done", Name: "runzero-done", Backend: KindWSL2, TargetRepo: "o/r"})
	shared.store.Register(state.RunnerInfo{ID: "runzero-busy", Name: "runzero-busy", Backend: KindWSL2})
	shared.store.Register(state.RunnerInfo{ID: "other", Name: "runzero-docker", Backend: KindDocker})
	runners, err = shared.ListRunners(ctx)
	status = map[string]string{}
	for _, r := range runners {
		status[r.Name] = r.Status
	}
	if err != nil || len(runners) != 2 || status["runzero-done"] != "stopped" || status["runzero-busy"] != "running" {
		t.Fatalf("shared list: %v %v", err, status)
	}
	if err := shared.StopRunner(ctx, "runzero-done"); err != nil || !exec.called("wsl.exe -d Ubuntu-24.04 -u root -- bash -c pkill -f '/home/runner/runzero-done'/actions-runner") {
		t.Fatalf("shared stop: %v %v", err, exec.calls)
	}
	if err := newTestWSL(failing, "").StopRunner(ctx, "x"); err == nil {
		t.Error("shared removal failure must fail")
	}

	nd := NewWSLDriver(nil, nil, "Debian", "", "")
	if _, ok := nd.executor.(*OSExecutor); !ok || nd.distroBase != "Debian" || nd.Backend() != KindWSL2 {
		t.Error("unexpected defaults")
	}
}

func TestRouter_SelectsVMDriverForEveryVMBackendName(t *testing.T) {
	docker, vm := &dummyDriver{backend: "docker"}, &dummyDriver{backend: "vm"}
	for _, name := range []string{"orbstack", "orbstack-vm", "vm-orb", "orb", "vm", "wsl2", "multipass"} {
		if got := NewRouter(docker, vm, "auto", false, nil).SelectDriver(RunnerSpec{Backend: name}); got != vm {
			t.Errorf("spec backend %q went to %s", name, got.Backend())
		}
		if got := NewRouter(docker, vm, name, false, nil).SelectDriver(RunnerSpec{}); got != vm {
			t.Errorf("default mode %q went to %s", name, got.Backend())
		}
	}
	if got := NewRouter(docker, vm, "multipass", false, nil).SelectDriver(RunnerSpec{Backend: "container"}); got != docker {
		t.Error("an explicit container backend must use docker")
	}
}
