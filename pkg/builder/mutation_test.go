package builder

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
)

func TestNewBuildManager_UsesStateDirFromEnvironment(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("RUNZERO_STATE_DIR", dir)
	if m := NewBuildManager(nil, &mockExecutor{}, nil, nil); !strings.HasPrefix(m.gb.StampPath("amd64"), dir) {
		t.Fatalf("stamp path %q", m.gb.StampPath("amd64"))
	}
}

func TestProvisionScript_PrefersANonEmptyCustomFile(t *testing.T) {
	dir := t.TempDir()
	custom := filepath.Join(dir, "custom.sh")
	_ = os.WriteFile(custom, []byte("echo custom"), 0o644)
	empty := filepath.Join(dir, "empty.sh")
	_ = os.WriteFile(empty, nil, 0o644)

	embedded := NewGoldenBuilder(Config{}, &mockExecutor{}).provisionScript()
	for path, want := range map[string]string{custom: "echo custom", empty: embedded, filepath.Join(dir, "missing.sh"): embedded, "": embedded} {
		if got := NewGoldenBuilder(Config{ProvisionScriptPath: path}, &mockExecutor{}).provisionScript(); got != want {
			t.Errorf("%q: got %.20q", path, got)
		}
	}
}

func TestBuildBaseImage_CreateArgs(t *testing.T) {
	var create string
	exec := &mockExecutor{runFunc: func(_ context.Context, name string, args ...string) ([]byte, error) {
		if name == "orbctl" && len(args) > 0 && args[0] == "create" {
			create = strings.Join(args, " ")
		}
		return []byte("[]"), nil
	}}
	_, _ = NewGoldenBuilder(Config{StateDir: t.TempDir(), CPUs: "4", Memory: "8G", Distro: "debian:12"}, exec).BuildBaseImage(context.Background(), "arm64")
	if !strings.Contains(create, "--cpus 4 --memory 8G debian:12") {
		t.Fatalf("create args %q", create)
	}
	_, _ = NewGoldenBuilder(Config{StateDir: t.TempDir()}, exec).BuildBaseImage(context.Background(), "arm64")
	if strings.Contains(create, "--cpus") || strings.Contains(create, "--memory") || !strings.Contains(create, "ubuntu:24.04") {
		t.Fatalf("defaults: create args %q", create)
	}
}

func TestPromoteStaging_DeletesOnlyAnExistingBase(t *testing.T) {
	var deleted []string
	exec := &mockExecutor{runFunc: func(_ context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "list" {
			return []byte(`[{"name":"other","state":"stopped"}]`), nil
		}
		if len(args) > 0 && args[0] == "delete" {
			deleted = append(deleted, args[len(args)-1])
		}
		return nil, nil
	}}
	_ = NewGoldenBuilder(Config{StateDir: t.TempDir()}, exec).PromoteStaging(context.Background(), "staging", "runzero-vm-base-arm64")
	for _, d := range deleted {
		if d == "runzero-vm-base-arm64" {
			t.Fatalf("a base that does not exist must not be deleted: %v", deleted)
		}
	}
}

func TestAllImagesReady(t *testing.T) {
	ready := []InfrastructureImageStatus{{Status: string(StatusReady)}}
	missing := []InfrastructureImageStatus{{Status: "missing"}}
	if !allImagesReady(ready, ready) || allImagesReady(missing, ready) || allImagesReady(ready, missing) || !allImagesReady() {
		t.Fatal("readiness misjudged")
	}
}

func TestInspect_ReportsStampedVersion(t *testing.T) {
	exec := &mockExecutor{runFunc: func(_ context.Context, name string, args ...string) ([]byte, error) {
		return []byte(vmListJSON("stopped")), nil
	}}
	gb := NewGoldenBuilder(Config{StateDir: t.TempDir()}, exec)
	_ = gb.WriteStamp("arm64")
	resp := NewImageInspector(gb, exec).Inspect(context.Background())
	if resp.VMImages[0].Version != gb.stampValue() {
		t.Fatalf("version %q, want %q", resp.VMImages[0].Version, gb.stampValue())
	}
}

func TestCancelBuild_CancelsAndPublishes(t *testing.T) {
	var published []ImageBuildProgress
	m := NewBuildManager(NewGoldenBuilder(Config{StateDir: t.TempDir()}, &mockExecutor{}), &mockExecutor{}, nil, func(p ImageBuildProgress) { published = append(published, p) })
	cancelled := false
	m.activeBuild = &ImageBuildProgress{Status: string(StatusBuilding)}
	m.cancelFunc = func() { cancelled = true }
	_ = m.CancelBuild()
	if !cancelled || m.cancelFunc != nil || len(published) != 1 || published[0].Status != string(StatusFailed) {
		t.Fatalf("cancelled %v, published %+v", cancelled, published)
	}
}

func TestBuildTargets(t *testing.T) {
	for _, c := range []struct{ target, arch, want string }{
		{"container", "all", "[{container arm64} {container amd64}]"},
		{"container", "both", "[{container arm64} {container amd64}]"},
		{"vm", "amd64", "[{vm amd64}]"},
		{"all", "arm64", "[{container arm64} {vm arm64}]"},
	} {
		if got := fmt.Sprint(buildTargets(c.target, c.arch)); got != c.want {
			t.Errorf("%s/%s: got %s", c.target, c.arch, got)
		}
	}
}

// dockerLog installs a fake docker that records its arguments.
func dockerLog(t *testing.T) string {
	t.Helper()
	log := filepath.Join(t.TempDir(), "docker.log")
	fakeDocker(t, `echo "$@" >> `+log)
	return log
}

func withDockerfile(t *testing.T, dir string) {
	t.Helper()
	_ = os.MkdirAll(dir, 0o755)
	_ = os.WriteFile(filepath.Join(dir, "Dockerfile"), []byte("FROM scratch"), 0o644)
}

func TestRunBuild_ReportsStepProgress(t *testing.T) {
	_ = dockerLog(t)
	var mu sync.Mutex
	var steps []string
	m := NewBuildManager(NewGoldenBuilder(Config{StateDir: t.TempDir()}, &mockExecutor{}), &mockExecutor{}, nil, func(p ImageBuildProgress) {
		mu.Lock()
		steps = append(steps, fmt.Sprintf("%d %s", p.ProgressPct, p.CurrentStep))
		mu.Unlock()
	})
	m.dockerDir = t.TempDir()
	withDockerfile(t, m.dockerDir)
	p := &ImageBuildProgress{Status: string(StatusBuilding), Target: "container", Arch: "both"}
	m.activeBuild = p
	m.runBuild(context.Background(), p, ImageBuildRequest{})
	want := []string{"0 [1/2] Building container image for arm64...", "50 [2/2] Building container image for amd64..."}
	if len(steps) < 2 || steps[0] != want[0] || steps[1] != want[1] {
		t.Fatalf("steps %q", steps)
	}
}

func TestBuildContainerImage_FindsTheDockerfile(t *testing.T) {
	log := dockerLog(t)
	cwd := t.TempDir()
	withDockerfile(t, filepath.Join(cwd, "docker"))
	t.Chdir(cwd)
	m := NewBuildManager(NewGoldenBuilder(Config{StateDir: t.TempDir()}, &mockExecutor{}), &mockExecutor{}, nil, nil)

	configured := t.TempDir()
	withDockerfile(t, configured)
	m.dockerDir = configured
	_ = m.buildContainerImage(context.Background(), "arm64")
	m.dockerDir = filepath.Join(t.TempDir(), "nothing-here")
	_ = m.buildContainerImage(context.Background(), "arm64")

	data, _ := os.ReadFile(log)
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != 2 || !strings.HasSuffix(lines[0], " "+configured) || !strings.HasSuffix(lines[1], " docker") {
		t.Fatalf("expected the configured dir, then the ./docker fallback; docker calls %q", lines)
	}
}

func TestBuildVMImage_LogsOnlyStoppedTemplates(t *testing.T) {
	t.Setenv("HOST_VM_BRIDGE_URL", "")
	run := func(state string) string {
		var mu sync.Mutex
		var logs []string
		exec := &mockExecutor{runFunc: func(_ context.Context, name string, args ...string) ([]byte, error) {
			return []byte(vmListJSON(state)), nil
		}}
		gb := NewGoldenBuilder(Config{StateDir: t.TempDir()}, exec)
		_ = gb.WriteStamp("arm64")
		m := NewBuildManager(gb, exec, func(l string) { mu.Lock(); logs = append(logs, l); mu.Unlock() }, nil)
		_ = m.buildVMImage(context.Background(), "arm64")
		return strings.Join(logs, "\n")
	}
	if out := run("stopped"); strings.Contains(out, "Verified golden base VMs are stopped") {
		t.Fatalf("nothing stopped must not be logged:\n%s", out)
	}
	if out := run("running"); !strings.Contains(out, "Verified golden base VMs are stopped") {
		t.Fatalf("stopped templates must be logged:\n%s", out)
	}
}

func TestBridgeRequests_SendTheTokenOnlyWhenSet(t *testing.T) {
	var auths []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auths = append(auths, r.Header.Get("Authorization"))
		w.WriteHeader(http.StatusAccepted)
		_, _ = w.Write([]byte(`{"build_id":"b1"}`))
	}))
	defer srv.Close()
	for _, token := range []string{"tok", ""} {
		auths = nil
		_, _ = startBridgeBuild(context.Background(), srv.Client(), srv.URL, token, "arm64")
		cancelBridgeBuild(srv.Client(), srv.URL, token, "b1")
		_, _ = fetchBridgeProgress(context.Background(), srv.Client(), srv.URL+"/api/images/build/b1", token)
		want := ""
		if token != "" {
			want = "Bearer " + token
		}
		for i, a := range auths {
			if a != want {
				t.Errorf("token %q, request %d: Authorization %q", token, i, a)
			}
		}
		if len(auths) != 3 {
			t.Fatalf("expected 3 requests, got %d", len(auths))
		}
	}
}

func TestAppendLog_KeepsTheLast1000Lines(t *testing.T) {
	m := &BuildManager{activeBuild: &ImageBuildProgress{}}
	for i := 1; i <= 1001; i++ {
		m.appendLogLocked(fmt.Sprintf("line%d", i))
	}
	lines := m.activeBuild.LogLines
	if len(lines) != maxBuildLogLines || lines[0] != "line2" || lines[len(lines)-1] != "line1001" {
		t.Fatalf("len %d, first %q, last %q", len(lines), lines[0], lines[len(lines)-1])
	}
}

func TestMirrorBridgeProgress(t *testing.T) {
	m := &BuildManager{activeBuild: &ImageBuildProgress{}}
	if next := m.mirrorBridgeProgress(ImageBuildProgress{LogLines: []string{"a", "b"}}, 1); next != 2 || len(m.activeBuild.LogLines) != 1 || m.activeBuild.LogLines[0] != "b" {
		t.Fatalf("next %d, lines %v", next, m.activeBuild.LogLines)
	}
	if next := m.mirrorBridgeProgress(ImageBuildProgress{LogLines: []string{"a"}}, 5); next != 5 || len(m.activeBuild.LogLines) != 1 {
		t.Fatalf("a shorter (restarted) bridge log must not rewind: next %d", next)
	}
}
