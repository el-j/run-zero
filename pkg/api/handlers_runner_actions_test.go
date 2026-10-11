package api

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

type pruneTestDriver struct {
	runners []state.RunnerInfo
	logs    map[string]string
	stopped []string
}

func (d *pruneTestDriver) Backend() string { return "mock" }
func (d *pruneTestDriver) SpawnRunner(context.Context, driver.RunnerSpec) (*state.RunnerInfo, error) {
	return nil, nil
}
func (d *pruneTestDriver) ListRunners(context.Context) ([]state.RunnerInfo, error) {
	return d.runners, nil
}
func (d *pruneTestDriver) StopRunner(_ context.Context, runnerID string) error {
	d.stopped = append(d.stopped, runnerID)
	return nil
}
func (d *pruneTestDriver) CleanupAll(context.Context) error { return nil }
func (d *pruneTestDriver) RunnerLogs(_ context.Context, runnerID string, _ int) (string, error) {
	return d.logs[runnerID], nil
}

func TestHandlePrune_PrunesFinishedRunners(t *testing.T) {
	st := state.NewState(3, "test", nil)
	drv := &pruneTestDriver{
		runners: []state.RunnerInfo{
			{ID: "runner-a", Name: "runner-a", State: "exited", Status: "stopped"},
			{ID: "runner-b", Name: "runner-b", State: "running", Status: "running"},
		},
		logs: map[string]string{"runner-a": "failure-tail"},
	}

	req := httptest.NewRequest(http.MethodPost, "/api/actions/prune", nil)
	rec := httptest.NewRecorder()
	handlePrune(st, drv).ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	if len(drv.stopped) != 1 || drv.stopped[0] != "runner-a" {
		t.Fatalf("expected only runner-a to be stopped, got %v", drv.stopped)
	}
	if logTail, ok := st.GetRunnerLog("runner-a"); !ok || logTail != "failure-tail" {
		t.Fatalf("expected retained runner log for runner-a, got ok=%v log=%q", ok, logTail)
	}

	var body map[string]any
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if got, ok := body["pruned"].(float64); !ok || int(got) != 1 {
		t.Fatalf("expected pruned=1, got %#v", body["pruned"])
	}
}

func TestHandlePrune_RejectsInvalidMethod(t *testing.T) {
	st := state.NewState(3, "test", nil)
	req := httptest.NewRequest(http.MethodGet, "/api/actions/prune", nil)
	rec := httptest.NewRecorder()
	handlePrune(st).ServeHTTP(rec, req)
	if rec.Code != http.StatusMethodNotAllowed {
		t.Fatalf("expected 405, got %d", rec.Code)
	}
}
