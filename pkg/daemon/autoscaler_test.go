package daemon

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

type mockDriver struct {
	spawned []driver.RunnerSpec
	runners []state.RunnerInfo
}

func (m *mockDriver) Backend() string { return "mock" }
func (m *mockDriver) SpawnRunner(ctx context.Context, spec driver.RunnerSpec) (*state.RunnerInfo, error) {
	m.spawned = append(m.spawned, spec)
	now := time.Now().UTC().Format(time.RFC3339)
	info := state.RunnerInfo{
		ID:         spec.ID,
		Name:       spec.Name,
		Status:     "running",
		State:      "running",
		TargetRepo: spec.Repo,
		TargetArch: spec.Arch,
		Backend:    "mock",
		CreatedAt:  &now,
	}
	m.runners = append(m.runners, info)
	return &info, nil
}
func (m *mockDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	return m.runners, nil
}
func (m *mockDriver) StopRunner(ctx context.Context, runnerID string) error { return nil }
func (m *mockDriver) CleanupAll(ctx context.Context) error                  { return nil }

func TestScaler_ScaleCycle(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case strings.Contains(r.URL.Path, "/runs") && strings.Contains(r.URL.RawQuery, "status=queued"):
			_, _ = w.Write([]byte(`{
				"total_count": 1,
				"workflow_runs": [{"id": 101, "name": "CI", "status": "queued", "head_branch": "main"}]
			}`))
		case strings.Contains(r.URL.Path, "/jobs"):
			_, _ = w.Write([]byte(`{
				"total_count": 1,
				"jobs": [{"id": 202, "run_id": 101, "name": "build", "status": "queued", "labels": ["self-hosted", "local", "amd64"]}]
			}`))
		case strings.Contains(r.URL.Path, "/registration-token"):
			_, _ = w.Write([]byte(`{"token": "test-reg-token-456", "expires_at": "2026-10-06T22:00:00Z"}`))
		case strings.Contains(r.URL.Path, "/settings/billing/actions"):
			_, _ = w.Write([]byte(`{"total_minutes_used": 50, "included_minutes": 2000, "total_paid_minutes_used": 0}`))
		default:
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{}`))
		}
	}))
	defer server.Close()

	cfg := &config.Config{
		MaxRunners:                    3,
		PollInterval:                  10,
		DiscoveryInterval:             1800,
		ReposConfig:                   "el-j/herbful",
		AutoDiscover:                  false,
		RunnerArch:                    "both",
		AutoRouteVM:                   true,
		RunnerBackend:                 "auto",
		ActionsBillingRefreshInterval: 300,
	}

	st := state.NewState(3, "1.0.0", nil)
	drv := &mockDriver{}
	gh := github.NewClient("token", server.URL, server.Client())
	pm, _ := github.NewPriorityManager("", []string{"el-j/herbful"}, nil)
	rec := github.NewReconciler(pm)
	poller := github.NewPoller(gh, rec, st, []string{"el-j/herbful"}, 10*time.Second)

	scaler := NewScaler(cfg, st, drv, gh, pm, rec, poller, nil)

	ctx := context.Background()
	scaler.ScaleCycle(ctx)

	// Verify runner was spawned
	if len(drv.spawned) != 1 {
		t.Fatalf("expected 1 spawned runner, got %d", len(drv.spawned))
	}
	spawned := drv.spawned[0]
	if spawned.Repo != "el-j/herbful" {
		t.Errorf("expected repo el-j/herbful, got %s", spawned.Repo)
	}
	if spawned.Arch != "amd64" {
		t.Errorf("expected arch amd64, got %s", spawned.Arch)
	}
	if spawned.Token != "test-reg-token-456" {
		t.Errorf("expected token test-reg-token-456, got %s", spawned.Token)
	}

	// Verify state snapshot
	snap := st.GetSnapshot()
	if len(snap.Runners) != 1 {
		t.Errorf("expected 1 runner in state, got %d", len(snap.Runners))
	}
	if snap.BusyRunners != 1 {
		t.Errorf("expected 1 busy runner, got %d", snap.BusyRunners)
	}
}
