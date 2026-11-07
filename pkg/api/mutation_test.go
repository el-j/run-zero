package api

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/cache"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

func serve(h http.HandlerFunc, method, body string) *httptest.ResponseRecorder {
	rec := httptest.NewRecorder()
	h(rec, httptest.NewRequest(method, "/", strings.NewReader(body)))
	return rec
}

func TestHandleCache_UsesConfiguredDirectory(t *testing.T) {
	dir := t.TempDir()
	_ = os.MkdirAll(filepath.Join(dir, "npm"), 0o755)
	_ = os.WriteFile(filepath.Join(dir, "npm", "a"), make([]byte, 10), 0o644)
	cache.InvalidateStatsCache()

	var stats cache.CacheStats
	_ = json.Unmarshal(serve(handleCache(&config.Config{HostCacheDir: dir}, nil), http.MethodGet, "").Body.Bytes(), &stats)
	if stats.TotalBytes != 10 {
		t.Fatalf("got %+v", stats)
	}
}

func TestHandleCachePurge_PurgesTheRequestedCategoryOfTheConfiguredDir(t *testing.T) {
	dir := t.TempDir()
	for _, c := range []string{"npm", "pip"} {
		_ = os.MkdirAll(filepath.Join(dir, c), 0o755)
		_ = os.WriteFile(filepath.Join(dir, c, "a"), []byte("x"), 0o644)
	}
	st := state.NewState(1, "t", nil)
	serve(handleCachePurge(&config.Config{HostCacheDir: dir}, st), http.MethodPost, `{"category":"npm"}`)

	if _, err := os.Stat(filepath.Join(dir, "npm", "a")); !os.IsNotExist(err) {
		t.Error("the npm cache must be purged")
	}
	if _, err := os.Stat(filepath.Join(dir, "pip", "a")); err != nil {
		t.Error("other categories must survive")
	}
	logs := st.GetLogs()
	if !strings.HasSuffix(logs[len(logs)-1].Message, "Purged cache: npm") {
		t.Errorf("unexpected log %q", logs[len(logs)-1].Message)
	}
}

func TestHandleSettings_ReportsWhetherATokenIsConfigured(t *testing.T) {
	for token, want := range map[string]bool{"tok": true, "": false} {
		var body map[string]any
		_ = json.Unmarshal(serve(handleSettings(&config.Config{AccessToken: token}, state.NewState(1, "t", nil)), http.MethodGet, "").Body.Bytes(), &body)
		settings, _ := body["settings"].(map[string]any)
		if settings == nil {
			settings = body
		}
		if settings["access_token_configured"] != want {
			t.Errorf("token %q: got %v", token, settings["access_token_configured"])
		}
	}
}

func TestHandleRepoPriority_KeepsGivenListsAndDefaultsMissingOnes(t *testing.T) {
	st := state.NewState(1, "t", nil)
	var body struct{ Priority, Paused []string }
	_ = json.Unmarshal(serve(handleRepoPriority(st), http.MethodPost, `{"priority":["o/a"],"paused":["o/b"]}`).Body.Bytes(), &body)
	if len(body.Priority) != 1 || len(body.Paused) != 1 {
		t.Fatalf("given lists must be kept: %+v", body)
	}
	_ = json.Unmarshal(serve(handleRepoPriority(st), http.MethodPost, `{}`).Body.Bytes(), &body)
	if body.Priority == nil || body.Paused == nil || len(body.Priority) != 0 {
		t.Fatalf("missing lists must become empty lists: %+v", body)
	}
}

func TestHandleWorkflowAction_RejectsRunIDZero(t *testing.T) {
	if rec := serve(handleWorkflowAction(state.NewState(1, "t", nil)), http.MethodPost, `{"repo":"o/r","run_id":0,"action":"rerun"}`); rec.Code != http.StatusBadRequest {
		t.Fatalf("got %d", rec.Code)
	}
}

func TestValidateAndApplySettings_AcceptsLimitValues(t *testing.T) {
	one, zero, four, max := 1, 0, 4, 3600
	for _, p := range []SettingsPayload{
		{MaxRunners: &one}, {MinRunners: &zero}, {MinRunners: &four}, {PollInterval: &one}, {PollInterval: &max},
	} {
		if _, err := validateAndApplySettings(&config.Config{MaxRunners: 4}, state.NewState(4, "t", nil), &p); err != nil {
			t.Errorf("%+v rejected: %v", p, err)
		}
	}
	cfg := &config.Config{MaxRunners: 4}
	if _, err := validateAndApplySettings(cfg, state.NewState(4, "t", nil), &SettingsPayload{RunnerCPUs: &one}); err != nil || cfg.RunnerCPUs != 1 {
		t.Fatalf("RUNNER_CPUS=1 must apply: %v %d", err, cfg.RunnerCPUs)
	}
}

func TestStopRunnerWithFallback_RetriesByName(t *testing.T) {
	var stopped []string
	rd := &actDriver{stopFunc: func(id string) error {
		stopped = append(stopped, id)
		if id == "runner-abc" {
			return nil
		}
		return errors.New("unknown id")
	}}
	st := state.NewState(1, "t", nil)
	st.UpdateFleet([]state.RunnerInfo{{ID: "abc", Name: "runner-abc"}}, nil)
	if err := stopRunnerWithFallback(context.Background(), rd, st, "abc"); err != nil || len(stopped) != 2 || stopped[1] != "runner-abc" {
		t.Fatalf("err %v, stopped %v", err, stopped)
	}
}

func TestRandomHex(t *testing.T) {
	old := randRead
	defer func() { randRead = old }()
	randRead = func(b []byte) (int, error) { copy(b, []byte{1, 2, 3}); return len(b), nil }
	if got := randomHex(3); got != "010203" {
		t.Fatalf("got %q", got)
	}
	randRead = func([]byte) (int, error) { return 0, errors.New("no entropy") }
	if got := randomHex(3); len(got) > 6 {
		t.Fatalf("fallback must stay within 6 hex digits, got %q", got)
	}
}

func TestLaunchBridgeTerminal_Status300IsAFailure(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusMultipleChoices)
		_, _ = w.Write([]byte(`{"terminal_launched":true}`))
	}))
	defer srv.Close()
	t.Setenv("HOST_VM_BRIDGE_URL", srv.URL)
	if launchBridgeTerminal(httptest.NewRequest(http.MethodPost, "/", nil), RunnerActionPayload{}, "r", "docker") {
		t.Fatal("HTTP 300 from the bridge must not count as launched")
	}
}

func TestStopRunnerWithFallback_NeverStopsAnotherRunner(t *testing.T) {
	var stopped []string
	rd := &actDriver{stopFunc: func(id string) error {
		stopped = append(stopped, id)
		if id == "abc" {
			return errors.New("unknown id")
		}
		return nil
	}}
	st := state.NewState(2, "t", nil)
	st.UpdateFleet([]state.RunnerInfo{{ID: "other", Name: "other-name"}, {ID: "abc", Name: "runner-abc"}}, nil)
	_ = stopRunnerWithFallback(context.Background(), rd, st, "abc")
	for _, s := range stopped {
		if s == "other-name" {
			t.Fatalf("stopped an unrelated runner: %v", stopped)
		}
	}
}
