package state

const (
	// MaxCompletedJobs bounds how many finished jobs are kept for the history tab.
	MaxCompletedJobs = 100
	// maxRunnerLogs bounds how many local runner log tails are retained.
	maxRunnerLogs = 100
	// maxRunnerLogBytes bounds the size of a single retained log tail.
	maxRunnerLogBytes = 16 * 1024
)

func derefStr(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

// SetCompletedJobs replaces the finished-job history (newest first). The next
// UpdateFleet broadcast carries it to SSE clients.
func (s *State) SetCompletedJobs(jobs []CompletedJob) {
	s.mu.Lock()
	if len(jobs) > MaxCompletedJobs {
		jobs = jobs[:MaxCompletedJobs]
	}
	s.completedJobs = make([]CompletedJob, len(jobs))
	copy(s.completedJobs, jobs)
	s.mu.Unlock()
}

// SetRunnerLog stores the last log lines captured from a runner before its
// container/VM was removed, so failures stay diagnosable after cleanup.
func (s *State) SetRunnerLog(runnerName, log string) {
	if runnerName == "" || log == "" {
		return
	}
	if len(log) > maxRunnerLogBytes {
		log = log[len(log)-maxRunnerLogBytes:]
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, exists := s.runnerLogs[runnerName]; !exists {
		s.runnerLogOrder = append(s.runnerLogOrder, runnerName)
		if len(s.runnerLogOrder) > maxRunnerLogs {
			oldest := s.runnerLogOrder[0]
			s.runnerLogOrder = s.runnerLogOrder[1:]
			delete(s.runnerLogs, oldest)
		}
	}
	s.runnerLogs[runnerName] = log
}

// GetRunnerLog returns a retained runner log tail, if any.
func (s *State) GetRunnerLog(runnerName string) (string, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	log, ok := s.runnerLogs[runnerName]
	return log, ok
}

// RequestHistoryRefresh asks the autoscaler to re-fetch job history on its next cycle
// (used right after a retry so the UI reflects the change quickly).
func (s *State) RequestHistoryRefresh() {
	s.mu.Lock()
	s.historyDirty = true
	s.mu.Unlock()
}

// ConsumeHistoryRefresh returns true once per RequestHistoryRefresh call.
func (s *State) ConsumeHistoryRefresh() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	d := s.historyDirty
	s.historyDirty = false
	return d
}
