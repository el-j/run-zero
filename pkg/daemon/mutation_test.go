package daemon

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/state"
)

func TestRandomHex(t *testing.T) {
	old := randRead
	defer func() { randRead = old }()
	randRead = func(b []byte) (int, error) { copy(b, []byte{0xab, 0xcd, 0xef}); return len(b), nil }
	if got := randomHex(3); got != "abcdef" {
		t.Fatalf("got %q", got)
	}
	randRead = func([]byte) (int, error) { return 0, errors.New("no entropy") }
	if got := randomHex(3); len(got) > 6 {
		t.Fatalf("fallback must stay within 6 hex digits, got %q", got)
	}
}

// TestIntervals_DueExactlyAtTheInterval checks every periodic refresh with a
// fixed clock: due once the full interval has passed, not a second earlier.
func TestIntervals_DueExactlyAtTheInterval(t *testing.T) {
	now := time.Unix(1_900_000_000, 0)
	cfg := baseCfg("o/a")
	cfg.RateLimitRefreshInterval = 60
	cfg.Owner = "me"
	f, gh := newFakeGH(t, map[string]string{
		"/rate_limit": `{"resources":{"core":{"limit":5000,"remaining":10,"reset":1900003600}}}`,
	})

	for _, c := range []struct {
		age  time.Duration
		want bool
	}{{60 * time.Second, true}, {59 * time.Second, false}} {
		s, _ := newTestScaler(t, cfg, gh, nil, nil, "o/a")
		s.now = func() time.Time { return now }
		s.lastDiscovery = now.Add(-time.Duration(cfg.DiscoveryInterval)*time.Second + (60*time.Second - c.age))
		s.lastRateLimit = now.Add(-c.age)
		s.lastBilling = now.Add(-time.Duration(cfg.ActionsBillingRefreshInterval)*time.Second + (60*time.Second - c.age))
		discovered, rate, billing := s.lastDiscovery, f.hit("GET /rate_limit"), f.hit("GET /users/me/settings/billing")
		s.DiscoverAndSync(context.Background())
		if got := s.lastDiscovery != discovered; got != c.want {
			t.Errorf("age %s: discovery ran = %v", c.age, got)
		}
		if got := f.hit("GET /rate_limit") > rate; got != c.want {
			t.Errorf("age %s: rate-limit refresh ran = %v", c.age, got)
		}
		if got := f.hit("GET /users/me/settings/billing") > billing; got != c.want {
			t.Errorf("age %s: billing refresh ran = %v", c.age, got)
		}
	}
}

func TestHistoryRefreshDue_ExactlyAtTheIntervals(t *testing.T) {
	now := time.Unix(1_900_000_000, 0)
	s := &Scaler{state: state.NewState(1, "t", nil), now: func() time.Time { return now }}

	s.lastHistoryRefresh = now.Add(-historyRefreshMinInterval)
	if !s.historyRefreshDue() {
		t.Error("the periodic sweep is due exactly at historyRefreshMinInterval")
	}
	s.lastHistoryRefresh = now.Add(-finishedRefreshMinInterval)
	s.runnersFinished.Store(true)
	if !s.historyRefreshDue() {
		t.Error("a finished runner makes the sweep due exactly at finishedRefreshMinInterval")
	}
	s.lastHistoryRefresh = now.Add(-finishedRefreshMinInterval + time.Second)
	s.runnersFinished.Store(true)
	if s.historyRefreshDue() {
		t.Error("not due a second before finishedRefreshMinInterval")
	}
}

func TestDiscoverAndSync_UnknownQuotaStaysUnset(t *testing.T) {
	_, gh := newFakeGH(t, nil)
	s, st := newTestScaler(t, baseCfg("o/a"), gh, nil, nil, "o/a")
	// fakeGH always sends quota headers; a fresh client without traffic has none.
	s.ghClient = newTestScalerClientWithoutQuota(t)
	s.DiscoverAndSync(context.Background())
	if st.GetSnapshot().RateLimitRemaining != nil {
		t.Fatal("an unknown quota must not reach the dashboard")
	}
}

func TestCollectRunners_RunningStatusWithoutUp(t *testing.T) {
	drv := &mockDriver{runners: []state.RunnerInfo{{ID: "a", Status: "Running"}, {ID: "b", Status: "exited", State: "exited"}}}
	s := &Scaler{driver: drv}
	if got := s.CollectRunners(context.Background()); len(got) != 1 || got[0].ID != "a" {
		t.Fatalf("got %+v", got)
	}
}

func TestPruneFinishedRunners_NothingRemovedNothingReported(t *testing.T) {
	s, st := newTestScaler(t, baseCfg("o/a"), nil, &mockDriver{}, nil, "o/a")
	s.pruneFinishedRunners(context.Background())
	if s.runnersFinished.Load() || hasLog(st, "Pruned") {
		t.Fatal("an empty prune must not report or mark runners finished")
	}
}

func TestTrackedRepos_WithoutPoller(t *testing.T) {
	s, _ := newTestScaler(t, baseCfg("o/a"), nil, nil, nil, "o/a", "o/b")
	s.poller = nil
	if got := fmt.Sprint(s.trackedRepos()); got != "[o/a o/b]" {
		t.Fatalf("got %s", got)
	}
}

func TestScaleUp_SpawnsOnlyForUncoveredJobs(t *testing.T) {
	_, gh := newFakeGH(t, standbyRoutes("o/a"))
	cfg := baseCfg("o/a")
	cfg.MaxRunners = 10
	drv := &mockDriver{}
	s, _ := newTestScaler(t, cfg, gh, drv, nil, "o/a")
	active := []state.RunnerInfo{{ID: "standby", TargetRepo: "o/a"}} // covers one queued job
	jobs := map[string][]state.QueuedJob{"o/a": {{ID: 1, RunID: 9, Status: "queued"}, {ID: 2, RunID: 9, Status: "queued"}}}
	s.scaleUp(context.Background(), active, []string{"o/a"}, jobs)
	if len(drv.spawned) != 1 {
		t.Fatalf("one standby covers one of two jobs: expected 1 spawn, got %d", len(drv.spawned))
	}
}

func TestPublishFleet_NoRemoteRunnersLeavesLocalOnesAsIs(t *testing.T) {
	s, st := newTestScaler(t, baseCfg("o/a"), nil, nil, nil, "o/a")
	s.SetProviderManager(provider.NewManager())
	s.historyRunning.Store(true) // skip the async history sweep
	s.publishFleet(context.Background(), []state.RunnerInfo{{ID: "a"}}, nil, nil)
	if r := st.GetSnapshot().Runners; len(r) != 1 || r[0].Origin != nil {
		t.Fatalf("got %+v", r)
	}
}

func TestTopUpStandby_SpawnsOnlyTheMissingRunners(t *testing.T) {
	_, gh := newFakeGH(t, standbyRoutes("o/a"))
	cfg := baseCfg("o/a")
	cfg.MinRunners, cfg.MaxRunners = 2, 10
	drv := &mockDriver{}
	s, _ := newTestScaler(t, cfg, gh, drv, nil, "o/a")
	s.topUpStandby(context.Background(), []state.RunnerInfo{{ID: "idle"}}, []string{"o/a"})
	if len(drv.spawned) != 1 {
		t.Fatalf("expected 1 spawn to reach 2 standby runners, got %d", len(drv.spawned))
	}
}

func TestCountStandby(t *testing.T) {
	id := int64(1)
	if n := countStandby([]state.RunnerInfo{{}, {}, {JobID: &id}, {RunID: &id}}); n != 2 {
		t.Fatalf("got %d", n)
	}
}

func TestJobDeclaresServices_CachedResult(t *testing.T) {
	f, gh := newFakeGH(t, workflowRoute(servicesWorkflow))
	s, _ := newTestScaler(t, baseCfg("o/a"), gh, nil, nil, "o/a")
	for i := 0; i < 2; i++ {
		if !s.jobDeclaresServices(context.Background(), "o/a", servicesJob("integration")) {
			t.Fatalf("call %d: expected services", i)
		}
	}
	if n := f.hit("GET /repos/o/a/contents/"); n != 1 {
		t.Fatalf("fetched %d times", n)
	}
}

func TestInitVMDriver_BridgeURL(t *testing.T) {
	cfg, _ := config.LoadConfig(config.MapEnv{"RUNNER_BACKEND": "multipass"})
	for url, bridged := range map[string]bool{"http://127.0.0.1:1": true, "none": false, "": false} {
		t.Setenv("HOST_VM_BRIDGE_URL", url)
		_, isBridge := initVMDriver(cfg, driver.NewInstanceStore("")).(*driver.BridgeDriver)
		if isBridge != bridged {
			t.Errorf("HOST_VM_BRIDGE_URL=%q: bridge = %v", url, isBridge)
		}
	}
}

func TestWSLRunnerDir(t *testing.T) {
	t.Setenv("RUNZERO_STATE_DIR", "/state")
	if got := wslRunnerDir(&config.Config{}); got != "/state/wsl" {
		t.Errorf("default: %q", got)
	}
	if got := wslRunnerDir(&config.Config{WSLRunnerDir: `D:\wsl`}); got != `D:\wsl` {
		t.Errorf("configured: %q", got)
	}
}

func TestSplitListAndPollerInterval(t *testing.T) {
	if got := fmt.Sprint(splitList(" a, ,b ,")); got != "[a b]" {
		t.Errorf("splitList: %s", got)
	}
	if splitList("") != nil {
		t.Error("an empty setting has no items")
	}
	cfg := &config.Config{PollInterval: 7, ReposConfig: "o/a, o/b"}
	pm, _ := github.NewPriorityManager("", nil, nil)
	p := initPoller(cfg, pm, state.NewState(1, "t", nil))
	if p.Interval() != 7*time.Second || fmt.Sprint(p.Repos()) != "[o/a o/b]" {
		t.Errorf("poller: %s %v", p.Interval(), p.Repos())
	}
}

// newTestScalerClientWithoutQuota returns a GitHub client whose server never
// sends quota headers.
func newTestScalerClientWithoutQuota(t *testing.T) *github.Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = w.Write([]byte(`{}`)) }))
	t.Cleanup(srv.Close)
	return github.NewClient("t", srv.URL, srv.Client())
}
