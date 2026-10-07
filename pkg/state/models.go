package state

import "time"

// StepInfo describes one step (stage) of a workflow job.
type StepInfo struct {
	Number     int     `json:"number"`
	Name       string  `json:"name"`
	Status     string  `json:"status"`
	Conclusion *string `json:"conclusion,omitempty"`
}

// CompletedJob describes a finished (successful, failed, cancelled or timed-out)
// GitHub Actions workflow job together with a human-readable failure diagnosis.
type CompletedJob struct {
	ID            int64      `json:"id"`
	RunID         int64      `json:"run_id"`
	Name          string     `json:"name"`
	WorkflowName  *string    `json:"workflow_name,omitempty"`
	HeadBranch    *string    `json:"head_branch,omitempty"`
	RunAttempt    *int       `json:"run_attempt,omitempty"`
	Conclusion    string     `json:"conclusion"`
	StartedAt     *string    `json:"started_at,omitempty"`
	CompletedAt   *string    `json:"completed_at,omitempty"`
	DurationSec   *int       `json:"duration_sec,omitempty"`
	Labels        []string   `json:"labels"`
	HTMLURL       string     `json:"html_url"`
	RunURL        *string    `json:"run_url,omitempty"`
	Repo          string     `json:"repo"`
	RunnerName    *string    `json:"runner_name,omitempty"`
	FailedStep    *string    `json:"failed_step,omitempty"`
	FailureReason *string    `json:"failure_reason,omitempty"`
	Messages      []string   `json:"messages,omitempty"`
	HasRunnerLog  bool       `json:"has_runner_log"`
	Steps         []StepInfo `json:"steps,omitempty"`
}

// RunnerInfo contains metadata about an ephemeral runner instance.
type RunnerInfo struct {
	ID             string     `json:"id"`
	Name           string     `json:"name"`
	Status         string     `json:"status"`
	State          string     `json:"state"`
	TargetRepo     string     `json:"target_repo"`
	TargetArch     string     `json:"target_arch"`
	Backend        string     `json:"backend"`
	CreatedAt      *string    `json:"created_at,omitempty"`
	JobID          *int64     `json:"job_id,omitempty"`
	RunID          *int64     `json:"run_id,omitempty"`
	JobURL         *string    `json:"job_url,omitempty"`
	RunURL         *string    `json:"run_url,omitempty"`
	JobName        *string    `json:"job_name,omitempty"`
	WorkflowName   *string    `json:"workflow_name,omitempty"`
	StagesDone     *int       `json:"stages_done,omitempty"`
	StagesTotal    *int       `json:"stages_total,omitempty"`
	StepsCompleted *int       `json:"steps_completed,omitempty"`
	StepsTotal     *int       `json:"steps_total,omitempty"`
	CurrentStep    *string    `json:"current_step,omitempty"`
	ProgressPct    *int       `json:"progress_pct,omitempty"`
	Steps          []StepInfo `json:"steps,omitempty"`
}

// QueuedJob describes a queued or active GitHub Actions workflow job.
type QueuedJob struct {
	ID             int64      `json:"id"`
	RunID          int64      `json:"run_id"`
	Name           string     `json:"name"`
	WorkflowName   *string    `json:"workflow_name,omitempty"`
	HeadBranch     *string    `json:"head_branch,omitempty"`
	RunAttempt     *int       `json:"run_attempt,omitempty"`
	Status         string     `json:"status"`
	CreatedAt      *string    `json:"created_at,omitempty"`
	StartedAt      *string    `json:"started_at,omitempty"`
	Labels         []string   `json:"labels"`
	HTMLURL        string     `json:"html_url"`
	Repo           string     `json:"repo"`
	QueuePosition  *int       `json:"queue_position,omitempty"`
	WaitingReason  *string    `json:"waiting_reason,omitempty"`
	RunURL         *string    `json:"run_url,omitempty"`
	RunnerName     *string    `json:"runner_name,omitempty"`
	StagesDone     *int       `json:"stages_done,omitempty"`
	StagesTotal    *int       `json:"stages_total,omitempty"`
	StepsCompleted *int       `json:"steps_completed,omitempty"`
	StepsTotal     *int       `json:"steps_total,omitempty"`
	CurrentStep    *string    `json:"current_step,omitempty"`
	ProgressPct    *int       `json:"progress_pct,omitempty"`
	Steps          []StepInfo `json:"steps,omitempty"`
}

// ActionsBilling contains GitHub Actions runner minutes statistics.
type ActionsBilling struct {
	IncludedMinutes      int `json:"included_minutes,omitempty"`
	TotalMinutesUsed     int `json:"total_minutes_used,omitempty"`
	TotalPaidMinutesUsed int `json:"total_paid_minutes_used,omitempty"`
}

// FleetState represents the live status snapshot returned by /api/fleet and /api/status.
type FleetState struct {
	Runners            []RunnerInfo    `json:"runners"`
	QueuedJobs         []QueuedJob     `json:"queued_jobs"`
	CompletedJobs      []CompletedJob  `json:"completed_jobs"`
	BusyRunners        int             `json:"busy_runners"`
	MaxRunners         int             `json:"max_runners"`
	FreeSlots          int             `json:"free_slots"`
	RepoPriority       []string        `json:"repo_priority"`
	PausedRepos        []string        `json:"paused_repos"`
	RateLimitRemaining *int            `json:"rate_limit_remaining,omitempty"`
	RateLimitLimit     *int            `json:"rate_limit_limit,omitempty"`
	ActionsBilling     *ActionsBilling `json:"actions_billing,omitempty"`
	AutoscalerStatus   string          `json:"autoscaler_status"`
	Version            string          `json:"version"`
}

// LogEntry represents a single timestamped log line.
type LogEntry struct {
	Timestamp string `json:"timestamp"`
	Message   string `json:"message"`
}

func newTimestamp() string {
	return time.Now().UTC().Format(time.RFC3339)
}
