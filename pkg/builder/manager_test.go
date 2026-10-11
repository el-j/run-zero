package builder

import (
	"context"
	"strings"
	"sync"
	"testing"
	"time"
)

func TestImageInspector_Inspect(t *testing.T) {
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			if name == "orbctl" && len(args) > 0 && args[0] == "list" {
				return []byte(`[{"name":"runzero-vm-base-arm64"},{"name":"other-vm"}]`), nil
			}
			if name == "docker" && len(args) > 0 && args[0] == "images" {
				return []byte("local-github-runner:arm64|img1|1.5GB|2026-10-10\n"), nil
			}
			return nil, nil
		},
	}

	gb := NewGoldenBuilder(Config{
		StateDir:      t.TempDir(),
		RunnerVersion: DefaultRunnerVersion,
	}, mock)

	// Write stamp for arm64
	_ = gb.WriteStamp("arm64")

	ins := NewImageInspector(gb, mock)
	resp := ins.Inspect(context.Background())

	if len(resp.VMImages) != 2 {
		t.Fatalf("expected 2 VM images, got %d", len(resp.VMImages))
	}
	if resp.VMImages[0].Arch != "arm64" || resp.VMImages[0].Status != string(StatusReady) {
		t.Errorf("expected VM arm64 to be ready, got %+v", resp.VMImages[0])
	}
	if resp.VMImages[1].Arch != "amd64" || resp.VMImages[1].Status != "missing" {
		t.Errorf("expected VM amd64 to be missing, got %+v", resp.VMImages[1])
	}

	if len(resp.ContainerImages) != 2 {
		t.Fatalf("expected 2 container images, got %d", len(resp.ContainerImages))
	}
	if resp.ContainerImages[0].Arch != "arm64" || resp.ContainerImages[0].Status != string(StatusReady) {
		t.Errorf("expected container arm64 to be ready, got %+v", resp.ContainerImages[0])
	}
	if resp.ContainerImages[1].Arch != "amd64" || resp.ContainerImages[1].Status != "missing" {
		t.Errorf("expected container amd64 to be missing, got %+v", resp.ContainerImages[1])
	}

	if resp.AllReady {
		t.Error("expected AllReady to be false when some images are missing")
	}
}

func TestBuildManager_TriggerAndCancel(t *testing.T) {
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return nil, nil
		},
	}

	gb := NewGoldenBuilder(Config{
		StateDir:      t.TempDir(),
		RunnerVersion: DefaultRunnerVersion,
	}, mock)

	var mu sync.Mutex
	var loggedLines []string
	logHook := func(line string) {
		mu.Lock()
		loggedLines = append(loggedLines, line)
		mu.Unlock()
	}

	var lastProgress ImageBuildProgress
	progressHook := func(p ImageBuildProgress) {
		mu.Lock()
		lastProgress = p
		mu.Unlock()
	}

	mgr := NewBuildManager(gb, mock, logHook, progressHook)

	// Trigger build for target "container"
	p, err := mgr.TriggerBuild(context.Background(), ImageBuildRequest{
		Target: "container",
		Arch:   "arm64",
	})
	if err != nil {
		t.Fatalf("unexpected trigger error: %v", err)
	}
	if p.Status != string(StatusBuilding) {
		t.Errorf("expected building status, got %s", p.Status)
	}

	// Triggering second build concurrently should error
	_, err2 := mgr.TriggerBuild(context.Background(), ImageBuildRequest{Target: "all"})
	if err2 == nil || !strings.Contains(err2.Error(), "already in progress") {
		t.Errorf("expected already in progress error, got %v", err2)
	}

	// Wait briefly or cancel
	time.Sleep(50 * time.Millisecond)
	err = mgr.CancelBuild()
	if err != nil {
		t.Errorf("unexpected cancel error: %v", err)
	}

	active := mgr.GetActiveBuild()
	if active == nil || active.Status != string(StatusFailed) {
		t.Errorf("expected failed status after cancel, got %+v", active)
	}

	mu.Lock()
	_ = lastProgress
	_ = loggedLines
	mu.Unlock()
}
