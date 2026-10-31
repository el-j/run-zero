package github

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestWorkflowGettersAndListActiveJobsBranches(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case strings.HasSuffix(r.URL.Path, "/actions/runs/10"):
			w.WriteHeader(http.StatusBadGateway)
		case strings.HasSuffix(r.URL.Path, "/actions/jobs/20"):
			w.WriteHeader(http.StatusBadGateway)
		case strings.Contains(r.URL.RawQuery, "status=queued"):
			_, _ = fmt.Fprint(w, `{"workflow_runs":[{"id":1,"name":"queued-run","head_branch":"main","run_attempt":2},{"id":3,"name":"failed-run"}]}`)
		case strings.Contains(r.URL.RawQuery, "status=in_progress"):
			_, _ = fmt.Fprint(w, `{"workflow_runs":[{"id":1,"name":"duplicate"},{"id":2,"name":"active-run","workflow_name":"workflow display","head_branch":"dev"}]}`)
		case strings.Contains(r.URL.Path, "/runs/1/jobs"):
			_, _ = fmt.Fprint(w, `{"jobs":[{"id":11,"name":"queued","status":"queued","created_at":"then","labels":["linux"],"steps":[{"name":"done","status":"completed"},{"name":"next","status":"queued"}]},{"id":12,"name":"running","status":"in_progress","steps":[{"name":"current","status":"in_progress"}]},{"id":13,"status":"completed"}]}`)
		case strings.Contains(r.URL.Path, "/runs/2/jobs"):
			_, _ = fmt.Fprint(w, `{"jobs":[{"id":22,"name":"default stage","status":"in_progress"}]}`)
		case strings.Contains(r.URL.Path, "/runs/3/jobs"):
			w.WriteHeader(http.StatusBadGateway)
		default:
			http.NotFound(w, r)
		}
	}))
	defer srv.Close()
	c := NewClient("", srv.URL, srv.Client())
	if _, err := c.GetWorkflowRun(context.Background(), "o/r", 10); err == nil {
		t.Fatal("expected run error")
	}
	if _, err := c.GetWorkflowJob(context.Background(), "o/r", 20); err == nil {
		t.Fatal("expected job error")
	}
	jobs, err := c.ListActiveJobs(context.Background(), "o/r")
	if err != nil || len(jobs) != 3 {
		t.Fatalf("jobs=%+v err=%v", jobs, err)
	}
	if jobs[0].CurrentStep == nil || *jobs[0].CurrentStep != "next" || jobs[0].ProgressPct == nil || *jobs[0].ProgressPct != 50 || !strings.Contains(jobs[0].HTMLURL, "/job/11") {
		t.Fatalf("queued job %+v", jobs[0])
	}
	if jobs[1].CurrentStep == nil || *jobs[1].CurrentStep != "current" {
		t.Fatalf("in progress step %+v", jobs[1])
	}
	if jobs[2].CurrentStep == nil || *jobs[2].CurrentStep != "Executing workflow job..." || jobs[2].WorkflowName == nil || *jobs[2].WorkflowName != "workflow display" || jobs[2].ProgressPct == nil || *jobs[2].ProgressPct != 0 {
		t.Fatalf("default stage %+v", jobs[2])
	}
}

func TestListActiveJobsOptionalRequestErrors(t *testing.T) {
	mode := 0
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.Contains(r.URL.RawQuery, "status=queued") {
			if mode == 1 {
				w.WriteHeader(http.StatusBadGateway)
			} else {
				_, _ = fmt.Fprint(w, `{"workflow_runs":[]}`)
			}
			return
		}
		if strings.Contains(r.URL.RawQuery, "status=in_progress") {
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		http.NotFound(w, r)
	}))
	defer srv.Close()
	c := NewClient("", srv.URL, srv.Client())
	jobs, err := c.ListActiveJobs(context.Background(), "o/r")
	if err != nil || len(jobs) != 0 {
		t.Fatalf("optional in-progress failure jobs=%v err=%v", jobs, err)
	}
	mode = 1
	if _, err := c.ListActiveJobs(context.Background(), "o/r"); err == nil {
		t.Fatal("expected required queued-runs failure")
	}
}
