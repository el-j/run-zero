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

type workflowStep struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	Number int    `json:"number"`
}

type workflowJob struct {
	ID         int64          `json:"id"`
	RunID      int64          `json:"run_id"`
	Name       string         `json:"name"`
	Status     string         `json:"status"`
	CreatedAt  string         `json:"created_at"`
	StartedAt  *string        `json:"started_at,omitempty"`
	HTMLURL    string         `json:"html_url"`
	Labels     []string       `json:"labels"`
	RunnerName *string        `json:"runner_name,omitempty"`
	Steps      []workflowStep `json:"steps,omitempty"`
}

// ListActiveJobs finds queued and in-progress workflow jobs in repo, calculating stage & step progress.
func (c *Client) ListActiveJobs(ctx context.Context, repo string) ([]state.QueuedJob, error) {
	seenRuns := make(map[int64]bool)
	var allRuns []workflowRun

	endpoint := fmt.Sprintf("/repos/%s/actions/runs?status=queued&per_page=30", repo)
	var runsResp workflowRunsResponse
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &runsResp); err != nil {
		return nil, err
	}
	for _, r := range runsResp.WorkflowRuns {
		seenRuns[r.ID] = true
		allRuns = append(allRuns, r)
	}

	// Also check in-progress runs opportunistically
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

		runURL := fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, run.ID)

		for _, j := range jobsResp.Jobs {
			if j.Status == "queued" || j.Status == "in_progress" {
				cAt := j.CreatedAt
				hb := run.HeadBranch
				att := run.RunAttempt
				wName := run.Name
				if run.WorkflowName != nil {
					wName = *run.WorkflowName
				}

				stepsTotal := len(j.Steps)
				stepsCompleted := 0
				var currentStep *string
				for _, st := range j.Steps {
					if st.Status == "completed" {
						stepsCompleted++
					} else if st.Status == "in_progress" && currentStep == nil {
						sName := st.Name
						currentStep = &sName
					}
				}
				if currentStep == nil && stepsTotal > 0 && stepsCompleted < stepsTotal {
					sName := j.Steps[stepsCompleted].Name
					currentStep = &sName
				}
				if currentStep == nil && j.Status == "in_progress" {
					defaultStage := "Executing workflow job..."
					currentStep = &defaultStage
				}

				var progressPct *int
				if stepsTotal > 0 {
					pct := (stepsCompleted * 100) / stepsTotal
					progressPct = &pct
				} else if stagesTotal > 0 {
					pct := (stagesDone * 100) / stagesTotal
					progressPct = &pct
				}

				jobURL := j.HTMLURL
				if jobURL == "" {
					jobURL = fmt.Sprintf("https://github.com/%s/actions/runs/%d/job/%d", repo, run.ID, j.ID)
				}
				var steps []state.StepInfo
				for _, st := range j.Steps {
					steps = append(steps, state.StepInfo{Number: st.Number, Name: st.Name, Status: st.Status})
				}

				activeJobs = append(activeJobs, state.QueuedJob{
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
				})
			}
		}
	}

	return activeJobs, nil
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
