package driver

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestBridgeDriver_Methods(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/api/drivers/orbstack/spawn":
			_ = json.NewEncoder(w).Encode(map[string]string{"runner_id": "remote-orb-1"})
		case "/api/drivers/orbstack/runners":
			_ = json.NewEncoder(w).Encode(map[string]any{
				"runners": []state.RunnerInfo{{ID: "remote-orb-1", Name: "orb-1"}},
			})
		case "/api/drivers/orbstack/stop", "/api/drivers/orbstack/cleanup":
			w.WriteHeader(http.StatusOK)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer srv.Close()

	bd := NewBridgeDriver(srv.URL, "orbstack", "test-token", srv.Client())
	if bd.Backend() != "orbstack" {
		t.Fatalf("expected backend orbstack, got %s", bd.Backend())
	}

	info, err := bd.SpawnRunner(context.Background(), RunnerSpec{Name: "orb-1", Repo: "o/r"})
	if err != nil || info.ID != "remote-orb-1" {
		t.Fatalf("unexpected spawn result: info=%v, err=%v", info, err)
	}

	list, err := bd.ListRunners(context.Background())
	if err != nil || len(list) != 1 || list[0].ID != "remote-orb-1" {
		t.Fatalf("unexpected list result: list=%v, err=%v", list, err)
	}

	if err := bd.StopRunner(context.Background(), "remote-orb-1"); err != nil {
		t.Fatalf("unexpected stop error: %v", err)
	}

	if err := bd.CleanupAll(context.Background()); err != nil {
		t.Fatalf("unexpected cleanup error: %v", err)
	}
}
