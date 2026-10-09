package api

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

type nonFlusherWriter struct {
	http.ResponseWriter
}

func TestServer_StaticAssetRoutes(t *testing.T) {
	srv, _, _, tmpDist, tmpStatic := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	respIndex, err := http.Get("http://" + addr + "/")
	if err != nil || respIndex.StatusCode != http.StatusOK {
		t.Fatalf("GET / failed: %v", err)
	}

	respCSS, _ := http.Get("http://" + addr + "/assets/style.css")
	if respCSS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for assets/style.css, got %d", respCSS.StatusCode)
	}
	respJS, _ := http.Get("http://" + addr + "/assets/script.js")
	if respJS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for assets/script.js, got %d", respJS.StatusCode)
	}

	respFont, _ := http.Get("http://" + addr + "/fonts/test-font.woff2")
	if respFont.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for test-font.woff2, got %d", respFont.StatusCode)
	}

	respFaviconSVG, _ := http.Get("http://" + addr + "/favicon.svg")
	if respFaviconSVG.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for favicon.svg, got %d", respFaviconSVG.StatusCode)
	}
	respFaviconICO, _ := http.Get("http://" + addr + "/favicon.ico")
	if respFaviconICO.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for favicon.ico, got %d", respFaviconICO.StatusCode)
	}
	respAppIcon, _ := http.Get("http://" + addr + "/icon.svg")
	if respAppIcon.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for icon.svg, got %d", respAppIcon.StatusCode)
	}

	respBadFont1, _ := http.Get("http://" + addr + "/fonts/../bad.woff2")
	if respBadFont1.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on font traversal, got %d", respBadFont1.StatusCode)
	}
	respBadFont2, _ := http.Get("http://" + addr + "/fonts/font.ttf")
	if respBadFont2.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on non-woff2 font, got %d", respBadFont2.StatusCode)
	}

	respBadAsset, _ := http.Get("http://" + addr + "/assets/../bad.css")
	if respBadAsset.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on asset traversal, got %d", respBadAsset.StatusCode)
	}
	respMissingAsset, _ := http.Get("http://" + addr + "/assets/missing.css")
	if respMissingAsset.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on missing asset, got %d", respMissingAsset.StatusCode)
	}

	respLegacyCSS, _ := http.Get("http://" + addr + "/dashboard.css")
	if respLegacyCSS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on dashboard.css, got %d", respLegacyCSS.StatusCode)
	}
	respLegacyJS, _ := http.Get("http://" + addr + "/dashboard.js")
	if respLegacyJS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on dashboard.js, got %d", respLegacyJS.StatusCode)
	}

	_ = os.Remove(filepath.Join(tmpDist, "index.html"))
	respFallback, _ := http.Get("http://" + addr + "/index.html")
	if respFallback.StatusCode != http.StatusOK {
		t.Errorf("expected fallback to static index.html, got %d", respFallback.StatusCode)
	}

	_ = os.Remove(filepath.Join(tmpStatic, "index.html"))
	respNoIndex, _ := http.Get("http://" + addr + "/")
	if respNoIndex.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 when no index exists, got %d", respNoIndex.StatusCode)
	}

	resp404, _ := http.Get("http://" + addr + "/does-not-exist")
	if resp404.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on unknown route, got %d", resp404.StatusCode)
	}

	respUnsupportedRootAsset, _ := http.Get("http://" + addr + "/favicon.gif")
	if respUnsupportedRootAsset.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on unsupported root asset type, got %d", respUnsupportedRootAsset.StatusCode)
	}
}

func TestServer_EdgeCases(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "49505",
		"DASHBOARD_HOST": "127.0.0.1",
	})
	st := state.NewState(2, "v1.0.0", nil)

	srv := NewServer(cfg, st, "", "", nil, time.Second)
	if srv.Addr() != "127.0.0.1:49505" {
		t.Errorf("expected 127.0.0.1:49505 before start, got %s", srv.Addr())
	}

	badCfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "49505",
		"DASHBOARD_HOST": "999.999.999.999",
	})
	badSrv := NewServer(badCfg, st, "", "", nil, time.Second)
	if err := badSrv.Start(); err == nil {
		t.Error("expected start error with invalid IP")
	}

	handler := handleSSEStream(st, 0)
	req := httptest.NewRequest("GET", "/api/stream", nil)
	rec := httptest.NewRecorder()
	handler.ServeHTTP(&nonFlusherWriter{rec}, req)
	if rec.Code != http.StatusInternalServerError {
		t.Errorf("expected 500 for non-flusher, got %d", rec.Code)
	}

	prioHandler := handleRepoPriority(st)
	reqPrio := httptest.NewRequest("POST", "/api/actions/repo-priority", strings.NewReader("{}"))
	recPrio := httptest.NewRecorder()
	prioHandler.ServeHTTP(recPrio, reqPrio)
	if recPrio.Code != http.StatusOK {
		t.Errorf("expected 200 for empty priority object, got %d", recPrio.Code)
	}

	tmpDir := t.TempDir()
	_ = os.MkdirAll(filepath.Join(tmpDir, "assets"), 0755)
	_ = os.WriteFile(filepath.Join(tmpDir, "assets", "image.png"), []byte("png"), 0644)
	staticHandler := handleStatic(tmpDir, tmpDir)
	recAsset := httptest.NewRecorder()
	reqAsset := httptest.NewRequest("GET", "/assets/image.png", nil)
	staticHandler.ServeHTTP(recAsset, reqAsset)
	if recAsset.Code != http.StatusOK {
		t.Errorf("expected 200 for png asset, got %d", recAsset.Code)
	}

	recMissing := httptest.NewRecorder()
	reqMissing := httptest.NewRequest("GET", "/dashboard.css", nil)
	staticHandler.ServeHTTP(recMissing, reqMissing)
	if recMissing.Code != http.StatusNotFound {
		t.Errorf("expected 404 for missing legacy css, got %d", recMissing.Code)
	}
}
