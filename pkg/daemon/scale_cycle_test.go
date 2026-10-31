package daemon

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/state"
)

// fakeGH is a scriptable GitHub API. Routes are keyed by URL path, optionally
// suffixed with "?status=<value>" when the request carries a status filter.
// Unscripted routes answer 200 "{}".
type fakeGH struct {
	mu     sync.Mutex
	routes map[string]string
	codes  map[string]int
	hits   []string
}

func (f *fakeGH) handler(w http.ResponseWriter, r *http.Request) {
	key := r.URL.Path
	if q := r.URL.Query().Get("status"); q != "" {
		key += "?status=" + q
	}
	f.mu.Lock()
	f.hits = append(f.hits, r.Method+" "+key)
	body, ok := f.routes[key]
	code := f.codes[key]
	f.mu.Unlock()
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-RateLimit-Remaining", "4990")
	w.Header().Set("X-RateLimit-Limit", "5000")
	if code != 0 {
		w.WriteHeader(code)
	}
	if !ok {
		body = `{}`
	}
	_, _ = w.Write([]byte(body))
}

func (f *fakeGH) hit(prefix string) int {
	f.mu.Lock()
	defer f.mu.Unlock()
	n := 0
	for _, h := range f.hits {
		if strings.HasPrefix(h, prefix) {
			n++
		}
	}
	return n
}

func newFakeGH(t *testing.T, routes map[string]string) (*fakeGH, *github.Client) {
	t.Helper()
	f := &fakeGH{routes: routes, codes: map[string]int{}}
	if f.routes == nil {
		f.routes = map[string]string{}
	}
	srv := httptest.NewServer(http.HandlerFunc(f.handler))
	t.Cleanup(srv.Close)
	return f, github.NewClient("token", srv.URL, srv.Client())
}

// queuedRoutes scripts one queued run (id 101) with the given jobs JSON array.
func queuedRoutes(repo, jobsJSON string) map[string]string {
	return map[string]string{
		"/repos/" + repo + "/actions/runs?status=queued":         `{"workflow_runs":[{"id":101,"name":"CI","head_branch":"main"}]}`,
		"/repos/" + repo + "/actions/runs/101/jobs":              `{"jobs":` + jobsJSON + `}`,
		"/repos/" + repo + "/actions/runners/registration-token": `{"token":"tok","expires_at":"2030-01-01T00:00:00Z"}`,
	}
}

func baseCfg(repos ...string) *config.Config {
	return &config.Config{
		MaxRunners:                    5,
		PollInterval:                  10,
		DiscoveryInterval:             1800,
		ReposConfig:                   strings.Join(repos, ","),
		RunnerArch:                    "both",
		RunnerBackend:                 "auto",
		ActionsBillingRefreshInterval: 300,
	}
}

func newTestScaler(t *testing.T, cfg *config.Config, gh *github.Client, drv driver.RunnerDriver, paused []string, repos ...string) (*Scaler, *state.State) {
	t.Helper()
	st := state.NewState(cfg.MaxRunners, "test", nil)
	pm, _ := github.NewPriorityManager("", repos, paused)
	rec := github.NewReconciler(pm)
	poller := github.NewPoller(gh, rec, st, repos, 10*time.Second)
	return NewScaler(cfg, st, drv, gh, pm, rec, poller, nil), st
}

func hasLog(st *state.State, sub string) bool {
	for _, l := range st.GetLogs() {
		if strings.Contains(l.Message, sub) {
			return true
		}
	}
	return false
}

// stubDriver layers scripted failures and log capture over mockDriver.
type stubDriver struct {
	*mockDriver
	listErr error
	stopErr error
	logs    string
}

func (d *stubDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	if d.listErr != nil {
		return nil, d.listErr
	}
	return d.mockDriver.ListRunners(ctx)
}

func (d *stubDriver) StopRunner(ctx context.Context, id string) error {
	if d.stopErr != nil {
		return d.stopErr
	}
	return d.mockDriver.StopRunner(ctx, id)
}

func (d *stubDriver) RunnerLogs(context.Context, string, int) (string, error) { return d.logs, nil }

type failingBuilder struct{}

func (failingBuilder) TriggerBuild(context.Context, builder.ImageBuildRequest) (*builder.ImageBuildProgress, error) {
	return nil, errors.New("no builder")
}
func (failingBuilder) GetActiveBuild() *builder.ImageBuildProgress { return nil }

type fakeProvider struct{ runners []state.RunnerInfo }

func (p *fakeProvider) ID() string                  { return "fake" }
func (p *fakeProvider) Name() string                { return "Fake" }
func (p *fakeProvider) Type() provider.ProviderType { return provider.TypeGitLab }
func (p *fakeProvider) BaseURL() string             { return "" }
func (p *fakeProvider) FetchRemoteRunners(context.Context) ([]state.RunnerInfo, error) {
	return p.runners, nil
}
func (p *fakeProvider) FetchQueuedJobs(context.Context) ([]state.QueuedJob, error) { return nil, nil }
func (p *fakeProvider) AcquireRegistrationToken(context.Context, string) (string, time.Time, error) {
	return "", time.Time{}, nil
}
func (p *fakeProvider) DeregisterRunner(context.Context, string) error { return nil }

func TestScaleCycle_PrunesFinishedRunners(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &stubDriver{mockDriver: &mockDriver{runners: []state.RunnerInfo{
		{ID: "dead1", Name: "runzero-dead1", State: "exited", TargetRepo: "o/r", Backend: "docker"},
	}}, logs: "boom tail"}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())

	if len(drv.stopped) != 1 || drv.stopped[0] != "dead1" {
		t.Fatalf("finished runner not pruned: %v", drv.stopped)
	}
	if log, _ := st.GetRunnerLog("runzero-dead1"); log != "boom tail" {
		t.Fatalf("expected captured log tail, got %q", log)
	}
	if !hasLog(st, "Pruned 1 finished") {
		t.Fatal("expected prune summary log")
	}
}

func TestScaleCycle_PruneFailureIsLogged(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &stubDriver{mockDriver: &mockDriver{runners: []state.RunnerInfo{
		{ID: "dead1", Name: "runzero-dead1", State: "exited"},
	}}, stopErr: errors.New("rm failed")}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())

	if !hasLog(st, "Failed to prune finished runners") {
		t.Fatal("expected prune failure log")
	}
}

func TestScaleCycle_NilDriverStillPublishesFleet(t *testing.T) {
	_, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"status":"queued"}]`))
	s, st := newTestScaler(t, baseCfg("o/r"), gh, nil, nil, "o/r")

	s.ScaleCycle(context.Background())

	snap := st.GetSnapshot()
	if len(snap.Runners) != 0 || len(snap.QueuedJobs) != 1 {
		t.Fatalf("expected 0 runners and 1 queued job, got %d/%d", len(snap.Runners), len(snap.QueuedJobs))
	}
}

func TestScaleCycle_FallsBackToPriorityReposWhenPollerEmpty(t *testing.T) {
	f, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"status":"queued"}]`))
	drv := &mockDriver{}
	s, _ := newTestScaler(t, baseCfg(), gh, drv, nil)
	pm, _ := github.NewPriorityManager("", []string{"o/r"}, nil)
	s.priorityMgr = pm

	s.ScaleCycle(context.Background())

	if f.hit("GET /repos/o/r/actions/runs?status=queued") == 0 {
		t.Fatal("expected priority repo to be polled when poller has none")
	}
	if len(drv.spawned) != 1 {
		t.Fatalf("expected 1 spawn, got %d", len(drv.spawned))
	}
}

func TestScaleCycle_ResolvesLossyRepoAndTracksFirstSeen(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &mockDriver{runners: []state.RunnerInfo{{
		ID: "abc", Name: "runzero-j1-r2-amd64-el-j-herbful-abc", Status: "running", State: "running", TargetRepo: "el-j-herbful",
	}}}
	s, st := newTestScaler(t, baseCfg("el-j/herbful"), gh, drv, nil, "el-j/herbful")

	s.ScaleCycle(context.Background())

	runners := st.GetSnapshot().Runners
	if len(runners) != 1 || runners[0].TargetRepo != "el-j/herbful" || runners[0].CreatedAt == nil {
		t.Fatalf("expected resolved repo and synthesized CreatedAt, got %+v", runners)
	}
	if _, ok := s.firstSeen["runzero-j1-r2-amd64-el-j-herbful-abc"]; !ok {
		t.Fatal("expected firstSeen entry")
	}

	drv.runners = nil
	s.ScaleCycle(context.Background())
	if len(s.firstSeen) != 0 {
		t.Fatalf("expected firstSeen pruned for gone runners, got %v", s.firstSeen)
	}
}

func TestScaleCycle_FirstSeenMapIsLazilyCreated(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &mockDriver{runners: []state.RunnerInfo{{ID: "a", Name: "n", Status: "running", TargetRepo: "o/r"}}}
	s, _ := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
	s.firstSeen = nil

	s.ScaleCycle(context.Background())

	if len(s.firstSeen) != 1 {
		t.Fatalf("expected firstSeen to be created, got %v", s.firstSeen)
	}
}

func TestScaleCycle_SkipsPausedReposAndToleratesJobErrors(t *testing.T) {
	f, gh := newFakeGH(t, queuedRoutes("o/ok", `[{"id":1,"status":"queued"}]`))
	f.codes["/repos/o/err/actions/runs?status=queued"] = http.StatusInternalServerError
	drv := &mockDriver{}
	s, _ := newTestScaler(t, baseCfg("o/ok", "o/err", "o/paused"), gh, drv, []string{"o/paused"}, "o/ok", "o/err", "o/paused")

	s.ScaleCycle(context.Background())

	if f.hit("GET /repos/o/paused/") != 0 {
		t.Fatal("paused repo must not be polled for jobs")
	}
	if len(drv.spawned) != 1 || drv.spawned[0].Repo != "o/ok" {
		t.Fatalf("expected one spawn for o/ok, got %+v", drv.spawned)
	}
}

func i64(v int64) *int64 { return &v }

func TestScaleCycle_ReapsOnlyRunnersWhoseWorkIsDone(t *testing.T) {
	routes := map[string]string{
		"/repos/o/r/actions/runs?status=in_progress": `{"workflow_runs":[{"id":50,"name":"CI"}]}`,
		"/repos/o/r/actions/runs/50/jobs": `{"jobs":[
			{"id":5,"run_id":50,"status":"in_progress"},
			{"id":7,"run_id":50,"status":"in_progress","runner_name":"by-name"}]}`,
		"/repos/o/r/actions/jobs/1":  `{"id":1,"status":"completed","conclusion":"success"}`,
		"/repos/o/r/actions/jobs/3":  `{"id":3,"status":"in_progress"}`,
		"/repos/o/r/actions/runs/20": `{"id":20,"status":"completed","conclusion":"failure"}`,
		"/repos/o/r/actions/runs/30": `{"id":30,"status":"in_progress"}`,
	}
	f, gh := newFakeGH(t, routes)
	run := func(id, name string, job, runID *int64) state.RunnerInfo {
		return state.RunnerInfo{ID: id, Name: name, Status: "running", State: "running", TargetRepo: "o/r", JobID: job, RunID: runID}
	}
	drv := &mockDriver{runners: []state.RunnerInfo{
		run("r1", "job-done", i64(1), nil),
		run("r2", "run-done", nil, i64(20)),
		run("r3", "still-going", i64(3), i64(30)),
		run("r4", "no-ids", nil, nil),
		run("r5", "by-job", i64(5), nil),
		run("r6", "by-name", i64(6), nil),
		run("r7", "by-run", nil, i64(50)),
		{ID: "r8", Name: "no-repo", Status: "running", JobID: i64(8)},
	}}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())

	if got := strings.Join(drv.stopped, ","); got != "r1,r2" {
		t.Fatalf("expected only r1,r2 reaped, got %q", got)
	}
	if len(st.GetSnapshot().Runners) != 6 {
		t.Fatalf("expected 6 surviving runners, got %d", len(st.GetSnapshot().Runners))
	}
	if f.hit("GET /repos/o/r/actions/jobs/5") != 0 || f.hit("GET /repos/o/r/actions/jobs/6") != 0 {
		t.Fatal("active runners must not trigger completion lookups")
	}
	if !hasLog(st, "job #1 is completed (success)") || !hasLog(st, "workflow run #20 is completed (failure)") {
		t.Fatal("expected reap reasons in log")
	}
}

func TestScaleCycle_ReaperRemovesOrphansAndRecollects(t *testing.T) {
	routes := map[string]string{
		"/repos/o/r/actions/runners":          `{"runners":[{"id":9,"name":"runzero-orphan","status":"offline","busy":false}]}`,
		"/repos/el-j/herbful/actions/runners": `{"runners":[{"id":10,"name":"runzero-j1-r2-amd64-el-j-herbful-abc","status":"online","busy":true}]}`,
	}
	_, gh := newFakeGH(t, routes)
	old := time.Now().Add(-time.Hour).UTC().Format(time.RFC3339)
	drv := &mockDriver{runners: []state.RunnerInfo{
		{ID: "orphan", Name: "runzero-orphan", Status: "running", TargetRepo: "o/r", CreatedAt: &old},
		{ID: "abc", Name: "runzero-j1-r2-amd64-el-j-herbful-abc", Status: "running", TargetRepo: "el-j-herbful"},
		{ID: "ok", Name: "runzero-ok", Status: "running", TargetRepo: "o/r"},
	}}
	s, st := newTestScaler(t, baseCfg("o/r", "el-j/herbful"), gh, drv, nil, "o/r", "el-j/herbful")
	s.reaper = reaper.NewReaper(drv, gh, reaper.DefaultTimeouts())

	s.ScaleCycle(context.Background())

	if len(drv.stopped) != 1 || drv.stopped[0] != "orphan" {
		t.Fatalf("expected orphan reaped, got %v", drv.stopped)
	}
	if !hasLog(st, "Reaped 1 orphaned/idle runner(s)") {
		t.Fatal("expected reaper log")
	}
	for _, r := range st.GetSnapshot().Runners {
		if r.ID == "abc" && r.TargetRepo != "el-j/herbful" {
			t.Fatalf("repo not re-resolved after recollect: %q", r.TargetRepo)
		}
	}
	if len(st.GetSnapshot().Runners) != 2 {
		t.Fatalf("expected 2 survivors, got %d", len(st.GetSnapshot().Runners))
	}
}

func oneJob(labels, name string) string {
	return fmt.Sprintf(`[{"id":202,"run_id":101,"name":%q,"status":"queued","labels":%s}]`, name, labels)
}

func spawnOnce(t *testing.T, cfg *config.Config, jobsJSON string, mutate func(*Scaler, *state.State)) (*mockDriver, *state.State) {
	t.Helper()
	_, gh := newFakeGH(t, queuedRoutes("o/r", jobsJSON))
	drv := &mockDriver{}
	s, st := newTestScaler(t, cfg, gh, drv, nil, "o/r")
	if mutate != nil {
		mutate(s, st)
	}
	s.ScaleCycle(context.Background())
	return drv, st
}

func TestScaleCycle_ResolvesArchitecture(t *testing.T) {
	cases := []struct {
		name, arch, labels, want string
	}{
		{"label arm64", "", `["arm64"]`, "arm64"},
		{"label aarch64", "", `["AArch64"]`, "arm64"},
		{"label arm", "both", `["arm"]`, "arm64"},
		{"no label defaults amd64", "both", `["self-hosted"]`, "amd64"},
		{"explicit config wins", "arm64", `["x64"]`, "arm64"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			cfg := baseCfg("o/r")
			cfg.RunnerArch = c.arch
			drv, _ := spawnOnce(t, cfg, oneJob(c.labels, "build"), nil)
			if len(drv.spawned) != 1 || drv.spawned[0].Arch != c.want {
				t.Fatalf("want arch %s, got %+v", c.want, drv.spawned)
			}
		})
	}

	t.Run("native override", func(t *testing.T) {
		drv, _ := spawnOnce(t, baseCfg("o/r"), oneJob(`["self-hosted"]`, "build"), func(s *Scaler, _ *state.State) {
			s.archOverride, _ = arch.NewNativeArchOverride("all", "arm64")
		})
		if len(drv.spawned) != 1 || drv.spawned[0].Arch != "arm64" {
			t.Fatalf("expected native arm64 override, got %+v", drv.spawned)
		}
	})
}

func TestScaleCycle_ResolvesBackend(t *testing.T) {
	t.Run("configured backend", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.RunnerBackend = "orbstack"
		drv, _ := spawnOnce(t, cfg, oneJob(`[]`, "build"), nil)
		if len(drv.spawned) != 1 || drv.spawned[0].Backend != "orbstack" {
			t.Fatalf("got %+v", drv.spawned)
		}
	})
	t.Run("auto route to VM", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.AutoRouteVM = true
		cfg.VMTriggerLabels = []string{"e2e"}
		drv, _ := spawnOnce(t, cfg, oneJob(`[]`, "E2E suite"), nil)
		if len(drv.spawned) != 1 || drv.spawned[0].Backend != "orbstack" {
			t.Fatalf("got %+v", drv.spawned)
		}
	})
	t.Run("auto route without match stays docker", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.AutoRouteVM = true
		cfg.VMTriggerLabels = []string{"e2e"}
		drv, _ := spawnOnce(t, cfg, oneJob(`[]`, "lint"), nil)
		if len(drv.spawned) != 1 || drv.spawned[0].Backend != "docker" {
			t.Fatalf("got %+v", drv.spawned)
		}
	})
}

func TestScaleCycle_ResolvesSizing(t *testing.T) {
	t.Run("defaults", func(t *testing.T) {
		drv, _ := spawnOnce(t, baseCfg("o/r"), oneJob(`[]`, "b"), nil)
		if drv.spawned[0].CPUs != 3 || drv.spawned[0].MemoryMB != 4096 {
			t.Fatalf("got %+v", drv.spawned[0])
		}
	})
	t.Run("configured", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.RunnerCPUs = 6
		cfg.RunnerMemory = "2g"
		drv, _ := spawnOnce(t, cfg, oneJob(`[]`, "b"), nil)
		if drv.spawned[0].CPUs != 6 || drv.spawned[0].MemoryMB != 2048 {
			t.Fatalf("got %+v", drv.spawned[0])
		}
	})
	t.Run("unparsable memory keeps default", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.RunnerMemory = "lots"
		drv, _ := spawnOnce(t, cfg, oneJob(`[]`, "b"), nil)
		if drv.spawned[0].MemoryMB != 4096 {
			t.Fatalf("got %+v", drv.spawned[0])
		}
	})
}

func TestScaleCycle_SpawnedRunnerCarriesJobDetails(t *testing.T) {
	jobs := `[{"id":202,"run_id":101,"name":"build","status":"queued","labels":["x"],"html_url":"https://gh/job",
		"steps":[{"name":"s1","status":"completed","number":1},{"name":"s2","status":"queued","number":2}]}]`
	drv, st := spawnOnce(t, baseCfg("o/r"), jobs, nil)

	spec := drv.spawned[0]
	if spec.JobName != "build" || spec.JobID == nil || *spec.JobID != 202 || *spec.RunID != 101 {
		t.Fatalf("spec missing job identity: %+v", spec)
	}
	if got := strings.Join(spec.Labels, ","); got != "self-hosted,local,amd64,x" {
		t.Fatalf("labels = %q", got)
	}
	r := st.GetSnapshot().Runners[0]
	if r.JobURL == nil || *r.JobURL != "https://gh/job" || r.RunURL == nil || *r.RunURL != "https://github.com/o/r/actions/runs/101" {
		t.Fatalf("missing links: %+v", r)
	}
	if r.ProgressPct == nil || *r.ProgressPct != 50 || r.StepsTotal == nil || *r.StepsTotal != 2 {
		t.Fatalf("missing progress: %+v", r)
	}
}

func TestScaleCycle_NoSpawnWhenPausedCappedOrCovered(t *testing.T) {
	two := `[{"id":1,"run_id":101,"status":"queued"},{"id":2,"run_id":101,"status":"queued"}]`

	t.Run("autoscaler paused", func(t *testing.T) {
		drv, _ := spawnOnce(t, baseCfg("o/r"), two, func(_ *Scaler, st *state.State) { st.SetAutoscalerStatus("paused") })
		if len(drv.spawned) != 0 {
			t.Fatalf("paused autoscaler spawned %d", len(drv.spawned))
		}
	})
	t.Run("max runners cap", func(t *testing.T) {
		cfg := baseCfg("o/r")
		cfg.MaxRunners = 1
		drv, _ := spawnOnce(t, cfg, two, nil)
		if len(drv.spawned) != 1 {
			t.Fatalf("expected cap of 1, got %d", len(drv.spawned))
		}
	})
	t.Run("existing runner covers a job", func(t *testing.T) {
		_, gh := newFakeGH(t, queuedRoutes("o/r", two))
		drv := &mockDriver{runners: []state.RunnerInfo{{ID: "e", Name: "e", Status: "running", TargetRepo: "o/r"}}}
		s, _ := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
		s.ScaleCycle(context.Background())
		if len(drv.spawned) != 1 {
			t.Fatalf("expected 1 spawn for 2 jobs with 1 runner, got %d", len(drv.spawned))
		}
	})
	t.Run("repo fully covered", func(t *testing.T) {
		_, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"run_id":101,"status":"queued"}]`))
		drv := &mockDriver{runners: []state.RunnerInfo{{ID: "e", Name: "e", Status: "running", TargetRepo: "o/r"}}}
		s, _ := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
		s.ScaleCycle(context.Background())
		if len(drv.spawned) != 0 {
			t.Fatalf("expected no spawn, got %d", len(drv.spawned))
		}
	})
}

func TestScaleCycle_SkipsPausedRepoDuringScaling(t *testing.T) {
	_, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"run_id":101,"status":"queued"}]`))
	drv := &mockDriver{}
	s, _ := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
	// Pause lands between job collection and scaling.
	pm, _ := github.NewPriorityManager("", []string{"o/r"}, []string{"o/r"})
	s.priorityMgr = pm
	s.ScaleCycle(context.Background())
	if len(drv.spawned) != 0 {
		t.Fatalf("paused repo must not scale, got %d", len(drv.spawned))
	}
}

func TestScaleCycle_TokenFailureSkipsSpawn(t *testing.T) {
	f, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"run_id":101,"status":"queued"}]`))
	f.codes["/repos/o/r/actions/runners/registration-token"] = http.StatusInternalServerError
	drv := &mockDriver{}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())

	if len(drv.spawned) != 0 || !hasLog(st, "Failed to get registration token for o/r") {
		t.Fatalf("expected token failure to skip spawn; spawned=%d", len(drv.spawned))
	}
}

func TestScaleCycle_SuccessfulSpawnClearsBackoffAndFailureIsLogged(t *testing.T) {
	_, gh := newFakeGH(t, queuedRoutes("o/r", `[{"id":1,"run_id":101,"status":"queued"}]`))
	drv := &mockDriver{spawnErr: errors.New("docker down")}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())
	if !hasLog(st, "Failed to spawn docker runner for o/r") {
		t.Fatal("expected spawn failure log")
	}
	if _, ok := s.spawnBackoff["docker/amd64"]; !ok {
		t.Fatal("expected backoff after failure")
	}

	drv.spawnErr = nil
	s.spawnBackoff["docker/amd64"] = spawnBackoff{until: time.Now().Add(-time.Second), delay: time.Second}
	s.ScaleCycle(context.Background())
	if _, ok := s.spawnBackoff["docker/amd64"]; ok {
		t.Fatal("successful spawn must clear backoff")
	}
}

func TestScaleCycle_EnrichesRunnersFromActiveJobs(t *testing.T) {
	routes := map[string]string{
		"/repos/o/r/actions/runs?status=in_progress": `{"workflow_runs":[{"id":50,"name":"CI"}]}`,
		"/repos/o/r/actions/runs/50/jobs": `{"jobs":[
			{"id":5,"run_id":50,"name":"deploy","status":"in_progress","html_url":"https://gh/5","runner_name":"by-name"}]}`,
	}
	_, gh := newFakeGH(t, routes)
	runID := int64(77)
	drv := &mockDriver{runners: []state.RunnerInfo{
		{ID: "a", Name: "by-name", Status: "running", TargetRepo: "o/r"},
		{ID: "b", Name: "by-job", Status: "running", TargetRepo: "o/r", JobID: i64(5)},
		{ID: "c", Name: "by-run", Status: "running", TargetRepo: "o/r", RunID: i64(50)},
		{ID: "d", Name: "run-link-only", Status: "running", TargetRepo: "o/r", RunID: &runID},
		{ID: "e", Name: "unrelated", Status: "running", TargetRepo: "o/r"},
	}}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")

	s.ScaleCycle(context.Background())

	byName := map[string]state.RunnerInfo{}
	for _, r := range st.GetSnapshot().Runners {
		byName[r.Name] = r
	}
	for _, n := range []string{"by-name", "by-job", "by-run"} {
		r := byName[n]
		if r.JobName == nil || *r.JobName != "deploy" || r.JobURL == nil || *r.JobURL != "https://gh/5" ||
			r.RunURL == nil || *r.RunURL != "https://github.com/o/r/actions/runs/50" || r.WorkflowName == nil {
			t.Errorf("%s not enriched: %+v", n, r)
		}
	}
	if r := byName["run-link-only"]; r.RunURL == nil || *r.RunURL != "https://github.com/o/r/actions/runs/77" || r.JobName != nil {
		t.Errorf("run-link-only should only get a run URL: %+v", r)
	}
	if byName["unrelated"].JobName != nil || byName["unrelated"].RunURL != nil {
		t.Errorf("unrelated runner must stay untouched")
	}
}

func TestScaleCycle_MergesRemoteProviderRunners(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &mockDriver{runners: []state.RunnerInfo{{ID: "l", Name: "local", Status: "running", TargetRepo: "o/r"}}}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
	mgr := provider.NewManager()
	mgr.Register(&fakeProvider{runners: []state.RunnerInfo{{ID: "x", Name: "remote", Status: "online"}}})
	s.SetProviderManager(mgr)

	s.ScaleCycle(context.Background())

	if n := len(st.GetSnapshot().Runners); n != 2 {
		t.Fatalf("expected local+remote runners, got %d", n)
	}
}

func TestCollectRunners(t *testing.T) {
	s := &Scaler{}
	if got := s.CollectRunners(context.Background()); got == nil || len(got) != 0 {
		t.Fatalf("nil driver should yield empty slice, got %v", got)
	}

	s.driver = &stubDriver{mockDriver: &mockDriver{}, listErr: errors.New("nope")}
	if got := s.CollectRunners(context.Background()); got == nil || len(got) != 0 {
		t.Fatalf("list error should yield empty slice, got %v", got)
	}

	s.driver = &mockDriver{runners: []state.RunnerInfo{
		{ID: "1", Status: "Up 3 minutes"},
		{ID: "2", State: "pending"},
		{ID: "3", State: "Creating"},
		{ID: "4", Status: "Exited (0)"},
		{ID: "5", Status: "running"},
	}}
	got := s.CollectRunners(context.Background())
	if len(got) != 4 {
		t.Fatalf("expected 4 active runners, got %+v", got)
	}
}

func TestDiscoverAndSync(t *testing.T) {
	t.Run("nil client is a no-op", func(t *testing.T) {
		(&Scaler{}).DiscoverAndSync(context.Background())
	})

	t.Run("discovers repos, rate limit and billing", func(t *testing.T) {
		f, gh := newFakeGH(t, map[string]string{
			"/users/me/settings/billing/actions":    `{"total_minutes_used":5,"included_minutes":2000}`,
			"/repos/o/a/actions/runs?status=queued": `{}`,
		})
		cfg := baseCfg("o/a, o/b")
		cfg.Owner = "me"
		s, st := newTestScaler(t, cfg, gh, nil, nil, "o/a")
		_, _ = gh.GetWorkflowRun(context.Background(), "o/a", 1) // primes the observed rate limit

		s.DiscoverAndSync(context.Background())

		snap := st.GetSnapshot()
		if len(snap.RepoPriority) != 2 || snap.RateLimitRemaining == nil || *snap.RateLimitRemaining != 4990 || snap.ActionsBilling == nil {
			t.Fatalf("unexpected snapshot: %+v", snap)
		}
		if !hasLog(st, "Monitoring 2 active repository(ies)") {
			t.Fatal("expected monitoring log")
		}

		// Second call is throttled: no extra billing request.
		before := f.hit("GET /users/me/settings/billing/actions")
		s.DiscoverAndSync(context.Background())
		if f.hit("GET /users/me/settings/billing/actions") != before {
			t.Fatal("billing refresh should be throttled")
		}
	})

	t.Run("discovery without poller", func(t *testing.T) {
		_, gh := newFakeGH(t, nil)
		s, _ := newTestScaler(t, baseCfg("o/a"), gh, nil, nil, "o/a")
		s.poller = nil
		s.DiscoverAndSync(context.Background())
		if s.lastDiscovery.IsZero() {
			t.Fatal("expected discovery timestamp")
		}
	})

	t.Run("discovery error is logged", func(t *testing.T) {
		f, gh := newFakeGH(t, nil)
		f.codes["/user/repos"] = http.StatusInternalServerError
		cfg := baseCfg()
		cfg.AutoDiscover = true
		s, st := newTestScaler(t, cfg, gh, nil, nil)

		s.DiscoverAndSync(context.Background())

		if !hasLog(st, "Repository discovery warning") {
			t.Fatal("expected discovery warning")
		}
	})

	t.Run("empty discovery result is silent", func(t *testing.T) {
		_, gh := newFakeGH(t, map[string]string{"/user/repos": `[]`})
		cfg := baseCfg()
		cfg.AutoDiscover = true
		s, st := newTestScaler(t, cfg, gh, nil, nil)
		s.DiscoverAndSync(context.Background())
		if hasLog(st, "Monitoring") || hasLog(st, "warning") {
			t.Fatal("expected no logs for empty discovery")
		}
	})
}

func TestRefreshCompletedJobs(t *testing.T) {
	t.Run("no client or repos", func(t *testing.T) {
		(&Scaler{}).refreshCompletedJobs(context.Background(), []string{"o/r"})
		_, gh := newFakeGH(t, nil)
		(&Scaler{ghClient: gh}).refreshCompletedJobs(context.Background(), nil)
	})

	t.Run("collects jobs, logs errors and skips blanks", func(t *testing.T) {
		f, gh := newFakeGH(t, map[string]string{
			"/repos/o/ok/actions/runs?status=completed": `{"workflow_runs":[{"id":1,"name":"CI","conclusion":"success","updated_at":"2026-01-01T00:00:00Z"}]}`,
		})
		f.codes["/repos/o/bad/actions/runs?status=completed"] = http.StatusInternalServerError
		st := state.NewState(1, "t", nil)
		s := &Scaler{ghClient: gh, state: st}

		s.refreshCompletedJobs(context.Background(), []string{"", "o/bad", "o/ok"})

		if !hasLog(st, "Could not refresh completed jobs for o/bad") {
			t.Fatal("expected error log")
		}
		if s.lastHistoryRefresh.IsZero() || s.historyFetcher == nil {
			t.Fatal("expected refresh bookkeeping")
		}
	})

	t.Run("all failures publish an empty list", func(t *testing.T) {
		_, gh := newFakeGH(t, nil)
		st := state.NewState(1, "t", nil)
		s := &Scaler{ghClient: gh, state: st}
		s.refreshCompletedJobs(context.Background(), []string{"o/r"})
		if st.GetSnapshot().CompletedJobs == nil {
			t.Fatal("expected non-nil completed jobs")
		}
	})

	t.Run("async sweep runs at most once at a time", func(t *testing.T) {
		_, gh := newFakeGH(t, nil)
		s := &Scaler{ghClient: gh, state: state.NewState(1, "t", nil)}
		s.historyRunning.Store(true)
		s.refreshCompletedJobsAsync(context.Background(), []string{"o/r"})
		if !s.lastHistoryRefresh.IsZero() {
			t.Fatal("overlapping sweep must be skipped")
		}

		s.historyRunning.Store(false)
		s.refreshCompletedJobsAsync(context.Background(), []string{"o/r"})
		deadline := time.Now().Add(2 * time.Second)
		for s.historyRunning.Load() && time.Now().Before(deadline) {
			time.Sleep(5 * time.Millisecond)
		}
	})
}

func TestNoteSpawnFailure_RebuildBranches(t *testing.T) {
	missing := fmt.Errorf("%w: img", driver.ErrImageMissing)

	t.Run("rebuild already running", func(t *testing.T) {
		ib := &mockImageBuilder{status: "building"}
		s := &Scaler{state: state.NewState(1, "t", nil), imageBuilder: ib}
		s.noteSpawnFailure(context.Background(), "docker/amd64", "amd64", missing)
		if len(ib.requests) != 0 {
			t.Fatal("must not start a second rebuild")
		}
	})

	t.Run("rebuild cannot start", func(t *testing.T) {
		ib := &failingBuilder{}
		st := state.NewState(1, "t", nil)
		s := &Scaler{state: st, imageBuilder: ib}
		s.noteSpawnFailure(context.Background(), "docker/amd64", "amd64", missing)
		if !hasLog(st, "Could not start rebuild") {
			t.Fatal("expected rebuild failure log")
		}
	})

	t.Run("backoff doubles and caps", func(t *testing.T) {
		s := &Scaler{state: state.NewState(1, "t", nil)}
		other := errors.New("x")
		for i := 0; i < 10; i++ {
			s.noteSpawnFailure(context.Background(), "k", "amd64", other)
		}
		if s.spawnBackoff["k"].delay != maxSpawnBackoff {
			t.Fatalf("delay = %s", s.spawnBackoff["k"].delay)
		}
	})
}

func TestSpawnBlocked_KeepsPauseUntilImageReady(t *testing.T) {
	s := &Scaler{spawnBackoff: map[string]spawnBackoff{}}
	if s.spawnBlocked("k") {
		t.Fatal("unknown key must not be blocked")
	}
	s.spawnBackoff["k"] = spawnBackoff{until: time.Now().Add(time.Hour), awaitingImage: true}
	if !s.spawnBlocked("k") {
		t.Fatal("expected block without image builder")
	}
	s.imageBuilder = &mockImageBuilder{}
	if !s.spawnBlocked("k") {
		t.Fatal("expected block while no build is active")
	}
}

func TestTokenizeAndRoutingEdges(t *testing.T) {
	if tokenizeLower("   ") != nil {
		t.Fatal("blank input should yield no tokens")
	}
	job := state.QueuedJob{Name: "e2e"}
	if shouldRouteToVM(job, nil) || shouldRouteToVM(job, []string{"", "  "}) {
		t.Fatal("empty triggers must never route")
	}
}

func TestRandomHex_FallsBackWhenEntropyFails(t *testing.T) {
	orig := randRead
	randRead = func([]byte) (int, error) { return 0, errors.New("no entropy") }
	t.Cleanup(func() { randRead = orig })
	if got := randomHex(3); len(got) != 6 {
		t.Fatalf("fallback id = %q", got)
	}
}

func TestScaler_StartRunsCyclesUntilCancelled(t *testing.T) {
	f, gh := newFakeGH(t, nil)
	cfg := baseCfg("o/r")
	cfg.PollInterval = 1
	s, _ := newTestScaler(t, cfg, gh, &mockDriver{}, nil, "o/r")

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	go func() { s.Start(ctx); close(done) }()

	deadline := time.Now().Add(3 * time.Second)
	for f.hit("GET /repos/o/r/actions/runs?status=queued") < 2 && time.Now().Before(deadline) {
		time.Sleep(20 * time.Millisecond)
	}
	cancel()
	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("Start did not return after cancel")
	}
	if f.hit("GET /repos/o/r/actions/runs?status=queued") < 2 {
		t.Fatal("expected a second cycle from the ticker")
	}
}

func TestScaler_StartUsesDefaultIntervalWhenUnset(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	cfg := baseCfg("o/r")
	cfg.PollInterval = 0
	s, _ := newTestScaler(t, cfg, gh, &mockDriver{}, nil, "o/r")
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	s.Start(ctx)
}

func TestScaleCycle_ReaperKeepingEveryoneLeavesFleetUntouched(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	drv := &mockDriver{runners: []state.RunnerInfo{{ID: "a", Name: "runzero-a", Status: "running", TargetRepo: "o/r"}}}
	s, st := newTestScaler(t, baseCfg("o/r"), gh, drv, nil, "o/r")
	s.reaper = reaper.NewReaper(drv, gh, reaper.DefaultTimeouts())

	s.ScaleCycle(context.Background())

	if len(drv.stopped) != 0 || len(st.GetSnapshot().Runners) != 1 {
		t.Fatalf("expected untouched fleet, stopped=%v", drv.stopped)
	}
}

func TestResolveJobArch_WithoutOverride(t *testing.T) {
	s := &Scaler{cfg: baseCfg()}
	if got := s.resolveJobArch(state.QueuedJob{Labels: []string{"arm64"}}, "o/r"); got != "arm64" {
		t.Fatalf("got %s", got)
	}
}
