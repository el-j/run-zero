package github

import (
	"context"
	"encoding/base64"
	"fmt"
	"net/url"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

type workflowRunsResponse struct {
	TotalCount   int           `json:"total_count"`
	WorkflowRuns []WorkflowRun `json:"workflow_runs"`
}

// WorkflowRun represents a GitHub Actions workflow run.
type WorkflowRun struct {
	// ID Unique workflow run or job identifier.
	ID int64 `json:"id"`
	// Name Workflow or job name.
	Name string `json:"name"`
	// HeadBranch Branch associated with the workflow run.
	HeadBranch string `json:"head_branch"`
	// Status Current workflow run or job status.
	Status string `json:"status"`
	// Conclusion Final workflow run or job result.
	Conclusion string `json:"conclusion"`
	// HTMLURL Browser URL for the workflow object.
	HTMLURL string `json:"html_url"`
	// RunAttempt Attempt number for this workflow run.
	RunAttempt int `json:"run_attempt"`
	// CreatedAt RFC3339 timestamp when the run or job was created.
	CreatedAt string `json:"created_at"`
	// UpdatedAt RFC3339 timestamp when the workflow run was last updated.
	UpdatedAt string `json:"updated_at"`
	// WorkflowName Display name of the workflow.
	WorkflowName *string `json:"workflow_name,omitempty"`
	// Path Repository path of the workflow file, e.g. .github/workflows/ci.yml.
	Path string `json:"path"`
	// HeadSHA Commit the run executes.
	HeadSHA string `json:"head_sha"`
}

type workflowRun = WorkflowRun

type workflowJobsResponse struct {
	TotalCount int           `json:"total_count"`
	Jobs       []WorkflowJob `json:"jobs"`
}

type workflowStep struct {
	Name       string  `json:"name"`
	Status     string  `json:"status"`
	Conclusion *string `json:"conclusion,omitempty"`
	Number     int     `json:"number"`
}

// WorkflowJob represents a single job within a GitHub Actions workflow run.
type WorkflowJob struct {
	// ID Unique workflow run or job identifier.
	ID int64 `json:"id"`
	// RunID Identifier of the workflow run containing the job.
	RunID int64 `json:"run_id"`
	// Name Workflow or job name.
	Name string `json:"name"`
	// Status Current workflow run or job status.
	Status string `json:"status"`
	// Conclusion Final workflow run or job result.
	Conclusion string `json:"conclusion"`
	// CreatedAt RFC3339 timestamp when the run or job was created.
	CreatedAt string `json:"created_at"`
	// StartedAt RFC3339 timestamp when the job started.
	StartedAt *string `json:"started_at,omitempty"`
	// CompletedAt RFC3339 timestamp when the job completed.
	CompletedAt *string `json:"completed_at,omitempty"`
	// HTMLURL Browser URL for the workflow object.
	HTMLURL string `json:"html_url"`
	// Labels Runner labels required by the job.
	Labels []string `json:"labels"`
	// RunnerName Name of the runner executing the job.
	RunnerName *string `json:"runner_name,omitempty"`
	// Steps Workflow steps included in the job.
	Steps []workflowStep `json:"steps,omitempty"`
}

type workflowJob = WorkflowJob

// GetWorkflowRun retrieves a single workflow run by ID.
func (c *Client) GetWorkflowRun(ctx context.Context, repo string, runID int64) (*WorkflowRun, error) {
	endpoint := fmt.Sprintf("/repos/%s/actions/runs/%d", repo, runID)
	var run WorkflowRun
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &run); err != nil {
		return nil, err
	}
	return &run, nil
}

// GetWorkflowJob retrieves a single workflow job by ID.
func (c *Client) GetWorkflowJob(ctx context.Context, repo string, jobID int64) (*WorkflowJob, error) {
	endpoint := fmt.Sprintf("/repos/%s/actions/jobs/%d", repo, jobID)
	var job WorkflowJob
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &job); err != nil {
		return nil, err
	}
	return &job, nil
}

// ListActiveJobs finds queued and in-progress workflow jobs in repo, calculating stage & step progress.
func (c *Client) ListActiveJobs(ctx context.Context, repo string) ([]state.QueuedJob, error) {
	allRuns, err := c.listActiveRuns(ctx, repo)
	if err != nil {
		return nil, err
	}

	var activeJobs []state.QueuedJob
	for _, run := range allRuns {
		jobsEndpoint := fmt.Sprintf("/repos/%s/actions/runs/%d/jobs?per_page=50", repo, run.ID)
		var jobsResp workflowJobsResponse
		if _, err := c.DoRequest(ctx, "GET", jobsEndpoint, nil, &jobsResp); err != nil {
			continue
		}

		stagesTotal := len(jobsResp.Jobs)
		stagesDone := 0
		for _, j := range jobsResp.Jobs {
			if j.Status == "completed" {
				stagesDone++
			}
		}

		for _, j := range jobsResp.Jobs {
			if j.Status == "queued" || j.Status == "in_progress" {
				activeJobs = append(activeJobs, activeJob(repo, run, j, stagesDone, stagesTotal))
			}
		}
	}

	return activeJobs, nil
}

// listActiveRuns returns the repo's queued runs, plus its in-progress runs when
// that (opportunistic) lookup succeeds, without duplicates.
func (c *Client) listActiveRuns(ctx context.Context, repo string) ([]workflowRun, error) {
	endpoint := fmt.Sprintf("/repos/%s/actions/runs?status=queued&per_page=30", repo)
	var runsResp workflowRunsResponse
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &runsResp); err != nil {
		return nil, err
	}
	allRuns := runsResp.WorkflowRuns
	seenRuns := make(map[int64]bool)
	for _, r := range allRuns {
		seenRuns[r.ID] = true
	}

	inProgEndpoint := fmt.Sprintf("/repos/%s/actions/runs?status=in_progress&per_page=30", repo)
	var inProgResp workflowRunsResponse
	if _, err := c.DoRequest(ctx, "GET", inProgEndpoint, nil, &inProgResp); err == nil {
		for _, r := range inProgResp.WorkflowRuns {
			if !seenRuns[r.ID] {
				seenRuns[r.ID] = true
				allRuns = append(allRuns, r)
			}
		}
	}
	return allRuns, nil
}

// activeJob builds the dashboard view of one queued or in-progress job.
func activeJob(repo string, run workflowRun, j workflowJob, stagesDone, stagesTotal int) state.QueuedJob {
	cAt := j.CreatedAt
	hb := run.HeadBranch
	att := run.RunAttempt
	wName := run.Name
	if run.WorkflowName != nil {
		wName = *run.WorkflowName
	}
	runURL := fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, run.ID)
	jobURL := j.HTMLURL
	if jobURL == "" {
		jobURL = fmt.Sprintf("https://github.com/%s/actions/runs/%d/job/%d", repo, run.ID, j.ID)
	}
	var steps []state.StepInfo
	for _, st := range j.Steps {
		steps = append(steps, state.StepInfo{Number: st.Number, Name: st.Name, Status: st.Status})
	}

	stepsTotal := len(j.Steps)
	stepsCompleted, currentStep := stepProgress(j)
	var progressPct *int
	if stepsTotal > 0 {
		pct := (stepsCompleted * 100) / stepsTotal
		progressPct = &pct
	} else {
		// j belongs to its run, so stagesTotal is at least 1.
		pct := (stagesDone * 100) / stagesTotal
		progressPct = &pct
	}

	return state.QueuedJob{
		WorkflowPath:   run.Path,
		HeadSHA:        run.HeadSHA,
		Steps:          steps,
		ID:             j.ID,
		RunID:          run.ID,
		Name:           j.Name,
		WorkflowName:   &wName,
		HeadBranch:     &hb,
		RunAttempt:     &att,
		Status:         j.Status,
		CreatedAt:      &cAt,
		StartedAt:      j.StartedAt,
		Labels:         j.Labels,
		HTMLURL:        jobURL,
		Repo:           repo,
		RunURL:         &runURL,
		RunnerName:     j.RunnerName,
		StagesDone:     &stagesDone,
		StagesTotal:    &stagesTotal,
		StepsCompleted: &stepsCompleted,
		StepsTotal:     &stepsTotal,
		CurrentStep:    currentStep,
		ProgressPct:    progressPct,
	}
}

// stepProgress counts a job's completed steps and names the step it is on: the
// first in-progress step, else the first unfinished one, else a generic label
// while the job runs.
func stepProgress(j workflowJob) (int, *string) {
	completed := 0
	var current *string
	for _, st := range j.Steps {
		if st.Status == "completed" {
			completed++
		} else if st.Status == "in_progress" && current == nil {
			sName := st.Name
			current = &sName
		}
	}
	if current == nil && completed < len(j.Steps) {
		sName := j.Steps[completed].Name
		current = &sName
	}
	if current == nil && j.Status == "in_progress" {
		defaultStage := "Executing workflow job..."
		current = &defaultStage
	}
	return completed, current
}

// ListQueuedJobs finds pending workflow jobs waiting for runner allocation in repo.
func (c *Client) ListQueuedJobs(ctx context.Context, repo string) ([]state.QueuedJob, error) {
	all, err := c.ListActiveJobs(ctx, repo)
	if err != nil {
		return nil, err
	}
	var queued []state.QueuedJob
	for _, j := range all {
		if j.Status == "queued" {
			queued = append(queued, j)
		}
	}
	return queued, nil
}

// GetWorkflowFile returns the text of the workflow file at path in repo, as of
// commit ref.
func (c *Client) GetWorkflowFile(ctx context.Context, repo, path, ref string) (string, error) {
	endpoint := fmt.Sprintf("/repos/%s/contents/%s?ref=%s", repo, path, url.QueryEscape(ref))
	var body struct {
		Content  string `json:"content"`
		Encoding string `json:"encoding"`
	}
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &body); err != nil {
		return "", err
	}
	if body.Encoding != "base64" {
		return "", fmt.Errorf("unexpected workflow file encoding %q", body.Encoding)
	}
	data, err := base64.StdEncoding.DecodeString(strings.ReplaceAll(body.Content, "\n", ""))
	if err != nil {
		return "", fmt.Errorf("failed decoding workflow file: %w", err)
	}
	return string(data), nil
}
