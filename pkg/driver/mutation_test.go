package driver

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestRunnerNames_DefaultsAndExactLength(t *testing.T) {
	if got := ManualRunnerName("o/r", "", ""); got != "runzero-manual-amd64-o__r-rand" {
		t.Errorf("empty arch/entropy: %q", got)
	}
	if got := JobScopedRunnerName("o/r", "!!!", 2, 1, "???"); got != "runzero-j1-r2-amd64-o__r-rand" {
		t.Errorf("unusable arch/entropy: %q", got)
	}
	long := "owner/" + strings.Repeat("r", 80)
	for _, n := range []string{ManualRunnerName(long, "arm64", "abc123"), JobScopedRunnerName(long, "arm64", 2, 1, "abc123")} {
		if len(n) != maxRunnerNameLen || !strings.HasSuffix(n, "-abc123") {
			t.Errorf("a long repo must fill exactly %d chars: %q (%d)", maxRunnerNameLen, n, len(n))
		}
	}
}

func TestFitRepoPart(t *testing.T) {
	if got := fitRepoPart("abcdefghij", maxRunnerNameLen-3); got != "abcdefgh" {
		t.Errorf("must keep at least 8 chars, got %q", got)
	}
	if got := fitRepoPart("abc-", 10); got != "abc" {
		t.Errorf("trailing separators are trimmed, got %q", got)
	}
}

func TestResolveRepoFromMachineName_MinimalTokenCounts(t *testing.T) {
	repos := []string{"repo"}
	if got := ResolveRepoFromMachineName(ManualRunnerName("repo", "amd64", "abc"), repos); got != "repo" {
		t.Errorf("4-token manual name: %q", got)
	}
	if got := ResolveRepoFromMachineName(JobScopedRunnerName("repo", "amd64", 2, 1, "abc"), repos); got != "repo" {
		t.Errorf("5-token job name: %q", got)
	}
}

func TestBridgeDriver_TokenOnEveryRequestAndHTTP400(t *testing.T) {
	var auths []string
	code := http.StatusOK
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auths = append(auths, r.Header.Get("Authorization"))
		w.WriteHeader(code)
		_, _ = w.Write([]byte(`{"runner_id":"x","runners":[]}`))
	}))
	defer srv.Close()
	ctx := context.Background()
	for _, token := range []string{"tok", ""} {
		auths = nil
		b := NewBridgeDriver(srv.URL, "orbstack", token, srv.Client())
		_, _ = b.SpawnRunner(ctx, RunnerSpec{Name: "n"})
		_, _ = b.ListRunners(ctx)
		_ = b.StopRunner(ctx, "x")
		_ = b.CleanupAll(ctx)
		want := ""
		if token != "" {
			want = "Bearer " + token
		}
		if len(auths) != 4 {
			t.Fatalf("expected 4 requests, got %d", len(auths))
		}
		for i, a := range auths {
			if a != want {
				t.Errorf("token %q, request %d: %q", token, i, a)
			}
		}
	}
	code = http.StatusBadRequest
	if err := NewBridgeDriver(srv.URL, "orbstack", "", srv.Client()).StopRunner(ctx, "x"); err == nil {
		t.Error("HTTP 400 must fail a stop")
	}
	if NewBridgeDriver(srv.URL, "", "", nil).client.Timeout != bridgeRequestTimeout {
		t.Error("default client must use bridgeRequestTimeout")
	}
}

func TestOrbStackSpawn_SetsSizeOnlyWhenGiven(t *testing.T) {
	exec := &recordingExec{}
	_, _ = NewOrbStackDriver(exec, nil, "").SpawnRunner(context.Background(), RunnerSpec{Name: "runzero-x"})
	if exec.called("orbctl config set") {
		t.Fatalf("no size means no config set: %v", exec.calls)
	}
	exec = &recordingExec{}
	_, _ = NewOrbStackDriver(exec, nil, "").SpawnRunner(context.Background(), RunnerSpec{Name: "runzero-x", CPUs: 2, MemoryMB: 4096})
	if !exec.called("orbctl config set runzero-x cpu 2") || !exec.called("orbctl config set runzero-x memory 4096M") {
		t.Fatalf("calls %v", exec.calls)
	}
}

func TestOrbStackEnrichFromStore(t *testing.T) {
	store := NewInstanceStore("")
	when := "2026-11-01T10:00:00Z"
	store.Register(state.RunnerInfo{ID: "k", Name: "runzero-known", TargetRepo: "o/r", CreatedAt: &when})
	o := NewOrbStackDriver(&recordingExec{}, store, "")

	listed := "2026-11-02T10:00:00Z"
	runners := []state.RunnerInfo{{Name: "runzero-known"}, {Name: "runzero-known", CreatedAt: &listed}, {Name: "runzero-new"}}
	o.enrichFromStore(runners)
	if *runners[0].CreatedAt != when || *runners[1].CreatedAt != listed {
		t.Errorf("known runner: created %v / %v", *runners[0].CreatedAt, *runners[1].CreatedAt)
	}
	if runners[2].CreatedAt == nil {
		t.Fatal("an unknown runner must get a first-seen time")
	}
	if _, ok := store.Get(""); !ok {
		t.Error("an unknown runner must be recorded in the store")
	}
	NewOrbStackDriver(&recordingExec{}, nil, "").enrichFromStore([]state.RunnerInfo{{Name: "runzero-y"}})
}

func TestOrbStackStop_UsesTheStoredMachineName(t *testing.T) {
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "abc", Name: "runzero-real"})
	exec := &recordingExec{replies: []reply{{prefix: "orbctl list", out: ""}}}
	_ = NewOrbStackDriver(exec, store, "").StopRunner(context.Background(), "abc")
	if !exec.called("orbctl delete -f runzero-real") {
		t.Fatalf("calls %v", exec.calls)
	}
}

func TestParseOrbctlList_TwoColumns(t *testing.T) {
	if r := parseOrbctlList("runzero-x stopped"); len(r) != 1 || r[0].Status != "stopped" {
		t.Fatalf("got %+v", r)
	}
}

// logDriver serves fixed logs.
type logDriver struct {
	dummyDriver
	logs string
}

func (l *logDriver) RunnerLogs(context.Context, string, int) (string, error) { return l.logs, nil }

func TestRouter_StoreAndLogOrder(t *testing.T) {
	store := NewInstanceStore("")
	docker := &logDriver{dummyDriver: dummyDriver{backend: "docker"}, logs: "D"}
	vm := &logDriver{dummyDriver: dummyDriver{backend: "multipass"}, logs: "V"}
	r := NewRouter(docker, vm, "auto", false, store)

	if _, err := r.SpawnRunner(context.Background(), RunnerSpec{ID: "new", Backend: "docker"}); err != nil {
		t.Fatal(err)
	}
	if _, ok := store.Get("new"); !ok {
		t.Error("a spawned runner must be recorded")
	}
	if _, err := r.ListRunners(context.Background()); err != nil {
		t.Fatal(err)
	}
	if _, ok := store.Get("r-docker"); !ok {
		t.Error("listed runners must be recorded")
	}

	store.Register(state.RunnerInfo{ID: "vm1", Backend: "multipass"})
	store.Register(state.RunnerInfo{ID: "c1", Backend: "docker"})
	if got, _ := r.RunnerLogs(context.Background(), "vm1", 10); got != "V" {
		t.Errorf("a VM runner's logs come from the VM driver first, got %q", got)
	}
	if got, _ := r.RunnerLogs(context.Background(), "c1", 10); got != "D" {
		t.Errorf("a container runner's logs come from docker first, got %q", got)
	}

	failing := &dummyDriver{backend: "docker", spawnFunc: func(RunnerSpec) (*state.RunnerInfo, error) { return nil, errors.New("boom") }}
	fr := NewRouter(failing, nil, "auto", false, store)
	_, _ = fr.SpawnRunner(context.Background(), RunnerSpec{ID: "failed"})
	if _, ok := store.Get("failed"); ok {
		t.Error("a failed spawn must not be recorded")
	}

	noStore := NewRouter(docker, vm, "auto", false, nil)
	_, _ = noStore.SpawnRunner(context.Background(), RunnerSpec{ID: "x"})
	_, _ = noStore.ListRunners(context.Background())
}

func TestRouter_OwnerFromStoreMatchesByName(t *testing.T) {
	store := NewInstanceStore("")
	for i := 0; i < 20; i++ {
		store.Register(state.RunnerInfo{ID: fmt.Sprintf("d%d", i), Name: fmt.Sprintf("docker-%d", i), Backend: "docker"})
	}
	store.Register(state.RunnerInfo{ID: "v", Name: "vm-runner", Backend: "orbstack"})
	docker, vm := &dummyDriver{backend: "docker"}, &dummyDriver{backend: "vm"}
	if got := NewRouter(docker, vm, "auto", false, store).ownerFromStore("vm-runner"); got != vm {
		t.Fatal("lookup by name must find that runner's driver")
	}
}

func TestDockerSpawn_PlatformAndImage(t *testing.T) {
	exec := &recordingExec{}
	d := NewDockerDriver(exec, nil, "default-image", "")
	_, _ = d.SpawnRunner(context.Background(), RunnerSpec{ID: "a", Arch: "arm64"})
	_, _ = d.SpawnRunner(context.Background(), RunnerSpec{ID: "b"})
	if !strings.Contains(exec.calls[0], "--platform linux/arm64") || !strings.HasSuffix(exec.calls[0], " local-github-runner:arm64") {
		t.Errorf("with arch: %s", exec.calls[0])
	}
	if strings.Contains(exec.calls[1], "--platform") || !strings.HasSuffix(exec.calls[1], " default-image") {
		t.Errorf("without arch: %s", exec.calls[1])
	}
}

func TestParseWSLList_TwoColumns(t *testing.T) {
	if got := parseWSLList("NAME STATE\nrunzero-x Running"); got["runzero-x"] != "running" {
		t.Fatalf("got %v", got)
	}
}

func TestWSLStop_WithoutStore(t *testing.T) {
	d := NewWSLDriver(&recordingExec{}, nil, "", `C:\base.tar`, `C:\wsl`)
	if err := d.StopRunner(context.Background(), "runzero-x"); err != nil {
		t.Fatal(err)
	}
}

func TestBridgeDriver_JSONContentTypeOnlyWithABody(t *testing.T) {
	types := map[string]string{}
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		types[r.URL.Path] = r.Header.Get("Content-Type")
		_, _ = w.Write([]byte(`{"runner_id":"x","runners":[]}`))
	}))
	defer srv.Close()
	b := NewBridgeDriver(srv.URL, "orbstack", "", srv.Client())
	_, _ = b.SpawnRunner(context.Background(), RunnerSpec{Name: "n"})
	_ = b.StopRunner(context.Background(), "x")
	_, _ = b.ListRunners(context.Background())
	if types["/api/drivers/orbstack/spawn"] != "application/json" || types["/api/drivers/orbstack/stop"] != "application/json" || types["/api/drivers/orbstack/runners"] != "" {
		t.Fatalf("content types %v", types)
	}
}

func TestDockerResourceArgs_SizesOnlyWhenGiven(t *testing.T) {
	d := NewDockerDriver(&recordingExec{}, nil, "", "")
	if args := strings.Join(d.resourceArgs(RunnerSpec{}), " "); strings.Contains(args, "--cpus") || strings.Contains(args, "-m=") {
		t.Errorf("no size: %q", args)
	}
	if args := strings.Join(d.resourceArgs(RunnerSpec{CPUs: 1, MemoryMB: 1}), " "); !strings.Contains(args, "--cpus=1") || !strings.Contains(args, "-m=1m") {
		t.Errorf("size 1: %q", args)
	}
}

func TestDockerResolveTargets_IncludesLabelledContainers(t *testing.T) {
	exec := &recordingExec{replies: []reply{{prefix: "docker ps -aq --filter label=runzero.id=abc", out: "c1\nc2"}}}
	got := NewDockerDriver(exec, nil, "", "").resolveTargets(context.Background(), "abc")
	if !strings.Contains(strings.Join(got, ","), "c1") || !strings.Contains(strings.Join(got, ","), "c2") {
		t.Fatalf("targets %v", got)
	}
	failing := &recordingExec{replies: []reply{{prefix: "docker ps", out: "c9", err: errBoom}}}
	if got := NewDockerDriver(failing, nil, "", "").resolveTargets(context.Background(), "abc"); strings.Contains(strings.Join(got, ","), "c9") {
		t.Fatalf("a failed listing must not add targets: %v", got)
	}
}

func TestDockerStop_IgnoresARunIDOfZero(t *testing.T) {
	store := NewInstanceStore("")
	zero := int64(0)
	store.Register(state.RunnerInfo{ID: "abc", RunID: &zero})
	exec := &recordingExec{replies: []reply{{prefix: "docker rm -f", out: "abc"}}}
	if err := NewDockerDriver(exec, store, "", "").StopRunner(context.Background(), "abc"); err != nil {
		t.Fatal(err)
	}
	if exec.called("docker ps -aq --filter name=0") {
		t.Fatalf("run ID 0 must not select sibling containers: %v", exec.calls)
	}
}

func TestExtractRunIDToken(t *testing.T) {
	for in, want := range map[string]string{
		"runzero-j1-r1-amd64": "1",
		"runzero-j1-r09-x":    "09",
		"runzero-r9:x":        "",
		"runzero-r-x":         "",
		"runzero-repo-x":      "",
		"runzero-r/1":         "",
	} {
		if got := extractRunIDToken(in); got != want {
			t.Errorf("extractRunIDToken(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestDockerRunnerLogs_DefaultTail(t *testing.T) {
	exec := &recordingExec{replies: []reply{{prefix: "docker ps", out: "c1"}}}
	_, _ = NewDockerDriver(exec, nil, "", "").RunnerLogs(context.Background(), "abc", 0)
	if !exec.called("docker logs --tail 100") {
		t.Fatalf("calls %v", exec.calls)
	}
}

func TestParseDockerPSRow_FiveColumns(t *testing.T) {
	if r := parseDockerPSRow([]string{"id", "name", "Up", "running", "o/r"}); r.TargetRepo != "o/r" {
		t.Fatalf("got %+v", r)
	}
}

func TestApplyKnown_KeepsParsedArchWithoutAStoredOne(t *testing.T) {
	known := map[string]state.RunnerInfo{"n": {ID: "n", Name: "n"}}
	r := state.RunnerInfo{Name: "n", TargetArch: "arm64"}
	applyKnown(&r, known)
	if r.TargetArch != "arm64" {
		t.Fatalf("got %q", r.TargetArch)
	}
	known["n"] = state.RunnerInfo{ID: "n", Name: "n", TargetArch: "amd64"}
	applyKnown(&r, known)
	if r.TargetArch != "amd64" {
		t.Fatalf("stored arch must win, got %q", r.TargetArch)
	}
}

func TestResolveMachineName_ByName(t *testing.T) {
	store := NewInstanceStore("")
	for i := 0; i < 20; i++ {
		store.Register(state.RunnerInfo{ID: fmt.Sprintf("k%d", i), Name: fmt.Sprintf("runzero-m%d", i)})
	}
	if got := resolveMachineName(store, "runzero-m7"); got != "runzero-m7" {
		t.Fatalf("by name: got %q", got)
	}
	if got := resolveMachineName(store, "k3"); got != "runzero-m3" {
		t.Fatalf("by ID: got %q", got)
	}
	store.Register(state.RunnerInfo{ID: "other-key", Name: "runzero-zzz-abc123"})
	if got := resolveMachineName(store, "abc123"); got != "runzero-zzz-abc123" {
		t.Fatalf("by suffix: got %q", got)
	}
}

func TestSanitizeNamePart_Charset(t *testing.T) {
	if got := sanitizeNamePart("az09-_.`{/:"); got != "az09-_." {
		t.Fatalf("got %q", got)
	}
}

func TestParseJobScopedName_FiveTokens(t *testing.T) {
	if n, ok := parseJobScopedName("runzero-j1-r2-amd64-repo-abc"); !ok || n.repo != "repo" || n.id != "abc" {
		t.Fatalf("got %+v %v", n, ok)
	}
}

func TestWSLSpawn_WithoutStore(t *testing.T) {
	d := NewWSLDriver(&recordingExec{}, nil, "", `C:\base.tar`, `C:\wsl`)
	d.hostArch = "amd64"
	if _, err := d.SpawnRunner(context.Background(), RunnerSpec{Name: "runzero-x", Arch: "amd64"}); err != nil {
		t.Fatal(err)
	}
}
