package gitlab

import (
	"context"
	"fmt"
	"net/url"

	"github.com/el-j/run-zero/pkg/state"
)

// GitLabJob represents a CI job in GitLab CI/CD.
type GitLabJob struct {
	// ID Unique GitLab job or pipeline identifier.
	ID int64 `json:"id"`
	// Status Current pipeline or job status.
	Status string `json:"status"` // pending, running, success, failed, canceled
	// Stage Pipeline stage containing the job.
	Stage string `json:"stage"`
	// Name Job name.
	Name string `json:"name"`
	// Ref Branch or tag used by the pipeline.
	Ref string `json:"ref"`
	// CreatedAt RFC3339 timestamp when the job was created.
	CreatedAt *string `json:"created_at,omitempty"`
	// StartedAt RFC3339 timestamp when the job started.
	StartedAt *string `json:"started_at,omitempty"`
	// TagList Runner tags requested by the job.
	TagList []string `json:"tag_list"`
	// WebURL Browser URL for the job.
	WebURL string `json:"web_url"`
	// Pipeline Pipeline metadata associated with this job.
	Pipeline GitLabPipeline `json:"pipeline"`
}

// GitLabPipeline represents pipeline metadata associated with a job.
type GitLabPipeline struct {
	// ID Unique GitLab job or pipeline identifier.
	ID int64 `json:"id"`
	// ProjectID GitLab project identifier.
	ProjectID int64 `json:"project_id"`
	// Ref Branch or tag used by the pipeline.
	Ref string `json:"ref"`
	// Status Current pipeline or job status.
	Status string `json:"status"`
}

// ListProjectPendingJobs fetches all pending jobs for a specific project.
func (c *Client) ListProjectPendingJobs(ctx context.Context, projectID string) ([]GitLabJob, error) {
	var jobs []GitLabJob
	endpoint := fmt.Sprintf("/projects/%s/jobs?scope[]=pending&per_page=50", url.PathEscape(projectID))
	_, err := c.DoRequest(ctx, "GET", endpoint, nil, &jobs)
	if err != nil {
		return nil, err
	}
	return jobs, nil
}

// ConvertToQueuedJob maps a GitLabJob to RunZero's unified QueuedJob model.
func (c *Client) ConvertToQueuedJob(j GitLabJob, projectPath string) state.QueuedJob {
	runID := j.Pipeline.ID
	workflowName := j.Stage
	headBranch := j.Ref
	attempt := 1

	return state.QueuedJob{
		ID:           j.ID,
		RunID:        runID,
		Name:         j.Name,
		WorkflowName: &workflowName,
		HeadBranch:   &headBranch,
		RunAttempt:   &attempt,
		Status:       "queued",
		CreatedAt:    j.CreatedAt,
		StartedAt:    j.StartedAt,
		Labels:       j.TagList,
		HTMLURL:      j.WebURL,
		Repo:         projectPath,
		RunURL:       &j.WebURL,
	}
}
