package daemon

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/sizing"
	"github.com/el-j/run-zero/pkg/state"
)

func TestPacedInterval(t *testing.T) {
	base := 10 * time.Second
	now := time.Unix(1_000_000, 0)
	farReset := now.Add(time.Hour)
	cases := []struct {
		name string
		rl   github.RateLimit
		want time.Duration
	}{
		{"unknown quota", github.RateLimit{}, base},
		{"plenty left", github.RateLimit{Limit: 5000, Remaining: 4000, Reset: farReset}, base},
		{"below half", github.RateLimit{Limit: 5000, Remaining: 2000, Reset: farReset}, 2 * base},
		{"below 20%", github.RateLimit{Limit: 5000, Remaining: 900, Reset: farReset}, 4 * base},
		{"below 10%", github.RateLimit{Limit: 5000, Remaining: 100, Reset: farReset}, 8 * base},
		{"capped at reset", github.RateLimit{Limit: 5000, Remaining: 0, Reset: now.Add(25 * time.Second)}, 25 * time.Second},
		{"reset sooner than base", github.RateLimit{Limit: 5000, Remaining: 0, Reset: now.Add(time.Second)}, base},
		{"reset already passed", github.RateLimit{Limit: 5000, Remaining: 0, Reset: now.Add(-time.Minute)}, base},
	}
	for _, c := range cases {
		if got := pacedInterval(base, c.rl, now); got != c.want {
			t.Errorf("%s: got %s, want %s", c.name, got, c.want)
		}
	}
}

// quotaClient returns a GitHub client whose observed quota is remaining/5000.
func quotaClient(t *testing.T, remaining string) *github.Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-RateLimit-Remaining", remaining)
		w.Header().Set("X-RateLimit-Limit", "5000")
		w.Header().Set("X-RateLimit-Reset", "4102444800")
		_, _ = w.Write([]byte(`{}`))
	}))
	t.Cleanup(srv.Close)
	gh := github.NewClient("t", srv.URL, srv.Client())
	_, _ = gh.GetWorkflowRun(context.Background(), "o/a", 1)
	return gh
}

func TestNextCycleDelay_PacesAndLogsChanges(t *testing.T) {
	st := state.NewState(1, "test", nil)
	s := &Scaler{cfg: &config.Config{PollInterval: 2}, state: st}

	if d := s.nextCycleDelay(); d != 2*time.Second {
		t.Fatalf("without a client: got %s", d)
	}

	s.ghClient = quotaClient(t, "100")
	if d := s.nextCycleDelay(); d != 16*time.Second || !hasLog(st, "quota low (100/5000 left)") {
		t.Fatalf("low quota: got %s", d)
	}

	s.ghClient = quotaClient(t, "4900")
	if d := s.nextCycleDelay(); d != 2*time.Second || !hasLog(st, "quota recovered") {
		t.Fatalf("recovered quota: got %s", d)
	}

	s.cfg.PollInterval = 0
	if d := s.nextCycleDelay(); d != 10*time.Second {
		t.Fatalf("default interval: got %s", d)
	}
}

func TestLogSizing_WarnsOnOversubscription(t *testing.T) {
	st := state.NewState(1, "test", nil)
	s := &Scaler{cfg: &config.Config{MaxRunners: 4, RunnerCPUs: 4}, state: st, host: sizing.HostCapacity{CPUs: 9, MemoryMiB: 18432}}
	s.logSizing()
	if !hasLog(st, "Runner sizing: 4 CPU") || !hasLog(st, "⚠️ Sizing: max_runners x cpus") {
		t.Fatalf("expected sizing summary and warning, got %+v", st.GetLogs())
	}
}
