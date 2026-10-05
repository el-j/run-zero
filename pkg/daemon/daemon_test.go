package daemon

import (
	"context"
	"syscall"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
)

func TestDaemon_Lifecycle(t *testing.T) {
	cfg, err := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "0",
		"DASHBOARD_HOST": "127.0.0.1",
		"REPO_PRIORITY":  "org/repo-prio,org/repo2",
		"REPOS":          "org/repo-prio,org/repo2",
	})
	if err != nil {
		t.Fatalf("LoadConfig error: %v", err)
	}

	d := NewDaemon(cfg, "v1.0.0", "", "")
	if d.Config() == nil || d.State() == nil || d.Server() == nil || d.PriorityManager() == nil || d.Poller() == nil {
		t.Fatal("expected non-nil config, state, server, priority manager, and poller")
	}

	if err := d.Start(); err != nil {
		t.Fatalf("Start error: %v", err)
	}

	if err := d.Stop(); err != nil {
		t.Fatalf("Stop error: %v", err)
	}

	if d.State().GetSnapshot().AutoscalerStatus != "stopped" {
		t.Errorf("expected stopped autoscaler status")
	}
}

func TestDaemon_RunAndCancel(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "0",
		"DASHBOARD_HOST": "127.0.0.1",
	})

	d := NewDaemon(cfg, "v1.0.0", "", "")

	ctx, cancel := context.WithCancel(context.Background())

	errCh := make(chan error, 1)
	go func() {
		errCh <- d.Run(ctx)
	}()

	time.Sleep(50 * time.Millisecond)
	cancel()

	select {
	case err := <-errCh:
		if err != nil {
			t.Fatalf("Run returned error: %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("Run did not exit within timeout")
	}
}

func TestDaemon_DisabledDashboard(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_ENABLED": "false",
	})

	d := NewDaemon(cfg, "v1.0.0", "", "")
	if d.Server() != nil {
		t.Error("expected nil server when dashboard is disabled")
	}

	if err := d.Start(); err != nil {
		t.Fatalf("Start error with disabled dashboard: %v", err)
	}
	if err := d.Stop(); err != nil {
		t.Fatalf("Stop error with disabled dashboard: %v", err)
	}
}

func TestDaemon_StartError(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_HOST": "999.999.999.999",
	})

	d := NewDaemon(cfg, "v1.0.0", "", "")
	if err := d.Start(); err == nil {
		t.Error("expected error starting with invalid host")
	}

	ctx := context.Background()
	if err := d.Run(ctx); err == nil {
		t.Error("expected error from Run when Start fails")
	}
}

func TestDaemon_Signals(t *testing.T) {
	sigs := DefaultSignals()
	if len(sigs) != 2 || sigs[0] != syscall.SIGINT || sigs[1] != syscall.SIGTERM {
		t.Errorf("unexpected default signals: %v", sigs)
	}

	ctx, cancel := SignalContext(context.Background())
	defer cancel()
	if ctx == nil {
		t.Fatal("expected non-nil context from SignalContext")
	}
}
