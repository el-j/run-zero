package bridge

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

type mockDriver struct {
	backend string
	spawnID string
	runners []state.RunnerInfo
	stopped bool
}

func (m *mockDriver) Backend() string { return m.backend }
func (m *mockDriver) SpawnRunner(ctx context.Context, spec driver.RunnerSpec) (*state.RunnerInfo, error) {
	return &state.RunnerInfo{ID: m.spawnID, Name: spec.Name, Status: "running"}, nil
}
func (m *mockDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	return m.runners, nil
}
func (m *mockDriver) StopRunner(ctx context.Context, runnerID string) error {
	m.stopped = true
	return nil
}
func (m *mockDriver) CleanupAll(ctx context.Context) error { return nil }

func TestBridgeServer_Endpoints(t *testing.T) {
	md := &mockDriver{
		backend: "orbstack",
		spawnID: "orb-123",
		runners: []state.RunnerInfo{{ID: "orb-123", Name: "test-runner"}},
	}
	drivers := map[string]driver.RunnerDriver{"orbstack": md}
	srv := NewServer(49504, "127.0.0.1", "secret", "1.0.0", "sha123", drivers)

	// 1. Health
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var h HealthResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &h); err != nil || h.Status != "ok" {
		t.Fatalf("unexpected health payload: %v", h)
	}

	// 2. Status
	req = httptest.NewRequest(http.MethodGet, "/api/status", nil)
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}

	// 3. Unauthorized
	req = httptest.NewRequest(http.MethodGet, "/api/drivers/orbstack/runners", nil)
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", rec.Code)
	}

	// 4. Authorized List Runners
	req = httptest.NewRequest(http.MethodGet, "/api/drivers/orbstack/runners", nil)
	req.Header.Set("Authorization", "Bearer secret")
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}

	// 5. Spawn runner
	body, _ := json.Marshal(SpawnRequest{Name: "my-runner", Repo: "org/repo", Labels: "vm,gpu"})
	req = httptest.NewRequest(http.MethodPost, "/api/drivers/orbstack/spawn", bytes.NewReader(body))
	req.Header.Set("Authorization", "Bearer secret")
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var sResp SpawnResponse
	_ = json.Unmarshal(rec.Body.Bytes(), &sResp)
	if sResp.RunnerID != "orb-123" {
		t.Fatalf("expected orb-123, got %s", sResp.RunnerID)
	}

	// 6. Stop runner
	body, _ = json.Marshal(map[string]string{"runner_id": "orb-123"})
	req = httptest.NewRequest(http.MethodPost, "/api/drivers/orbstack/stop", bytes.NewReader(body))
	req.Header.Set("Authorization", "Bearer secret")
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK || !md.stopped {
		t.Fatalf("expected 200 and stopped, got %d", rec.Code)
	}

	// 7. Prune and Cleanup
	req = httptest.NewRequest(http.MethodPost, "/api/drivers/orbstack/prune", nil)
	req.Header.Set("Authorization", "Bearer secret")
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}

	req = httptest.NewRequest(http.MethodPost, "/api/drivers/orbstack/cleanup", nil)
	req.Header.Set("Authorization", "Bearer secret")
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}

	// 8. Not found
	req = httptest.NewRequest(http.MethodGet, "/invalid", nil)
	rec = httptest.NewRecorder()
	srv.ServeHTTP(rec, req)
	if rec.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", rec.Code)
	}
}
