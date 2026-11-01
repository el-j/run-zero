package bridge

import (
	"context"
	"encoding/json"
	"errors"
	"net"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

type errDriver struct{ mockDriver }

func (errDriver) SpawnRunner(context.Context, driver.RunnerSpec) (*state.RunnerInfo, error) {
	return nil, errors.New("spawn failed")
}
func (errDriver) ListRunners(context.Context) ([]state.RunnerInfo, error) {
	return nil, errors.New("list failed")
}
func (errDriver) StopRunner(context.Context, string) error { return errors.New("stop failed") }

type fakeExec struct {
	run func(ctx context.Context, name string, args ...string) ([]byte, error)
}

func (f fakeExec) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
	if f.run != nil {
		return f.run(ctx, name, args...)
	}
	return []byte("[]"), nil
}
func (fakeExec) LookPath(file string) (string, error) { return file, nil }

func newTestServer(t *testing.T, token string, drivers map[string]driver.RunnerDriver) *Server {
	t.Helper()
	t.Setenv("RUNZERO_STATE_DIR", t.TempDir())
	return NewServer(0, "", token, "v", "sha", drivers)
}

func do(s *Server, method, path, body, token string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(method, path, strings.NewReader(body))
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	rec := httptest.NewRecorder()
	s.ServeHTTP(rec, req)
	return rec
}

func TestNewServerDefaults(t *testing.T) {
	t.Setenv("RUNZERO_GIT_SHA", "envsha")
	t.Setenv("RUNZERO_STATE_DIR", t.TempDir())
	s := NewServer(0, "", "", "v", "", nil)
	if s.port != 49504 || s.host != "127.0.0.1" || s.gitSHA != "envsha" {
		t.Errorf("defaults: %+v", s)
	}
	t.Setenv("RUNZERO_STATE_DIR", "")
	t.Chdir(t.TempDir())
	if s := NewServer(1234, "0.0.0.0", "t", "v", "x", nil); s.port != 1234 || s.host != "0.0.0.0" || s.gitSHA != "x" {
		t.Errorf("explicit: %+v", s)
	}
}

func TestResolveDriverAndAuth(t *testing.T) {
	orb := &mockDriver{backend: "orbstack"}
	s := newTestServer(t, "", map[string]driver.RunnerDriver{"orbstack": orb})
	for _, n := range []string{"orbstack", "VM", "orb", " orbstack-vm "} {
		if s.resolveDriver(n) == nil {
			t.Errorf("%q should resolve", n)
		}
	}
	if s.resolveDriver("nope") != nil {
		t.Error("unknown driver should be nil")
	}
	if rec := do(s, http.MethodGet, "/api/drivers/orbstack/runners", "", ""); rec.Code != http.StatusOK {
		t.Errorf("tokenless server should allow: %d", rec.Code)
	}
}

func TestDriverHandlerErrors(t *testing.T) {
	good := &mockDriver{backend: "orbstack", spawnID: "x"}
	s := newTestServer(t, "tok", map[string]driver.RunnerDriver{"orbstack": good, "docker": &errDriver{}})

	cases := []struct {
		method, path, body string
		code               int
	}{
		{"GET", "/api/drivers/nope/runners", "", 400},
		{"GET", "/api/drivers/docker/runners", "", 500},
		{"POST", "/api/drivers/nope/spawn", "", 400},
		{"POST", "/api/drivers/orbstack/spawn", "{bad", 400},
		{"POST", "/api/drivers/orbstack/spawn", "", 200},
		{"POST", "/api/drivers/docker/spawn", "{}", 500},
		{"POST", "/api/drivers/nope/stop", "", 400},
		{"POST", "/api/drivers/orbstack/stop", `{"id":"abc"}`, 200},
		{"POST", "/api/drivers/docker/destroy", `{"runner_id":"abc"}`, 500},
		{"POST", "/api/drivers/nope/cleanup", "", 200},
		{"GET", "/api/drivers/orbstack", "", 404},
		{"GET", "/api/drivers/orbstack/spawn", "", 404},
		{"POST", "/api/drivers/orbstack/unknown", "", 404},
		{"GET", "/unknown", "", 404},
	}
	for _, c := range cases {
		if rec := do(s, c.method, c.path, c.body, "tok"); rec.Code != c.code {
			t.Errorf("%s %s: got %d want %d (%s)", c.method, c.path, rec.Code, c.code, rec.Body.String())
		}
	}
	if rec := do(s, "GET", "/api/drivers/orbstack/runners", "", "wrong"); rec.Code != 401 {
		t.Errorf("expected 401, got %d", rec.Code)
	}
}

func TestImageAndBuildRoutes(t *testing.T) {
	s := newTestServer(t, "tok", nil)
	mock := fakeExec{}
	gb := builder.NewGoldenBuilder(builder.Config{StateDir: t.TempDir()}, mock)
	s.gb = gb
	s.imgInspector = builder.NewImageInspector(gb, mock)
	s.buildMgr = builder.NewBuildManager(gb, mock, nil, nil)

	if rec := do(s, "GET", "/api/images", "", ""); rec.Code != 200 {
		t.Errorf("images: %d", rec.Code)
	}
	if rec := do(s, "POST", "/api/actions/build-image", `{}`, ""); rec.Code != 401 {
		t.Errorf("unauth build: %d", rec.Code)
	}
	if rec := do(s, "POST", "/api/actions/build-image", `{bad`, "tok"); rec.Code != 400 {
		t.Errorf("bad json: %d", rec.Code)
	}
	if rec := do(s, "POST", "/api/actions/build-image/cancel", "", ""); rec.Code != 401 {
		t.Errorf("unauth cancel: %d", rec.Code)
	}
	if rec := do(s, "POST", "/api/actions/build-image/cancel", "", "tok"); rec.Code != 200 {
		t.Errorf("cancel: %d", rec.Code)
	}
	if rec := do(s, "GET", "/api/images/build/none", "", ""); rec.Code != 404 {
		t.Errorf("missing build: %d", rec.Code)
	}

	rec := do(s, "POST", "/api/actions/build-image", `{"target":"vm","arch":"arm64"}`, "tok")
	if rec.Code != 202 {
		t.Fatalf("trigger: %d %s", rec.Code, rec.Body.String())
	}
	var prog builder.ImageBuildProgress
	_ = json.Unmarshal(rec.Body.Bytes(), &prog)
	if rec := do(s, "POST", "/api/actions/build-image", `{}`, "tok"); rec.Code != 409 && rec.Code != 202 {
		t.Errorf("second trigger: %d", rec.Code)
	}
	if rec := do(s, "GET", "/api/images/build/"+prog.BuildID, "", ""); rec.Code != 200 {
		t.Errorf("get build: %d", rec.Code)
	}
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		if p := s.buildMgr.GetActiveBuild(); p != nil && p.Status != "building" {
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func TestBuildImageConflict(t *testing.T) {
	s := newTestServer(t, "", nil)
	release := make(chan struct{})
	mock := fakeExec{run: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		<-release
		return []byte("[]"), nil
	}}
	gb := builder.NewGoldenBuilder(builder.Config{StateDir: t.TempDir()}, mock)
	s.buildMgr = builder.NewBuildManager(gb, mock, nil, nil)
	if rec := do(s, "POST", "/api/actions/build-image", `{"target":"vm","arch":"arm64"}`, ""); rec.Code != 202 {
		t.Fatalf("first: %d", rec.Code)
	}
	if rec := do(s, "POST", "/api/actions/build-image", `{}`, ""); rec.Code != 409 {
		t.Errorf("second: %d", rec.Code)
	}
	_ = s.buildMgr.CancelBuild()
	close(release)
}

func TestOpenTerminal(t *testing.T) {
	var scripts []string
	var fail atomic.Bool
	oldOS, oldRun := hostOS, runOsascript
	t.Cleanup(func() { hostOS, runOsascript = oldOS, oldRun })
	runOsascript = func(ctx context.Context, script string) ([]byte, error) {
		scripts = append(scripts, script)
		if fail.Load() {
			return []byte("denied"), errors.New("osascript failed")
		}
		return []byte("ok"), nil
	}
	s := newTestServer(t, "tok", nil)
	path := "/api/actions/open-terminal"

	if rec := do(s, "POST", path, `{}`, ""); rec.Code != 401 {
		t.Errorf("unauth: %d", rec.Code)
	}
	if rec := do(s, "POST", path, `{bad`, "tok"); rec.Code != 400 {
		t.Errorf("bad json: %d", rec.Code)
	}
	if rec := do(s, "POST", path, `{"runner_name":"  "}`, "tok"); rec.Code != 400 {
		t.Errorf("empty name: %d", rec.Code)
	}
	if rec := do(s, "POST", path, `{"runner_name":"a;rm -rf"}`, "tok"); rec.Code != 400 {
		t.Errorf("injection: %d", rec.Code)
	}

	type resp struct {
		Success bool   `json:"success"`
		Command string `json:"command"`
	}
	call := func(body string) resp {
		rec := do(s, "POST", path, body, "tok")
		var r resp
		_ = json.Unmarshal(rec.Body.Bytes(), &r)
		if rec.Code != 200 {
			t.Fatalf("%s: %d", body, rec.Code)
		}
		return r
	}

	hostOS = "linux"
	if r := call(`{"runner_id":"runzero-abc"}`); r.Success || r.Command != "docker exec -it runzero-abc bash" {
		t.Errorf("linux docker: %+v", r)
	}
	hostOS = "darwin"
	if r := call(`{"runner_name":"runzero-j1"}`); !r.Success || r.Command != "orb -m runzero-j1 -u runner bash" {
		t.Errorf("orbstack by prefix: %+v", r)
	}
	if r := call(`{"runner_name":"runzero-vm-2"}`); !r.Success || !strings.Contains(r.Command, "orb -m") {
		t.Errorf("vm prefix: %+v", r)
	}
	if r := call(`{"runner_name":"x","backend":"orbstack"}`); !r.Success {
		t.Errorf("explicit backend: %+v", r)
	}
	fail.Store(true)
	if r := call(`{"runner_name":"x"}`); r.Success {
		t.Errorf("failure should not report success: %+v", r)
	}
	if len(scripts) != 4 {
		t.Errorf("osascript calls: %d", len(scripts))
	}
}

func TestRunOsascriptDefaultSeam(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := runOsascript(ctx, "return 1"); err == nil {
		t.Error("cancelled context must not run osascript")
	}
}

func freePort(t *testing.T) int {
	t.Helper()
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = l.Close() }()
	return l.Addr().(*net.TCPAddr).Port
}

func TestRunServesAndShutsDown(t *testing.T) {
	s := newTestServer(t, "", nil)
	s.port = freePort(t)
	stopCalled := make(chan struct{}, 1)
	s.gb = builder.NewGoldenBuilder(builder.Config{StateDir: t.TempDir()}, fakeExec{run: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "list" {
			return []byte(`[{"name":"runzero-vm-base-arm64","state":"running"}]`), nil
		}
		if len(args) > 0 && args[0] == "stop" {
			select {
			case stopCalled <- struct{}{}:
			default:
			}
		}
		return nil, nil
	}})

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- s.Run(ctx) }()

	url := "http://" + net.JoinHostPort("127.0.0.1", strconv.Itoa(s.port)) + "/health"
	deadline := time.Now().Add(5 * time.Second)
	for {
		resp, err := http.Get(url)
		if err == nil {
			_ = resp.Body.Close()
			break
		}
		if time.Now().After(deadline) {
			t.Fatalf("server never came up: %v", err)
		}
		time.Sleep(10 * time.Millisecond)
	}
	select {
	case <-stopCalled:
		time.Sleep(100 * time.Millisecond)
	case <-time.After(5 * time.Second):
		t.Fatal("startup cleanup never ran")
	}
	cancel()
	if err := <-done; err != nil {
		t.Errorf("shutdown: %v", err)
	}
}

func TestRunReportsListenError(t *testing.T) {
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = l.Close() }()
	s := newTestServer(t, "", nil)
	s.gb = nil
	s.port = l.Addr().(*net.TCPAddr).Port
	if err := s.Run(context.Background()); err == nil {
		t.Error("expected address-in-use error")
	}
}
