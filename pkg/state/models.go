package state

import "time"

// StepInfo describes one step (stage) of a workflow job.
type StepInfo struct {
	// Number Step number within the job.
	Number int `json:"number"`
	// Name Human-readable step or job name.
	Name string `json:"name"`
	// Status Runner or job status.
	Status string `json:"status"`
	// Conclusion Final step conclusion, when available.
	Conclusion *string `json:"conclusion,omitempty"`
}

// CompletedJob describes a finished (successful, failed, cancelled or timed-out)
// GitHub Actions workflow job together with a human-readable failure diagnosis.
type CompletedJob struct {
	// ID Unique job or runner identifier.
	ID int64 `json:"id"`
	// RunID Identifier of the workflow run or pipeline.
	RunID int64 `json:"run_id"`
	// Name Human-readable step or job name.
	Name string `json:"name"`
	// WorkflowName Display name of the workflow.
	WorkflowName *string `json:"workflow_name,omitempty"`
	// HeadBranch Source branch for the run.
	HeadBranch *string `json:"head_branch,omitempty"`
	// RunAttempt Attempt number for the run.
	RunAttempt *int `json:"run_attempt,omitempty"`
	// Conclusion Final step conclusion, when available.
	Conclusion string `json:"conclusion"`
	// StartedAt RFC3339 time when execution started.
	StartedAt *string `json:"started_at,omitempty"`
	// CompletedAt RFC3339 time when execution finished.
	CompletedAt *string `json:"completed_at,omitempty"`
	// DurationSec Elapsed execution time in seconds.
	DurationSec *int `json:"duration_sec,omitempty"`
	// Labels Runner labels or tags reported by the provider.
	Labels []string `json:"labels"`
	// HTMLURL Browser URL for the job.
	HTMLURL string `json:"html_url"`
	// RunURL Browser URL for the workflow run.
	RunURL *string `json:"run_url,omitempty"`
	// Repo Repository or project associated with the job.
	Repo string `json:"repo"`
	// RunnerName Name of the runner that handled the job.
	RunnerName *string `json:"runner_name,omitempty"`
	// FailedStep Name of the step diagnosed as failing.
	FailedStep *string `json:"failed_step,omitempty"`
	// FailureReason Human-readable diagnosis for the job result.
	FailureReason *string `json:"failure_reason,omitempty"`
	// Messages Distinct annotation messages associated with the failure.
	Messages []string `json:"messages,omitempty"`
	// HasRunnerLog Whether a retained runner log is available.
	HasRunnerLog bool `json:"has_runner_log"`
	// Steps Steps reported for the job.
	Steps []StepInfo `json:"steps,omitempty"`
}

// RunnerInfo contains metadata about an ephemeral runner instance.
type RunnerInfo struct {
	// ID Unique job or runner identifier.
	ID string `json:"id"`
	// Name Human-readable step or job name.
	Name string `json:"name"`
	// Status Runner or job status.
	Status string `json:"status"`
	// State RunZero lifecycle state.
	State string `json:"state"`
	// TargetRepo Repository or provider scope targeted by the runner.
	TargetRepo string `json:"target_repo"`
	// TargetArch CPU architecture requested for the runner.
	TargetArch string `json:"target_arch"`
	// Backend Runtime backend hosting the runner.
	Backend string `json:"backend"`
	// CreatedAt RFC3339 time when the runner or job was created.
	CreatedAt *string `json:"created_at,omitempty"`
	// JobID Identifier of the assigned job.
	JobID *int64 `json:"job_id,omitempty"`
	// RunID Identifier of the workflow run or pipeline.
	RunID *int64 `json:"run_id,omitempty"`
	// JobURL Browser URL for the assigned job.
	JobURL *string `json:"job_url,omitempty"`
	// RunURL Browser URL for the workflow run.
	RunURL *string `json:"run_url,omitempty"`
	// JobName Name of the assigned job.
	JobName *string `json:"job_name,omitempty"`
	// WorkflowName Display name of the workflow.
	WorkflowName *string `json:"workflow_name,omitempty"`
	// StagesDone Number of completed workflow stages.
	StagesDone *int `json:"stages_done,omitempty"`
	// StagesTotal Total number of workflow stages.
	StagesTotal *int `json:"stages_total,omitempty"`
	// StepsCompleted Number of completed job steps.
	StepsCompleted *int `json:"steps_completed,omitempty"`
	// StepsTotal Total number of job steps.
	StepsTotal *int `json:"steps_total,omitempty"`
	// CurrentStep Name of the currently executing or next step.
	CurrentStep *string `json:"current_step,omitempty"`
	// ProgressPct Approximate completion percentage.
	ProgressPct *int `json:"progress_pct,omitempty"`
	// Steps Steps reported for the job.
	Steps []StepInfo `json:"steps,omitempty"`
	// Provider Provider family identifier.
	Provider *string `json:"provider,omitempty"`
	// ProviderInst Provider instance host.
	ProviderInst *string `json:"provider_instance,omitempty"`
	// Origin Runner origin classification.
	Origin *string `json:"origin,omitempty"`
	// IsCloud Whether the runner is provider-hosted.
	IsCloud bool `json:"is_cloud,omitempty"`
	// Tags Provider labels associated with the runner.
	Tags []string `json:"tags,omitempty"`
}

// QueuedJob describes a queued or active GitHub Actions workflow job.
type QueuedJob struct {
	// ID Unique job or runner identifier.
	ID int64 `json:"id"`
	// RunID Identifier of the workflow run or pipeline.
	RunID int64 `json:"run_id"`
	// Name Human-readable step or job name.
	Name string `json:"name"`
	// WorkflowName Display name of the workflow.
	WorkflowName *string `json:"workflow_name,omitempty"`
	// HeadBranch Source branch for the run.
	HeadBranch *string `json:"head_branch,omitempty"`
	// RunAttempt Attempt number for the run.
	RunAttempt *int `json:"run_attempt,omitempty"`
	// Status Runner or job status.
	Status string `json:"status"`
	// CreatedAt RFC3339 time when the runner or job was created.
	CreatedAt *string `json:"created_at,omitempty"`
	// StartedAt RFC3339 time when execution started.
	StartedAt *string `json:"started_at,omitempty"`
	// Labels Runner labels or tags reported by the provider.
	Labels []string `json:"labels"`
	// HTMLURL Browser URL for the job.
	HTMLURL string `json:"html_url"`
	// Repo Repository or project associated with the job.
	Repo string `json:"repo"`
	// QueuePosition One-based position among active queued jobs.
	QueuePosition *int `json:"queue_position,omitempty"`
	// WaitingReason Explanation for why the job is waiting.
	WaitingReason *string `json:"waiting_reason,omitempty"`
	// RunURL Browser URL for the workflow run.
	RunURL *string `json:"run_url,omitempty"`
	// RunnerName Name of the runner that handled the job.
	RunnerName *string `json:"runner_name,omitempty"`
	// StagesDone Number of completed workflow stages.
	StagesDone *int `json:"stages_done,omitempty"`
	// StagesTotal Total number of workflow stages.
	StagesTotal *int `json:"stages_total,omitempty"`
	// StepsCompleted Number of completed job steps.
	StepsCompleted *int `json:"steps_completed,omitempty"`
	// StepsTotal Total number of job steps.
	StepsTotal *int `json:"steps_total,omitempty"`
	// CurrentStep Name of the currently executing or next step.
	CurrentStep *string `json:"current_step,omitempty"`
	// ProgressPct Approximate completion percentage.
	ProgressPct *int `json:"progress_pct,omitempty"`
	// Steps Steps reported for the job.
	Steps []StepInfo `json:"steps,omitempty"`
}

// ActionsBilling contains GitHub Actions runner minutes statistics.
type ActionsBilling struct {
	// IncludedMinutes Actions minutes included in the billing plan.
	IncludedMinutes int `json:"included_minutes,omitempty"`
	// TotalMinutesUsed Total Actions minutes consumed.
	TotalMinutesUsed int `json:"total_minutes_used,omitempty"`
	// TotalPaidMinutesUsed Paid Actions minutes consumed.
	TotalPaidMinutesUsed int `json:"total_paid_minutes_used,omitempty"`
}

// FleetState represents the live status snapshot returned by /api/fleet and /api/status.
type FleetState struct {
	// Runners Current runner inventory.
	Runners []RunnerInfo `json:"runners"`
	// QueuedJobs Jobs waiting for or using runner capacity.
	QueuedJobs []QueuedJob `json:"queued_jobs"`
	// CompletedJobs Recently completed workflow jobs.
	CompletedJobs []CompletedJob `json:"completed_jobs"`
	// BusyRunners Number of busy non-cloud runners.
	BusyRunners int `json:"busy_runners"`
	// MaxRunners Configured runner capacity.
	MaxRunners int `json:"max_runners"`
	// FreeSlots Available runner capacity.
	FreeSlots int `json:"free_slots"`
	// RepoPriority Repository allocation priority order.
	RepoPriority []string `json:"repo_priority"`
	// PausedRepos Repositories excluded from allocation.
	PausedRepos []string `json:"paused_repos"`
	// RateLimitRemaining Remaining provider API requests.
	RateLimitRemaining *int `json:"rate_limit_remaining,omitempty"`
	// RateLimitLimit Provider API request limit.
	RateLimitLimit *int `json:"rate_limit_limit,omitempty"`
	// ActionsBilling GitHub Actions billing usage, when available.
	ActionsBilling *ActionsBilling `json:"actions_billing,omitempty"`
	// AutoscalerStatus Current autoscaler status.
	AutoscalerStatus string `json:"autoscaler_status"`
	// Version RunZero version string.
	Version string `json:"version"`
}

// LogEntry represents a single timestamped log line.
type LogEntry struct {
	// Timestamp RFC3339 time when the log entry was recorded.
	Timestamp string `json:"timestamp"`
	// Message Log message text.
	Message string `json:"message"`
}

func newTimestamp() string {
	return time.Now().UTC().Format(time.RFC3339)
}
