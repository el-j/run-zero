package api

import (
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

func setupTestServer(t *testing.T) (*Server, *config.Config, *state.State, string, string) {
	tmpDist := t.TempDir()
	tmpStatic := t.TempDir()

	_ = os.WriteFile(filepath.Join(tmpDist, "index.html"), []byte("<html>dist index</html>"), 0644)
	_ = os.MkdirAll(filepath.Join(tmpDist, "assets"), 0755)
	_ = os.WriteFile(filepath.Join(tmpDist, "assets", "style.css"), []byte("body{color:red;}"), 0644)
	_ = os.WriteFile(filepath.Join(tmpDist, "assets", "script.js"), []byte("console.log('test');"), 0644)
	_ = os.MkdirAll(filepath.Join(tmpDist, "fonts"), 0755)
	_ = os.WriteFile(filepath.Join(tmpDist, "fonts", "test-font.woff2"), []byte("woff2-data"), 0644)

	_ = os.WriteFile(filepath.Join(tmpStatic, "index.html"), []byte("<html>static index</html>"), 0644)
	_ = os.WriteFile(filepath.Join(tmpStatic, "dashboard.css"), []byte("/* css */"), 0644)
	_ = os.WriteFile(filepath.Join(tmpStatic, "dashboard.js"), []byte("// js"), 0644)

	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "0",
		"DASHBOARD_HOST": "127.0.0.1",
	})
	st := state.NewState(4, "v1.0.0", nil)

	srv := NewServer(cfg, st, tmpDist, tmpStatic, []string{"127.0.0.1", "localhost"}, 50*time.Millisecond)
	if err := srv.Start(); err != nil {
		t.Fatalf("failed to start server: %v", err)
	}

	return srv, cfg, st, tmpDist, tmpStatic
}
