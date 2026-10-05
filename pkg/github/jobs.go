package github

import (
	"context"
	"fmt"

	"github.com/el-j/run-zero/pkg/state"
)

type workflowRunsResponse struct {
	TotalCount   int           `json:"total_count"`
	WorkflowRuns []workflowRun `json:"workflow_runs"`
}

type workflowRun struct {
	ID           int64   `json:"id"`
	Name         string  `json:"name"`
	HeadBranch   string  `json:"head_branch"`
	Status       string  `json:"status"`
	HTMLURL      string  `json:"html_url"`
	RunAttempt   int     `json:"run_attempt"`
	CreatedAt    string  `json:"created_at"`
	WorkflowName *string `json:"workflow_name,omitempty"`
}

type workflowJobsResponse struct {
	TotalCount int           `json:"total_count"`
	Jobs       []workflowJob `json:"jobs"`
}

type workflowJob struct {
	ID        int64    `json:"id"`
	RunID     int64    `json:"run_id"`
	Name      string   `json:"name"`
	Status    string   `json:"status"`
	CreatedAt string   `json:"created_at"`
	StartedAt *string  `json:"started_at,omitempty"`
	HTMLURL   string   `json:"html_url"`
	Labels    []string `json:"labels"`
}

// ListQueuedJobs finds pending workflow jobs waiting for runner allocation in repo.
func (c *Client) ListQueuedJobs(ctx context.Context, repo string) ([]state.QueuedJob, error) {
	endpoint := fmt.Sprintf("/repos/%s/actions/runs?status=queued&per_page=30", repo)
	var runsResp workflowRunsResponse
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &runsResp); err != nil {
		return nil, err
	}

	var queuedJobs []state.QueuedJob
	for _, run := range runsResp.WorkflowRuns {
		jobsEndpoint := fmt.Sprintf("/repos/%s/actions/runs/%d/jobs?per_page=50", repo, run.ID)
		var jobsResp workflowJobsResponse
		if _, err := c.DoRequest(ctx, "GET", jobsEndpoint, nil, &jobsResp); err != nil {
			continue
		}

		for _, j := range jobsResp.Jobs {
			if j.Status == "queued" {
				cAt := j.CreatedAt
				hb := run.HeadBranch
				att := run.RunAttempt
				queuedJobs = append(queuedJobs, state.QueuedJob{
					ID:         j.ID,
					RunID:      run.ID,
					Name:       j.Name,
					HeadBranch: &hb,
					RunAttempt: &att,
					Status:     j.Status,
					CreatedAt:  &cAt,
					StartedAt:  j.StartedAt,
					Labels:     j.Labels,
					HTMLURL:    j.HTMLURL,
					Repo:       repo,
				})
			}
		}
	}

	return queuedJobs, nil
}
