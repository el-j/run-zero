package api

import (
	"context"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

func do(h http.Handler, method, target, body string) *httptest.ResponseRecorder {
	var rd io.Reader
	if body != "" {
		rd = strings.NewReader(body)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, target, rd))
	return rec
}

func expectCode(t *testing.T, rec *httptest.ResponseRecorder, want int) {
	t.Helper()
	if rec.Code != want {
		t.Fatalf("status = %d, want %d (body %s)", rec.Code, want, rec.Body.String())
	}
}

// ---- images ----

type fakeInspector struct{}

func (fakeInspector) Inspect(context.Context) builder.ImagesStatusResponse {
	return builder.ImagesStatusResponse{}
}

type fakeBuilds struct {
	active    *builder.ImageBuildProgress
	byID      map[string]*builder.ImageBuildProgress
	triggerEr error
	cancelErr error
}

func (f *fakeBuilds) GetActiveBuild() *builder.ImageBuildProgress { return f.active }
func (f *fakeBuilds) GetBuildByID(id string) (*builder.ImageBuildProgress, bool) {
	p, ok := f.byID[id]
	return p, ok
}
func (f *fakeBuilds) TriggerBuild(context.Context, builder.ImageBuildRequest) (*builder.ImageBuildProgress, error) {
	if f.triggerEr != nil {
		return nil, f.triggerEr
	}
	return &builder.ImageBuildProgress{BuildID: "b1"}, nil
}
func (f *fakeBuilds) CancelBuild() error { return f.cancelErr }

func TestImageHandlers(t *testing.T) {
	fb := &fakeBuilds{byID: map[string]*builder.ImageBuildProgress{"b1": {BuildID: "b1"}}}

	expectCode(t, do(handleGetImages(fakeInspector{}, nil), http.MethodPost, "/api/images", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(handleGetImages(fakeInspector{}, nil), http.MethodGet, "/api/images", ""), http.StatusOK)
	expectCode(t, do(handleGetImages(fakeInspector{}, fb), http.MethodGet, "/api/images", ""), http.StatusOK)

	expectCode(t, do(handleTriggerBuild(fb), http.MethodGet, "/", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(handleTriggerBuild(fb), http.MethodPost, "/", "{bad"), http.StatusBadRequest)
	expectCode(t, do(handleTriggerBuild(fb), http.MethodPost, "/", ""), http.StatusAccepted)
	fb.triggerEr = errors.New("busy")
	expectCode(t, do(handleTriggerBuild(fb), http.MethodPost, "/", `{}`), http.StatusConflict)

	expectCode(t, do(handleCancelBuild(fb), http.MethodGet, "/", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(handleCancelBuild(fb), http.MethodPost, "/", ""), http.StatusOK)
	fb.cancelErr = errors.New("boom")
	expectCode(t, do(handleCancelBuild(fb), http.MethodPost, "/", ""), http.StatusInternalServerError)

	prog := handleGetBuildProgress(fb)
	expectCode(t, do(prog, http.MethodPost, "/api/images/build/", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(prog, http.MethodGet, "/api/images/build/", ""), http.StatusNotFound)
	fb.active = &builder.ImageBuildProgress{BuildID: "act"}
	expectCode(t, do(prog, http.MethodGet, "/api/images/build/", ""), http.StatusOK)
	expectCode(t, do(prog, http.MethodGet, "/elsewhere", ""), http.StatusOK)
	expectCode(t, do(prog, http.MethodGet, "/api/images/build/b1", ""), http.StatusOK)
	expectCode(t, do(prog, http.MethodGet, "/api/images/build/nope", ""), http.StatusNotFound)
}

// ---- static ----

type fakeFS map[string]string

func (f fakeFS) ReadFile(name string) ([]byte, error) {
	if v, ok := f[name]; ok {
		return []byte(v), nil
	}
	return nil, os.ErrNotExist
}

func withEmbedded(t *testing.T, fs fakeFS) {
	t.Helper()
	old := embeddedFS
	embeddedFS = fs
	t.Cleanup(func() { embeddedFS = old })
}

func TestStatic_EmbeddedFallbacks(t *testing.T) {
	withEmbedded(t, fakeFS{
		"dist/index.html":                "<emb index>",
		"dist/assets/app.css":            "css",
		"dist/assets/app.js":             "js",
		"dist/assets/data.bin":           "bin",
		"dist/fonts/f.woff2":             "font",
		"dist/logo.png":                  "png",
		"dist/site.webmanifest":          "{}",
		"dist/favicon.ico":               "ico",
		"dist/only-embedded-icon.svg":    "svg",
		"dist/only-embedded-nothing.ico": "x",
	})
	empty := t.TempDir()
	h := handleStatic("", empty)

	for path, want := range map[string]string{
		"/":                       "<emb index>",
		"/assets/app.css":         "css",
		"/assets/app.js":          "js",
		"/assets/data.bin":        "bin",
		"/fonts/f.woff2":          "font",
		"/logo.png":               "png",
		"/site.webmanifest":       "{}",
		"/only-embedded-icon.svg": "svg",
	} {
		rec := do(h, http.MethodGet, path, "")
		expectCode(t, rec, http.StatusOK)
		if rec.Body.String() != want {
			t.Errorf("%s body = %q, want %q", path, rec.Body.String(), want)
		}
	}

	expectCode(t, do(h, http.MethodGet, "/assets/missing.css", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/fonts/missing.woff2", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/missing.svg", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/unknown.txt", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/dashboard.css", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/a/b.svg", ""), http.StatusNotFound)
}

func TestStatic_NoEmbeddedAndCustomDist(t *testing.T) {
	withEmbedded(t, fakeFS{})
	dist, static := t.TempDir(), t.TempDir()

	// Not eligible for the embedded fallback: custom dist dir, nothing on disk.
	h := handleStatic(dist, static)
	expectCode(t, do(h, http.MethodGet, "/", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/assets/x.css", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/fonts/x.woff2", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/x.svg", ""), http.StatusNotFound)

	// Eligible but the embedded bundle is empty.
	he := handleStatic("web/dist", static)
	expectCode(t, do(he, http.MethodGet, "/", ""), http.StatusNotFound)
	expectCode(t, do(he, http.MethodGet, "/assets/x.css", ""), http.StatusNotFound)
	expectCode(t, do(he, http.MethodGet, "/fonts/x.woff2", ""), http.StatusNotFound)
	expectCode(t, do(he, http.MethodGet, "/x.ico", ""), http.StatusNotFound)

	// Traversal is rejected.
	expectCode(t, do(h, http.MethodGet, "/assets/a..b", ""), http.StatusNotFound)
}

func TestStatic_StaticDirFallbacks(t *testing.T) {
	withEmbedded(t, fakeFS{})
	dist, static := t.TempDir(), t.TempDir()
	write := func(p, c string) {
		if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(p, []byte(c), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	write(filepath.Join(static, "index.html"), "static index")
	write(filepath.Join(static, "fonts", "s.woff2"), "sfont")
	write(filepath.Join(static, "s.png"), "spng")
	write(filepath.Join(dist, "assets", "plain.txt"), "plain")
	h := handleStatic(dist, static)

	for path, want := range map[string]string{
		"/index.html":       "static index",
		"/fonts/s.woff2":    "sfont",
		"/s.png":            "spng",
		"/assets/plain.txt": "plain",
	} {
		rec := do(h, http.MethodGet, path, "")
		expectCode(t, rec, http.StatusOK)
		if rec.Body.String() != want {
			t.Errorf("%s body = %q, want %q", path, rec.Body.String(), want)
		}
	}
}

// ---- runner actions ----

type actDriver struct {
	stopErr  error
	listErr  error
	spawnErr error
	spawned  []driver.RunnerSpec
}

func (d *actDriver) Backend() string { return "mock" }
func (d *actDriver) SpawnRunner(_ context.Context, s driver.RunnerSpec) (*state.RunnerInfo, error) {
	if d.spawnErr != nil {
		return nil, d.spawnErr
	}
	d.spawned = append(d.spawned, s)
	return &state.RunnerInfo{ID: s.ID, Name: s.Name}, nil
}
func (d *actDriver) ListRunners(context.Context) ([]state.RunnerInfo, error) { return nil, d.listErr }
func (d *actDriver) StopRunner(context.Context, string) error                { return d.stopErr }
func (d *actDriver) CleanupAll(context.Context) error                        { return nil }

func fakeGitHub(t *testing.T, status int, body string) *github.Client {
	t.Helper()
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(status)
		_, _ = w.Write([]byte(body))
	}))
	t.Cleanup(ts.Close)
	return github.NewClient("tok", ts.URL, ts.Client())
}

func TestRunnerAction_Basics(t *testing.T) {
	st := state.NewState(3, "t", nil)
	h := handleRunnerActionWithDeps(st, nil, nil)
	expectCode(t, do(h, http.MethodGet, "/", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(h, http.MethodPost, "/", "{bad"), http.StatusBadRequest)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"nuke"}`), http.StatusBadRequest)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"pause"}`), http.StatusOK)
	if st.GetSnapshot().AutoscalerStatus != "paused" {
		t.Errorf("expected paused, got %q", st.GetSnapshot().AutoscalerStatus)
	}
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"resume"}`), http.StatusOK)
	if st.GetSnapshot().AutoscalerStatus != "running" {
		t.Errorf("expected running, got %q", st.GetSnapshot().AutoscalerStatus)
	}
	// start/stop/drain without deps are accepted no-ops.
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start"}`), http.StatusOK)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"drain"}`), http.StatusOK)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"stop","runner_id":"x"}`), http.StatusOK)

	var nilDriver driver.RunnerDriver
	if firstDriver([]driver.RunnerDriver{nilDriver}) != nil {
		t.Fatal("expected nil driver")
	}
}

func TestRunnerAction_Stop(t *testing.T) {
	st := state.NewState(3, "t", nil)
	d := &actDriver{}
	h := handleRunnerActionWithDeps(st, nil, nil, d)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"stop","runner_id":"r1"}`), http.StatusOK)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"stop"}`), http.StatusOK)
	d.stopErr = errors.New("nope")
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"stop","runner_id":"r1"}`), http.StatusInternalServerError)
}

func TestRunnerAction_Start(t *testing.T) {
	st := state.NewState(3, "t", nil)
	d := &actDriver{}
	gh := fakeGitHub(t, http.StatusOK, `{"token":"reg"}`)
	cfg := &config.Config{RunnerBackend: "orbstack", RunnerCPUs: 5, HostCacheDir: "/cache"}

	h := handleRunnerActionWithDeps(st, cfg, gh, d)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start"}`), http.StatusBadRequest)

	st.SetRepoPriority([]string{"o/prio"}, nil)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start"}`), http.StatusOK)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start","repo":"o/r","arch":"arm64","backend":"docker"}`), http.StatusOK)
	if len(d.spawned) != 2 {
		t.Fatalf("spawned = %d", len(d.spawned))
	}
	if s := d.spawned[0]; s.Repo != "o/prio" || s.Arch != "amd64" || s.Backend != "orbstack" || s.CPUs != 5 || s.CacheDir != "/cache" {
		t.Errorf("unexpected spec %+v", s)
	}
	if s := d.spawned[1]; s.Backend != "docker" || s.Arch != "arm64" {
		t.Errorf("unexpected spec %+v", s)
	}

	// nil config and "auto" backend fall back to docker with default sizing.
	h = handleRunnerActionWithDeps(st, nil, gh, d)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start","repo":"o/r"}`), http.StatusOK)
	if s := d.spawned[2]; s.Backend != "docker" || s.CPUs != 3 {
		t.Errorf("unexpected spec %+v", s)
	}
	auto := buildManualSpec(&config.Config{RunnerBackend: "auto"}, RunnerActionPayload{}, "o/r", "amd64", "t")
	if auto.Backend != "docker" || auto.CPUs != 3 {
		t.Errorf("auto spec %+v", auto)
	}

	d.spawnErr = errors.New("spawn fail")
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start","repo":"o/r"}`), http.StatusInternalServerError)

	bad := fakeGitHub(t, http.StatusInternalServerError, `{}`)
	h = handleRunnerActionWithDeps(st, cfg, bad, d)
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"start","repo":"o/r"}`), http.StatusInternalServerError)
}

func TestRunnerAction_OpenTerminal(t *testing.T) {
	st := state.NewState(3, "t", nil)
	st.UpdateFleet([]state.RunnerInfo{
		{ID: "id1", Name: "runzero-j1", Backend: "docker"},
		{ID: "id2", Name: "other"},
	}, nil)
	h := handleRunnerActionWithDeps(st, nil, nil)

	t.Setenv("HOST_VM_BRIDGE_URL", "")
	rec := do(h, http.MethodPost, "/", `{"action":"open-terminal","runner_id":"id1"}`)
	expectCode(t, rec, http.StatusOK)
	if !strings.Contains(rec.Body.String(), "docker exec -it runzero-j1 bash") {
		t.Errorf("unexpected body %s", rec.Body.String())
	}
	rec = do(h, http.MethodPost, "/", `{"action":"open-terminal","runner_id":"runzero-vm9"}`)
	if !strings.Contains(rec.Body.String(), "orb -m runzero-vm9 -u runner bash") {
		t.Errorf("unexpected body %s", rec.Body.String())
	}
	rec = do(h, http.MethodPost, "/", `{"action":"open-terminal","runner_id":"id2","backend":"orbstack"}`)
	if !strings.Contains(rec.Body.String(), "orb -m other") {
		t.Errorf("unexpected body %s", rec.Body.String())
	}
	t.Setenv("HOST_VM_BRIDGE_URL", "none")
	expectCode(t, do(h, http.MethodPost, "/", `{"action":"open-terminal","runner_id":"id1"}`), http.StatusOK)
}

func TestLaunchBridgeTerminal(t *testing.T) {
	var gotAuth string
	respond := func(status int, body string) *httptest.Server {
		return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			gotAuth = r.Header.Get("Authorization")
			w.WriteHeader(status)
			_, _ = w.Write([]byte(body))
		}))
	}
	p := RunnerActionPayload{RunnerID: "x"}
	req := httptest.NewRequest(http.MethodPost, "/", nil)

	t.Setenv("RUNZERO_BRIDGE_TOKEN", "secret")
	ok := respond(http.StatusOK, `{"terminal_launched":true}`)
	defer ok.Close()
	t.Setenv("HOST_VM_BRIDGE_URL", ok.URL+"/")
	if !launchBridgeTerminal(req, p, "n", "docker") || gotAuth != "Bearer secret" {
		t.Errorf("expected launch with bearer token, auth=%q", gotAuth)
	}

	h := handleRunnerActionWithDeps(state.NewState(1, "t", nil), nil, nil)
	rec := do(h, http.MethodPost, "/", `{"action":"open-terminal","runner_id":"n"}`)
	if !strings.Contains(rec.Body.String(), "Terminal opened for n") {
		t.Errorf("unexpected body %s", rec.Body.String())
	}

	t.Setenv("RUNZERO_BRIDGE_TOKEN", "")
	gotAuth = "unset"
	launchBridgeTerminal(req, p, "n", "docker")
	if gotAuth != "" {
		t.Errorf("expected no auth header, got %q", gotAuth)
	}

	fail := respond(http.StatusInternalServerError, `{}`)
	defer fail.Close()
	t.Setenv("HOST_VM_BRIDGE_URL", fail.URL)
	if launchBridgeTerminal(req, p, "n", "docker") {
		t.Error("expected false on 500")
	}

	junk := respond(http.StatusOK, `not json`)
	defer junk.Close()
	t.Setenv("HOST_VM_BRIDGE_URL", junk.URL)
	if launchBridgeTerminal(req, p, "n", "docker") {
		t.Error("expected false on bad JSON")
	}

	dead := respond(http.StatusOK, `{}`)
	dead.Close()
	t.Setenv("HOST_VM_BRIDGE_URL", dead.URL)
	if launchBridgeTerminal(req, p, "n", "docker") {
		t.Error("expected false on connection error")
	}

	t.Setenv("HOST_VM_BRIDGE_URL", "http://bad host\x7f")
	if launchBridgeTerminal(req, p, "n", "docker") {
		t.Error("expected false on bad URL")
	}
}

func TestRandomHexFallback(t *testing.T) {
	old := randRead
	randRead = func([]byte) (int, error) { return 0, errors.New("no entropy") }
	defer func() { randRead = old }()
	if got := randomHex(3); got == "" {
		t.Error("expected fallback value")
	}
}

func TestHandlePrune_ErrorsAndNoDriver(t *testing.T) {
	st := state.NewState(3, "t", nil)
	expectCode(t, do(handlePrune(st), http.MethodPost, "/", ""), http.StatusOK)
	expectCode(t, do(handlePrune(st, nil), http.MethodPost, "/", ""), http.StatusOK)
	expectCode(t, do(handlePrune(st, &actDriver{listErr: errors.New("x")}), http.MethodPost, "/", ""), http.StatusInternalServerError)
}

// ---- settings / status / workflow ----

func TestSettingsValidation(t *testing.T) {
	cfg := &config.Config{MaxRunners: 4}
	st := state.NewState(4, "t", nil)
	i := func(v int) *int { return &v }
	for name, p := range map[string]SettingsPayload{
		"max<1":     {MaxRunners: i(0)},
		"min<0":     {MinRunners: i(-1)},
		"min>max":   {MaxRunners: i(2), MinRunners: i(3)},
		"poll low":  {PollInterval: i(0)},
		"poll high": {PollInterval: i(3601)},
	} {
		if _, err := validateAndApplySettings(cfg, st, &p); err == nil {
			t.Errorf("%s: expected error", name)
		}
	}
}

func TestSettingsApplyAll(t *testing.T) {
	cfg := &config.Config{MaxRunners: 4}
	st := state.NewState(4, "t", nil)
	i, s, b := func(v int) *int { return &v }, func(v string) *string { return &v }, func(v bool) *bool { return &v }
	p := SettingsPayload{
		MaxRunners: i(6), MinRunners: i(1), RunnerCPUs: i(2), RunnerMemory: s("8G"), PollInterval: i(30),
		AutoDiscover: b(true), AutoRouteVM: b(true), ProxiesEnabled: b(true), CacheEnabled: b(true),
		RunnerBackend: s("docker"), RunnerArch: s("arm64"), NativeArchOverride: s("amd64"),
		HostCacheDir: s("/c"), AccessToken: s("tok"),
	}
	u, err := validateAndApplySettings(cfg, st, &p)
	if err != nil || len(u) != 14 || cfg.AccessToken != "tok" || cfg.MaxRunners != 6 {
		t.Fatalf("u=%v err=%v cfg=%+v", u, err, cfg)
	}
}

func TestSettingsHandler_Errors(t *testing.T) {
	t.Chdir(t.TempDir())
	cfg := &config.Config{MaxRunners: 4}
	st := state.NewState(4, "t", nil)
	h := handleSettings(cfg, st)
	expectCode(t, do(h, http.MethodPost, "/", "{bad"), http.StatusBadRequest)
	expectCode(t, do(h, http.MethodPost, "/", `{"max_runners":0}`), http.StatusBadRequest)
	expectCode(t, do(h, http.MethodPut, "/", ""), http.StatusMethodNotAllowed)
}

func TestRunnerLogHandler(t *testing.T) {
	st := state.NewState(1, "t", nil)
	st.SetRunnerLog("r1", "tail")
	h := handleRunnerLog(st)
	expectCode(t, do(h, http.MethodPost, "/", ""), http.StatusMethodNotAllowed)
	expectCode(t, do(h, http.MethodGet, "/api/runner-log", ""), http.StatusBadRequest)
	expectCode(t, do(h, http.MethodGet, "/api/runner-log?name=zz", ""), http.StatusNotFound)
	expectCode(t, do(h, http.MethodGet, "/api/runner-log?name=r1", ""), http.StatusOK)
}

func TestWorkflowAction_GitHubFailure(t *testing.T) {
	st := state.NewState(1, "t", nil)
	gh := fakeGitHub(t, http.StatusInternalServerError, `{}`)
	h := handleWorkflowAction(st, gh)
	expectCode(t, do(h, http.MethodPost, "/", `{"repo":"o/r","run_id":1,"action":"cancel"}`), http.StatusBadGateway)
	ok := handleWorkflowAction(st, fakeGitHub(t, http.StatusOK, `{}`))
	expectCode(t, do(ok, http.MethodPost, "/", `{"repo":"o/r","run_id":1,"action":"rerun"}`), http.StatusOK)
	expectCode(t, do(handleWorkflowAction(st, nil), http.MethodPost, "/", `{"repo":"o/r","run_id":1,"action":"rerun"}`), http.StatusOK)
}

// ---- SSE ----

type sseWriter struct {
	mu     sync.Mutex
	hdr    http.Header
	buf    strings.Builder
	failed bool
}

func newSSEWriter(failed bool) *sseWriter { return &sseWriter{hdr: http.Header{}, failed: failed} }

func (w *sseWriter) Header() http.Header { return w.hdr }
func (w *sseWriter) WriteHeader(int)     {}
func (w *sseWriter) Flush()              {}
func (w *sseWriter) Write(b []byte) (int, error) {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.failed {
		return 0, errors.New("closed")
	}
	return w.buf.Write(b)
}
func (w *sseWriter) String() string {
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.buf.String()
}

func runSSE(st *state.State, w http.ResponseWriter, hb time.Duration, ctx context.Context) chan struct{} {
	done := make(chan struct{})
	go func() {
		defer close(done)
		handleSSEStream(st, hb).ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/api/stream", nil).WithContext(ctx))
	}()
	return done
}

func waitDone(t *testing.T, done chan struct{}) {
	t.Helper()
	select {
	case <-done:
	case <-time.After(3 * time.Second):
		t.Fatal("handler did not return")
	}
}

func TestSSE_Branches(t *testing.T) {
	// Broker closed: subscription channel is closed, handler returns.
	st := state.NewState(1, "t", nil)
	st.Broker().Close()
	waitDone(t, runSSE(st, newSSEWriter(false), 0, context.Background()))

	// Ping write failure ends the stream.
	st = state.NewState(1, "t", nil)
	waitDone(t, runSSE(st, newSSEWriter(true), 5*time.Millisecond, context.Background()))

	// Event write failure ends the stream.
	st = state.NewState(1, "t", nil)
	w := newSSEWriter(true)
	done := runSSE(st, w, time.Hour, context.Background())
	deadline := time.Now().Add(3 * time.Second)
	for {
		select {
		case <-done:
			goto failedDone
		default:
		}
		if time.Now().After(deadline) {
			t.Fatal("handler did not return on write failure")
		}
		st.Broker().Broadcast(state.Event{Type: "x", Data: 1})
		time.Sleep(5 * time.Millisecond)
	}
failedDone:

	// Unformattable events are skipped; later ones are delivered.
	st = state.NewState(1, "t", nil)
	good := newSSEWriter(false)
	ctx, cancel := context.WithCancel(context.Background())
	done = runSSE(st, good, time.Hour, ctx)
	deadline = time.Now().Add(3 * time.Second)
	for !strings.Contains(good.String(), "event: good") {
		if time.Now().After(deadline) {
			t.Fatal("good event not delivered")
		}
		st.Broker().Broadcast(state.Event{Type: "bad", Data: make(chan int)})
		st.Broker().Broadcast(state.Event{Type: "good", Data: 1})
		time.Sleep(5 * time.Millisecond)
	}
	cancel()
	waitDone(t, done)
}
