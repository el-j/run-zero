package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestClient_ListQueuedJobs(t *testing.T) {
	runsJSON := `{
		"total_count": 2,
		"workflow_runs": [
			{"id": 101, "name": "CI", "head_branch": "main", "status": "queued", "run_attempt": 1, "created_at": "2026-10-05T09:00:00Z"},
			{"id": 102, "name": "Deploy", "head_branch": "feat", "status": "queued", "run_attempt": 2, "created_at": "2026-10-05T09:05:00Z"}
		]
	}`

	jobsRun101JSON := `{
		"total_count": 2,
		"jobs": [
			{"id": 201, "run_id": 101, "name": "build", "status": "queued", "created_at": "2026-10-05T09:00:10Z", "labels": ["ubuntu-latest"]},
			{"id": 202, "run_id": 101, "name": "lint", "status": "in_progress", "created_at": "2026-10-05T09:00:15Z", "labels": ["ubuntu-latest"]}
		]
	}`

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if strings.Contains(r.URL.Path, "/runs/101/jobs") {
			_, _ = w.Write([]byte(jobsRun101JSON))
			return
		}
		if strings.Contains(r.URL.Path, "/runs/102/jobs") {
			// Simulate sub-request error
			w.WriteHeader(http.StatusInternalServerError)
			_, _ = w.Write([]byte(`{"message": "internal server error"}`))
			return
		}
		if strings.Contains(r.URL.Path, "/runs") {
			_, _ = w.Write([]byte(runsJSON))
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer ts.Close()

	client := NewClient("test-token", ts.URL, nil)
	jobs, err := client.ListQueuedJobs(context.Background(), "owner/repo")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(jobs) != 1 {
		t.Fatalf("expected 1 queued job (id 201), got %d", len(jobs))
	}
	if jobs[0].ID != 201 || jobs[0].Repo != "owner/repo" {
		t.Fatalf("unexpected job details: %+v", jobs[0])
	}
}

func TestClient_ListQueuedJobs_RunFetchError(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"message": "bad credentials"}`))
	}))
	defer ts.Close()

	client := NewClient("bad-token", ts.URL, nil)
	_, err := client.ListQueuedJobs(context.Background(), "owner/repo")
	if err == nil {
		t.Fatal("expected error on 401 unauthorized")
	}
}

func TestClient_GetWorkflowRunAndJob(t *testing.T) {
	runJSON := `{
		"id": 101,
		"name": "CI",
		"head_branch": "main",
		"status": "completed",
		"conclusion": "success"
	}`

	jobJSON := `{
		"id": 201,
		"run_id": 101,
		"name": "build",
		"status": "completed",
		"conclusion": "success"
	}`

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/repos/owner/repo/actions/runs/101" {
			_, _ = w.Write([]byte(runJSON))
			return
		}
		if r.URL.Path == "/repos/owner/repo/actions/jobs/201" {
			_, _ = w.Write([]byte(jobJSON))
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer ts.Close()

	client := NewClient("test-token", ts.URL, nil)
	run, err := client.GetWorkflowRun(context.Background(), "owner/repo", 101)
	if err != nil {
		t.Fatalf("unexpected error fetching workflow run: %v", err)
	}
	if run.ID != 101 || run.Status != "completed" || run.Conclusion != "success" {
		t.Errorf("unexpected workflow run: %+v", run)
	}

	job, err := client.GetWorkflowJob(context.Background(), "owner/repo", 201)
	if err != nil {
		t.Fatalf("unexpected error fetching workflow job: %v", err)
	}
	if job.ID != 201 || job.Status != "completed" || job.Conclusion != "success" {
		t.Errorf("unexpected workflow job: %+v", job)
	}
}
