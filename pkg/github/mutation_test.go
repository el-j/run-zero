package github

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

func TestNewClient_DefaultTimeout(t *testing.T) {
	if c := NewClient("t", "", nil); c.httpClient.Timeout != 15*time.Second {
		t.Fatalf("timeout %s", c.httpClient.Timeout)
	}
}

func TestDoRequest_ZeroRemainingQuotaBlocksUntilReset(t *testing.T) {
	calls := 0
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { calls++; _, _ = w.Write([]byte(`{}`)) }))
	defer srv.Close()
	c := NewClient("t", srv.URL, srv.Client())
	c.rateLimit = RateLimit{Limit: 5000, Remaining: 0, Reset: time.Now().Add(time.Hour)}
	var out map[string]any
	if _, err := c.DoRequest(context.Background(), "GET", "/x", nil, &out); err == nil || calls != 0 {
		t.Fatalf("an exhausted quota must not call GitHub: err %v, calls %d", err, calls)
	}
}

func TestDoRequest_Status300IsAnError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusMultipleChoices)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()
	var out map[string]any
	if _, err := NewClient("t", srv.URL, srv.Client()).DoRequest(context.Background(), "GET", "/x", nil, &out); err == nil {
		t.Fatal("HTTP 300 must be an error")
	}
}

// discoveryServer serves /user/repos: page 1 holds 100 recent repos, page 2
// one more, and the last repo on page 2 was pushed 30 days ago.
func discoveryServer(t *testing.T, pages *[]string) *Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		page := r.URL.Query().Get("page")
		*pages = append(*pages, page)
		recent := time.Now().UTC().Add(-time.Hour).Format(time.RFC3339)
		old := time.Now().UTC().AddDate(0, 0, -30).Format(time.RFC3339)
		var items []map[string]any
		switch page {
		case "1":
			for i := 0; i < 100; i++ {
				items = append(items, map[string]any{"full_name": fmt.Sprintf("o/r%03d", i), "pushed_at": recent})
			}
		case "2":
			items = append(items, map[string]any{"full_name": "o/month-old", "pushed_at": old})
		}
		_ = json.NewEncoder(w).Encode(items)
	}))
	t.Cleanup(srv.Close)
	return NewClient("t", srv.URL, srv.Client())
}

func TestDiscoverRepositories_PagesAndActiveDays(t *testing.T) {
	var pages []string
	c := discoveryServer(t, &pages)

	repos, err := c.DiscoverRepositories(context.Background(), "", "", 0, true, "")
	if err != nil || len(repos) != 101 {
		t.Fatalf("activeDays 0 means the 60-day default and a full page means another page: %d repos, err %v, pages %v", len(repos), err, pages)
	}
	if len(pages) != 2 || pages[1] != "2" {
		t.Fatalf("expected pages 1 and 2, got %v", pages)
	}

	pages = nil
	repos, _ = c.DiscoverRepositories(context.Background(), "", "", 10, true, "")
	if len(repos) != 100 {
		t.Fatalf("a 10-day window must drop the month-old repo, got %d repos", len(repos))
	}
}

func TestAnnotationMessages_TruncatesOnlyPastTheLimit(t *testing.T) {
	exact := strings.Repeat("a", maxAnnotationMsgSize)
	long := strings.Repeat("b", maxAnnotationMsgSize+1)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode([]map[string]string{
			{"annotation_level": "failure", "message": exact},
			{"annotation_level": "failure", "message": long},
		})
	}))
	defer srv.Close()
	msgs := NewHistoryFetcher(NewClient("t", srv.URL, srv.Client())).annotationMessages(context.Background(), "o/r", 1)
	if len(msgs) != 2 || msgs[0] != exact || msgs[1] != long[:maxAnnotationMsgSize]+"…" {
		t.Fatalf("unexpected messages (lengths %d)", len(msgs))
	}
}

func TestSortCompletedJobs_NewestFirstNilLastStable(t *testing.T) {
	ts := func(s string) *string { return &s }
	jobs := []state.CompletedJob{
		{ID: 1},
		{ID: 2, CompletedAt: ts("2026-11-01T10:00:00Z")},
		{ID: 3, CompletedAt: ts("2026-11-02T10:00:00Z")},
		{ID: 4, CompletedAt: ts("2026-11-01T10:00:00Z")},
	}
	SortCompletedJobs(jobs)
	var got []int64
	for _, j := range jobs {
		got = append(got, j.ID)
	}
	if fmt.Sprint(got) != "[3 2 4 1]" {
		t.Fatalf("got %v, want newest first, equal times in input order, missing time last", got)
	}
}

func TestActiveJob_RunProgressWithoutSteps(t *testing.T) {
	job := activeJob("o/r", workflowRun{ID: 9}, workflowJob{ID: 1, Status: "queued"}, 1, 4)
	if job.ProgressPct == nil || *job.ProgressPct != 25 {
		t.Fatalf("1 of 4 jobs done must be 25%%, got %v", job.ProgressPct)
	}
}

func TestListActiveJobs_CountsCompletedStages(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case r.URL.Path == "/repos/o/r/actions/runs" && r.URL.Query().Get("status") == "queued":
			_, _ = w.Write([]byte(`{"workflow_runs":[{"id":9}]}`))
		case r.URL.Path == "/repos/o/r/actions/runs":
			_, _ = w.Write([]byte(`{"workflow_runs":[]}`))
		default:
			_, _ = w.Write([]byte(`{"jobs":[{"id":1,"status":"completed"},{"id":2,"status":"queued"}]}`))
		}
	}))
	defer srv.Close()
	jobs, err := NewClient("t", srv.URL, srv.Client()).ListActiveJobs(context.Background(), "o/r")
	if err != nil || len(jobs) != 1 || *jobs[0].StagesDone != 1 || *jobs[0].ProgressPct != 50 {
		t.Fatalf("got %+v, err %v", jobs, err)
	}
}

func TestStepProgress_CurrentStepIsFirstInProgress(t *testing.T) {
	j := workflowJob{Status: "in_progress", Steps: []workflowStep{
		{Name: "X", Status: "in_progress"},
		{Name: "Y", Status: "completed"},
		{Name: "Z", Status: "queued"},
	}}
	if done, cur := stepProgress(j); done != 1 || cur == nil || *cur != "X" {
		t.Fatalf("got %d, %v", done, cur)
	}
}

func TestPollOnce_LeavesQuotaUnsetWhenUnknown(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = w.Write([]byte(`{}`)) }))
	defer srv.Close()
	st := state.NewState(1, "t", nil)
	pm, _ := NewPriorityManager("", []string{"o/r"}, nil)
	p := NewPoller(NewClient("t", srv.URL, srv.Client()), NewReconciler(pm), st, []string{"o/r"}, time.Second)
	_ = p.PollOnce(context.Background())
	if st.GetSnapshot().RateLimitRemaining != nil {
		t.Fatal("no quota headers means no quota in the dashboard")
	}
}

func TestProviderAdapter_FetchQueuedJobsSkipsFailingRepos(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case strings.HasPrefix(r.URL.Path, "/repos/o/bad/"):
			w.WriteHeader(http.StatusInternalServerError)
		case r.URL.Path == "/repos/o/ok/actions/runs" && r.URL.Query().Get("status") == "queued":
			_, _ = w.Write([]byte(`{"workflow_runs":[{"id":9}]}`))
		case r.URL.Path == "/repos/o/ok/actions/runs":
			_, _ = w.Write([]byte(`{"workflow_runs":[]}`))
		default:
			_, _ = w.Write([]byte(`{"jobs":[{"id":1,"status":"queued"}]}`))
		}
	}))
	defer srv.Close()
	jobs, err := NewProviderAdapter(NewClient("t", srv.URL, srv.Client()), "o", "", []string{"o/bad", "o/ok"}).FetchQueuedJobs(context.Background())
	if err != nil || len(jobs) != 1 || jobs[0].Repo != "o/ok" {
		t.Fatalf("got %+v, err %v", jobs, err)
	}
}

func TestReconcile_TiesBreakByJobID(t *testing.T) {
	pm, _ := NewPriorityManager("", nil, nil)
	out := NewReconciler(pm).Reconcile([]state.QueuedJob{{ID: 2, Repo: "o/r", Status: "queued"}, {ID: 1, Repo: "o/r", Status: "queued"}}, 0, 4)
	if out[0].ID != 1 || out[1].ID != 2 {
		t.Fatalf("got %d, %d", out[0].ID, out[1].ID)
	}
}

func TestConvertToRunnerInfo_OfflineState(t *testing.T) {
	c := NewClient("t", "", nil)
	if s := c.ConvertToRunnerInfo(RunnerRegistration{ID: 1, Name: "r", Status: "offline"}).State; s != "offline" {
		t.Fatalf("offline: %q", s)
	}
	if s := c.ConvertToRunnerInfo(RunnerRegistration{ID: 1, Name: "r", Status: "online"}).State; s != "active" {
		t.Fatalf("online: %q", s)
	}
}

func TestPoller_Interval(t *testing.T) {
	if got := NewPoller(nil, nil, nil, nil, 3*time.Second).Interval(); got != 3*time.Second {
		t.Fatalf("got %s", got)
	}
}
