package driver

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// LogProvider is implemented by drivers that can return a runner's recent output.
type LogProvider interface {
	RunnerLogs(ctx context.Context, runnerID string, tail int) (string, error)
}

// runnerLogTail is the number of log lines retained for finished runners.
const runnerLogTail = 80

// IsFinished reports whether a listed runner has already exited and merely
// occupies disk/registry space (stopped/exited/dead container or stopped VM).
func IsFinished(r state.RunnerInfo) bool {
	for _, v := range []string{r.State, r.Status} {
		v = strings.ToLower(strings.TrimSpace(v))
		if strings.HasPrefix(v, "exited") || strings.HasPrefix(v, "dead") ||
			strings.HasPrefix(v, "stopped") || strings.HasPrefix(v, "created") {
			return true
		}
	}
	return false
}

// PruneFinished removes every finished runner container/VM managed by RunZero.
// onRemove, when non-nil, receives each runner together with the last lines of its
// output (captured before removal) so failures remain diagnosable afterwards.
// It returns the runners that were removed.
func PruneFinished(
	ctx context.Context,
	d RunnerDriver,
	onRemove func(r state.RunnerInfo, logTail string),
) ([]state.RunnerInfo, error) {
	if d == nil {
		return nil, nil
	}
	all, err := d.ListRunners(ctx)
	if err != nil {
		return nil, err
	}

	provider, canLog := d.(LogProvider)
	var removed []state.RunnerInfo
	var firstErr error

	for _, r := range all {
		if !IsFinished(r) {
			continue
		}
		logTail := ""
		if canLog {
			if out, lerr := provider.RunnerLogs(ctx, r.ID, runnerLogTail); lerr == nil {
				logTail = out
			}
		}
		if serr := d.StopRunner(ctx, r.ID); serr != nil {
			if firstErr == nil {
				firstErr = fmt.Errorf("remove %s: %w", r.Name, serr)
			}
			continue
		}
		removed = append(removed, r)
		if onRemove != nil {
			onRemove(r, logTail)
		}
	}
	return removed, firstErr
}
