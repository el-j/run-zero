package daemon

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/cache"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/scheduling"
	"github.com/el-j/run-zero/pkg/state"
)

// ScaleCycle runs one complete autoscaling cycle across tracked repositories.
func (s *Scaler) ScaleCycle(ctx context.Context) {
	s.DiscoverAndSync(ctx)
	s.pruneFinishedRunners(ctx)

	activeRunners := s.CollectRunners(ctx)
	tracked := s.trackedRepos()

	// Runners listed without a spawn-time record (e.g. OrbStack VMs whose host-side
	// store entry is gone) carry a repo parsed from their hostname-safe name, such as
	// "el-j-landing-in". Map it back to the tracked "owner/repo" so capacity counts,
	// reaper, the dashboard and run links use the real repo.
	resolveRunnerRepos(activeRunners, tracked)
	s.stampFirstSeen(activeRunners)

	allJobs, jobsByRepo := s.collectActiveJobs(ctx, tracked)
	activeRunners = s.reapCompletedRunners(ctx, activeRunners, allJobs)
	activeRunners = s.reapStaleRunners(ctx, activeRunners, tracked)
	activeRunners = s.scaleUp(ctx, activeRunners, tracked, jobsByRepo)
	activeRunners = s.topUpStandby(ctx, activeRunners, tracked)
	enrichRunners(activeRunners, allJobs)
	s.publishFleet(ctx, activeRunners, allJobs, tracked)
}

// pruneFinishedRunners removes exited containers/VMs left behind by old jobs.
func (s *Scaler) pruneFinishedRunners(ctx context.Context) {
	if s.driver == nil {
		return
	}
	removed, err := driver.PruneFinished(ctx, s.driver, func(r state.RunnerInfo, logTail string) {
		if r.Name != "" && logTail != "" {
			s.state.SetRunnerLog(r.Name, logTail)
		}
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧹 Removed finished runner '%s' for %s (%s)", r.Name, r.TargetRepo, r.Backend))
	})
	if err != nil {
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] ⚠️ Failed to prune finished runners: %v", err))
	}
	if len(removed) > 0 {
		s.runnersFinished.Store(true)
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧹 Pruned %d finished runner container(s)/VM(s) from old jobs.", len(removed)))
	}
}

// trackedRepos returns the repos to poll: the poller's list, else the priority list.
func (s *Scaler) trackedRepos() []string {
	var tracked []string
	if s.poller != nil {
		tracked = s.poller.Repos()
	}
	if len(tracked) == 0 && s.priorityMgr != nil {
		prio, _ := s.priorityMgr.GetState()
		tracked = prio
	}
	return tracked
}

// resolveRunnerRepos rewrites lossy repo names ("el-j-landing-in") to tracked "owner/repo" names.
func resolveRunnerRepos(runners []state.RunnerInfo, tracked []string) {
	for i := range runners {
		r := &runners[i]
		if strings.Contains(r.TargetRepo, "/") {
			continue
		}
		if repo := driver.ResolveRepoFromMachineName(r.Name, tracked); repo != "" {
			r.TargetRepo = repo
		}
	}
}

// stampFirstSeen gives runners without a creation time the time we first saw
// them, and forgets runners that are no longer active.
func (s *Scaler) stampFirstSeen(runners []state.RunnerInfo) {
	for i := range runners {
		r := &runners[i]
		if r.CreatedAt != nil {
			continue
		}
		if s.firstSeen == nil {
			s.firstSeen = make(map[string]time.Time)
		}
		seen, ok := s.firstSeen[r.Name]
		if !ok {
			seen = time.Now()
			s.firstSeen[r.Name] = seen
		}
		cStr := seen.UTC().Format(time.RFC3339)
		r.CreatedAt = &cStr
	}

	activeNames := make(map[string]bool, len(runners))
	for _, r := range runners {
		activeNames[r.Name] = true
	}
	for k := range s.firstSeen {
		if !activeNames[k] {
			delete(s.firstSeen, k)
		}
	}
}

// collectActiveJobs lists queued/in-progress jobs for every non-paused tracked repo.
func (s *Scaler) collectActiveJobs(ctx context.Context, tracked []string) ([]state.QueuedJob, map[string][]state.QueuedJob) {
	var allJobs []state.QueuedJob
	jobsByRepo := make(map[string][]state.QueuedJob)
	for _, repo := range tracked {
		if s.priorityMgr != nil && s.priorityMgr.IsPaused(repo) {
			continue
		}
		jobs, err := s.ghClient.ListActiveJobs(ctx, repo)
		if err == nil && len(jobs) > 0 {
			allJobs = append(allJobs, jobs...)
			jobsByRepo[repo] = jobs
		}
	}
	return allJobs, jobsByRepo
}

// jobMatchesRunner reports whether j is the job a runner is serving.
func jobMatchesRunner(j state.QueuedJob, r *state.RunnerInfo) bool {
	if j.RunnerName != nil && *j.RunnerName == r.Name {
		return true
	}
	if r.JobID != nil && *r.JobID == j.ID {
		return true
	}
	return r.JobID == nil && r.RunID != nil && *r.RunID == j.RunID && r.TargetRepo == j.Repo
}

// completionReason asks GitHub whether the runner's job or run has finished.
func (s *Scaler) completionReason(ctx context.Context, r state.RunnerInfo) (string, bool) {
	if r.JobID != nil {
		job, err := s.ghClient.GetWorkflowJob(ctx, r.TargetRepo, *r.JobID)
		if err == nil && job != nil && job.Status == "completed" {
			return fmt.Sprintf("job #%d is completed (%s)", *r.JobID, job.Conclusion), true
		}
	}
	if r.RunID != nil {
		run, err := s.ghClient.GetWorkflowRun(ctx, r.TargetRepo, *r.RunID)
		if err == nil && run != nil && run.Status == "completed" {
			return fmt.Sprintf("workflow run #%d is completed (%s)", *r.RunID, run.Conclusion), true
		}
	}
	return "", false
}

// reapCompletedRunners stops runners whose job or workflow run has already
// completed on GitHub Actions. In ephemeral single-job runner architectures such
// a runner is orphaned and must not occupy capacity or linger in the UI.
func (s *Scaler) reapCompletedRunners(ctx context.Context, active []state.RunnerInfo, allJobs []state.QueuedJob) []state.RunnerInfo {
	if s.ghClient == nil || s.driver == nil || len(active) == 0 {
		return active
	}
	var surviving []state.RunnerInfo
	for _, r := range active {
		if s.runnerStillNeeded(ctx, r, allJobs) {
			surviving = append(surviving, r)
		}
	}
	return surviving
}

// runnerStillNeeded reports whether r must be kept; a finished runner is stopped as a side effect.
func (s *Scaler) runnerStillNeeded(ctx context.Context, r state.RunnerInfo, allJobs []state.QueuedJob) bool {
	if r.TargetRepo == "" || (r.JobID == nil && r.RunID == nil) {
		return true
	}
	for _, j := range allJobs {
		if jobMatchesRunner(j, &r) {
			return true
		}
	}
	reason, done := s.completionReason(ctx, r)
	if !done {
		return true
	}
	s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧹 Reaped finished runner '%s' for %s: %s", r.Name, r.TargetRepo, reason))
	s.runnersFinished.Store(true)
	if err := s.driver.StopRunner(ctx, r.ID); err != nil && r.Name != "" && r.Name != r.ID {
		_ = s.driver.StopRunner(ctx, r.Name)
	}
	if s.firstSeen != nil {
		delete(s.firstSeen, r.Name)
	}
	return false
}

// reapStaleRunners lets the reaper remove orphaned/idle/stale runners and re-reads the fleet if any went.
func (s *Scaler) reapStaleRunners(ctx context.Context, active []state.RunnerInfo, tracked []string) []state.RunnerInfo {
	if s.reaper == nil || len(active) == 0 {
		return active
	}
	// Up to MIN_RUNNERS idle runners are the standby pool, exempt from idle reaping.
	reaped := s.reaper.Reconcile(ctx, active, s.cfg.MinRunners)
	if len(reaped) == 0 {
		return active
	}
	s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧹 Reaped %d orphaned/idle runner(s) blocking capacity: %s", len(reaped), strings.Join(reaped, ", ")))
	active = s.CollectRunners(ctx)
	resolveRunnerRepos(active, tracked)
	return active
}

// runnerServingJob reports whether an active runner is already assigned to job.
func runnerServingJob(active []state.RunnerInfo, job state.QueuedJob) bool {
	for i := range active {
		if jobMatchesRunner(job, &active[i]) {
			return true
		}
	}
	return false
}

// scaleUp spawns runners for queued jobs not yet covered, by repo priority, up to MaxRunners.
func (s *Scaler) scaleUp(ctx context.Context, active []state.RunnerInfo, tracked []string, jobsByRepo map[string][]state.QueuedJob) []state.RunnerInfo {
	if s.state.GetSnapshot().AutoscalerStatus == "paused" || s.driver == nil {
		return active
	}
	activeByRepo := make(map[string]int)
	for _, r := range active {
		activeByRepo[r.TargetRepo]++
	}

	for _, repo := range s.priorityMgr.SortRepos(tracked) {
		if s.priorityMgr.IsPaused(repo) {
			continue
		}
		var queued []state.QueuedJob
		for _, j := range jobsByRepo[repo] {
			if j.Status == "queued" {
				queued = append(queued, j)
			}
		}
		uncovered := len(queued) - activeByRepo[repo]
		if uncovered <= 0 {
			continue
		}
		for _, job := range queued {
			if len(active) >= s.cfg.MaxRunners || uncovered <= 0 {
				break
			}
			if runnerServingJob(active, job) {
				continue
			}
			info := s.spawnForJob(ctx, repo, job)
			if info == nil {
				continue
			}
			active = append(active, *info)
			activeByRepo[repo]++
			uncovered--
		}
	}
	return active
}

// policy is the scheduling configuration currently in effect.
func (s *Scaler) policy() scheduling.Policy {
	return scheduling.Policy{
		Backend:         s.cfg.RunnerBackend,
		AutoRouteVM:     s.cfg.AutoRouteVM,
		VMTriggerLabels: s.cfg.VMTriggerLabels,
		RunnerArch:      s.cfg.RunnerArch,
		ArchOverride:    s.archOverride,
		RunnerCPUs:      s.cfg.RunnerCPUs,
		RunnerMemory:    s.cfg.RunnerMemory,
		MaxRunners:      s.cfg.MaxRunners,
	}
}

// schedJob describes a queued job of repo for scheduling.
func schedJob(job state.QueuedJob, repo string) scheduling.Job {
	j := scheduling.Job{Repo: repo, Name: job.Name, Labels: job.Labels}
	if job.WorkflowName != nil {
		j.WorkflowName = *job.WorkflowName
	}
	return j
}

// resolveJobArch picks the architecture a job needs, honouring native-arch override.
func (s *Scaler) resolveJobArch(job state.QueuedJob, repo string) string {
	return scheduling.Arch(s.policy(), schedJob(job, repo))
}

// resolveJobBackend picks docker or orbstack from config and VM triggers.
func (s *Scaler) resolveJobBackend(job state.QueuedJob) string {
	backend, _ := scheduling.Backend(s.policy(), schedJob(job, ""))
	return backend
}

// resolveSizing returns the CPU and memory (MiB) for a new runner.
func (s *Scaler) resolveSizing(labels []string) (cpus, memMB int) {
	return scheduling.Size(s.policy(), labels)
}

// spawnForJob provisions a runner for one queued job; nil means nothing was
// spawned (backing off, token failure or spawn failure).
func (s *Scaler) spawnForJob(ctx context.Context, repo string, job state.QueuedJob) *state.RunnerInfo {
	info := s.spawnRunner(ctx, repo, &job)
	if info == nil {
		return nil
	}
	applyJob(info, job)
	runURL := fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, job.RunID)
	info.RunURL = &runURL
	return info
}

// spawnRunner provisions a runner for repo: job-scoped when job is non-nil,
// otherwise an idle standby runner that takes the repo's next job.
func (s *Scaler) spawnRunner(ctx context.Context, repo string, job *state.QueuedJob) *state.RunnerInfo {
	forJob := state.QueuedJob{}
	if job != nil {
		forJob = *job
	}
	targetArch := s.resolveJobArch(forJob, repo)
	backend := s.resolveJobBackend(forJob)
	spawnKey := backend + "/" + targetArch
	if s.spawnBlocked(spawnKey) {
		return nil
	}

	token, err := s.ghClient.CreateRegistrationToken(ctx, repo, s.cfg.Org)
	if err != nil {
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] ❌ Failed to get registration token for %s: %v", repo, err))
		return nil
	}

	spec := s.runnerSpec(repo, targetArch, backend, job)
	spec.Token = token
	info, err := s.driver.SpawnRunner(ctx, spec)
	if err != nil {
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] ❌ Failed to spawn %s runner for %s: %v", backend, repo, err))
		s.noteSpawnFailure(ctx, spawnKey, targetArch, err)
		return nil
	}
	delete(s.spawnBackoff, spawnKey)

	purpose := "standby"
	if job != nil {
		purpose = job.Name
	}
	s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🚀 Spawned %s runner '%s' for %s (%s, %s)", backend, spec.Name, repo, purpose, targetArch))
	return info
}

// runnerSpec describes a new runner (without its registration token).
func (s *Scaler) runnerSpec(repo, targetArch, backend string, job *state.QueuedJob) driver.RunnerSpec {
	id := randomHex(3)
	spec := driver.RunnerSpec{
		ID:       id,
		Name:     driver.ManualRunnerName(repo, targetArch, id),
		Repo:     repo,
		Arch:     targetArch,
		Backend:  backend,
		Labels:   []string{"self-hosted", "local", targetArch},
		CacheDir: s.cfg.HostCacheDir,
		Network:  "host",
	}
	scope := repo + "_standby"
	if job != nil {
		spec.Name = driver.JobScopedRunnerName(repo, targetArch, job.RunID, job.ID, id)
		spec.JobName = job.Name
		spec.JobID = &job.ID
		spec.RunID = &job.RunID
		spec.WorkflowName = job.WorkflowName
		spec.Labels = append(spec.Labels, job.Labels...)
		scope = fmt.Sprintf("%s_%s", repo, job.Name)
	}
	spec.CPUs, spec.MemoryMB = s.resolveSizing(spec.Labels)
	spec.Mounts = cache.InitCacheDirs(s.cfg.HostCacheDir, targetArch, s.cfg.CacheEnabled, scope)
	return spec
}

// applyJob copies a job's identity and progress onto the runner serving it.
func applyJob(r *state.RunnerInfo, j state.QueuedJob) {
	jobID, runID, jobName := j.ID, j.RunID, j.Name
	r.JobID = &jobID
	r.RunID = &runID
	r.JobURL = &j.HTMLURL
	r.JobName = &jobName
	r.WorkflowName = j.WorkflowName
	r.StagesDone = j.StagesDone
	r.StagesTotal = j.StagesTotal
	r.StepsCompleted = j.StepsCompleted
	r.StepsTotal = j.StepsTotal
	r.CurrentStep = j.CurrentStep
	r.Steps = j.Steps
	r.ProgressPct = j.ProgressPct
}

// enrichRunners attaches live workflow links, stages and current steps to active runners.
func enrichRunners(active []state.RunnerInfo, allJobs []state.QueuedJob) {
	for i := range active {
		r := &active[i]
		if r.RunURL == nil && r.RunID != nil && r.TargetRepo != "" {
			u := fmt.Sprintf("https://github.com/%s/actions/runs/%d", r.TargetRepo, *r.RunID)
			r.RunURL = &u
		}
		for _, j := range allJobs {
			if !jobMatchesRunner(j, r) {
				continue
			}
			applyJob(r, j)
			if j.RunURL != nil {
				r.RunURL = j.RunURL
			}
			break
		}
	}
}

// publishFleet reconciles queue vs capacity and pushes fleet state to the dashboard.
func (s *Scaler) publishFleet(ctx context.Context, active []state.RunnerInfo, allJobs []state.QueuedJob, tracked []string) {
	reconciled := s.reconciler.Reconcile(allJobs, len(active), s.cfg.MaxRunners)
	s.refreshCompletedJobsAsync(ctx, tracked)

	fleet := active
	if s.providerMgr != nil {
		if remote, _ := s.providerMgr.FetchAllRemoteRunners(ctx); len(remote) > 0 {
			fleet = provider.MergeRunners(active, remote)
		}
	}
	s.state.UpdateFleet(fleet, reconciled)
}
