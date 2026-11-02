package daemon

import (
	"context"

	"github.com/el-j/run-zero/pkg/state"
)

// topUpStandby keeps MIN_RUNNERS idle runners warm once queued jobs are served,
// so the next job starts without waiting for a spawn. Standby runners are
// spread round-robin across the tracked, unpaused repos in priority order (in
// ORG mode they register at org scope and serve any of the org's repos), and
// the pool never pushes the fleet past MAX_RUNNERS.
func (s *Scaler) topUpStandby(ctx context.Context, active []state.RunnerInfo, tracked []string) []state.RunnerInfo {
	if s.cfg.MinRunners <= 0 || s.driver == nil || s.state.GetSnapshot().AutoscalerStatus == "paused" {
		return active
	}
	repos := s.standbyRepos(tracked)
	if len(repos) == 0 {
		return active
	}

	missing := s.cfg.MinRunners - countStandby(active)
	for ; missing > 0 && len(active) < s.cfg.MaxRunners; missing-- {
		repo := repos[s.standbyCursor%len(repos)]
		s.standbyCursor++
		info := s.spawnRunner(ctx, repo, nil)
		if info == nil {
			break // backing off or GitHub/driver failure; retry next cycle
		}
		active = append(active, *info)
	}
	return active
}

// standbyRepos lists the repos standby runners may register for, by priority.
func (s *Scaler) standbyRepos(tracked []string) []string {
	var repos []string
	for _, repo := range s.priorityMgr.SortRepos(tracked) {
		if !s.priorityMgr.IsPaused(repo) {
			repos = append(repos, repo)
		}
	}
	return repos
}

// countStandby counts runners not assigned to any job.
func countStandby(active []state.RunnerInfo) int {
	n := 0
	for _, r := range active {
		if r.JobID == nil && r.RunID == nil {
			n++
		}
	}
	return n
}
