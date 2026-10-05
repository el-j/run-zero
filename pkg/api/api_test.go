package api

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
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

func TestServer_HostHeaderAndCORS(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()
	url := "http://" + addr + "/api/status"

	// OPTIONS preflight
	reqOpt, _ := http.NewRequest(http.MethodOptions, url, nil)
	respOpt, err := http.DefaultClient.Do(reqOpt)
	if err != nil || respOpt.StatusCode != http.StatusNoContent {
		t.Fatalf("expected 204 for OPTIONS, got err=%v, code=%v", err, respOpt.StatusCode)
	}

	// Allowed host
	reqOk, _ := http.NewRequest(http.MethodGet, url, nil)
	respOk, err := http.DefaultClient.Do(reqOk)
	if err != nil || respOk.StatusCode != http.StatusOK {
		t.Fatalf("expected 200 for allowed host, got err=%v, code=%v", err, respOk.StatusCode)
	}

	// Rejected host
	reqBad, _ := http.NewRequest(http.MethodGet, url, nil)
	reqBad.Host = "evil.attacker.com"
	respBad, err := http.DefaultClient.Do(reqBad)
	if err != nil || respBad.StatusCode != http.StatusMisdirectedRequest {
		t.Fatalf("expected 421 for rejected host, got err=%v, code=%v", err, respBad.StatusCode)
	}

	// Default loopback allowance when allowedHosts is empty
	h := CheckHostHeader(nil)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	rec1 := httptest.NewRecorder()
	reqLoopback := httptest.NewRequest("GET", "/api/status", nil)
	reqLoopback.Host = "127.0.0.1:49505"
	h.ServeHTTP(rec1, reqLoopback)
	if rec1.Code != http.StatusOK {
		t.Errorf("expected 200 for 127.0.0.1 loopback default, got %d", rec1.Code)
	}

	rec2 := httptest.NewRecorder()
	reqBadHost := httptest.NewRequest("GET", "/api/status", nil)
	reqBadHost.Host = "random.domain.com"
	h.ServeHTTP(rec2, reqBadHost)
	if rec2.Code != http.StatusMisdirectedRequest {
		t.Errorf("expected 421 for random host, got %d", rec2.Code)
	}
}

func TestServer_FleetAndLogs(t *testing.T) {
	srv, _, st, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	// GET /api/fleet
	resp, err := http.Get("http://" + addr + "/api/fleet")
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/fleet failed: %v, code=%d", err, resp.StatusCode)
	}
	var fleet state.FleetState
	_ = json.NewDecoder(resp.Body).Decode(&fleet)
	if fleet.MaxRunners != 4 {
		t.Errorf("expected max_runners=4, got %d", fleet.MaxRunners)
	}

	// POST /api/fleet not allowed
	respPost, _ := http.Post("http://"+addr+"/api/fleet", "application/json", nil)
	if respPost.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/fleet, got %d", respPost.StatusCode)
	}

	// Logs
	st.AppendLog("system test log")
	respLogs, err := http.Get("http://" + addr + "/api/logs")
	if err != nil || respLogs.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/logs failed: %v", err)
	}
	var logsResp map[string][]state.LogEntry
	_ = json.NewDecoder(respLogs.Body).Decode(&logsResp)
	if len(logsResp["logs"]) == 0 {
		t.Errorf("expected logs, got none")
	}

	respLogsBad, _ := http.Post("http://"+addr+"/api/logs", "application/json", nil)
	if respLogsBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/logs, got %d", respLogsBad.StatusCode)
	}
}

func TestServer_Settings(t *testing.T) {
	srv, cfg, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()
	url := "http://" + addr + "/api/settings"

	// GET /api/settings
	resp, err := http.Get(url)
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/settings failed: %v", err)
	}

	// POST /api/settings - valid mutation
	newMax := 8
	newMin := 2
	newPoll := 15
	payload := SettingsPayload{
		MaxRunners:   &newMax,
		MinRunners:   &newMin,
		PollInterval: &newPoll,
	}
	body, _ := json.Marshal(payload)
	respPost, err := http.Post(url, "application/json", bytes.NewReader(body))
	if err != nil || respPost.StatusCode != http.StatusOK {
		t.Fatalf("POST /api/settings failed: %v, code=%d", err, respPost.StatusCode)
	}
	if cfg.MaxRunners != 8 || cfg.MinRunners != 2 || cfg.PollInterval != 15 {
		t.Errorf("expected updated config values, got max=%d, min=%d, poll=%d", cfg.MaxRunners, cfg.MinRunners, cfg.PollInterval)
	}

	// POST /api/settings - invalid max_runners (< 1)
	badMax := 0
	badBody, _ := json.Marshal(SettingsPayload{MaxRunners: &badMax})
	respBadMax, _ := http.Post(url, "application/json", bytes.NewReader(badBody))
	if respBadMax.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for max_runners < 1, got %d", respBadMax.StatusCode)
	}

	// POST /api/settings - min > max
	badMin := 10
	badBody2, _ := json.Marshal(SettingsPayload{MinRunners: &badMin})
	respBadMin, _ := http.Post(url, "application/json", bytes.NewReader(badBody2))
	if respBadMin.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for min > max, got %d", respBadMin.StatusCode)
	}

	// POST /api/settings - min < 0
	negMin := -1
	badBodyNeg, _ := json.Marshal(SettingsPayload{MinRunners: &negMin})
	respBadNeg, _ := http.Post(url, "application/json", bytes.NewReader(badBodyNeg))
	if respBadNeg.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for min < 0, got %d", respBadNeg.StatusCode)
	}

	// POST /api/settings - bad poll interval
	badPoll := 5000
	badBody3, _ := json.Marshal(SettingsPayload{PollInterval: &badPoll})
	respBadPoll, _ := http.Post(url, "application/json", bytes.NewReader(badBody3))
	if respBadPoll.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for poll > 3600, got %d", respBadPoll.StatusCode)
	}

	// POST /api/settings - other fields update
	autoDisc := false
	autoRoute := false
	proxies := false
	cache := false
	otherPayload := SettingsPayload{
		AutoDiscover:   &autoDisc,
		AutoRouteVM:    &autoRoute,
		ProxiesEnabled: &proxies,
		CacheEnabled:   &cache,
	}
	otherBody, _ := json.Marshal(otherPayload)
	respOther, _ := http.Post(url, "application/json", bytes.NewReader(otherBody))
	if respOther.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for other fields update, got %d", respOther.StatusCode)
	}

	// Bad JSON
	respBadJSON, _ := http.Post(url, "application/json", strings.NewReader("bad-json{"))
	if respBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json, got %d", respBadJSON.StatusCode)
	}

	// Method not allowed
	reqDel, _ := http.NewRequest(http.MethodDelete, url, nil)
	respDel, _ := http.DefaultClient.Do(reqDel)
	if respDel.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on DELETE, got %d", respDel.StatusCode)
	}
}

func TestServer_CacheHandlers(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	// GET /api/cache
	resp, err := http.Get("http://" + addr + "/api/cache")
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/cache failed: %v", err)
	}

	respCacheBad, _ := http.Post("http://"+addr+"/api/cache", "application/json", nil)
	if respCacheBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/cache, got %d", respCacheBad.StatusCode)
	}

	// POST /api/cache/purge
	purgeBody, _ := json.Marshal(CachePurgePayload{Category: "npm"})
	respPurge, err := http.Post("http://"+addr+"/api/cache/purge", "application/json", bytes.NewReader(purgeBody))
	if err != nil || respPurge.StatusCode != http.StatusOK {
		t.Fatalf("POST /api/cache/purge failed: %v", err)
	}

	// POST /api/cache/purge with all=true
	purgeAll, _ := json.Marshal(CachePurgePayload{All: true})
	respPurgeAll, _ := http.Post("http://"+addr+"/api/cache/purge", "application/json", bytes.NewReader(purgeAll))
	if respPurgeAll.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on purge all, got %d", respPurgeAll.StatusCode)
	}

	respPurgeBad, _ := http.Get("http://" + addr + "/api/cache/purge")
	if respPurgeBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET /api/cache/purge, got %d", respPurgeBad.StatusCode)
	}

	// Legacy clean-cache
	cleanBody, _ := json.Marshal(map[string]string{"category": "npm"})
	respClean, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", bytes.NewReader(cleanBody))
	if respClean.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on clean-cache, got %d", respClean.StatusCode)
	}

	// Legacy clean-cache non-string category
	badCleanBody, _ := json.Marshal(map[string]int{"category": 123})
	respBadClean, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", bytes.NewReader(badCleanBody))
	if respBadClean.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for non-string category, got %d", respBadClean.StatusCode)
	}

	// Legacy clean-cache bad JSON
	respBadCleanJSON, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", strings.NewReader("bad{{{"))
	if respBadCleanJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json in clean-cache, got %d", respBadCleanJSON.StatusCode)
	}

	respCleanBadMethod, _ := http.Get("http://" + addr + "/api/actions/clean-cache")
	if respCleanBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET clean-cache, got %d", respCleanBadMethod.StatusCode)
	}
}

func TestServer_Actions(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	// Repo priority
	prioBody, _ := json.Marshal(RepoPriorityPayload{Priority: []string{"repo1"}, Paused: []string{"repo2"}})
	respPrio, _ := http.Post("http://"+addr+"/api/actions/repo-priority", "application/json", bytes.NewReader(prioBody))
	if respPrio.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on repo-priority, got %d", respPrio.StatusCode)
	}
	respPrioBadJSON, _ := http.Post("http://"+addr+"/api/actions/repo-priority", "application/json", strings.NewReader("bad"))
	if respPrioBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad json repo-priority, got %d", respPrioBadJSON.StatusCode)
	}
	respPrioBadMethod, _ := http.Get("http://" + addr + "/api/actions/repo-priority")
	if respPrioBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET repo-priority, got %d", respPrioBadMethod.StatusCode)
	}

	// Workflow actions
	wfBody, _ := json.Marshal(WorkflowActionPayload{Repo: "org/repo", RunID: 101, Action: "rerun"})
	respWf, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBody))
	if respWf.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on workflow rerun, got %d", respWf.StatusCode)
	}
	wfBadRepo, _ := json.Marshal(WorkflowActionPayload{Repo: "", RunID: 101, Action: "rerun"})
	respWfBadRepo, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBadRepo))
	if respWfBadRepo.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on empty repo, got %d", respWfBadRepo.StatusCode)
	}
	wfBadAction, _ := json.Marshal(WorkflowActionPayload{Repo: "org/repo", RunID: 101, Action: "destroy"})
	respWfBadAction, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBadAction))
	if respWfBadAction.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad workflow action, got %d", respWfBadAction.StatusCode)
	}
	respWfBadJSON, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", strings.NewReader("bad"))
	if respWfBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad json workflow, got %d", respWfBadJSON.StatusCode)
	}
	respWfBadMethod, _ := http.Get("http://" + addr + "/api/actions/workflow")
	if respWfBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET workflow, got %d", respWfBadMethod.StatusCode)
	}

	// Runner actions
	for _, act := range []string{"start", "stop", "pause", "resume", "drain"} {
		rBody, _ := json.Marshal(RunnerActionPayload{Action: act, RunnerID: "r-1"})
		respR, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", bytes.NewReader(rBody))
		if respR.StatusCode != http.StatusOK {
			t.Errorf("expected 200 on runner action %s, got %d", act, respR.StatusCode)
		}
	}
	badRunnerAction, _ := json.Marshal(RunnerActionPayload{Action: "terminate"})
	respBadRunner, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", bytes.NewReader(badRunnerAction))
	if respBadRunner.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad runner action, got %d", respBadRunner.StatusCode)
	}
	respBadRunnerJSON, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", strings.NewReader("bad"))
	if respBadRunnerJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json runner action, got %d", respBadRunnerJSON.StatusCode)
	}
	respRunnerBadMethod, _ := http.Get("http://" + addr + "/api/actions/runner")
	if respRunnerBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET runner action, got %d", respRunnerBadMethod.StatusCode)
	}

	// Prune action
	respPrune, _ := http.Post("http://"+addr+"/api/actions/prune", "application/json", nil)
	if respPrune.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on prune, got %d", respPrune.StatusCode)
	}
	respPruneBadMethod, _ := http.Get("http://" + addr + "/api/actions/prune")
	if respPruneBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET prune, got %d", respPruneBadMethod.StatusCode)
	}
}

func TestServer_SSEStreaming(t *testing.T) {
	srv, _, st, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	req, _ := http.NewRequest(http.MethodGet, "http://"+addr+"/api/stream", nil)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	req = req.WithContext(ctx)

	resp, err := http.DefaultClient.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("failed to connect SSE stream: %v", err)
	}
	defer resp.Body.Close()

	buf := make([]byte, 1024)
	n, err := resp.Body.Read(buf)
	if err != nil && err != io.EOF {
		t.Fatalf("failed reading SSE initial event: %v", err)
	}
	dataStr := string(buf[:n])
	if !strings.Contains(dataStr, "event: state") {
		t.Errorf("expected initial state event, got: %s", dataStr)
	}

	// Push log event
	st.AppendLog("realtime sse event")

	// Read next chunk
	n2, _ := resp.Body.Read(buf)
	dataStr2 := string(buf[:n2])
	if !strings.Contains(dataStr2, "realtime sse event") && !strings.Contains(dataStr2, ": ping") {
		t.Logf("received chunk: %s", dataStr2)
	}
}

func TestServer_StaticAssetRoutes(t *testing.T) {
	srv, _, _, tmpDist, tmpStatic := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	// Root / index.html
	respIndex, err := http.Get("http://" + addr + "/")
	if err != nil || respIndex.StatusCode != http.StatusOK {
		t.Fatalf("GET / failed: %v", err)
	}

	// Assets
	respCSS, _ := http.Get("http://" + addr + "/assets/style.css")
	if respCSS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for assets/style.css, got %d", respCSS.StatusCode)
	}
	respJS, _ := http.Get("http://" + addr + "/assets/script.js")
	if respJS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for assets/script.js, got %d", respJS.StatusCode)
	}

	// Font
	respFont, _ := http.Get("http://" + addr + "/fonts/test-font.woff2")
	if respFont.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for test-font.woff2, got %d", respFont.StatusCode)
	}

	// Font traversal / bad extension
	respBadFont1, _ := http.Get("http://" + addr + "/fonts/../bad.woff2")
	if respBadFont1.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on font traversal, got %d", respBadFont1.StatusCode)
	}
	respBadFont2, _ := http.Get("http://" + addr + "/fonts/font.ttf")
	if respBadFont2.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on non-woff2 font, got %d", respBadFont2.StatusCode)
	}

	// Asset traversal
	respBadAsset, _ := http.Get("http://" + addr + "/assets/../bad.css")
	if respBadAsset.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on asset traversal, got %d", respBadAsset.StatusCode)
	}
	respMissingAsset, _ := http.Get("http://" + addr + "/assets/missing.css")
	if respMissingAsset.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on missing asset, got %d", respMissingAsset.StatusCode)
	}

	// Legacy static files
	respLegacyCSS, _ := http.Get("http://" + addr + "/dashboard.css")
	if respLegacyCSS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on dashboard.css, got %d", respLegacyCSS.StatusCode)
	}
	respLegacyJS, _ := http.Get("http://" + addr + "/dashboard.js")
	if respLegacyJS.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on dashboard.js, got %d", respLegacyJS.StatusCode)
	}

	// Missing index fallback
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

	// Nonexistent path
	resp404, _ := http.Get("http://" + addr + "/does-not-exist")
	if resp404.StatusCode != http.StatusNotFound {
		t.Errorf("expected 404 on unknown route, got %d", resp404.StatusCode)
	}
}

type nonFlusherWriter struct {
	http.ResponseWriter
}

func TestServer_EdgeCases(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "49505",
		"DASHBOARD_HOST": "127.0.0.1",
	})
	st := state.NewState(2, "v1.0.0", nil)

	// Addr before start
	srv := NewServer(cfg, st, "", "", nil, time.Second)
	if srv.Addr() != "127.0.0.1:49505" {
		t.Errorf("expected 127.0.0.1:49505 before start, got %s", srv.Addr())
	}

	// Start with invalid address
	badCfg, _ := config.LoadConfig(config.MapEnv{
		"DASHBOARD_PORT": "49505",
		"DASHBOARD_HOST": "999.999.999.999",
	})
	badSrv := NewServer(badCfg, st, "", "", nil, time.Second)
	if err := badSrv.Start(); err == nil {
		t.Error("expected start error with invalid IP")
	}

	// SSE non-flusher
	handler := handleSSEStream(st, 0)
	req := httptest.NewRequest("GET", "/api/stream", nil)
	rec := httptest.NewRecorder()
	handler.ServeHTTP(&nonFlusherWriter{rec}, req)
	if rec.Code != http.StatusInternalServerError {
		t.Errorf("expected 500 for non-flusher, got %d", rec.Code)
	}

	// Repo priority nil arrays
	prioHandler := handleRepoPriority(st)
	reqPrio := httptest.NewRequest("POST", "/api/actions/repo-priority", strings.NewReader("{}"))
	recPrio := httptest.NewRecorder()
	prioHandler.ServeHTTP(recPrio, reqPrio)
	if recPrio.Code != http.StatusOK {
		t.Errorf("expected 200 for empty priority object, got %d", recPrio.Code)
	}

	// Other asset mime type
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

	// Missing legacy file
	recMissing := httptest.NewRecorder()
	reqMissing := httptest.NewRequest("GET", "/dashboard.css", nil)
	staticHandler.ServeHTTP(recMissing, reqMissing)
	if recMissing.Code != http.StatusNotFound {
		t.Errorf("expected 404 for missing legacy css, got %d", recMissing.Code)
	}
}
