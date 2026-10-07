package github

import (
	"context"
	"fmt"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

const (
	historyRunsPerRepo   = 20
	maxAnnotationMsgs    = 5
	maxAnnotationMsgSize = 400
)

type annotation struct {
	Path            string `json:"path"`
	Title           string `json:"title"`
	Message         string `json:"message"`
	AnnotationLevel string `json:"annotation_level"`
}

// HistoryFetcher collects finished workflow jobs and diagnoses why they failed.
// Finished runs are immutable, so results are cached per (repo, run, attempt) to
// keep GitHub API usage low across repeated refreshes.
type HistoryFetcher struct {
	client *Client
	mu     sync.Mutex
	cache  map[string][]state.CompletedJob
}

// NewHistoryFetcher creates a history fetcher backed by client.
func NewHistoryFetcher(client *Client) *HistoryFetcher {
	return &HistoryFetcher{client: client, cache: make(map[string][]state.CompletedJob)}
}

// Fetch returns recently finished self-hosted jobs of repo, newest first.
func (h *HistoryFetcher) Fetch(ctx context.Context, repo string) ([]state.CompletedJob, error) {
	endpoint := fmt.Sprintf("/repos/%s/actions/runs?status=completed&per_page=%d", repo, historyRunsPerRepo)
	var runsResp workflowRunsResponse
	if _, err := h.client.DoRequest(ctx, "GET", endpoint, nil, &runsResp); err != nil {
		return nil, err
	}

	var out []state.CompletedJob
	live := make(map[string]bool)
	for _, run := range runsResp.WorkflowRuns {
		if run.Conclusion == "" || run.Conclusion == "skipped" || run.Conclusion == "neutral" {
			continue
		}
		key := fmt.Sprintf("%s#%d#%d#%s", repo, run.ID, run.RunAttempt, run.UpdatedAt)
		live[key] = true

		h.mu.Lock()
		cached, ok := h.cache[key]
		h.mu.Unlock()
		if ok {
			out = append(out, cached...)
			continue
		}

		jobs, err := h.runJobs(ctx, repo, run)
		if err != nil {
			continue // transient: retry on the next refresh
		}
		h.mu.Lock()
		h.cache[key] = jobs
		h.mu.Unlock()
		out = append(out, jobs...)
	}

	h.evict(repo, live)
	sortNewestFirst(out)
	return out, nil
}

// evict drops cache entries of repo that are no longer part of the latest run window.
func (h *HistoryFetcher) evict(repo string, live map[string]bool) {
	prefix := repo + "#"
	h.mu.Lock()
	defer h.mu.Unlock()
	for k := range h.cache {
		if strings.HasPrefix(k, prefix) && !live[k] {
			delete(h.cache, k)
		}
	}
}

func (h *HistoryFetcher) runJobs(ctx context.Context, repo string, run workflowRun) ([]state.CompletedJob, error) {
	var jobsResp workflowJobsResponse
	endpoint := fmt.Sprintf("/repos/%s/actions/runs/%d/jobs?filter=latest&per_page=100", repo, run.ID)
	if _, err := h.client.DoRequest(ctx, "GET", endpoint, nil, &jobsResp); err != nil {
		return nil, err
	}

	var jobs []state.CompletedJob
	for _, j := range jobsResp.Jobs {
		if j.Status != "completed" || j.Conclusion == "" || j.Conclusion == "skipped" {
			continue
		}
		if !isSelfHosted(j.Labels) {
			continue
		}
		jobs = append(jobs, h.buildJob(ctx, repo, run, j))
	}
	return jobs, nil
}

func (h *HistoryFetcher) buildJob(ctx context.Context, repo string, run workflowRun, j workflowJob) state.CompletedJob {
	wName := run.Name
	if run.WorkflowName != nil {
		wName = *run.WorkflowName
	}
	hb := run.HeadBranch
	att := run.RunAttempt
	runURL := fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, run.ID)
	jobURL := j.HTMLURL
	if jobURL == "" {
		jobURL = fmt.Sprintf("%s/job/%d", runURL, j.ID)
	}

	steps := make([]state.StepInfo, 0, len(j.Steps))
	for _, s := range j.Steps {
		steps = append(steps, state.StepInfo{Number: s.Number, Name: s.Name, Status: s.Status, Conclusion: s.Conclusion})
	}

	job := state.CompletedJob{
		ID:           j.ID,
		RunID:        run.ID,
		Name:         j.Name,
		WorkflowName: &wName,
		HeadBranch:   &hb,
		RunAttempt:   &att,
		Conclusion:   j.Conclusion,
		StartedAt:    j.StartedAt,
		CompletedAt:  j.CompletedAt,
		DurationSec:  durationSeconds(j.StartedAt, j.CompletedAt),
		Labels:       j.Labels,
		HTMLURL:      jobURL,
		RunURL:       &runURL,
		Repo:         repo,
		RunnerName:   j.RunnerName,
		Steps:        steps,
	}

	if j.Conclusion != "success" {
		failedStep, reason := Diagnose(j)
		job.FailedStep = failedStep
		job.FailureReason = &reason
		if j.Conclusion == "failure" || j.Conclusion == "timed_out" {
			job.Messages = h.annotationMessages(ctx, repo, j.ID)
		}
	}
	return job
}

func (h *HistoryFetcher) annotationMessages(ctx context.Context, repo string, jobID int64) []string {
	var annos []annotation
	endpoint := fmt.Sprintf("/repos/%s/check-runs/%d/annotations?per_page=30", repo, jobID)
	if _, err := h.client.DoRequest(ctx, "GET", endpoint, nil, &annos); err != nil {
		return nil
	}

	seen := make(map[string]bool)
	var failures, others []string
	for _, a := range annos {
		msg := strings.TrimSpace(a.Message)
		if msg == "" || seen[msg] {
			continue
		}
		seen[msg] = true
		if len(msg) > maxAnnotationMsgSize {
			msg = msg[:maxAnnotationMsgSize] + "…"
		}
		if a.AnnotationLevel == "failure" {
			failures = append(failures, msg)
		} else {
			others = append(others, msg)
		}
	}
	msgs := append(failures, others...)
	if len(msgs) > maxAnnotationMsgs {
		msgs = msgs[:maxAnnotationMsgs]
	}
	return msgs
}

// Diagnose turns a finished job's conclusion and step results into a short,
// human-readable explanation. It returns the offending step name when known.
func Diagnose(j workflowJob) (failedStep *string, reason string) {
	var culprit *workflowStep
	wantConclusion := j.Conclusion
	if wantConclusion == "timed_out" {
		wantConclusion = "cancelled" // GitHub marks the running step as cancelled on timeout
	}
	for i := range j.Steps {
		c := ""
		if j.Steps[i].Conclusion != nil {
			c = *j.Steps[i].Conclusion
		}
		if c == "failure" || (c == wantConclusion && c != "success") {
			culprit = &j.Steps[i]
			break
		}
	}

	ranAnyStep := false
	for _, s := range j.Steps {
		if s.Status != "queued" && s.Status != "pending" {
			ranAnyStep = true
			break
		}
	}

	if culprit != nil {
		name := culprit.Name
		failedStep = &name
	}

	switch j.Conclusion {
	case "failure":
		switch {
		case culprit != nil:
			reason = fmt.Sprintf("Step %d “%s” failed.", culprit.Number, culprit.Name)
		case !ranAnyStep:
			reason = "Job failed before any step ran — likely a runner or setup problem (runner crashed, image/registration error). Check the local runner log."
		default:
			reason = "Job failed, but GitHub reported no failing step."
		}
	case "timed_out":
		if culprit != nil {
			reason = fmt.Sprintf("Timed out while running step %d “%s”.", culprit.Number, culprit.Name)
		} else {
			reason = "Job exceeded its time limit."
		}
	case "cancelled":
		switch {
		case culprit != nil:
			reason = fmt.Sprintf("Cancelled while running step %d “%s”.", culprit.Number, culprit.Name)
		case !ranAnyStep:
			reason = "Cancelled before any step started (e.g. runner was removed or run cancelled while queued)."
		default:
			reason = "Cancelled."
		}
	case "startup_failure":
		reason = "Workflow failed to start (invalid workflow file or missing permissions)."
	case "action_required":
		reason = "Waiting for manual approval."
	default:
		reason = fmt.Sprintf("Finished with conclusion “%s”.", j.Conclusion)
	}
	return failedStep, reason
}

func isSelfHosted(labels []string) bool {
	for _, l := range labels {
		if strings.EqualFold(l, "self-hosted") {
			return true
		}
	}
	return false
}

func durationSeconds(start, end *string) *int {
	if start == nil || end == nil {
		return nil
	}
	s, err1 := time.Parse(time.RFC3339, *start)
	e, err2 := time.Parse(time.RFC3339, *end)
	if err1 != nil || err2 != nil || e.Before(s) {
		return nil
	}
	d := int(e.Sub(s).Seconds())
	return &d
}

// SortCompletedJobs orders jobs newest-finished first.
func SortCompletedJobs(jobs []state.CompletedJob) { sortNewestFirst(jobs) }

func sortNewestFirst(jobs []state.CompletedJob) {
	sort.SliceStable(jobs, func(a, b int) bool {
		ta, tb := "", ""
		if jobs[a].CompletedAt != nil {
			ta = *jobs[a].CompletedAt
		}
		if jobs[b].CompletedAt != nil {
			tb = *jobs[b].CompletedAt
		}
		return ta > tb // RFC3339 UTC timestamps sort lexicographically
	})
}
