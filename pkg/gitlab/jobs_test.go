package gitlab

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLab_ListProjectPendingJobs(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`[
			{
				"id": 1001,
				"status": "pending",
				"stage": "build",
				"name": "compile-binary",
				"ref": "feature/ui",
				"tag_list": ["docker", "amd64"],
				"web_url": "https://gitlab.com/org/repo/-/jobs/1001",
				"pipeline": {
					"id": 501,
					"project_id": 12,
					"ref": "feature/ui",
					"status": "pending"
				}
			}
		]`))
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	jobs, err := client.ListProjectPendingJobs(context.Background(), "org/repo")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(jobs) != 1 {
		t.Fatalf("expected 1 job, got %d", len(jobs))
	}

	qJob := client.ConvertToQueuedJob(jobs[0], "org/repo")
	if qJob.ID != 1001 || qJob.RunID != 501 || qJob.Name != "compile-binary" || qJob.Status != "queued" {
		t.Errorf("unexpected queued job conversion: %+v", qJob)
	}
}
