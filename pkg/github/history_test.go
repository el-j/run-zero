package github

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestDiagnose(t *testing.T) {
	str := func(s string) *string { return &s }
	tests := []struct {
		name, conclusion, wantReason, wantStep string
		steps                                  []workflowStep
	}{
		{"failure step", "failure", "Step 2 “compile” failed.", "compile", []workflowStep{{Number: 1, Name: "setup", Status: "completed", Conclusion: str("success")}, {Number: 2, Name: "compile", Status: "completed", Conclusion: str("failure")}}},
		{"failure no step before run", "failure", "Job failed before any step ran — likely a runner or setup problem (runner crashed, image/registration error). Check the local runner log.", "", []workflowStep{{Status: "queued"}}},
		{"failure unknown culprit", "failure", "Job failed, but GitHub reported no failing step.", "", []workflowStep{{Status: "completed", Conclusion: str("success")}}},
		{"timeout", "timed_out", "Timed out while running step 3 “wait”.", "wait", []workflowStep{{Number: 3, Name: "wait", Status: "completed", Conclusion: str("cancelled")}}},
		{"timeout no culprit", "timed_out", "Job exceeded its time limit.", "", nil},
		{"cancelled step", "cancelled", "Cancelled while running step 4 “deploy”.", "deploy", []workflowStep{{Number: 4, Name: "deploy", Conclusion: str("cancelled")}}},
		{"cancelled before run", "cancelled", "Cancelled before any step started (e.g. runner was removed or run cancelled while queued).", "", []workflowStep{{Status: "pending"}}},
		{"cancelled after run", "cancelled", "Cancelled.", "", []workflowStep{{Status: "completed", Conclusion: str("success")}}},
		{"startup", "startup_failure", "Workflow failed to start (invalid workflow file or missing permissions).", "", nil},
		{"approval", "action_required", "Waiting for manual approval.", "", nil},
		{"other", "neutral", "Finished with conclusion “neutral”.", "", nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			step, reason := Diagnose(workflowJob{Conclusion: tt.conclusion, Steps: tt.steps})
			if reason != tt.wantReason {
				t.Fatalf("reason %q, want %q", reason, tt.wantReason)
			}
			if tt.wantStep == "" {
				if step != nil {
					t.Fatalf("unexpected step %q", *step)
				}
			} else if step == nil || *step != tt.wantStep {
				t.Fatalf("step %v, want %q", step, tt.wantStep)
			}
		})
	}
}

func TestHistoryHelpers(t *testing.T) {
	if isSelfHosted([]string{"ubuntu", "SELF-HOSTED"}) != true || isSelfHosted([]string{"ubuntu"}) {
		t.Fatal("self-hosted label detection failed")
	}
	validStart, validEnd := "2026-01-01T00:00:00Z", "2026-01-01T00:00:03Z"
	if got := durationSeconds(&validStart, &validEnd); got == nil || *got != 3 {
		t.Fatalf("duration %v", got)
	}
	bad := "bad"
	if durationSeconds(nil, &validEnd) != nil || durationSeconds(&validStart, nil) != nil || durationSeconds(&bad, &validEnd) != nil || durationSeconds(&validEnd, &validStart) != nil {
		t.Fatal("invalid durations should be nil")
	}
	newer, older := "2026-02-01T00:00:00Z", "2026-01-01T00:00:00Z"
	completed := []state.CompletedJob{{ID: 1, CompletedAt: &older}, {ID: 2, CompletedAt: &newer}, {ID: 3}}
	SortCompletedJobs(completed)
	if completed[0].ID != 2 || completed[1].ID != 1 {
		t.Fatalf("sort order %+v", completed)
	}
	sortNewestFirst(nil)
}

func TestHistoryFetcherFetchCacheDiagnosisAndEviction(t *testing.T) {
	calls := map[string]int{}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls[r.URL.Path]++
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.Path {
		case "/repos/o/r/actions/runs":
			_, _ = fmt.Fprint(w, `{"workflow_runs":[{"id":1,"name":"fallback","head_branch":"main","conclusion":"failure","run_attempt":1,"updated_at":"2026-10-01T00:00:00Z"},{"id":2,"conclusion":"skipped"},{"id":3,"conclusion":"neutral"},{"id":4,"conclusion":""}]}`)
		case "/repos/o/r/actions/runs/1/jobs":
			_, _ = fmt.Fprint(w, `{"jobs":[{"id":11,"name":"test","status":"completed","conclusion":"failure","labels":["SELF-HOSTED"],"steps":[{"number":1,"name":"go test","status":"completed","conclusion":"failure"}]},{"id":12,"status":"queued","conclusion":"failure","labels":["self-hosted"]},{"id":13,"status":"completed","conclusion":"skipped","labels":["self-hosted"]},{"id":14,"status":"completed","conclusion":"failure","labels":["ubuntu"]}]}`)
		case "/repos/o/r/check-runs/11/annotations":
			_, _ = fmt.Fprint(w, `[{"message":" failure msg ","annotation_level":"failure"},{"message":"failure msg","annotation_level":"warning"},{"message":"extra","annotation_level":"notice"},{"message":""},{"message":"long","annotation_level":"failure"}]`)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	client := NewClient("", server.URL, server.Client())
	h := NewHistoryFetcher(client)
	jobs, err := h.Fetch(context.Background(), "o/r")
	if err != nil {
		t.Fatal(err)
	}
	if len(jobs) != 1 || jobs[0].ID != 11 || jobs[0].FailureReason == nil || jobs[0].FailedStep == nil || len(jobs[0].Messages) != 3 {
		t.Fatalf("unexpected history: %+v", jobs)
	}
	if jobs[0].HTMLURL != "https://github.com/o/r/actions/runs/1/job/11" || jobs[0].WorkflowName == nil || *jobs[0].WorkflowName != "fallback" {
		t.Fatalf("missing fallback fields: %+v", jobs[0])
	}
	_, err = h.Fetch(context.Background(), "o/r")
	if err != nil || calls["/repos/o/r/actions/runs/1/jobs"] != 1 {
		t.Fatalf("cache not used: calls=%v err=%v", calls, err)
	}
	// A changed live set evicts stale entries; reintroducing the run fetches its jobs again.
	// Exercise eviction directly without coupling the test to a second API client.
	h.evict("o/r", map[string]bool{})
	if len(h.cache) != 0 {
		t.Fatal("cache entry was not evicted")
	}
}

func TestHistoryFetcherRunFailuresAndAnnotationLimits(t *testing.T) {
	long := strings.Repeat("x", maxAnnotationMsgSize+10)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case strings.HasSuffix(r.URL.Path, "/actions/runs"):
			_, _ = fmt.Fprint(w, `{"workflow_runs":[{"id":5,"conclusion":"success","updated_at":"new"},{"id":6,"conclusion":"failure","updated_at":"old"}]}`)
		case strings.HasSuffix(r.URL.Path, "/runs/5/jobs"):
			_, _ = fmt.Fprint(w, `{"jobs":[{"id":51,"status":"completed","conclusion":"success","labels":["self-hosted"],"html_url":"job-url"}]}`)
		case strings.HasSuffix(r.URL.Path, "/runs/6/jobs"):
			w.WriteHeader(http.StatusBadGateway)
		case strings.Contains(r.URL.Path, "/check-runs/"):
			items := []annotation{{Message: long, AnnotationLevel: "failure"}}
			for i := 0; i < 7; i++ {
				items = append(items, annotation{Message: fmt.Sprintf("m%d", i), AnnotationLevel: "warning"})
			}
			_ = json.NewEncoder(w).Encode(items)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	h := NewHistoryFetcher(NewClient("", server.URL, server.Client()))
	jobs, err := h.Fetch(context.Background(), "o/r")
	if err != nil || len(jobs) != 1 || jobs[0].HTMLURL != "job-url" {
		t.Fatalf("fetch = %+v, %v", jobs, err)
	}
	// Build directly to hit annotation truncation and the non-failing-conclusion path (which skips annotations).
	workflowName := "custom workflow"
	j := h.buildJob(context.Background(), "o/r", workflowRun{ID: 9, WorkflowName: &workflowName}, workflowJob{ID: 2, Conclusion: "timed_out"})
	if j.FailureReason == nil || len(j.Messages) != maxAnnotationMsgs || !strings.HasSuffix(j.Messages[0], "…") || len(j.Messages[0]) != maxAnnotationMsgSize+len("…") {
		t.Fatalf("annotation limit not applied: %+v", j)
	}
	ok := h.buildJob(context.Background(), "o/r", workflowRun{ID: 9}, workflowJob{Conclusion: "success"})
	if ok.FailureReason != nil || ok.Messages != nil {
		t.Fatalf("success unexpectedly diagnosed: %+v", ok)
	}
}

func TestHistoryFetcherErrorsAndEmptyAnnotations(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.Contains(r.URL.Path, "/actions/runs") {
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		w.WriteHeader(http.StatusBadGateway)
	}))
	defer server.Close()
	h := NewHistoryFetcher(NewClient("", server.URL, server.Client()))
	if _, err := h.Fetch(context.Background(), "repo"); err == nil {
		t.Fatal("expected runs request error")
	}
	if got := h.annotationMessages(context.Background(), "repo", 1); got != nil {
		t.Fatalf("expected nil annotations, got %v", got)
	}
}

func TestHistoryFetcherAnnotationDedupeAndFailureOrder(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = fmt.Fprint(w, `[{"message":"other","annotation_level":"warning"},{"message":"fail","annotation_level":"failure"},{"message":"fail","annotation_level":"failure"},{"message":"third","annotation_level":"notice"},{"message":"fourth","annotation_level":"notice"},{"message":"fifth","annotation_level":"notice"},{"message":"sixth","annotation_level":"notice"}]`)
	}))
	defer server.Close()
	got := NewHistoryFetcher(NewClient("", server.URL, server.Client())).annotationMessages(context.Background(), "o/r", 2)
	if !reflect.DeepEqual(got, []string{"fail", "other", "third", "fourth", "fifth"}) {
		t.Fatalf("messages = %v", got)
	}
}
