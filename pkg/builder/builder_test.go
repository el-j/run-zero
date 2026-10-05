package builder

import (
	"context"
	"os"
	"strings"
	"testing"
)

type mockExecutor struct {
	runFunc func(ctx context.Context, name string, args ...string) ([]byte, error)
}

func (m *mockExecutor) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
	if m.runFunc != nil {
		return m.runFunc(ctx, name, args...)
	}
	return nil, nil
}

func (m *mockExecutor) LookPath(file string) (string, error) {
	return file, nil
}

func TestGoldenBuilder_MetadataAndStamps(t *testing.T) {
	tmp := t.TempDir()
	builder := NewGoldenBuilder(Config{
		StateDir:      tmp,
		RunnerVersion: "2.337.0",
	}, nil)

	if builder.BaseImageName("arm64") != "runzero-vm-base-arm64" {
		t.Fatalf("unexpected base image name: %s", builder.BaseImageName("arm64"))
	}
	if builder.StagingImageName("arm64") != "runzero-vm-base-arm64-building" {
		t.Fatalf("unexpected staging name: %s", builder.StagingImageName("arm64"))
	}

	// Missing stamp is stale
	if !builder.IsStale("arm64") {
		t.Fatalf("expected missing stamp to be stale")
	}

	// Write stamp
	if err := builder.WriteStamp("arm64"); err != nil {
		t.Fatalf("unexpected write error: %v", err)
	}
	if builder.IsStale("arm64") {
		t.Fatalf("expected matching stamp not to be stale")
	}

	// Mutate stamp to older version
	_ = os.WriteFile(builder.StampPath("arm64"), []byte("2.300.0\n"), 0644)
	if !builder.IsStale("arm64") {
		t.Fatalf("expected outdated stamp to be stale")
	}

	// Events channel
	ch := builder.Events()
	builder.EmitEvent(StatusReady, "arm64", "ready test")
	select {
	case evt := <-ch:
		if evt.Status != StatusReady || evt.Arch != "arm64" {
			t.Fatalf("unexpected event: %+v", evt)
		}
	default:
		t.Fatalf("expected event in channel")
	}
}

func TestGoldenBuilder_ListVMsAndExists(t *testing.T) {
	ctx := context.Background()
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte(`[{"name":"runzero-vm-base-arm64","state":"stopped"},{"name":"other-vm","state":"running"}]`), nil
		},
	}
	builder := NewGoldenBuilder(Config{}, mock)
	vms, err := builder.ListVMs(ctx)
	if err != nil || len(vms) != 2 {
		t.Fatalf("unexpected list: %v, err: %v", vms, err)
	}

	if !builder.BaseImageExists(ctx, "arm64") {
		t.Fatalf("expected arm64 base image to exist")
	}
	if builder.BaseImageExists(ctx, "amd64") {
		t.Fatalf("expected amd64 base image to not exist")
	}
}

func TestTemplates(t *testing.T) {
	docker := DockerEngineSnippet()
	if !strings.Contains(docker, "cgroupdriver=cgroupfs") {
		t.Fatalf("expected cgroupfs in docker snippet")
	}

	runnerArm := RunnerDownloadSnippet("arm64", "")
	if !strings.Contains(runnerArm, "actions-runner-linux-arm64-2.337.0.tar.gz") {
		t.Fatalf("unexpected arm64 snippet: %s", runnerArm)
	}

	runnerX64 := RunnerDownloadSnippet("amd64", "2.338.0")
	if !strings.Contains(runnerX64, "actions-runner-linux-x64-2.338.0.tar.gz") {
		t.Fatalf("unexpected x64 snippet: %s", runnerX64)
	}

	full := FullProvisionScript("arm64", "2.337.0", "echo custom")
	if !strings.Contains(full, "echo custom") || !strings.Contains(full, "provisioning complete") {
		t.Fatalf("unexpected full script: %s", full)
	}
}
