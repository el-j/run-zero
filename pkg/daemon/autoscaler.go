package daemon

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
	"sync/atomic"
	"time"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/inspector"
	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/reaper"
	"github.com/el-j/run-zero/pkg/sizing"
	"github.com/el-j/run-zero/pkg/state"
)

// randRead is swappable so tests can exercise the entropy-failure fallback.
var randRead = rand.Read

func randomHex(bytesLen int) string {
	b := make([]byte, bytesLen)
	if _, err := randRead(b); err != nil {
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
	lastRateLimit      time.Time
	standbyCursor      int
	pacing             bool // polling is currently slowed by a low API quota
	workflows          *inspector.WorkflowCache
	host               sizing.HostCapacity
	cachedWorkflows    int
	lastHistoryRefresh time.Time
	historyRunning     atomic.Bool
	// runnersFinished is set when a runner's job ended, so the finished job
	// shows up in history without waiting for the 5-minute sweep.
	runnersFinished atomic.Bool
	imageBuilder    ImageBuilder
	providerMgr     *provider.Manager
	spawnBackoff    map[string]spawnBackoff
	firstSeen       map[string]time.Time
}

// ImageBuilder rebuilds runner images; satisfied by *builder.BuildManager.
type ImageBuilder interface {
	TriggerBuild(ctx context.Context, req builder.ImageBuildRequest) (*builder.ImageBuildProgress, error)
	GetActiveBuild() *builder.ImageBuildProgress
}

type spawnBackoff struct {
	until time.Time
	delay time.Duration
	// awaitingImage: the failure was a missing image; lift the pause as soon
	// as the rebuild succeeds instead of waiting out the delay (a failed
	// rebuild keeps the pause, so it cannot turn into a rebuild loop).
	awaitingImage bool
}

const (
	minSpawnBackoff = 30 * time.Second
	maxSpawnBackoff = 10 * time.Minute
)

// SetImageBuilder lets the scaler rebuild a missing runner image on its own.
func (s *Scaler) SetImageBuilder(b ImageBuilder) { s.imageBuilder = b }

// SetProviderManager sets the multi-provider orchestrator manager.
func (s *Scaler) SetProviderManager(mgr *provider.Manager) { s.providerMgr = mgr }

// spawnBlocked reports whether spawns for key (backend/arch) are backing off
// after a failure. Checked before requesting a registration token, so a
// broken backend does not burn GitHub API quota on every queued job.
func (s *Scaler) spawnBlocked(key string) bool {
	b, ok := s.spawnBackoff[key]
	if !ok || !time.Now().Before(b.until) {
		return false
	}
	if b.awaitingImage && s.imageBuilder != nil {
		if active := s.imageBuilder.GetActiveBuild(); active != nil && active.Status == string(builder.StatusReady) {
			delete(s.spawnBackoff, key)
			return false
		}
	}
	return true
}

func (s *Scaler) noteSpawnFailure(ctx context.Context, key, arch string, err error) {
	if s.spawnBackoff == nil {
		s.spawnBackoff = make(map[string]spawnBackoff)
	}
	delay := minSpawnBackoff
	if prev, ok := s.spawnBackoff[key]; ok {
		delay = min(prev.delay*2, maxSpawnBackoff)
	}
	missing := errors.Is(err, driver.ErrImageMissing) && s.imageBuilder != nil
	s.spawnBackoff[key] = spawnBackoff{until: time.Now().Add(delay), delay: delay, awaitingImage: missing}
	s.state.AppendLog(fmt.Sprintf("[Autoscaler] ⏸️ Pausing %s spawns for %s after failure", key, delay))

	if missing {
		if active := s.imageBuilder.GetActiveBuild(); active != nil && active.Status == string(builder.StatusBuilding) {
			return // the rebuild we (or the dashboard) started is still running
		}
		if _, berr := s.imageBuilder.TriggerBuild(ctx, builder.ImageBuildRequest{Target: "container", Arch: arch}); berr != nil {
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] ⚠️ Could not start rebuild of missing runner image (%s): %v", arch, berr))
		} else {
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🔨 Runner image for %s is missing; rebuilding it", arch))
		}
	}
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
		host:           sizing.DetectHostCapacity(),
		firstSeen:      make(map[string]time.Time),
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

	// Refresh Rate Limit: every response updates it from headers; the explicit
	// refresh also catches an early reset while requests are held back.
	if time.Since(s.lastRateLimit) >= time.Duration(s.cfg.RateLimitRefreshInterval)*time.Second {
		if err := s.ghClient.RefreshRateLimit(ctx); err == nil {
			s.lastRateLimit = time.Now()
		}
	}
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

// isStartingStatus reports whether a runner is still coming up (e.g. an OrbStack VM
// that is being created/provisioned). Such runners already cover their job; ignoring
// them makes the next poll cycle spawn a duplicate.
func isStartingStatus(v string) bool {
	switch v {
	case "creating", "provisioning", "starting", "booting", "created":
		return true
	}
	return false
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
			runState == "running" || runState == "pending" || isStartingStatus(status) || isStartingStatus(runState) {
			active = append(active, r)
		}
	}
	return active
}

// historyRefreshMinInterval throttles the completed-jobs history sweep (one runs
// call per tracked repo); a dashboard-forced refresh bypasses it.
const historyRefreshMinInterval = 5 * time.Minute

// finishedRefreshMinInterval spaces out the history refreshes triggered by
// finishing runners, so a busy fleet does not sweep history every cycle.
const finishedRefreshMinInterval = 30 * time.Second

// refreshCompletedJobsAsync runs the history sweep off the scale loop so a slow
// (cold-start) sweep over many repos can never delay job detection or spawning.
// At most one sweep runs at a time, which also serialises access to the
// throttle fields used by refreshCompletedJobs.
func (s *Scaler) refreshCompletedJobsAsync(ctx context.Context, repos []string) {
	if !s.historyRunning.CompareAndSwap(false, true) {
		return
	}
	go func() {
		defer s.historyRunning.Store(false)
		s.refreshCompletedJobs(ctx, repos)
	}()
}

func (s *Scaler) refreshCompletedJobs(ctx context.Context, repos []string) {
	if s.ghClient == nil || len(repos) == 0 {
		return
	}
	if s.historyFetcher == nil {
		s.historyFetcher = github.NewHistoryFetcher(s.ghClient)
	}
	if !s.historyRefreshDue() {
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

// historyRefreshDue reports whether job history should be fetched now: on a
// dashboard request (retry/rerun), when runners finished and the last sweep is
// over finishedRefreshMinInterval old, or every historyRefreshMinInterval.
func (s *Scaler) historyRefreshDue() bool {
	if s.state.ConsumeHistoryRefresh() || s.lastHistoryRefresh.IsZero() {
		s.runnersFinished.Store(false)
		return true
	}
	since := time.Since(s.lastHistoryRefresh)
	if since >= historyRefreshMinInterval ||
		(since >= finishedRefreshMinInterval && s.runnersFinished.Load()) {
		s.runnersFinished.Store(false)
		return true
	}
	return false
}

// Start begins periodic scaling loops until ctx is canceled.
func (s *Scaler) Start(ctx context.Context) {
	for {
		s.ScaleCycle(ctx)
		select {
		case <-ctx.Done():
			return
		case <-time.After(s.nextCycleDelay()):
		}
	}
}
