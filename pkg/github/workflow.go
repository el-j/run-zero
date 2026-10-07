package github

import (
	"context"
	"fmt"
	"net/http"
)

// TriggerWorkflowAction executes a cancel, rerun, or rerun-failed action on a workflow run.
func (c *Client) TriggerWorkflowAction(ctx context.Context, repo string, runID int64, action string) error {
	var endpoint string
	switch action {
	case "cancel":
		endpoint = fmt.Sprintf("/repos/%s/actions/runs/%d/cancel", repo, runID)
	case "rerun":
		endpoint = fmt.Sprintf("/repos/%s/actions/runs/%d/rerun", repo, runID)
	case "rerun-failed":
		endpoint = fmt.Sprintf("/repos/%s/actions/runs/%d/rerun-failed-jobs", repo, runID)
	default:
		return fmt.Errorf("unsupported workflow action: %s", action)
	}

	resp, err := c.DoRequest(ctx, http.MethodPost, endpoint, nil, nil)
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusAccepted && resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("github api unexpected status (%d) for %s on run %d", resp.StatusCode, action, runID)
	}

	return nil
}

// RerunJob re-runs one specific job (and its dependent jobs) of a finished workflow run.
func (c *Client) RerunJob(ctx context.Context, repo string, jobID int64) error {
	endpoint := fmt.Sprintf("/repos/%s/actions/jobs/%d/rerun", repo, jobID)
	resp, err := c.DoRequest(ctx, http.MethodPost, endpoint, nil, nil)
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("github api unexpected status (%d) for rerun-job on job %d", resp.StatusCode, jobID)
	}
	return nil
}
