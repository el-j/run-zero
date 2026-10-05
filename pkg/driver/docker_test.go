package driver

import (
	"context"
	"fmt"
	"strings"
	"testing"
)

type mockCmdExecutor struct {
	runFunc      func(ctx context.Context, name string, args ...string) ([]byte, error)
	lookPathFunc func(file string) (string, error)
}

func (m *mockCmdExecutor) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
	if m.runFunc != nil {
		return m.runFunc(ctx, name, args...)
	}
	return []byte("ok"), nil
}

func (m *mockCmdExecutor) LookPath(file string) (string, error) {
	if m.lookPathFunc != nil {
		return m.lookPathFunc(file)
	}
	return "/usr/bin/" + file, nil
}

func TestNewDockerDriver_Defaults(t *testing.T) {
	d := NewDockerDriver(nil, nil, "", "")
	if d.executor == nil || d.defaultImage == "" {
		t.Errorf("expected default executor and image")
	}
}

func TestDockerDriver_SpawnRunner(t *testing.T) {
	var executedArgs []string
	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "docker" && args[0] == "run" {
				executedArgs = args
				return []byte("container-12345"), nil
			}
			return []byte(""), nil
		},
	}

	store := NewInstanceStore("")
	d := NewDockerDriver(mock, store, "default-runner:latest", "runzero-net")
	if d.Backend() != "docker" {
		t.Errorf("expected backend docker, got %s", d.Backend())
	}

	spec := RunnerSpec{
		ID:        "inst-1",
		Repo:      "org/repo",
		Arch:      "arm64",
		CPUs:      2,
		MemoryMB:  4096,
		CacheDir:  "/tmp/cache",
		Network:   "custom-net",
		Env:       map[string]string{"RUNNER_TOKEN": "abc"},
		ImageName: "custom-img:tag",
	}

	info, err := d.SpawnRunner(context.Background(), spec)
	if err != nil {
		t.Fatalf("unexpected spawn error: %v", err)
	}
	if info.ID != "inst-1" || info.Backend != "docker" {
		t.Fatalf("unexpected info: %+v", info)
	}

	joined := strings.Join(executedArgs, " ")
	if !strings.Contains(joined, "--cpus=2") || !strings.Contains(joined, "-m=4096m") || !strings.Contains(joined, "--network custom-net") {
		t.Errorf("expected cpus, memory, network in args, got: %s", joined)
	}
	if !strings.Contains(joined, "-v /tmp/cache:/cache:rw") {
		t.Errorf("expected cache volume mount in args, got: %s", joined)
	}
	if !strings.Contains(joined, "custom-img:tag") {
		t.Errorf("expected custom-img in args, got: %s", joined)
	}
}

func TestDockerDriver_Operations(t *testing.T) {
	psOutput := "c1\trunzero-inst-1\tUp 10m\trunning\torg/repo\tinst-1\n" +
		"c2\trunzero-inst-2\tExited (0)\tstopped\torg/repo2\tinst-2\n"

	mock := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if args[0] == "ps" {
				return []byte(psOutput), nil
			}
			return []byte("deleted"), nil
		},
	}

	store := NewInstanceStore("")
	d := NewDockerDriver(mock, store, "", "")

	runners, err := d.ListRunners(context.Background())
	if err != nil {
		t.Fatalf("unexpected list error: %v", err)
	}
	if len(runners) != 2 {
		t.Fatalf("expected 2 runners, got %d", len(runners))
	}
	if runners[0].ID != "inst-1" || runners[0].TargetRepo != "org/repo" {
		t.Errorf("unexpected runner 0: %+v", runners[0])
	}

	if err := d.StopRunner(context.Background(), "inst-1"); err != nil {
		t.Fatalf("unexpected stop error: %v", err)
	}
	if err := d.CleanupAll(context.Background()); err != nil {
		t.Fatalf("unexpected cleanup error: %v", err)
	}
}

func TestDockerDriver_Errors(t *testing.T) {
	mockErr := &mockCmdExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte("permission denied"), fmt.Errorf("exit 1")
		},
	}

	d := NewDockerDriver(mockErr, nil, "", "")
	_, err := d.SpawnRunner(context.Background(), RunnerSpec{ID: "err"})
	if err == nil {
		t.Fatal("expected error on spawn failure")
	}

	_, err = d.ListRunners(context.Background())
	if err == nil {
		t.Fatal("expected error on list failure")
	}

	err = d.StopRunner(context.Background(), "err")
	if err == nil {
		t.Fatal("expected error on stop failure")
	}

	err = d.CleanupAll(context.Background())
	if err == nil {
		t.Fatal("expected error on cleanup failure")
	}
}
