//go:build e2e

// Command harness runs the real RunZero control plane, autoscaler and dashboard
// against a fake GitHub API and an in-memory runner driver, so Playwright can
// drive whole operator journeys (job queued -> runner spawned -> job failed ->
// retry) through the real UI and HTTP API.
//
// Run it with: go run -tags e2e ./test/e2e/harness
//
// The fake GitHub API and the scenario controls listen on E2E_GITHUB_PORT
// (default 49599); the dashboard listens on E2E_DASHBOARD_PORT (default 49515).
//
//	POST /__e2e/fail   the queued job fails; its runner exits and job history
//	                   is refreshed now instead of after the daemon's 30 s
//	                   finished-runner floor
//	POST /__e2e/reset  back to a single queued job
//	GET  /__e2e/calls  write calls the daemon made to GitHub
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/api"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/daemon"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/state"
)

// The scenario: one repo whose name is lossy as an OrbStack machine name, with
// one workflow run holding one self-hosted job.
const (
	repo  = "el-j/landing.inquam-services"
	runID = int64(9001)
	jobID = int64(501)
)

func main() {
	ghPort := envOr("E2E_GITHUB_PORT", "49599")
	dashPort := envOr("E2E_DASHBOARD_PORT", "49515")
	distDir := envOr("E2E_DIST_DIR", filepath.Join("web", "dist"))

	stateDir, err := os.MkdirTemp("", "runzero-e2e-")
	if err != nil {
		log.Fatal(err)
	}
	defer func() { _ = os.RemoveAll(stateDir) }()

	cfg, err := config.LoadConfig(config.MapEnv{
		"ACCESS_TOKEN":                     "e2e-token",
		"REPOS":                            repo,
		"POLL_INTERVAL":                    "1",
		"DISCOVERY_INTERVAL":               "60",
		"ACTIONS_BILLING_REFRESH_INTERVAL": "3600",
		"MAX_RUNNERS":                      "2",
		"CACHE_ENABLED":                    "false",
		"HOST_CACHE_DIR":                   filepath.Join(stateDir, "cache"),
		"DASHBOARD_HOST":                   "127.0.0.1",
		"DASHBOARD_PORT":                   dashPort,
	})
	if err != nil {
		log.Fatal(err)
	}

	st := state.NewState(cfg.MaxRunners, "e2e", nil)
	drv := &fakeDriver{}
	sc := &scenario{phase: phaseQueued, drv: drv, st: st}
	go func() {
		log.Fatal(http.ListenAndServe("127.0.0.1:"+ghPort, sc))
	}()

	gh := github.NewClient(cfg.AccessToken, "http://127.0.0.1:"+ghPort, nil)
	pm, _ := github.NewPriorityManager(filepath.Join(stateDir, "priority.json"), []string{repo}, nil)
	prio, paused := pm.GetState()
	st.SetRepoPriority(prio, paused)
	rec := github.NewReconciler(pm)
	poller := github.NewPoller(gh, rec, st, []string{repo}, time.Second)
	scaler := daemon.NewScaler(cfg, st, drv, gh, pm, rec, poller, reaper.NewReaper(drv, gh, reaper.DefaultTimeouts()))

	srv := api.NewServerWithDeps(cfg, st, distDir, "", []string{"127.0.0.1", "localhost"}, time.Second, gh, drv)
	if err := srv.Start(); err != nil {
		log.Fatal(err)
	}
	log.Printf("e2e harness: dashboard http://127.0.0.1:%s, fake GitHub http://127.0.0.1:%s", dashPort, ghPort)

	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()
	go scaler.Start(ctx)
	<-ctx.Done()
	_ = srv.Shutdown(context.Background())
}

func envOr(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

type phase int

const (
	phaseQueued phase = iota
	phaseFailed
)

// scenario is the fake GitHub API plus the controls that advance it.
type scenario struct {
	mu    sync.Mutex
	phase phase
	calls []string
	drv   *fakeDriver
	st    *state.State
}

func (s *scenario) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()

	path := r.URL.Path
	if r.Method != http.MethodGet && !strings.HasPrefix(path, "/__e2e/") {
		s.calls = append(s.calls, r.Method+" "+path)
	}
	prefix := "/repos/" + repo
	runPath := fmt.Sprintf("%s/actions/runs/%d", prefix, runID)

	switch {
	case path == "/__e2e/fail":
		s.phase = phaseFailed
		s.drv.exitAll()
		s.st.RequestHistoryRefresh()
		writeJSON(w, map[string]string{"phase": "failed"})
	case path == "/__e2e/reset":
		s.phase, s.calls = phaseQueued, nil
		s.drv.reset()
		writeJSON(w, map[string]string{"phase": "queued"})
	case path == "/__e2e/calls":
		writeJSON(w, map[string][]string{"calls": append([]string{}, s.calls...)})

	case path == prefix+"/actions/runs":
		writeJSON(w, map[string]any{"workflow_runs": s.runsWithStatus(r.URL.Query().Get("status"))})
	case path == runPath+"/jobs":
		writeJSON(w, map[string]any{"jobs": []any{s.job()}})
	case path == fmt.Sprintf("%s/actions/jobs/%d", prefix, jobID):
		writeJSON(w, s.job())
	case path == runPath:
		writeJSON(w, s.run())
	case path == fmt.Sprintf("%s/check-runs/%d/annotations", prefix, jobID):
		writeJSON(w, []map[string]string{{"annotation_level": "failure", "message": "assertion failed in retry path"}})
	case path == prefix+"/actions/runners/registration-token":
		w.WriteHeader(http.StatusCreated)
		writeJSON(w, map[string]string{"token": "e2e-registration-token", "expires_at": time.Now().Add(time.Hour).UTC().Format(time.RFC3339)})
	case path == prefix+"/actions/runners":
		writeJSON(w, map[string]any{"total_count": 0, "runners": []any{}})
	case strings.HasPrefix(path, runPath+"/") && r.Method == http.MethodPost:
		w.WriteHeader(http.StatusCreated)
	default:
		w.WriteHeader(http.StatusNotFound)
		writeJSON(w, map[string]string{"message": "Not Found"})
	}
}

func (s *scenario) runsWithStatus(status string) []any {
	switch {
	case status == "queued" && s.phase == phaseQueued:
		return []any{s.run()}
	case status == "completed" && s.phase == phaseFailed:
		return []any{s.run()}
	}
	return []any{}
}

func (s *scenario) run() map[string]any {
	run := map[string]any{
		"id":            runID,
		"name":          "CI",
		"head_branch":   "develop",
		"run_attempt":   1,
		"status":        "queued",
		"html_url":      fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, runID),
		"created_at":    "2026-11-01T10:00:00Z",
		"updated_at":    "2026-11-01T10:00:00Z",
		"workflow_name": "CI",
	}
	if s.phase == phaseFailed {
		run["status"], run["conclusion"] = "completed", "failure"
	}
	return run
}

func (s *scenario) job() map[string]any {
	job := map[string]any{
		"id":         jobID,
		"run_id":     runID,
		"name":       "test-and-lint",
		"status":     "queued",
		"labels":     []string{"self-hosted"},
		"html_url":   fmt.Sprintf("https://github.com/%s/actions/runs/%d/job/%d", repo, runID, jobID),
		"created_at": "2026-11-01T10:00:00Z",
		"steps":      []any{},
	}
	if s.phase == phaseFailed {
		job["status"], job["conclusion"] = "completed", "failure"
		job["started_at"], job["completed_at"] = "2026-11-01T10:00:05Z", "2026-11-01T10:01:29Z"
		job["runner_name"] = "runzero-e2e"
		job["steps"] = []map[string]any{
			{"number": 1, "name": "Set up job", "status": "completed", "conclusion": "success"},
			{"number": 2, "name": "Checkout", "status": "completed", "conclusion": "success"},
			{"number": 3, "name": "Install", "status": "completed", "conclusion": "success"},
			{"number": 4, "name": "Run tests", "status": "completed", "conclusion": "failure"},
		}
	}
	return job
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(v)
}

// fakeDriver keeps runners in memory and lists them the way the OrbStack driver
// does: under a hostname-safe machine name whose repo token is lossy.
type fakeDriver struct {
	mu      sync.Mutex
	runners []state.RunnerInfo
}

func (d *fakeDriver) Backend() string { return "orbstack" }

func (d *fakeDriver) SpawnRunner(_ context.Context, spec driver.RunnerSpec) (*state.RunnerInfo, error) {
	d.mu.Lock()
	defer d.mu.Unlock()
	now := time.Now().UTC().Format(time.RFC3339)
	machine := hostnameSafe(spec.Name)
	info := state.RunnerInfo{
		ID:         machine,
		Name:       machine,
		Status:     "running",
		State:      "running",
		TargetRepo: spec.Repo,
		TargetArch: spec.Arch,
		Backend:    "orbstack",
		CreatedAt:  &now,
	}
	listed := info
	listed.TargetRepo = lossyRepo(spec.Repo)
	listed.JobID, listed.RunID = spec.JobID, spec.RunID
	d.runners = append(d.runners, listed)
	return &info, nil
}

func (d *fakeDriver) ListRunners(context.Context) ([]state.RunnerInfo, error) {
	d.mu.Lock()
	defer d.mu.Unlock()
	return append([]state.RunnerInfo{}, d.runners...), nil
}

func (d *fakeDriver) StopRunner(_ context.Context, id string) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	kept := d.runners[:0]
	for _, r := range d.runners {
		if r.ID != id && r.Name != id {
			kept = append(kept, r)
		}
	}
	d.runners = kept
	return nil
}

func (d *fakeDriver) CleanupAll(context.Context) error {
	d.reset()
	return nil
}

func (d *fakeDriver) exitAll() {
	d.mu.Lock()
	defer d.mu.Unlock()
	for i := range d.runners {
		d.runners[i].Status, d.runners[i].State = "exited", "exited"
	}
}

func (d *fakeDriver) reset() {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.runners = nil
}

// hostnameSafe mirrors OrbStack machine naming: lower-case alphanumerics with
// single dashes.
func hostnameSafe(name string) string {
	var b strings.Builder
	lastDash := false
	for _, r := range strings.ToLower(name) {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
			b.WriteRune(r)
			lastDash = false
			continue
		}
		if !lastDash {
			b.WriteByte('-')
			lastDash = true
		}
	}
	return strings.Trim(b.String(), "-")
}

// lossyRepo is the repo as recovered from a hostname-safe machine name.
func lossyRepo(repo string) string { return hostnameSafe(repo) }
