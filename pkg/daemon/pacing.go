package daemon

import (
	"fmt"
	"time"

	"github.com/el-j/run-zero/pkg/github"
)

// pacedInterval stretches the poll interval as the GitHub API quota runs low,
// so the remaining requests last until the quota resets: the base interval
// above 50% left, then 2x, 4x and 8x below 50%, 20% and 10%. It never waits
// past the reset, and never less than base.
func pacedInterval(base time.Duration, rl github.RateLimit, now time.Time) time.Duration {
	// An unknown quota (Limit 0) gives NaN or +Inf, which matches no tier, and
	// its zero reset time leaves the base interval.
	left := float64(rl.Remaining) / float64(rl.Limit)
	factor := 1
	switch {
	case left < 0.1:
		factor = 8
	case left < 0.2:
		factor = 4
	case left < 0.5:
		factor = 2
	}
	return min(base*time.Duration(factor), max(rl.Reset.Sub(now), base))
}

// nextCycleDelay returns the wait before the next scale cycle: POLL_INTERVAL
// (read each time, so dashboard edits apply), paced by the API quota. Changes
// in pacing are logged.
func (s *Scaler) nextCycleDelay() time.Duration {
	base := time.Duration(s.cfg.PollInterval) * time.Second
	if base <= 0 {
		base = 10 * time.Second
	}
	delay := base
	if s.ghClient != nil {
		delay = pacedInterval(base, s.ghClient.RateLimit(), time.Now())
	}
	slowed := delay > base
	if slowed != s.pacing {
		s.pacing = slowed
		if slowed {
			rl := s.ghClient.RateLimit()
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🐢 GitHub API quota low (%d/%d left): polling every %s until it recovers", rl.Remaining, rl.Limit, delay.Round(time.Second)))
		} else {
			s.state.AppendLog(fmt.Sprintf("[Autoscaler] GitHub API quota recovered: polling every %s", base))
		}
	}
	return delay
}
