package driver

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestBridgeDriver_DefaultsAndRequestErrors(t *testing.T) {
	store := NewInstanceStore("")
	d := NewBridgeDriver("", "", "", nil, store)
	if d.baseURL != "http://host.docker.internal:49504" || d.backend != "orbstack" || d.client == nil || d.store != store {
		t.Errorf("defaults: %+v", d)
	}

	ctx := context.Background()
	bad := NewBridgeDriver("http://[::1", "orbstack", "", nil)
	if _, err := bad.SpawnRunner(ctx, RunnerSpec{}); err == nil {
		t.Error("spawn: expected request error")
	}
	if _, err := bad.ListRunners(ctx); err == nil {
		t.Error("list: expected request error")
	}
	if err := bad.StopRunner(ctx, "x"); err == nil {
		t.Error("stop: expected request error")
	}
	if err := bad.CleanupAll(ctx); err == nil {
		t.Error("cleanup: expected request error")
	}

	closed := httptest.NewServer(http.NotFoundHandler())
	closed.Close()
	dead := NewBridgeDriver(closed.URL, "orbstack", "tok", closed.Client())
	if _, err := dead.SpawnRunner(ctx, RunnerSpec{}); err == nil {
		t.Error("spawn: expected transport error")
	}
	if _, err := dead.ListRunners(ctx); err == nil {
		t.Error("list: expected transport error")
	}
	if err := dead.StopRunner(ctx, "x"); err == nil {
		t.Error("stop: expected transport error")
	}
	if err := dead.CleanupAll(ctx); err == nil {
		t.Error("cleanup: expected transport error")
	}
}

func TestBridgeDriver_ResponseHandling(t *testing.T) {
	var mode atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch mode.Load() {
		case 0: // error with message
			w.WriteHeader(http.StatusBadGateway)
			_, _ = w.Write([]byte(`{"error":"kaput"}`))
		case 1: // error without message
			w.WriteHeader(http.StatusInternalServerError)
		case 2: // invalid body
			_, _ = w.Write([]byte("not json"))
		case 3: // 200 with error field
			_, _ = w.Write([]byte(`{"error":"inner"}`))
		case 4: // success
			_, _ = w.Write([]byte(`{"runner_id":"rid"}`))
		}
	}))
	defer srv.Close()

	store := NewInstanceStore("")
	d := NewBridgeDriver(srv.URL, "orbstack", "", srv.Client(), store)
	ctx := context.Background()

	check := func(m int32, call func() error, want string) {
		t.Helper()
		mode.Store(m)
		if err := call(); err == nil || !strings.Contains(err.Error(), want) {
			t.Errorf("mode %d: got %v want %q", m, err, want)
		}
	}
	spawn := func() error { _, err := d.SpawnRunner(ctx, RunnerSpec{Name: "n"}); return err }
	check(0, spawn, "kaput")
	check(1, spawn, "status 500")
	check(2, spawn, "invalid")
	check(3, spawn, "inner")

	mode.Store(4)
	info, err := d.SpawnRunner(ctx, RunnerSpec{Name: "n"})
	if err != nil || info.ID != "rid" {
		t.Fatalf("spawn: %v %v", info, err)
	}
	if _, ok := store.Get("rid"); !ok {
		t.Error("spawned runner not registered")
	}

	check(2, func() error { _, err := d.ListRunners(ctx); return err }, "invalid")
	stop := func() error { return d.StopRunner(ctx, "rid") }
	check(0, stop, "kaput")
	check(1, stop, "status 500")
	mode.Store(4)
	if err := stop(); err != nil {
		t.Error(err)
	}
	if _, ok := store.Get("rid"); ok {
		t.Error("stopped runner still registered")
	}
	if err := d.CleanupAll(ctx); err != nil {
		t.Error(err)
	}
}

func TestInstanceStore_FileErrors(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "plain")
	if err := os.WriteFile(file, nil, 0o644); err != nil {
		t.Fatal(err)
	}
	s := NewInstanceStore(filepath.Join(file, "sub", "state.json"))
	if err := s.Save(); err == nil {
		t.Error("expected MkdirAll error")
	}

	p := filepath.Join(dir, "state.json")
	if err := os.Mkdir(p+".tmp", 0o755); err != nil {
		t.Fatal(err)
	}
	s = NewInstanceStore(p)
	if err := s.Save(); err == nil {
		t.Error("expected WriteFile error")
	}

	// reading a directory fails with a non-NotExist error
	s = &InstanceStore{filePath: dir, instances: map[string]state.RunnerInfo{}}
	if err := s.Load(); err == nil {
		t.Error("expected read error")
	}
}

type dockerScript struct {
	listOut  string
	failStop bool
	logs     func(target string) ([]byte, error)
}

func (s dockerScript) run(ctx context.Context, name string, args ...string) ([]byte, error) {
	if len(args) == 0 {
		return nil, nil
	}
	switch args[0] {
	case "ps":
		if args[1] == "-a" {
			return []byte(s.listOut), nil
		}
		return nil, nil
	case "inspect":
		if s.failStop {
			return nil, errors.New("no such container")
		}
	case "logs":
		if s.logs != nil {
			return s.logs(args[len(args)-1])
		}
	}
	return []byte("ok"), nil
}

func TestDockerDriver_EnrichFromStoreAndListing(t *testing.T) {
	created := "2026-01-01T00:00:00Z"
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "id-a", Name: "by-name", TargetRepo: "o/a", TargetArch: "arm64", CreatedAt: &created})
	store.Register(state.RunnerInfo{ID: "by-id", TargetRepo: "o/b"})
	store.Register(state.RunnerInfo{ID: "", Name: "nameonly", TargetRepo: "o/c"})

	list := strings.Join([]string{
		"cid1\tby-name\tUp\trunning",
		"by-id\tother\tUp\trunning",
		"cid3\tunknown\tUp\trunning",
		"cid4\tnameonly\tUp\trunning\to/keep\t\t\tamd64",
		"short",
	}, "\n")
	d := NewDockerDriver(&mockCmdExecutor{runFunc: dockerScript{listOut: list}.run}, store, "", "")
	runners, err := d.ListRunners(context.Background())
	if err != nil || len(runners) != 4 {
		t.Fatalf("got %v %v", runners, err)
	}
	if runners[0].TargetRepo != "o/a" || runners[0].TargetArch != "arm64" || runners[0].CreatedAt == nil {
		t.Errorf("name enrichment: %+v", runners[0])
	}
	if runners[1].TargetRepo != "o/b" {
		t.Errorf("id enrichment: %+v", runners[1])
	}
	if runners[2].TargetRepo != "" {
		t.Errorf("unknown runner must stay blank: %+v", runners[2])
	}
	if runners[3].TargetRepo != "o/keep" || runners[3].TargetArch != "amd64" {
		t.Errorf("existing values must be kept: %+v", runners[3])
	}

	nilStore := NewDockerDriver(&mockCmdExecutor{}, nil, "", "")
	nilStore.enrichFromStore([]state.RunnerInfo{{ID: "x"}})
}

func TestDockerDriver_RunnerLogs(t *testing.T) {
	ctx := context.Background()
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "rid", Name: "storename"})
	var seen []string
	d := NewDockerDriver(&mockCmdExecutor{runFunc: dockerScript{logs: func(target string) ([]byte, error) {
		seen = append(seen, target)
		if target == "storename" {
			return []byte("  log body \n"), nil
		}
		return nil, errors.New("no such container")
	}}.run}, store, "", "")
	out, err := d.RunnerLogs(ctx, "rid", 0)
	if err != nil || out != "log body" {
		t.Fatalf("got %q %v (tried %v)", out, err, seen)
	}

	failing := NewDockerDriver(&mockCmdExecutor{runFunc: dockerScript{logs: func(string) ([]byte, error) {
		return nil, errors.New("nope")
	}}.run}, nil, "", "")
	if _, err := failing.RunnerLogs(ctx, "rid", 5); err == nil || !strings.Contains(err.Error(), "docker logs failed") {
		t.Errorf("got %v", err)
	}
}

func TestDockerDriver_StopUsesStoredRunIDAndCleanupError(t *testing.T) {
	ctx := context.Background()
	runID := int64(4242)
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "rid", Name: "runzero-rid", RunID: &runID})
	var auxQueried atomic.Bool
	d := NewDockerDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 3 && args[0] == "ps" && args[1] == "-aq" && args[3] == "name=4242" {
			auxQueried.Store(true)
		}
		return []byte("ok"), nil
	}}, store, "", "")
	if err := d.StopRunner(ctx, "rid"); err != nil || !auxQueried.Load() {
		t.Errorf("err=%v aux=%v", err, auxQueried.Load())
	}

	list := "c1\tn1\tUp\trunning\nc2\tn2\tUp\trunning"
	d = NewDockerDriver(&mockCmdExecutor{runFunc: dockerScript{listOut: list, failStop: true}.run}, nil, "", "")
	if err := d.CleanupAll(ctx); err == nil {
		t.Error("expected stop error to surface")
	}
	d = NewDockerDriver(&mockCmdExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) {
		return nil, errors.New("docker down")
	}}, nil, "", "")
	if err := d.CleanupAll(ctx); err == nil {
		t.Error("expected list error")
	}
}

func TestDockerDriver_SpawnRunnerAllOptions(t *testing.T) {
	var args []string
	d := NewDockerDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, a ...string) ([]byte, error) {
		args = a
		return []byte("cid"), nil
	}}, nil, "", "")
	job, run, wf := int64(1), int64(2), "build"
	_, err := d.SpawnRunner(context.Background(), RunnerSpec{
		ID: "x", Repo: "o/r", Arch: "arm64", JobID: &job, RunID: &run, JobName: "j", WorkflowName: &wf,
		Mounts: map[string]string{"/h": "/c"}, Token: "tok", Labels: []string{"a", "b"},
	})
	if err != nil {
		t.Fatal(err)
	}
	joined := strings.Join(args, " ")
	for _, want := range []string{"runzero.job_id=1", "runzero.run_id=2", "runzero.job=j", "runzero.workflow=build", "/h:/c:rw", "RUNNER_TOKEN=tok", "RUNNER_LABELS=a,b"} {
		if !strings.Contains(joined, want) {
			t.Errorf("missing %q in %s", want, joined)
		}
	}
}

func TestOrbStackDriver_StopResolvesNameAndCleanupError(t *testing.T) {
	ctx := context.Background()
	var deleted string
	list := "runzero-manual-amd64-o__r-abc running\n   \nother-vm running"
	d := NewOrbStackDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "list" {
			return []byte(list), nil
		}
		if len(args) > 0 && args[0] == "delete" {
			deleted = args[len(args)-1]
		}
		return []byte("ok"), nil
	}}, nil, "")
	if err := d.StopRunner(ctx, "abc"); err != nil || deleted != "runzero-manual-amd64-o__r-abc" {
		t.Errorf("err=%v deleted=%q", err, deleted)
	}

	d = NewOrbStackDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && args[0] == "list" {
			return []byte(list), nil
		}
		if len(args) > 0 && args[0] == "delete" {
			return []byte("boom"), errors.New("delete failed")
		}
		return nil, nil
	}}, nil, "")
	if err := d.CleanupAll(ctx); err == nil {
		t.Error("expected cleanup error")
	}
}

func TestParseOrbctlList_Formats(t *testing.T) {
	if got := parseOrbctlList("\n"); len(got) != 0 {
		t.Errorf("got %v", got)
	}
	got := parseOrbctlList(strings.Join([]string{
		"runzero-manual-amd64-o__r-abc running",
		"local-runner-amd64-el-j-herbful-063160 running",
		"local-runner-amd64-foo-bar-1 running",
		"local-runner-amd64-foo-1 running",
		"local-runner-x running",
		"runzero-plain running",
	}, "\n"))
	if len(got) != 6 {
		t.Fatalf("got %d runners: %+v", len(got), got)
	}
	if got[0].TargetRepo != "o/r" || got[0].TargetArch != "amd64" || got[0].ID != "abc" {
		t.Errorf("manual: %+v", got[0])
	}
	if got[1].TargetRepo != "el-j/herbful" {
		t.Errorf("el-j: %+v", got[1])
	}
	if got[2].TargetRepo != "foo/bar" {
		t.Errorf("split: %+v", got[2])
	}
	if got[3].TargetRepo != "foo" {
		t.Errorf("single: %+v", got[3])
	}
}

func TestOrbStackDriver_SpawnExplicitImageFailureStopsEarly(t *testing.T) {
	var creates int
	d := NewOrbStackDriver(&mockCmdExecutor{runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
		if len(args) > 0 && (args[0] == "create" || args[0] == "clone") {
			creates++
			return []byte("bad"), errors.New("fail")
		}
		return nil, nil
	}}, nil, "")
	if _, err := d.SpawnRunner(context.Background(), RunnerSpec{ID: "x", ImageName: "custom"}); err == nil || creates != 1 {
		t.Errorf("err=%v creates=%d", err, creates)
	}
}

func TestPruneFinished_Edges(t *testing.T) {
	ctx := context.Background()
	if got, err := PruneFinished(ctx, nil, nil); got != nil || err != nil {
		t.Errorf("nil driver: %v %v", got, err)
	}
	if _, err := PruneFinished(ctx, &dummyDriver{listFunc: func() ([]state.RunnerInfo, error) { return nil, errors.New("x") }}, nil); err == nil {
		t.Error("expected list error")
	}
	if IsFinished(state.RunnerInfo{State: "running", Status: "Up 2 hours"}) {
		t.Error("running runner is not finished")
	}
	d := &dummyDriver{
		listFunc: func() ([]state.RunnerInfo, error) {
			return []state.RunnerInfo{
				{ID: "live", Name: "live", State: "running"},
				{ID: "a", Name: "a", State: "exited"},
				{ID: "b", Name: "b", State: "exited"},
			}, nil
		},
		stopFunc: func(string) error { return errors.New("stuck") },
	}
	removed, err := PruneFinished(ctx, d, nil)
	if err == nil || len(removed) != 0 || !strings.Contains(err.Error(), "remove a") {
		t.Errorf("removed=%v err=%v", removed, err)
	}
}

func TestRouter_StopAndLogsEdges(t *testing.T) {
	ctx := context.Background()
	stopped := map[string]string{}
	mk := func(backend string, err error) *dummyDriver {
		return &dummyDriver{backend: backend, stopFunc: func(id string) error {
			stopped[backend] = id
			return err
		}}
	}

	// store entry found by name/ID scan (key differs from the requested id)
	for _, backend := range []string{"orbstack", "docker"} {
		store := NewInstanceStore("")
		store.Register(state.RunnerInfo{ID: "key", Name: "nm", Backend: backend})
		r := NewRouter(mk("docker", nil), mk("orbstack", nil), "auto", false, store)
		if err := r.StopRunner(ctx, "nm"); err != nil || stopped[backend] != "nm" {
			t.Errorf("%s: err=%v stopped=%v", backend, err, stopped)
		}
	}

	// fallthrough error combinations
	e1, e2 := errors.New("d-fail"), errors.New("v-fail")
	r := NewRouter(mk("docker", e1), mk("orbstack", e2), "auto", false, nil)
	if err := r.StopRunner(ctx, "x"); err == nil || !strings.Contains(err.Error(), "docker stop failed") {
		t.Errorf("both failing: %v", err)
	}
	r = NewRouter(nil, mk("orbstack", e2), "auto", false, nil)
	if err := r.StopRunner(ctx, "x"); err != e2 {
		t.Errorf("vm only: %v", err)
	}
	r = NewRouter(mk("docker", e1), nil, "auto", false, nil)
	if err := r.StopRunner(ctx, "x"); err != e1 {
		t.Errorf("docker only: %v", err)
	}
	r = NewRouter(mk("docker", e1), mk("orbstack", nil), "auto", false, nil)
	if err := r.StopRunner(ctx, "x"); err != nil {
		t.Errorf("vm rescues: %v", err)
	}

	// SelectDriver falls back to the VM driver when docker is absent
	r = NewRouter(nil, mk("orbstack", nil), "auto", false, nil)
	if r.SelectDriver(RunnerSpec{}) == nil {
		t.Error("expected vm fallback")
	}

	// RunnerLogs ordering, non-providers and errors
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "vm1", Backend: "orbstack"})
	vm := &loggingDriver{dummyDriver: dummyDriver{backend: "orbstack"}, logs: map[string]string{"vm1": "vm logs"}}
	r = NewRouter(&dummyDriver{backend: "docker"}, vm, "auto", false, store)
	if out, err := r.RunnerLogs(ctx, "vm1", 10); err != nil || out != "vm logs" {
		t.Errorf("got %q %v", out, err)
	}
	if _, err := r.RunnerLogs(ctx, "missing", 10); err == nil {
		t.Error("expected error when no provider has the runner")
	}
	r = NewRouter(&dummyDriver{backend: "docker"}, nil, "auto", false, nil)
	if _, err := r.RunnerLogs(ctx, "x", 10); err == nil {
		t.Error("expected no-provider error")
	}

	// CleanupAll: first error wins, VM error ignored when docker already failed
	cd := &dummyDriver{cleanFunc: func() error { return e1 }}
	cv := &dummyDriver{cleanFunc: func() error { return e2 }}
	if err := NewRouter(cd, cv, "auto", false, nil).CleanupAll(ctx); err != e1 {
		t.Errorf("got %v", err)
	}
	if err := NewRouter(&dummyDriver{}, cv, "auto", false, nil).CleanupAll(ctx); err != e2 {
		t.Errorf("vm error should surface: %v", err)
	}
}

func TestNamingEdges(t *testing.T) {
	if sanitizeNamePart("   ") != "" || sanitizeNamePart("!!!") != "unknown" || sanitizeNamePart("a  b!!c") != "a-b-c" {
		t.Error("sanitizeNamePart")
	}
	if repoToken("plain repo") != "plain-repo" {
		t.Error("repoToken without owner")
	}
	long := strings.Repeat("z", 60)
	if n := JobScopedRunnerName("o/r", "", 1, 2, ""); !strings.Contains(n, "amd64") || !strings.HasSuffix(n, "-rand") {
		t.Errorf("job defaults: %s", n)
	}
	if n := ManualRunnerName("o/r", "", ""); !strings.Contains(n, "amd64") || !strings.HasSuffix(n, "-rand") {
		t.Errorf("manual defaults: %s", n)
	}
	if n := ManualRunnerName("owner/repository", long, "e"); !strings.Contains(n, "owner__r") {
		t.Errorf("repo part should be clamped to 8: %s", n)
	}
	for _, name := range []string{"runzero-a-b", "x-y-z-w", "runzero-jx-r1-amd64-repo-e", "runzero-j1-ry-amd64-repo-e", "runzero-other-a-b-c"} {
		if ResolveRepoFromMachineName(name, []string{"o/r"}) != "" {
			t.Errorf("%s should not resolve", name)
		}
	}
}
