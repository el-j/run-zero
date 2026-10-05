package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

func TestNewPoller_DefaultInterval(t *testing.T) {
	p := NewPoller(nil, nil, nil, []string{"repo1", ""}, 0)
	if p.pollInterval != 10*time.Second {
		t.Errorf("expected 10s default interval, got %v", p.pollInterval)
	}
	if len(p.repos) != 1 {
		t.Errorf("expected 1 cleaned repo, got %d", len(p.repos))
	}
}

func TestPoller_PollOnceAndStart(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-RateLimit-Remaining", "4800")
		w.Header().Set("X-RateLimit-Limit", "5000")
		w.Header().Set("Content-Type", "application/json")

		if strings.Contains(r.URL.Path, "err-repo") {
			w.WriteHeader(http.StatusBadGateway)
			_, _ = w.Write([]byte(`{"error": "down"}`))
			return
		}

		if strings.Contains(r.URL.Path, "/jobs") {
			_, _ = w.Write([]byte(`{"total_count": 1, "jobs": [{"id": 999, "status": "queued", "name": "build", "created_at": "2026-10-05T09:00:00Z"}]}`))
			return
		}

		if strings.Contains(r.URL.Path, "/runs") {
			_, _ = w.Write([]byte(`{"total_count": 1, "workflow_runs": [{"id": 888, "name": "CI", "status": "queued"}]}`))
			return
		}

		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer ts.Close()

	client := NewClient("test-token", ts.URL, nil)
	pm, _ := NewPriorityManager("", []string{"good-repo"}, nil)
	rec := NewReconciler(pm)
	st := state.NewState(5, "1.0.0", nil)

	poller := NewPoller(client, rec, st, []string{"good-repo"}, 10*time.Millisecond)

	err := poller.PollOnce(context.Background())
	if err != nil {
		t.Fatalf("unexpected poll error: %v", err)
	}

	snap := st.GetSnapshot()
	if len(snap.QueuedJobs) != 1 {
		t.Fatalf("expected 1 queued job, got %d", len(snap.QueuedJobs))
	}
	if snap.RateLimitRemaining == nil || *snap.RateLimitRemaining != 4800 {
		t.Errorf("expected rate limit 4800, got %v", snap.RateLimitRemaining)
	}

	// Test with error repo
	pollerErr := NewPoller(client, rec, st, []string{"err-repo"}, 10*time.Millisecond)
	err = pollerErr.PollOnce(context.Background())
	if err == nil {
		t.Fatal("expected error on failing repo")
	}

	// Test Start loop with context cancel
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	go func() {
		poller.Start(ctx)
		close(done)
	}()

	time.Sleep(25 * time.Millisecond)
	cancel()
	select {
	case <-done:
	case <-time.After(1 * time.Second):
		t.Fatal("poller failed to stop on context cancel")
	}
}
