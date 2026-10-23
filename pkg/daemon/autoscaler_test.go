package daemon

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

type mockDriver struct {
	spawned  []driver.RunnerSpec
	runners  []state.RunnerInfo
	stopped  []string
	spawnErr error
	cleanups int
}

func (m *mockDriver) Backend() string { return "mock" }
func (m *mockDriver) SpawnRunner(ctx context.Context, spec driver.RunnerSpec) (*state.RunnerInfo, error) {
	m.spawned = append(m.spawned, spec)
	if m.spawnErr != nil {
		return nil, m.spawnErr
	}
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
func (m *mockDriver) StopRunner(ctx context.Context, runnerID string) error {
	m.stopped = append(m.stopped, runnerID)
	var remaining []state.RunnerInfo
	for _, r := range m.runners {
		if r.ID != runnerID && r.Name != runnerID {
			remaining = append(remaining, r)
		}
	}
	m.runners = remaining
	return nil
}
func (m *mockDriver) CleanupAll(ctx context.Context) error {
	m.cleanups++
	return nil
}

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

func TestShouldRouteToVM(t *testing.T) {
	triggers := []string{"vm", "browser", "e2e", "postgres", "db", "dind"}

	// 1. Matched by label
	job1 := state.QueuedJob{
		Name:   "unit-tests",
		Labels: []string{"self-hosted", "vm"},
	}
	if !shouldRouteToVM(job1, triggers) {
		t.Errorf("expected job1 to route to VM via label")
	}

	// 2. Matched by job name
	job2 := state.QueuedJob{
		Name:   "Matrix — E2E (mock auth)",
		Labels: []string{"self-hosted", "local"},
	}
	if !shouldRouteToVM(job2, triggers) {
		t.Errorf("expected job2 to route to VM via job name token e2e")
	}

	// 3. Matched by workflow name when job name is generic
	wfName := "E2E"
	job3 := state.QueuedJob{
		Name:         "Matrix — CI",
		WorkflowName: &wfName,
		Labels:       []string{"self-hosted", "local", "amd64"},
	}
	if !shouldRouteToVM(job3, triggers) {
		t.Errorf("expected job3 to route to VM via workflow name E2E")
	}

	// 4. Non-matching job
	wfCI := "Lint & Unit Tests"
	job4 := state.QueuedJob{
		Name:         "lint",
		WorkflowName: &wfCI,
		Labels:       []string{"self-hosted", "local", "amd64"},
	}
	if shouldRouteToVM(job4, triggers) {
		t.Errorf("expected job4 NOT to route to VM")
	}
}

type mockImageBuilder struct {
	requests []builder.ImageBuildRequest
	status   string // "" (no build), "building", "ready", "failed"
}

func (b *mockImageBuilder) TriggerBuild(ctx context.Context, req builder.ImageBuildRequest) (*builder.ImageBuildProgress, error) {
	b.requests = append(b.requests, req)
	b.status = string(builder.StatusBuilding)
	return &builder.ImageBuildProgress{BuildID: "b1"}, nil
}

func (b *mockImageBuilder) GetActiveBuild() *builder.ImageBuildProgress {
	if b.status == "" {
		return nil
	}
	return &builder.ImageBuildProgress{BuildID: "b1", Status: b.status}
}

// A missing runner image must not turn into a hot loop that burns a GitHub
// registration token per queued job per cycle: back off, and rebuild the image.
func TestScaler_SpawnFailureBacksOffAndRebuildsMissingImage(t *testing.T) {
	var tokenCalls int
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case strings.Contains(r.URL.Path, "/runs") && strings.Contains(r.URL.RawQuery, "status=queued"):
			_, _ = w.Write([]byte(`{"total_count": 1, "workflow_runs": [{"id": 101, "name": "CI", "status": "queued", "head_branch": "main"}]}`))
		case strings.Contains(r.URL.Path, "/jobs"):
			_, _ = w.Write([]byte(`{"total_count": 2, "jobs": [
				{"id": 202, "run_id": 101, "name": "a", "status": "queued", "labels": ["self-hosted", "local"]},
				{"id": 203, "run_id": 101, "name": "b", "status": "queued", "labels": ["self-hosted", "local"]}]}`))
		case strings.Contains(r.URL.Path, "/registration-token"):
			tokenCalls++
			_, _ = w.Write([]byte(`{"token": "t", "expires_at": "2026-10-06T22:00:00Z"}`))
		default:
			_, _ = w.Write([]byte(`{}`))
		}
	}))
	defer server.Close()

	cfg := &config.Config{MaxRunners: 3, PollInterval: 10, DiscoveryInterval: 1800, ReposConfig: "el-j/herbful",
		RunnerArch: "both", RunnerBackend: "auto", ActionsBillingRefreshInterval: 300}
	st := state.NewState(3, "1.0.0", nil)
	drv := &mockDriver{spawnErr: fmt.Errorf("%w: local-github-runner:amd64", driver.ErrImageMissing)}
	gh := github.NewClient("token", server.URL, server.Client())
	pm, _ := github.NewPriorityManager("", []string{"el-j/herbful"}, nil)
	rec := github.NewReconciler(pm)
	poller := github.NewPoller(gh, rec, st, []string{"el-j/herbful"}, 10*time.Second)
	scaler := NewScaler(cfg, st, drv, gh, pm, rec, poller, nil)
	ib := &mockImageBuilder{}
	scaler.SetImageBuilder(ib)

	ctx := context.Background()
	scaler.ScaleCycle(ctx)
	scaler.ScaleCycle(ctx)

	if len(drv.spawned) != 1 {
		t.Fatalf("expected 1 spawn attempt across two cycles, got %d", len(drv.spawned))
	}
	if tokenCalls != 1 {
		t.Fatalf("expected 1 registration token request, got %d", tokenCalls)
	}
	if len(ib.requests) != 1 || ib.requests[0].Target != "container" || ib.requests[0].Arch != "amd64" {
		t.Fatalf("expected one container/amd64 image build, got %+v", ib.requests)
	}

	// A failed rebuild keeps the pause (no rebuild loop).
	ib.status = string(builder.StatusFailed)
	scaler.ScaleCycle(ctx)
	if len(drv.spawned) != 1 || len(ib.requests) != 1 {
		t.Fatalf("failed rebuild must keep spawns paused: %d spawns, %d builds", len(drv.spawned), len(ib.requests))
	}

	// Once a rebuild succeeds, spawning resumes immediately rather than
	// waiting out the backoff delay.
	ib.status = string(builder.StatusReady)
	drv.spawnErr = nil
	scaler.ScaleCycle(ctx)
	if len(drv.spawned) < 2 {
		t.Fatalf("expected spawning to resume after the image rebuild, got %d attempts", len(drv.spawned))
	}
}

func TestScaler_ReapsCompletedJobAndRun(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case strings.Contains(r.URL.Path, "/runs") && strings.Contains(r.URL.RawQuery, "status="):
			// No active runs
			_, _ = w.Write([]byte(`{"total_count": 0, "workflow_runs": []}`))
		case r.URL.Path == "/repos/el-j/landing.inquam-services/actions/jobs/118881070610":
			// Completed job
			_, _ = w.Write([]byte(`{"id": 118881070610, "run_id": 39490761518, "status": "completed", "conclusion": "success"}`))
		case r.URL.Path == "/repos/el-j/landing.inquam-services/actions/runs/39490761518":
			// Completed run
			_, _ = w.Write([]byte(`{"id": 39490761518, "status": "completed", "conclusion": "success"}`))
		default:
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{}`))
		}
	}))
	defer server.Close()

	cfg := &config.Config{
		MaxRunners: 3, PollInterval: 10, DiscoveryInterval: 1800,
		ReposConfig: "el-j/landing.inquam-services", RunnerArch: "both",
	}

	st := state.NewState(3, "1.0.0", nil)
	jID := int64(118881070610)
	rID := int64(39490761518)
	drv := &mockDriver{
		runners: []state.RunnerInfo{
			{
				ID:         "e4efbc",
				Name:       "runzero-j118881070610-r39490761518-amd64-el-j-landing-in-e4efbc",
				Status:     "running",
				State:      "running",
				TargetRepo: "el-j-landing-in", // lossy repo from OrbStack machine name
				Backend:    "orbstack",
				JobID:      &jID,
				RunID:      &rID,
			},
		},
	}
	gh := github.NewClient("token", server.URL, server.Client())
	pm, _ := github.NewPriorityManager("", []string{"el-j/landing.inquam-services"}, nil)
	rec := github.NewReconciler(pm)
	poller := github.NewPoller(gh, rec, st, []string{"el-j/landing.inquam-services"}, 10*time.Second)

	scaler := NewScaler(cfg, st, drv, gh, pm, rec, poller, nil)
	scaler.ScaleCycle(context.Background())

	if len(drv.stopped) != 1 || drv.stopped[0] != "e4efbc" {
		t.Fatalf("expected runner e4efbc to be stopped, got %v", drv.stopped)
	}
	if len(st.GetSnapshot().Runners) != 0 {
		t.Fatalf("expected 0 runners in state snapshot, got %d", len(st.GetSnapshot().Runners))
	}
}
