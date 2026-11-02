package reaper

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"

	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

// zombieGitHub serves one offline-but-busy runzero runner for repo o/z whose
// run 55 holds an in-progress job on it.
func zombieGitHub(t *testing.T, cancelCode, runsCode int) (*github.Client, *[]string) {
	t.Helper()
	var mu sync.Mutex
	var calls []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		calls = append(calls, r.Method+" "+r.URL.Path)
		mu.Unlock()
		switch {
		case r.URL.Path == "/repos/o/z/actions/runners":
			_, _ = w.Write([]byte(`{"total_count":1,"runners":[{"id":9,"name":"runzero-zombie","status":"offline","busy":true}]}`))
		case r.URL.Path == "/repos/o/z/actions/runs" && runsCode != 0:
			w.WriteHeader(runsCode)
		case r.URL.Path == "/repos/o/z/actions/runs" && r.URL.Query().Get("status") == "in_progress":
			_, _ = w.Write([]byte(`{"workflow_runs":[{"id":55,"name":"CI"},{"id":56,"name":"CI"}]}`))
		case r.URL.Path == "/repos/o/z/actions/runs":
			_, _ = w.Write([]byte(`{"workflow_runs":[]}`))
		case r.URL.Path == "/repos/o/z/actions/runs/55/jobs":
			_, _ = w.Write([]byte(`{"jobs":[
				{"id":1,"run_id":55,"name":"build","status":"in_progress","runner_name":"runzero-zombie"},
				{"id":2,"run_id":55,"name":"lint","status":"in_progress","runner_name":"runzero-zombie"}]}`))
		case r.URL.Path == "/repos/o/z/actions/runs/56/jobs":
			_, _ = w.Write([]byte(`{"jobs":[
				{"id":3,"run_id":56,"name":"other","status":"in_progress","runner_name":"runzero-alive"},
				{"id":4,"run_id":56,"name":"waiting","status":"queued"}]}`))
		case strings.HasSuffix(r.URL.Path, "/cancel"):
			w.WriteHeader(cancelCode)
		case r.Method == http.MethodDelete:
			w.WriteHeader(http.StatusNoContent)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	t.Cleanup(srv.Close)
	return github.NewClient("t", srv.URL, srv.Client()), &calls
}

func reconcileZombie(t *testing.T, gh *github.Client) []string {
	t.Helper()
	var logs []string
	r := NewReaper(&mockDriver{}, gh, Timeouts{})
	r.Logf = func(format string, args ...any) { logs = append(logs, fmt.Sprintf(format, args...)) }
	r.Reconcile(context.Background(), []state.RunnerInfo{{ID: "x", Name: "runzero-zombie", TargetRepo: "o/z"}}, 0)
	return logs
}

func TestReconcile_CancelsJobsOrphanedOnZombieRunner(t *testing.T) {
	gh, calls := zombieGitHub(t, http.StatusAccepted, 0)
	logs := reconcileZombie(t, gh)

	cancelAt, deleteAt := -1, -1
	cancels := 0
	for i, c := range *calls {
		switch c {
		case "POST /repos/o/z/actions/runs/55/cancel":
			cancels++
			cancelAt = i
		case "DELETE /repos/o/z/actions/runners/9":
			deleteAt = i
		case "POST /repos/o/z/actions/runs/56/cancel":
			t.Error("run 56 is not on the zombie runner and must not be cancelled")
		}
	}
	if cancels != 1 {
		t.Fatalf("expected run 55 cancelled once, got %d (calls %v)", cancels, *calls)
	}
	if deleteAt < cancelAt {
		t.Fatalf("registration must be deleted after the cancel (calls %v)", *calls)
	}
	if len(logs) != 1 || !strings.Contains(logs[0], "Cancelled run #55") {
		t.Fatalf("unexpected logs %v", logs)
	}
}

func TestReconcile_ZombieCancelFailureIsLogged(t *testing.T) {
	gh, _ := zombieGitHub(t, http.StatusInternalServerError, 0)
	if logs := reconcileZombie(t, gh); len(logs) != 1 || !strings.Contains(logs[0], "Could not cancel run #55") {
		t.Fatalf("unexpected logs %v", logs)
	}
}

func TestReconcile_ZombieJobListingFailureIsTolerated(t *testing.T) {
	gh, calls := zombieGitHub(t, http.StatusAccepted, http.StatusInternalServerError)
	r := NewReaper(&mockDriver{}, gh, Timeouts{}) // no Logf: logging must be optional
	r.Reconcile(context.Background(), []state.RunnerInfo{{ID: "x", Name: "runzero-zombie", TargetRepo: "o/z"}}, 0)
	for _, c := range *calls {
		if strings.HasSuffix(c, "/cancel") {
			t.Fatalf("nothing can be cancelled when jobs cannot be listed: %v", *calls)
		}
	}
}
