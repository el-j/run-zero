package builder

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"testing"
)

func TestBuildBaseImage_AlreadyBuiltNotStale(t *testing.T) {
	ctx := context.Background()
	tmp := t.TempDir()

	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte(`[{"name":"runzero-vm-base-arm64","state":"stopped"}]`), nil
		},
	}
	b := NewGoldenBuilder(Config{
		StateDir:      tmp,
		RunnerVersion: "2.337.0",
	}, mock)

	_ = b.WriteStamp("arm64")

	rebuilt, err := b.BuildBaseImage(ctx, "arm64")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if rebuilt {
		t.Fatalf("expected rebuilt=false when already built and not stale")
	}
}

func TestBuildBaseImage_Success(t *testing.T) {
	ctx := context.Background()
	tmp := t.TempDir()
	provScript := filepath.Join(tmp, "provision.sh")
	_ = os.WriteFile(provScript, []byte("echo install custom deps"), 0644)

	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && args[0] == "list" {
				return []byte(`[]`), nil
			}
			return []byte("ok"), nil
		},
	}
	b := NewGoldenBuilder(Config{
		StateDir:            tmp,
		RunnerVersion:       "2.337.0",
		CPUs:                "4",
		Memory:              "8G",
		ProvisionScriptPath: provScript,
	}, mock)

	rebuilt, err := b.BuildBaseImage(ctx, "arm64")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !rebuilt {
		t.Fatalf("expected rebuilt=true")
	}
	if b.IsStale("arm64") {
		t.Fatalf("expected fresh stamp written")
	}
}

func TestBuildBaseImage_CreateFail(t *testing.T) {
	ctx := context.Background()
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && args[0] == "list" {
				return []byte(`[]`), nil
			}
			if name == "orbctl" && args[0] == "create" {
				return nil, errors.New("cannot create VM")
			}
			return []byte("ok"), nil
		},
	}
	b := NewGoldenBuilder(Config{StateDir: t.TempDir()}, mock)
	rebuilt, err := b.BuildBaseImage(ctx, "arm64")
	if err == nil || rebuilt {
		t.Fatalf("expected error on create failure")
	}
}

func TestBuildBaseImage_ProvisionFail(t *testing.T) {
	ctx := context.Background()
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && args[0] == "list" {
				return []byte(`[]`), nil
			}
			if name == "orb" {
				return nil, errors.New("script failed with exit 1")
			}
			return []byte("ok"), nil
		},
	}
	b := NewGoldenBuilder(Config{StateDir: t.TempDir()}, mock)
	rebuilt, err := b.BuildBaseImage(ctx, "arm64")
	if err == nil || rebuilt {
		t.Fatalf("expected error on provision failure")
	}
}
