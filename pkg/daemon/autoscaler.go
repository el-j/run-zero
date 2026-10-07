package daemon

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/cache"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/sizing"
	"github.com/el-j/run-zero/pkg/state"
)

func randomHex(bytesLen int) string {
	b := make([]byte, bytesLen)
	if _, err := rand.Read(b); err != nil {
		return fmt.Sprintf("%06x", time.Now().UnixNano()%0xFFFFFF)
	}
	return hex.EncodeToString(b)
}

// Scaler manages the background autoscaling loop, repository discovery,
// job queue reconciliation, and runner provisioning.
type Scaler struct {
	cfg                *config.Config
	state              *state.State
	driver             driver.RunnerDriver
	ghClient           *github.Client
	priorityMgr        *github.PriorityManager
	reconciler         *github.Reconciler
	poller             *github.Poller
	reaper             *reaper.Reaper
	archOverride       *arch.NativeArchOverride
	historyFetcher     *github.HistoryFetcher
	lastDiscovery      time.Time
	lastBilling        time.Time
	lastHistoryRefresh time.Time
	standbyCursor      int
}

// NewScaler creates an autoscaler engine.
func NewScaler(
	cfg *config.Config,
	st *state.State,
	drv driver.RunnerDriver,
	gh *github.Client,
	pm *github.PriorityManager,
	rec *github.Reconciler,
	poller *github.Poller,
	rp *reaper.Reaper,
) *Scaler {
	override, _ := arch.NewNativeArchOverride(cfg.NativeArchOverride, "")
	return &Scaler{
		cfg:            cfg,
		state:          st,
		driver:         drv,
		ghClient:       gh,
		priorityMgr:    pm,
		reconciler:     rec,
		poller:         poller,
		reaper:         rp,
		archOverride:   override,
		historyFetcher: github.NewHistoryFetcher(gh),
	}
}

// DiscoverAndSync updates repository discovery, rates, and priority state.
func (s *Scaler) DiscoverAndSync(ctx context.Context) {
	if s.ghClient == nil {
		return
	}

	needsDiscovery := s.lastDiscovery.IsZero() || time.Since(s.lastDiscovery) >= time.Duration(s.cfg.DiscoveryInterval)*time.Second
	if needsDiscovery && (s.cfg.AutoDiscover || s.cfg.ReposConfig != "") {
		discovered, err := s.ghClient.DiscoverRepositories(
			ctx,
			s.cfg.Owner,
			s.cfg.Org,
			s.cfg.ActiveDays,
			s.cfg.AutoDiscover,
			s.cfg.ReposConfig,
		)
		if err == nil && len(discovered) > 0 {
			s.lastDiscovery = time.Now()
			if s.poller != nil {
				s.poller.SetRepos(discovered)
			}
			s.priorityMgr.MergeDiscovered(discovered)
			prio, paused := s.priorityMgr.GetState()
			s.state.SetRepoPriority(prio, paused)

			s.state.AppendLog(fmt.Sprintf("[Autoscaler] Monitoring %d active repository(ies):", len(discovered)))
			for _, r := range discovered {
				s.state.AppendLog(fmt.Sprintf("  • %s", r))
			}
		} else if err != nil {
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] ⚠️ Repository discovery warning: %v", err))
		}
	}

	// Refresh Rate Limit
	rl := s.ghClient.RateLimit()
	if rl.Limit > 0 {
		rem := rl.Remaining
		lim := rl.Limit
		s.state.SetRateLimit(&rem, &lim)
	}

	// Refresh Actions Billing
	needsBilling := s.lastBilling.IsZero() || time.Since(s.lastBilling) >= time.Duration(s.cfg.ActionsBillingRefreshInterval)*time.Second
	if needsBilling {
		if billing, err := s.ghClient.GetActionsBilling(ctx, s.cfg.Owner, s.cfg.Org); err == nil {
			s.lastBilling = time.Now()
			s.state.SetActionsBilling(billing)
		}
	}
}

// CollectRunners inspects currently active runners from the driver.
func (s *Scaler) CollectRunners(ctx context.Context) []state.RunnerInfo {
	if s.driver == nil {
		return []state.RunnerInfo{}
	}
	all, err := s.driver.ListRunners(ctx)
	if err != nil {
		return []state.RunnerInfo{}
	}

	active := make([]state.RunnerInfo, 0, len(all))
	for _, r := range all {
		status := strings.ToLower(r.Status)
		runState := strings.ToLower(r.State)
		if strings.Contains(status, "up") || strings.Contains(status, "running") ||
			runState == "running" || runState == "pending" {
			active = append(active, r)
		}
	}
	return active
}

func (s *Scaler) refreshCompletedJobs(ctx context.Context, repos []string) {
	if s.ghClient == nil || len(repos) == 0 {
		return
	}
	if s.historyFetcher == nil {
		s.historyFetcher = github.NewHistoryFetcher(s.ghClient)
	}
	forceRefresh := s.state.ConsumeHistoryRefresh()
	if !forceRefresh && time.Since(s.lastHistoryRefresh) < 30*time.Second && !s.lastHistoryRefresh.IsZero() {
		return
	}

	var all []state.CompletedJob
	for _, repo := range repos {
		if repo == "" {
			continue
		}
		jobs, err := s.historyFetcher.Fetch(ctx, repo)
		if err != nil {
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] ⚠️ Could not refresh completed jobs for %s: %v", repo, err))
			continue
		}
		all = append(all, jobs...)
	}
	if len(all) == 0 {
		all = []state.CompletedJob{}
	}
	s.state.SetCompletedJobs(all)
	s.lastHistoryRefresh = time.Now()
}

// ScaleCycle runs one complete autoscaling cycle across tracked repositories.
func (s *Scaler) ScaleCycle(ctx context.Context) {
	s.DiscoverAndSync(ctx)

	if s.driver != nil {
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
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧹 Pruned %d finished runner container(s)/VM(s) from old jobs.", len(removed)))
		}
	}

	activeRunners := s.CollectRunners(ctx)

	var tracked []string
	if s.poller != nil {
		tracked = s.poller.Repos()
	}
	if len(tracked) == 0 {
		prio, _ := s.priorityMgr.GetState()
		tracked = prio
	}

	var allJobs []state.QueuedJob
	jobsByRepo := make(map[string][]state.QueuedJob)

	for _, repo := range tracked {
		if s.priorityMgr.IsPaused(repo) {
			continue
		}
		jobs, err := s.ghClient.ListActiveJobs(ctx, repo)
		if err == nil && len(jobs) > 0 {
			allJobs = append(allJobs, jobs...)
			jobsByRepo[repo] = jobs
		}
	}

	// Evaluate scaling
	snap := s.state.GetSnapshot()
	if snap.AutoscalerStatus != "paused" && s.driver != nil {
		activeByRepo := make(map[string]int)
		for _, r := range activeRunners {
			activeByRepo[r.TargetRepo]++
		}

		orderedRepos := s.priorityMgr.SortRepos(tracked)
		for _, repo := range orderedRepos {
			if s.priorityMgr.IsPaused(repo) {
				continue
			}

			repoJobs := jobsByRepo[repo]
			var queued []state.QueuedJob
			for _, j := range repoJobs {
				if j.Status == "queued" {
					queued = append(queued, j)
				}
			}

			uncovered := len(queued) - activeByRepo[repo]
			if uncovered <= 0 {
				continue
			}

			for _, job := range queued {
				if len(activeRunners) >= s.cfg.MaxRunners || uncovered <= 0 {
					break
				}

				// Resolve target architecture
				jobArch := "amd64"
				if s.cfg.RunnerArch != "both" && s.cfg.RunnerArch != "" {
					jobArch = s.cfg.RunnerArch
				} else {
					for _, l := range job.Labels {
						lower := strings.ToLower(l)
						if lower == "arm64" || lower == "aarch64" || lower == "arm" {
							jobArch = "arm64"
							break
						}
					}
				}
				targetArch := jobArch
				if s.archOverride != nil {
					targetArch = s.archOverride.ArchFor(jobArch, job.Labels, repo)
				}

				// Resolve Backend
				backend := "docker"
				if s.cfg.RunnerBackend != "" && s.cfg.RunnerBackend != "auto" {
					backend = s.cfg.RunnerBackend
				} else if s.cfg.AutoRouteVM {
					// Route to VM backend only if job explicitly demands a VM via labels
					for _, l := range job.Labels {
						low := strings.ToLower(strings.TrimSpace(l))
						if low == "vm" || low == "orbstack" || low == "linux-vm" {
							backend = "orbstack"
							break
						}
					}
				}

				// Resolve Sizing
				cpus := 3
				if s.cfg.RunnerCPUs > 0 {
					cpus = s.cfg.RunnerCPUs
				}
				memMB := 4096
				if s.cfg.RunnerMemory != "" {
					if m := sizing.ParseMemoryMiB(s.cfg.RunnerMemory); m != nil {
						memMB = *m
					}
				}

				// Cache Mounts
				scope := fmt.Sprintf("%s_%s", repo, job.Name)
				cacheMounts := cache.InitCacheDirs(s.cfg.HostCacheDir, targetArch, s.cfg.CacheEnabled, scope)

				// Registration Token
				token, err := s.ghClient.CreateRegistrationToken(ctx, repo, s.cfg.Org)
				if err != nil {
					s.state.AppendLog(fmt.Sprintf("[Autoscaler] ❌ Failed to get registration token for %s: %v", repo, err))
					continue
				}

				// Generate runner name and launch
				id := randomHex(3)
				runnerName := fmt.Sprintf("local-runner-%s-%s-%s", targetArch, strings.ReplaceAll(repo, "/", "-"), id)

				spec := driver.RunnerSpec{
					ID:       id,
					Name:     runnerName,
					Repo:     repo,
					Arch:     targetArch,
					Backend:  backend,
					CPUs:     cpus,
					MemoryMB: memMB,
					Labels:   append([]string{"self-hosted", "local", targetArch}, job.Labels...),
					Token:    token,
					CacheDir: s.cfg.HostCacheDir,
					Mounts:   cacheMounts,
					Network:  "host",
				}

				info, err := s.driver.SpawnRunner(ctx, spec)
				if err != nil {
					s.state.AppendLog(fmt.Sprintf("[Autoscaler] ❌ Failed to spawn %s runner for %s: %v", backend, repo, err))
					continue
				}

				jobID := job.ID
				runID := job.RunID
				runURL := fmt.Sprintf("https://github.com/%s/actions/runs/%d", repo, job.RunID)
				jobName := job.Name
				info.JobID = &jobID
				info.RunID = &runID
				info.JobURL = &job.HTMLURL
				info.RunURL = &runURL
				info.JobName = &jobName
				info.WorkflowName = job.WorkflowName
				info.StagesDone = job.StagesDone
				info.StagesTotal = job.StagesTotal
				info.StepsCompleted = job.StepsCompleted
				info.StepsTotal = job.StepsTotal
				info.CurrentStep = job.CurrentStep
				info.Steps = job.Steps
				info.ProgressPct = job.ProgressPct

				s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🚀 Spawned %s runner '%s' for %s (%s, %s)", backend, runnerName, repo, job.Name, targetArch))
				activeRunners = append(activeRunners, *info)
				activeByRepo[repo]++
				uncovered--
			}
		}
	}

	// Enrich all active runners with live workflow job links, stages, and current steps
	for i := range activeRunners {
		r := &activeRunners[i]
		if r.RunURL == nil && r.RunID != nil && r.TargetRepo != "" {
			u := fmt.Sprintf("https://github.com/%s/actions/runs/%d", r.TargetRepo, *r.RunID)
			r.RunURL = &u
		}
		for _, j := range allJobs {
			isMatch := false
			if j.RunnerName != nil && *j.RunnerName == r.Name {
				isMatch = true
			} else if r.JobID != nil && *r.JobID == j.ID {
				isMatch = true
			} else if r.RunID != nil && *r.RunID == j.RunID && r.TargetRepo == j.Repo {
				isMatch = true
			}
			if isMatch {
				jID := j.ID
				r.JobID = &jID
				rID := j.RunID
				r.RunID = &rID
				r.JobURL = &j.HTMLURL
				if j.RunURL != nil {
					r.RunURL = j.RunURL
				}
				jName := j.Name
				r.JobName = &jName
				r.WorkflowName = j.WorkflowName
				r.StagesDone = j.StagesDone
				r.StagesTotal = j.StagesTotal
				r.StepsCompleted = j.StepsCompleted
				r.StepsTotal = j.StepsTotal
				r.CurrentStep = j.CurrentStep
				r.Steps = j.Steps
				r.ProgressPct = j.ProgressPct
				break
			}
		}
	}

	// Reconcile and push state to dashboard
	reconciled := s.reconciler.Reconcile(allJobs, len(activeRunners), s.cfg.MaxRunners)
	s.refreshCompletedJobs(ctx, tracked)
	s.state.UpdateFleet(activeRunners, reconciled)
}

// Start begins periodic scaling loops until ctx is canceled.
func (s *Scaler) Start(ctx context.Context) {
	s.ScaleCycle(ctx)

	interval := time.Duration(s.cfg.PollInterval) * time.Second
	if interval <= 0 {
		interval = 10 * time.Second
	}

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.ScaleCycle(ctx)
		}
	}
}
