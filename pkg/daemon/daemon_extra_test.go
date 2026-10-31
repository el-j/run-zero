package daemon

import (
	"context"
	"net"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
)

func TestNewDaemon_RegistersProvidersFromTokens(t *testing.T) {
	cfg, err := config.LoadConfig(config.MapEnv{
		"DASHBOARD_ENABLED": "false",
		"ACCESS_TOKEN":      "gh-token",
		"GITLAB_TOKEN":      "gl-token",
		"GITLAB_GROUP":      "grp",
		"GITLAB_PROJECTS":   " a/b, ,c/d ",
	})
	if err != nil {
		t.Fatal(err)
	}

	d := NewDaemon(cfg, "v1", "", "")

	if d.Scaler() == nil {
		t.Fatal("expected scaler")
	}
	mgr := d.Scaler().providerMgr
	if _, ok := mgr.Get("github"); !ok {
		t.Error("expected github provider from ACCESS_TOKEN")
	}
	if _, ok := mgr.Get("gitlab"); !ok {
		t.Error("expected gitlab provider from GITLAB_TOKEN")
	}
}

func TestNewDaemon_ProvidersFile(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "providers.json")
	body := `{"providers":[
		{"id":"gh-extra","type":"github","url":"https://api.example.test","token":"t","owner":"me"},
		{"id":"gl-extra","type":"GitLab","url":"https://gl.example.test","token":"t","group":"g","projects":["x/y"]},
		{"id":"other","type":"gitea"}]}`
	if err := os.WriteFile(path, []byte(body), 0o600); err != nil {
		t.Fatal(err)
	}
	cfg, err := config.LoadConfig(config.MapEnv{"DASHBOARD_ENABLED": "false", "PROVIDERS_CONFIG": path})
	if err != nil {
		t.Fatal(err)
	}

	d := NewDaemon(cfg, "v1", "", "")

	if n := len(d.Scaler().providerMgr.All()); n != 2 {
		t.Fatalf("expected github+gitlab adapters (unknown type ignored), got %d", n)
	}
}

func TestNewDaemon_MissingProvidersFileIsIgnored(t *testing.T) {
	cfg, err := config.LoadConfig(config.MapEnv{"DASHBOARD_ENABLED": "false", "PROVIDERS_CONFIG": filepath.Join(t.TempDir(), "nope.json")})
	if err != nil {
		t.Fatal(err)
	}
	d := NewDaemon(cfg, "v1", "", "")
	if n := len(d.Scaler().providerMgr.All()); n != 0 {
		t.Fatalf("expected no providers, got %d", n)
	}
}

func TestDaemon_RunWithoutScalerUsesPoller(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{"DASHBOARD_ENABLED": "false"})
	d := NewDaemon(cfg, "v1", "", "")
	d.scaler = nil

	ctx, cancel := context.WithCancel(context.Background())
	errCh := make(chan error, 1)
	go func() { errCh <- d.Run(ctx) }()
	time.Sleep(30 * time.Millisecond)
	cancel()

	select {
	case err := <-errCh:
		if err != nil {
			t.Fatalf("Run: %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("Run did not exit")
	}
}

func TestDaemon_RunWithoutScalerOrPoller(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{"DASHBOARD_ENABLED": "false"})
	d := NewDaemon(cfg, "v1", "", "")
	d.scaler, d.poller = nil, nil

	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if err := d.Run(ctx); err != nil {
		t.Fatalf("Run: %v", err)
	}
}

// A client holding the live event stream open keeps Shutdown from finishing
// inside Stop's grace period, so Stop must surface the shutdown error.
func TestDaemon_StopReportsShutdownTimeout(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{"DASHBOARD_PORT": "0", "DASHBOARD_HOST": "127.0.0.1"})
	d := NewDaemon(cfg, "v1", "", "")
	if err := d.Start(); err != nil {
		t.Fatal(err)
	}

	conn, err := net.Dial("tcp", d.Server().Addr())
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = conn.Close() }()
	if _, err := conn.Write([]byte("GET /api/stream HTTP/1.1\r\nHost: localhost\r\n\r\n")); err != nil {
		t.Fatal(err)
	}
	buf := make([]byte, 64)
	_ = conn.SetReadDeadline(time.Now().Add(2 * time.Second))
	if _, err := conn.Read(buf); err != nil {
		t.Fatalf("stream did not start: %v", err)
	}

	if err := d.Stop(); err == nil {
		t.Fatal("expected shutdown timeout error while a stream is open")
	}
}

func TestNewDaemon_DefaultStateDir(t *testing.T) {
	t.Setenv("RUNZERO_STATE_DIR", "")
	t.Chdir(t.TempDir())
	cfg, _ := config.LoadConfig(config.MapEnv{"DASHBOARD_ENABLED": "false"})
	if d := NewDaemon(cfg, "v1", "", ""); d.InstanceStore() == nil {
		t.Fatal("expected instance store")
	}
}

func TestInitDriver_UsesBridgeWhenConfigured(t *testing.T) {
	t.Setenv("HOST_VM_BRIDGE_URL", "http://127.0.0.1:1")
	t.Setenv("RUNZERO_BRIDGE_TOKEN", "secret")
	cfg, _ := config.LoadConfig(config.MapEnv{})

	drv := initDriver(cfg, driver.NewInstanceStore(filepath.Join(t.TempDir(), "i.json")))

	if drv == nil {
		t.Fatal("expected router driver")
	}
}
