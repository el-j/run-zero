package driver

import (
	"context"
	"fmt"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestNewOrbStackDriver_Defaults(t *testing.T) {
	o := NewOrbStackDriver(nil, nil, "")
	if o.executor == nil || o.defaultDistro == "" {
		t.Errorf("expected default executor and distro")
	}
}

func TestOrbStackDriver_SpawnRunner(t *testing.T) {
	var calls [][]string
	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			calls = append(calls, args)
			return []byte("ok"), nil
		},
	}

	store := NewInstanceStore("")
	o := NewOrbStackDriver(mock, store, "ubuntu:jammy")
	if o.Backend() != "orbstack" {
		t.Errorf("expected backend orbstack, got %s", o.Backend())
	}

	spec := RunnerSpec{
		ID:        "vm-1",
		Repo:      "org/repo",
		Arch:      "arm64",
		CPUs:      4,
		MemoryMB:  8192,
		ImageName: "golden:rootfs",
	}

	info, err := o.SpawnRunner(context.Background(), spec)
	if err != nil {
		t.Fatalf("unexpected spawn error: %v", err)
	}
	if info.ID != "vm-1" || info.Backend != "orbstack" {
		t.Fatalf("unexpected info: %+v", info)
	}

	if len(calls) < 4 {
		t.Fatalf("expected at least 4 orbctl calls (create, cpu, mem, start), got %d", len(calls))
	}
	if calls[0][0] != "create" || calls[0][1] != "golden:rootfs" || calls[0][2] != "runzero-vm-1" {
		t.Errorf("unexpected create call: %v", calls[0])
	}
}

func TestOrbStackDriver_SpawnRunner_PrefersGoldenBaseWithFallback(t *testing.T) {
	var calls [][]string
	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			calls = append(calls, args)
			if args[0] == "clone" && len(args) >= 2 && args[1] == "runzero-vm-base-arm64" {
				return []byte("base image not found"), fmt.Errorf("not found")
			}
			return []byte("ok"), nil
		},
	}

	o := NewOrbStackDriver(mock, nil, "ubuntu:jammy")
	_, err := o.SpawnRunner(context.Background(), RunnerSpec{
		ID:   "vm-fallback",
		Repo: "org/repo",
		Arch: "arm64",
	})
	if err != nil {
		t.Fatalf("unexpected spawn error: %v", err)
	}

	if len(calls) < 3 {
		t.Fatalf("expected create retries + start sequence, got %d calls", len(calls))
	}
	if calls[0][0] != "clone" || calls[0][1] != "runzero-vm-base-arm64" {
		t.Fatalf("expected first call to clone the golden base, got %v", calls[0])
	}
	if calls[1][0] != "create" || calls[1][1] != "ubuntu:jammy" {
		t.Fatalf("expected fallback create to default distro, got %v", calls[1])
	}
	foundArch := false
	for _, token := range calls[1] {
		if token == "--arch" {
			foundArch = true
			break
		}
	}
	if !foundArch {
		t.Fatalf("expected fallback create call to include --arch, got %v", calls[1])
	}
}

func TestOrbStackDriver_Operations(t *testing.T) {
	listOutput := "runzero-vm-1 running\nrunzero-vm-2 stopped\nother-vm running\n"

	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "list" {
				return []byte(listOutput), nil
			}
			return []byte("deleted"), nil
		},
	}

	store := NewInstanceStore("")
	o := NewOrbStackDriver(mock, store, "")

	runners, err := o.ListRunners(context.Background())
	if err != nil {
		t.Fatalf("unexpected list error: %v", err)
	}
	if len(runners) != 2 {
		t.Fatalf("expected 2 runners, got %d", len(runners))
	}
	if runners[0].ID != "vm-1" || runners[1].ID != "vm-2" {
		t.Errorf("unexpected runners: %+v", runners)
	}

	if err := o.StopRunner(context.Background(), "vm-1"); err != nil {
		t.Fatalf("unexpected stop error: %v", err)
	}
	if err := o.CleanupAll(context.Background()); err != nil {
		t.Fatalf("unexpected cleanup error: %v", err)
	}
}

func TestOrbStackDriver_Errors(t *testing.T) {
	mockErr := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "create" {
				return []byte("failed to create"), fmt.Errorf("create err")
			}
			if args[0] == "start" {
				return []byte("failed to start"), fmt.Errorf("start err")
			}
			return nil, fmt.Errorf("err")
		},
	}

	o := NewOrbStackDriver(mockErr, nil, "")
	_, err := o.SpawnRunner(context.Background(), RunnerSpec{ID: "err"})
	if err == nil || !strings.Contains(err.Error(), "orbctl create failed") {
		t.Fatalf("expected create error, got: %v", err)
	}

	// Test start error
	mockStartErr := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "start" {
				return []byte("failed to start"), fmt.Errorf("start err")
			}
			return []byte("ok"), nil
		},
	}
	o2 := NewOrbStackDriver(mockStartErr, nil, "")
	_, err = o2.SpawnRunner(context.Background(), RunnerSpec{ID: "err-start"})
	if err == nil || !strings.Contains(err.Error(), "orbctl start failed") {
		t.Fatalf("expected start error, got: %v", err)
	}

	_, err = o.ListRunners(context.Background())
	if err == nil {
		t.Fatal("expected error on list failure")
	}

	err = o.StopRunner(context.Background(), "err")
	if err == nil {
		t.Fatal("expected error on stop failure")
	}

	err = o.CleanupAll(context.Background())
	if err == nil {
		t.Fatal("expected error on cleanup failure")
	}
}

func TestOrbStackDriver_ParseLocalRunner(t *testing.T) {
	listOutput := "local-runner-amd64-el-j-herbful-063160 running ubuntu jammy amd64 877.8 MB 192.168.139.219\nomv-dev stopped debian trixie arm64 12.7 GB\n"
	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "list" {
				return []byte(listOutput), nil
			}
			return []byte("ok"), nil
		},
	}
	o := NewOrbStackDriver(mock, nil, "")
	runners, err := o.ListRunners(context.Background())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(runners) != 1 {
		t.Fatalf("expected 1 runner, got %d", len(runners))
	}
	r := runners[0]
	if r.Name != "local-runner-amd64-el-j-herbful-063160" {
		t.Errorf("unexpected name: %s", r.Name)
	}
	if r.TargetRepo != "el-j/herbful" {
		t.Errorf("unexpected repo: %s", r.TargetRepo)
	}
	if r.TargetArch != "amd64" {
		t.Errorf("unexpected arch: %s", r.TargetArch)
	}
	if r.ID != "063160" {
		t.Errorf("unexpected id: %s", r.ID)
	}
}

func TestOrbStackDriver_ParseRunzeroJobScopedRunner(t *testing.T) {
	listOutput := "runzero-j202-r101-amd64-el-j__herbful-063160 running ubuntu jammy amd64 877.8 MB 192.168.139.219\n"
	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "list" {
				return []byte(listOutput), nil
			}
			return []byte("ok"), nil
		},
	}
	o := NewOrbStackDriver(mock, nil, "")
	runners, err := o.ListRunners(context.Background())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(runners) != 1 {
		t.Fatalf("expected 1 runner, got %d", len(runners))
	}
	r := runners[0]
	if r.Name != "runzero-j202-r101-amd64-el-j__herbful-063160" {
		t.Errorf("unexpected name: %s", r.Name)
	}
	if r.TargetRepo != "el-j/herbful" {
		t.Errorf("unexpected repo: %s", r.TargetRepo)
	}
	if r.TargetArch != "amd64" {
		t.Errorf("unexpected arch: %s", r.TargetArch)
	}
	if r.ID != "063160" {
		t.Errorf("unexpected id: %s", r.ID)
	}
}

func TestOrbstackMachineName(t *testing.T) {
	long := orbstackMachineName("runzero-j114507826426-r37108629324-amd64-el-j__landing.inquam-services-fd1de4")
	if len(long) > orbstackMaxMachineName {
		t.Fatalf("name too long (%d): %s", len(long), long)
	}
	if !strings.HasSuffix(long, "fd1de4") {
		t.Fatalf("entropy suffix lost: %s", long)
	}
	for _, r := range long {
		if !(r >= 'a' && r <= 'z') && !(r >= '0' && r <= '9') && r != '-' {
			t.Fatalf("invalid char %q in %s", r, long)
		}
	}
	if got := orbstackMachineName("__.."); got != "runzero" {
		t.Fatalf("empty fallback: %s", got)
	}
}

func TestOrbStackSpawnRunner_EmptyIDDoesNotCollideInStore(t *testing.T) {
	store := NewInstanceStore("")
	o := NewOrbStackDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) { return []byte("ok"), nil }}, store, "")
	for _, n := range []string{"runzero-a", "runzero-b"} {
		if _, err := o.SpawnRunner(context.Background(), RunnerSpec{Name: n, Repo: "el-j/x"}); err != nil {
			t.Fatal(err)
		}
	}
	if got := len(store.List()); got != 2 {
		t.Fatalf("want 2 registered VMs, got %d", got)
	}
}

func TestOrbStackEnrichFromStore_RestoresRepoAndArch(t *testing.T) {
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "runzero-j1-land-abc123", Name: "runzero-j1-land-abc123", TargetRepo: "el-j/landing.inquam-services", TargetArch: "amd64"})
	o := &OrbStackDriver{store: store}
	runners := []state.RunnerInfo{{Name: "runzero-j1-land-abc123"}}
	o.enrichFromStore(runners)
	if runners[0].TargetRepo != "el-j/landing.inquam-services" || runners[0].TargetArch != "amd64" {
		t.Fatalf("repo/arch not restored: %+v", runners[0])
	}
}

func TestRunnerLabels(t *testing.T) {
	got := runnerLabels(RunnerSpec{Labels: []string{"self-hosted", "local", "amd64", "Linux"}, Arch: "amd64"})
	if got != "local,amd64" {
		t.Fatalf("labels = %q, want local,amd64", got)
	}
}

func TestOrbStackSpawnRunner_RegistersRunnerAndCleansUpOnFailure(t *testing.T) {
	var scripts []string
	fail := false
	mock := &mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if name == "orb" {
			scripts = append(scripts, args[len(args)-1])
			if fail {
				return []byte("boom"), fmt.Errorf("exit 1")
			}
		}
		if name == "orbctl" && len(args) > 0 && args[0] == "delete" {
			scripts = append(scripts, "DELETE")
		}
		return []byte("ok"), nil
	}}
	o := NewOrbStackDriver(mock, NewInstanceStore(""), "")
	spec := RunnerSpec{Name: "runzero-x", Repo: "el-j/r", Arch: "amd64", Token: "TOK'EN", Labels: []string{"self-hosted", "local"}}
	if _, err := o.SpawnRunner(context.Background(), spec); err != nil {
		t.Fatal(err)
	}
	if len(scripts) != 1 || !strings.Contains(scripts[0], "--ephemeral") || !strings.Contains(scripts[0], `'TOK'\''EN'`) || !strings.Contains(scripts[0], "/etc/hosts") {
		t.Fatalf("unexpected registration script: %v", scripts)
	}
	scripts, fail = nil, true
	if _, err := o.SpawnRunner(context.Background(), spec); err == nil {
		t.Fatal("expected registration failure")
	}
	if len(scripts) != 2 || scripts[1] != "DELETE" {
		t.Fatalf("VM not deleted after failed registration: %v", scripts)
	}
}

func TestParseOrbctlList_SkipsGoldenBaseImages(t *testing.T) {
	out := "runzero-vm-base-amd64  stopped  ubuntu  noble  amd64\nrunzero-vm-base-arm64-building  running  ubuntu  noble  arm64\nrunzero-j1-r2-amd64-el-j__x-abc123  running  ubuntu  noble  amd64\nomv-dev stopped debian trixie arm64\n"
	got := parseOrbctlList(out)
	if len(got) != 1 || !strings.Contains(got[0].Name, "-j1-r2-") {
		t.Fatalf("want only the job runner, got %+v", got)
	}
}
