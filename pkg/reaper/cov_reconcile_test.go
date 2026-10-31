package reaper

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

func TestReaper_Reconcile_WithGitHub(t *testing.T) {
	var mu sync.Mutex
	var deleted []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		defer mu.Unlock()
		switch {
		case r.Method == http.MethodDelete:
			deleted = append(deleted, r.URL.Path)
			w.WriteHeader(http.StatusNoContent)
		case strings.Contains(r.URL.Path, "o/bad"):
			w.WriteHeader(http.StatusInternalServerError)
		default:
			_, _ = w.Write([]byte(`{"total_count":1,"runners":[{"id":7,"name":"runzero-dead","status":"offline","busy":false,"labels":[]}]}`))
		}
	}))
	defer srv.Close()

	old := time.Now().Add(-time.Hour).UTC().Format(time.RFC3339)
	runners := []state.RunnerInfo{
		{ID: "id-dead", Name: "runzero-dead", TargetRepo: "o/ok", CreatedAt: &old},
		{ID: "id-ghost", Name: "runzero-ghost", TargetRepo: "o/ok", CreatedAt: &old},
		{ID: "id-bad", Name: "runzero-bad", TargetRepo: "o/bad", CreatedAt: &old},
		{ID: "id-norepo", Name: "runzero-norepo"},
	}
	d := &mockDriver{}
	r := NewReaper(d, github.NewClient("t", srv.URL, srv.Client()), Timeouts{})
	reaped := r.Reconcile(context.Background(), runners, 0)
	if len(reaped) != 2 {
		t.Fatalf("reaped %v", reaped)
	}
	mu.Lock()
	defer mu.Unlock()
	if len(deleted) < 1 {
		t.Errorf("expected delete calls, got %v", deleted)
	}
}

func TestReconcileLocalRunners_NilDriverAndNilFirstSeen(t *testing.T) {
	old := time.Now().Add(-time.Hour).UTC().Format(time.RFC3339)
	r := &Reaper{timeouts: DefaultTimeouts()}
	runners := []state.RunnerInfo{{ID: "", Name: "n", TargetRepo: "o/r", CreatedAt: &old}, {Name: "fresh"}}
	got := r.ReconcileLocalRunners(context.Background(), runners, nil, map[string]bool{"o/r": true}, float64(time.Now().Unix()), 0)
	if len(got) != 1 {
		t.Errorf("got %v", got)
	}
}

func TestReconcileLocalRunners_PrunesFirstSeen(t *testing.T) {
	r := NewReaper(nil, nil, Timeouts{})
	now := float64(time.Now().Unix())
	r.ReconcileLocalRunners(context.Background(), []state.RunnerInfo{{ID: "a"}}, nil, nil, now, 0)
	r.ReconcileLocalRunners(context.Background(), []state.RunnerInfo{{ID: "b"}}, nil, nil, now, 0)
	if _, ok := r.firstSeen["a"]; ok {
		t.Error("stale firstSeen entry not pruned")
	}
}
