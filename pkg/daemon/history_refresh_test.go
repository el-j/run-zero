package daemon

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

func TestRefreshCompletedJobs_BypassesThrottleWhenHistoryDirty(t *testing.T) {
	var runsCalls int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.Contains(r.URL.Path, "/actions/runs") {
			atomic.AddInt32(&runsCalls, 1)
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{"workflow_runs":[]}`))
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer srv.Close()

	st := state.NewState(3, "test", nil)
	scaler := &Scaler{
		ghClient:           github.NewClient("token", srv.URL, srv.Client()),
		state:              st,
		lastHistoryRefresh: time.Now(),
	}

	repos := []string{"el-j/run-zero"}
	scaler.refreshCompletedJobs(context.Background(), repos)
	if got := atomic.LoadInt32(&runsCalls); got != 0 {
		t.Fatalf("expected throttled refresh to skip API call, got %d", got)
	}

	st.RequestHistoryRefresh()
	scaler.refreshCompletedJobs(context.Background(), repos)
	if got := atomic.LoadInt32(&runsCalls); got != 1 {
		t.Fatalf("expected dirty refresh to call API once, got %d", got)
	}
}
