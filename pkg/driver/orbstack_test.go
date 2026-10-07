package driver

import (
	"context"
	"fmt"
	"strings"
	"testing"
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
