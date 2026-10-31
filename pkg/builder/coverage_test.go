package builder

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/el-j/run-zero/docker"
)

func vmListJSON(state string) string {
	return `[{"name":"runzero-vm-base-arm64","state":"` + state + `"},{"name":"runzero-vm-base-amd64","state":"` + state + `"}]`
}

// fakeDocker puts a stub docker binary first on PATH.
func fakeDocker(t *testing.T, script string) {
	t.Helper()
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "docker"), []byte("#!/bin/sh\n"+script+"\n"), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("PATH", dir+string(os.PathListSeparator)+os.Getenv("PATH"))
}

func waitBuild(t *testing.T, m *BuildManager, want string) *ImageBuildProgress {
	t.Helper()
	deadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		if p := m.GetActiveBuild(); p != nil && p.Status == want {
			return p
		}
		time.Sleep(10 * time.Millisecond)
	}
	t.Fatalf("build never reached %s: %+v", want, m.GetActiveBuild())
	return nil
}

func newTestManager(t *testing.T, run func(ctx context.Context, name string, args ...string) ([]byte, error)) (*BuildManager, *GoldenBuilder) {
	t.Helper()
	mock := &mockExecutor{runFunc: run}
	gb := NewGoldenBuilder(Config{StateDir: t.TempDir(), RunnerVersion: DefaultRunnerVersion}, mock)
	return NewBuildManager(gb, mock, nil, nil), gb
}

func TestBuilder_WriteStampAndStampValueEdges(t *testing.T) {
	file := filepath.Join(t.TempDir(), "file")
	if err := os.WriteFile(file, nil, 0o644); err != nil {
		t.Fatal(err)
	}
	gb := NewGoldenBuilder(Config{StateDir: filepath.Join(file, "sub")}, nil)
	if err := gb.WriteStamp("arm64"); err == nil {
		t.Error("expected MkdirAll error")
	}

	orig := docker.ProvisionToolchainScript
	docker.ProvisionToolchainScript = ""
	t.Cleanup(func() { docker.ProvisionToolchainScript = orig })
	gb = NewGoldenBuilder(Config{StateDir: t.TempDir(), RunnerVersion: "9.9.9"}, nil)
	if gb.stampValue() != "9.9.9" {
		t.Errorf("got %s", gb.stampValue())
	}
}

func TestBuilder_ListVMsErrorsAndEvents(t *testing.T) {
	ctx := context.Background()
	gb := NewGoldenBuilder(Config{}, &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) {
		return nil, errors.New("boom")
	}})
	if _, err := gb.ListVMs(ctx); err == nil {
		t.Error("expected exec error")
	}
	if gb.BaseImageExists(ctx, "arm64") {
		t.Error("expected false on error")
	}
	gb = NewGoldenBuilder(Config{}, &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) {
		return []byte("not json"), nil
	}})
	if _, err := gb.ListVMs(ctx); err == nil {
		t.Error("expected json error")
	}
	if _, err := gb.EnsureBaseImagesStopped(ctx); err == nil {
		t.Error("expected json error")
	}
	gb2 := NewGoldenBuilder(Config{}, &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) {
		return nil, errors.New("boom")
	}})
	if _, err := gb2.EnsureBaseImagesStopped(ctx); err == nil {
		t.Error("expected exec error")
	}

	for i := 0; i < 40; i++ {
		gb.EmitEvent(StatusReady, "arm64", "x")
	}
	if len(gb.Events()) != 32 {
		t.Errorf("expected channel to saturate at 32, got %d", len(gb.Events()))
	}
}

func TestBuildBaseImage_StaleAndPromoteFailure(t *testing.T) {
	var promoteFails bool
	mock := &mockExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if name == "orbctl" && len(args) > 0 {
			switch args[0] {
			case "list":
				return []byte(vmListJSON("stopped")), nil
			case "rename", "clone":
				if promoteFails {
					return nil, errors.New("nope")
				}
			}
		}
		return nil, nil
	}}
	gb := NewGoldenBuilder(Config{StateDir: t.TempDir(), CPUs: "2", Memory: "4G"}, mock)
	promoteFails = true
	if built, err := gb.BuildBaseImage(context.Background(), "arm64"); err == nil || built {
		t.Errorf("expected promotion failure, got %v %v", built, err)
	}
	promoteFails = false
	if built, err := gb.BuildBaseImage(context.Background(), "arm64"); err != nil || !built {
		t.Errorf("expected stale rebuild success, got %v %v", built, err)
	}
}

func TestNewImageInspectorAndManagerDefaults(t *testing.T) {
	work := t.TempDir()
	if err := os.MkdirAll(filepath.Join(work, "docker"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(work, "docker", "Dockerfile"), []byte("FROM scratch\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	t.Chdir(work)

	t.Setenv("RUNZERO_STATE_DIR", "")
	t.Setenv("PROVISION_SCRIPT", "")
	ins := NewImageInspector(nil, nil)
	if ins.gb == nil || ins.exec == nil {
		t.Fatal("expected defaults")
	}
	if _, err := os.Stat(filepath.Join(work, ".runzero-state")); err != nil {
		t.Errorf("expected default state dir: %v", err)
	}

	mgr := NewBuildManager(nil, nil, nil, nil)
	if mgr.dockerDir != "docker" || mgr.gb == nil {
		t.Errorf("unexpected manager: %+v", mgr)
	}

	t.Setenv("RUNZERO_STATE_DIR", filepath.Join(work, "custom"))
	t.Setenv("PROVISION_SCRIPT", filepath.Join(work, "p.sh"))
	ins = NewImageInspector(nil, nil)
	mgr = NewBuildManager(nil, nil, nil, nil)
	if _, err := os.Stat(filepath.Join(work, "custom")); err != nil {
		t.Errorf("expected custom state dir: %v", err)
	}
	if ins.gb.cfg.ProvisionScriptPath != filepath.Join(work, "p.sh") || mgr.gb.cfg.ProvisionScriptPath != filepath.Join(work, "p.sh") {
		t.Error("provision script env ignored")
	}
}

func TestInspect_StaleAndContainerNotReady(t *testing.T) {
	mock := &mockExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if name == "orbctl" {
			return []byte(vmListJSON("stopped")), nil
		}
		return []byte("local-github-runner:arm64|i|1GB|now\n"), nil
	}}
	gb := NewGoldenBuilder(Config{StateDir: t.TempDir()}, mock)
	_ = gb.WriteStamp("arm64")
	_ = os.WriteFile(gb.StampPath("amd64"), []byte("old\n"), 0o644)
	resp := NewImageInspector(gb, mock).Inspect(context.Background())
	if resp.VMImages[1].Status != string(StatusStale) || resp.AllReady {
		t.Errorf("unexpected %+v", resp)
	}

	_ = gb.WriteStamp("amd64")
	resp = NewImageInspector(gb, mock).Inspect(context.Background())
	if resp.AllReady || resp.ContainerImages[1].Status != "missing" {
		t.Errorf("expected containers to block readiness: %+v", resp)
	}
}

func TestInspect_FetchVMsFromBridge(t *testing.T) {
	failing := &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) {
		return nil, errors.New("no orbctl")
	}}
	gb := NewGoldenBuilder(Config{StateDir: t.TempDir()}, failing)
	ins := NewImageInspector(gb, failing)
	ctx := context.Background()

	var mode atomic.Int32
	var gotAuth atomic.Value
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth.Store(r.Header.Get("Authorization"))
		switch mode.Load() {
		case 0:
			_ = json.NewEncoder(w).Encode(ImagesStatusResponse{VMImages: []InfrastructureImageStatus{{ID: "remote", Status: "ready"}}})
		case 1:
			w.WriteHeader(http.StatusInternalServerError)
		case 2:
			_, _ = w.Write([]byte("garbage"))
		case 3:
			_ = json.NewEncoder(w).Encode(ImagesStatusResponse{})
		}
	}))
	defer srv.Close()

	t.Setenv("RUNZERO_BRIDGE_TOKEN", "tok")
	t.Setenv("HOST_VM_BRIDGE_URL", srv.URL+"/")
	vms := ins.inspectVMs(ctx)
	if len(vms) != 1 || vms[0].ID != "remote" || gotAuth.Load() != "Bearer tok" {
		t.Errorf("bridge result %+v auth=%v", vms, gotAuth.Load())
	}

	for _, m := range []int32{1, 2, 3} {
		mode.Store(m)
		if vms := ins.inspectVMs(ctx); len(vms) != 2 || vms[0].Status != "missing" {
			t.Errorf("mode %d: expected local fallback, got %+v", m, vms)
		}
	}

	t.Setenv("RUNZERO_BRIDGE_TOKEN", "")
	if ins.fetchVMsFromBridge(ctx, "http://[::1") != nil {
		t.Error("expected nil for bad URL")
	}
	closed := httptest.NewServer(http.NotFoundHandler())
	closed.Close()
	if ins.fetchVMsFromBridge(ctx, closed.URL) != nil {
		t.Error("expected nil for connection error")
	}
	t.Setenv("HOST_VM_BRIDGE_URL", "none")
	if vms := ins.inspectVMs(ctx); len(vms) != 2 {
		t.Errorf("got %+v", vms)
	}
}

func TestPromoteStaging_DeletesExistingBase(t *testing.T) {
	var deleted bool
	mock := &mockExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "list" {
			return []byte(`[{"name":"other"},{"name":"base"}]`), nil
		}
		if len(args) > 2 && args[0] == "delete" && args[2] == "base" {
			deleted = true
		}
		return nil, nil
	}}
	if err := NewGoldenBuilder(Config{}, mock).PromoteStaging(context.Background(), "stage", "base"); err != nil || !deleted {
		t.Errorf("err=%v deleted=%v", err, deleted)
	}
}

func TestBuildManager_GetBuildByIDAndEmptyStates(t *testing.T) {
	m, _ := newTestManager(t, nil)
	if m.GetActiveBuild() != nil {
		t.Error("expected nil active build")
	}
	if err := m.CancelBuild(); err != nil {
		t.Error(err)
	}
	if _, ok := m.GetBuildByID("nope"); ok {
		t.Error("expected miss")
	}
	m.activeBuild = &ImageBuildProgress{BuildID: "active"}
	m.history["old"] = &ImageBuildProgress{BuildID: "old"}
	if p, ok := m.GetBuildByID("active"); !ok || p.BuildID != "active" {
		t.Error("active lookup failed")
	}
	if p, ok := m.GetBuildByID("old"); !ok || p.BuildID != "old" {
		t.Error("history lookup failed")
	}
	if _, ok := m.GetBuildByID("missing"); ok {
		t.Error("expected miss with active build")
	}
}

func TestBuildManager_FullBuildSuccess(t *testing.T) {
	fakeDocker(t, "echo out; echo err >&2")
	t.Setenv("HOST_VM_BRIDGE_URL", "")
	m, gb := newTestManager(t, func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if name == "orbctl" && len(args) > 0 && args[0] == "list" {
			return []byte(vmListJSON("running")), nil
		}
		return nil, nil
	})
	_ = gb.WriteStamp("arm64")
	// default target/arch -> container+vm for both arches; arm64 is up to date, amd64 is rebuilt
	if _, err := m.TriggerBuild(context.Background(), ImageBuildRequest{}); err != nil {
		t.Fatal(err)
	}
	p := waitBuild(t, m, string(StatusReady))
	joined := strings.Join(p.LogLines, "\n")
	for _, want := range []string{"[DOCKER] out", "already up to date", "Successfully built", "Verified golden base VMs are stopped"} {
		if !strings.Contains(joined, want) {
			t.Errorf("missing log %q in:\n%s", want, joined)
		}
	}
	if p.ProgressPct != 100 {
		t.Errorf("progress %d", p.ProgressPct)
	}
	if got, ok := m.GetBuildByID(p.BuildID); !ok || got.Status != string(StatusReady) {
		t.Errorf("lookup %+v %v", got, ok)
	}
}

func TestBuildManager_VMOnlyAndContainerOnlyArchSelection(t *testing.T) {
	fakeDocker(t, "exit 0")
	t.Setenv("HOST_VM_BRIDGE_URL", "")
	m, _ := newTestManager(t, nil)
	if _, err := m.TriggerBuild(context.Background(), ImageBuildRequest{Target: "vm", Arch: "amd64"}); err != nil {
		t.Fatal(err)
	}
	waitBuild(t, m, string(StatusReady))
	m2, _ := newTestManager(t, nil)
	if _, err := m2.TriggerBuild(context.Background(), ImageBuildRequest{Target: "container", Arch: "amd64"}); err != nil {
		t.Fatal(err)
	}
	waitBuild(t, m2, string(StatusReady))
}

func TestBuildManager_FailureModes(t *testing.T) {
	t.Setenv("HOST_VM_BRIDGE_URL", "")
	fakeDocker(t, "echo broken; exit 3")
	m, _ := newTestManager(t, nil)
	if _, err := m.TriggerBuild(context.Background(), ImageBuildRequest{Target: "container", Arch: "arm64"}); err != nil {
		t.Fatal(err)
	}
	p := waitBuild(t, m, string(StatusFailed))
	if !strings.Contains(p.Error, "Failed building container") {
		t.Errorf("error %q", p.Error)
	}

	m2, _ := newTestManager(t, func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "create" {
			return nil, errors.New("create failed")
		}
		return nil, nil
	})
	if _, err := m2.TriggerBuild(context.Background(), ImageBuildRequest{Target: "vm", Arch: "arm64"}); err != nil {
		t.Fatal(err)
	}
	p = waitBuild(t, m2, string(StatusFailed))
	if !strings.Contains(p.Error, "Failed building vm") {
		t.Errorf("error %q", p.Error)
	}
}

func TestBuildManager_RunBuildCancelledContext(t *testing.T) {
	m, _ := newTestManager(t, nil)
	prog := &ImageBuildProgress{BuildID: "x", Target: "vm", Arch: "arm64", Status: string(StatusBuilding)}
	m.activeBuild = prog
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	m.runBuild(ctx, prog, ImageBuildRequest{})
	if prog.Status != string(StatusFailed) || prog.Error != "Build cancelled" {
		t.Errorf("got %+v", prog)
	}
}

func TestBuildManager_ContainerDirFallbackAndPipes(t *testing.T) {
	fakeDocker(t, "exit 0")
	work := t.TempDir()
	if err := os.MkdirAll(filepath.Join(work, "docker"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(work, "docker", "Dockerfile"), nil, 0o644); err != nil {
		t.Fatal(err)
	}
	t.Chdir(work)
	m, _ := newTestManager(t, nil)
	m.dockerDir = "does-not-exist"
	if err := m.buildContainerImage(context.Background(), "arm64"); err != nil {
		t.Error(err)
	}

	cmd := exec.Command("true")
	cmd.Stdout = &strings.Builder{}
	if err := m.streamCommandOutput(cmd, "x"); err == nil {
		t.Error("expected stdout pipe error")
	}
	cmd = exec.Command("true")
	cmd.Stderr = &strings.Builder{}
	if err := m.streamCommandOutput(cmd, "x"); err == nil {
		t.Error("expected stderr pipe error")
	}
	if err := m.streamCommandOutput(exec.Command(filepath.Join(work, "missing-binary")), "x"); err == nil {
		t.Error("expected start error")
	}
}

func TestBuildManager_LogTrimming(t *testing.T) {
	m, _ := newTestManager(t, nil)
	m.activeBuild = &ImageBuildProgress{}
	for i := 0; i < 1005; i++ {
		m.appendLog("line")
	}
	if n := len(m.activeBuild.LogLines); n > 1002 {
		t.Errorf("log not trimmed: %d", n)
	}
}

func TestBuildVMImage_DelegatesToBridgeWhenOrbctlMissing(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			w.WriteHeader(http.StatusAccepted)
			_, _ = w.Write([]byte(`{"build_id":"b1"}`))
			return
		}
		_, _ = w.Write([]byte(`{"status":"ready"}`))
	}))
	defer srv.Close()
	old := bridgePollInterval
	bridgePollInterval = 5 * time.Millisecond
	t.Cleanup(func() { bridgePollInterval = old })
	t.Setenv("HOST_VM_BRIDGE_URL", srv.URL)

	m, _ := newTestManager(t, func(ctx context.Context, name string, args ...string) ([]byte, error) {
		return nil, errors.New("no orbctl")
	})
	if err := m.buildVMImage(context.Background(), "arm64"); err != nil {
		t.Error(err)
	}
}

func TestBuildVMImageViaBridge_Errors(t *testing.T) {
	fastPoll(t)
	t.Setenv("RUNZERO_BRIDGE_TOKEN", "")
	m, _ := newTestManager(t, nil)
	ctx := context.Background()

	if err := m.buildVMImageViaBridge(ctx, "http://[::1", "arm64"); err == nil {
		t.Error("expected request error")
	}

	closed := httptest.NewServer(http.NotFoundHandler())
	closed.Close()
	if err := m.buildVMImageViaBridge(ctx, closed.URL, "arm64"); err == nil || !strings.Contains(err.Error(), "contact bridge") {
		t.Errorf("got %v", err)
	}

	var mode atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch mode.Load() {
		case 0:
			w.WriteHeader(http.StatusConflict)
			_, _ = w.Write([]byte(`{"error":"busy"}`))
		case 1:
			w.WriteHeader(http.StatusInternalServerError)
		case 2:
			_, _ = w.Write([]byte("not json"))
		}
	}))
	defer srv.Close()
	for i, want := range []string{"bridge build error: busy", "HTTP 500", "failed to parse"} {
		mode.Store(int32(i))
		if err := m.buildVMImageViaBridge(ctx, srv.URL, "arm64"); err == nil || !strings.Contains(err.Error(), want) {
			t.Errorf("mode %d: got %v want %q", i, err, want)
		}
	}
}

func fastPoll(t *testing.T) {
	t.Helper()
	old := bridgePollInterval
	bridgePollInterval = 5 * time.Millisecond
	t.Cleanup(func() { bridgePollInterval = old })
}

// bridgeStub serves a scripted sequence of poll responses after accepting a build.
func bridgeStub(t *testing.T, buildID string, polls []func(w http.ResponseWriter, r *http.Request), cancelHits *atomic.Int32) *httptest.Server {
	t.Helper()
	var n atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case r.Method == http.MethodPost && strings.HasSuffix(r.URL.Path, "/cancel"):
			if cancelHits != nil {
				cancelHits.Add(1)
			}
		case r.Method == http.MethodPost:
			w.WriteHeader(http.StatusAccepted)
			_ = json.NewEncoder(w).Encode(ImageBuildProgress{BuildID: buildID})
		default:
			i := int(n.Add(1)) - 1
			if i >= len(polls) {
				i = len(polls) - 1
			}
			polls[i](w, r)
		}
	}))
	t.Cleanup(srv.Close)
	return srv
}

func jsonPoll(p ImageBuildProgress) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) { _ = json.NewEncoder(w).Encode(p) }
}

func TestBuildVMImageViaBridge_PollSequenceSuccess(t *testing.T) {
	fastPoll(t)
	t.Setenv("RUNZERO_BRIDGE_TOKEN", "tok")
	dropConn := func(w http.ResponseWriter, r *http.Request) {
		hj, _ := w.(http.Hijacker)
		c, _, _ := hj.Hijack()
		_ = c.Close()
	}
	// Two drops: the HTTP client may transparently retry the first idempotent GET.
	srv := bridgeStub(t, "b1", []func(http.ResponseWriter, *http.Request){
		dropConn,
		dropConn,
		func(w http.ResponseWriter, r *http.Request) { _, _ = w.Write([]byte("garbage")) },
		jsonPoll(ImageBuildProgress{Status: "building", CurrentStep: "step", LogLines: []string{"a", "b"}}),
		jsonPoll(ImageBuildProgress{Status: "building", LogLines: []string{"a", "b"}}),
		jsonPoll(ImageBuildProgress{Status: "ready", LogLines: []string{"a", "b", "c"}}),
	}, nil)

	var lines []string
	m, _ := newTestManager(t, nil)
	m.activeBuild = &ImageBuildProgress{}
	m.logHook = func(l string) { lines = append(lines, l) }
	if err := m.buildVMImageViaBridge(context.Background(), srv.URL, "arm64"); err != nil {
		t.Fatal(err)
	}
	if m.activeBuild.CurrentStep != "step" {
		t.Errorf("step %q", m.activeBuild.CurrentStep)
	}
	if got := strings.Join(lines, ","); !strings.Contains(got, "a,b,c") {
		t.Errorf("log lines %s", got)
	}
}

func TestBuildVMImageViaBridge_RemoteFailure(t *testing.T) {
	fastPoll(t)
	t.Setenv("RUNZERO_BRIDGE_TOKEN", "")
	m, _ := newTestManager(t, nil)
	srv := bridgeStub(t, "b1", []func(http.ResponseWriter, *http.Request){jsonPoll(ImageBuildProgress{Status: "failed", Error: "kaput"})}, nil)
	if err := m.buildVMImageViaBridge(context.Background(), srv.URL, "arm64"); err == nil || err.Error() != "kaput" {
		t.Errorf("got %v", err)
	}
	srv2 := bridgeStub(t, "b1", []func(http.ResponseWriter, *http.Request){jsonPoll(ImageBuildProgress{Status: "failed"})}, nil)
	if err := m.buildVMImageViaBridge(context.Background(), srv2.URL, "arm64"); err == nil || !strings.Contains(err.Error(), "bridge build failed") {
		t.Errorf("got %v", err)
	}
}

func TestBuildVMImageViaBridge_ContextCancelSendsCancel(t *testing.T) {
	fastPoll(t)
	for _, token := range []string{"", "tok"} {
		t.Setenv("RUNZERO_BRIDGE_TOKEN", token)
		var cancels atomic.Int32
		srv := bridgeStub(t, "b1", []func(http.ResponseWriter, *http.Request){jsonPoll(ImageBuildProgress{Status: "building"})}, &cancels)
		m, _ := newTestManager(t, nil)
		ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
		err := m.buildVMImageViaBridge(ctx, srv.URL, "arm64")
		cancel()
		if !errors.Is(err, context.DeadlineExceeded) || cancels.Load() != 1 {
			t.Errorf("token=%q err=%v cancels=%d", token, err, cancels.Load())
		}
	}
}

func TestBuildVMImageViaBridge_BadPollURL(t *testing.T) {
	fastPoll(t)
	t.Setenv("RUNZERO_BRIDGE_TOKEN", "")
	// A build id containing a control character makes the poll URL unparsable.
	srv := bridgeStub(t, "bad\u007fid", []func(http.ResponseWriter, *http.Request){jsonPoll(ImageBuildProgress{})}, nil)
	m, _ := newTestManager(t, nil)
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Millisecond)
	defer cancel()
	if err := m.buildVMImageViaBridge(ctx, srv.URL, "arm64"); err == nil {
		t.Error("expected context error")
	}
}
