package builder

import (
	"context"
	"errors"
	"testing"
)

func TestIsStagingProvisioned(t *testing.T) {
	ctx := context.Background()
	mockSuccess := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte("ok"), nil
		},
	}
	b := NewGoldenBuilder(Config{}, mockSuccess)
	if !b.IsStagingProvisioned(ctx, "vm-staging") {
		t.Fatalf("expected provisioned true")
	}

	mockFail := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return nil, errors.New("exit 1")
		},
	}
	bFail := NewGoldenBuilder(Config{}, mockFail)
	if bFail.IsStagingProvisioned(ctx, "vm-staging") {
		t.Fatalf("expected provisioned false")
	}
}

func TestStopVM(t *testing.T) {
	ctx := context.Background()
	called := false
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && args[0] == "stop" {
				called = true
				return nil, nil
			}
			return nil, nil
		},
	}
	b := NewGoldenBuilder(Config{}, mock)
	_ = b.StopVM(ctx, "my-vm")
	if !called {
		t.Fatalf("expected orbctl stop called")
	}
}

func TestPromoteStaging(t *testing.T) {
	ctx := context.Background()

	// Path 1: Rename succeeds
	renameCalled := false
	mockRename := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && len(args) > 0 && args[0] == "rename" {
				renameCalled = true
				return []byte("ok"), nil
			}
			return []byte("[]"), nil
		},
	}
	b1 := NewGoldenBuilder(Config{}, mockRename)
	if err := b1.PromoteStaging(ctx, "stage", "base"); err != nil || !renameCalled {
		t.Fatalf("expected rename success, got: %v", err)
	}

	// Path 2: Rename fails, clone succeeds
	cloneCalled := false
	mockClone := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && len(args) > 0 && args[0] == "rename" {
				return nil, errors.New("rename locked")
			}
			if name == "orbctl" && len(args) > 0 && args[0] == "clone" {
				cloneCalled = true
				return []byte("ok"), nil
			}
			return []byte("[]"), nil
		},
	}
	b2 := NewGoldenBuilder(Config{}, mockClone)
	if err := b2.PromoteStaging(ctx, "stage", "base"); err != nil || !cloneCalled {
		t.Fatalf("expected clone fallback success, got: %v", err)
	}

	// Path 3: Both fail
	mockBothFail := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && len(args) > 0 && (args[0] == "rename" || args[0] == "clone") {
				return nil, errors.New("disk full")
			}
			return []byte("[]"), nil
		},
	}
	b3 := NewGoldenBuilder(Config{}, mockBothFail)
	if err := b3.PromoteStaging(ctx, "stage", "base"); err == nil {
		t.Fatalf("expected error when both rename and clone fail")
	}
}

func TestEnsureBaseImagesStopped(t *testing.T) {
	ctx := context.Background()
	var stopped []string
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && args[0] == "list" {
				jsonStr := `[
					{"name":"runzero-vm-base-arm64","state":"running"},
					{"name":"runzero-vm-base-amd64","state":"stopped"},
					{"name":"other-job-vm","state":"running"}
				]`
				return []byte(jsonStr), nil
			}
			if name == "orbctl" && args[0] == "stop" {
				stopped = append(stopped, args[1])
				return []byte("ok"), nil
			}
			return nil, nil
		},
	}
	b := NewGoldenBuilder(Config{}, mock)
	halted, err := b.EnsureBaseImagesStopped(ctx)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(halted) != 1 || halted[0] != "runzero-vm-base-arm64" {
		t.Fatalf("expected only running base VM stopped, got: %v", halted)
	}
}
