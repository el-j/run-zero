package state

import "sync"

// State maintains the thread-safe global runtime state of the RunZero daemon.
type State struct {
	mu                 sync.RWMutex
	version            string
	autoscalerStatus   string
	runners            []RunnerInfo
	queuedJobs         []QueuedJob
	maxRunners         int
	repoPriority       []string
	pausedRepos        []string
	rateLimitRemaining *int
	rateLimitLimit     *int
	actionsBilling     *ActionsBilling
	logs               []LogEntry
	maxLogs            int
	broker             *Broker
}

// NewState creates an initialized State instance.
func NewState(maxRunners int, version string, broker *Broker) *State {
	if broker == nil {
		broker = NewBroker()
	}
	return &State{
		version:          version,
		autoscalerStatus: "running",
		runners:          make([]RunnerInfo, 0),
		queuedJobs:       make([]QueuedJob, 0),
		maxRunners:       maxRunners,
		repoPriority:     make([]string, 0),
		pausedRepos:      make([]string, 0),
		logs:             make([]LogEntry, 0),
		maxLogs:          500,
		broker:           broker,
	}
}

// Broker returns the state's event broker.
func (s *State) Broker() *Broker {
	return s.broker
}

// GetSnapshot returns an immutable point-in-time FleetState snapshot.
func (s *State) GetSnapshot() FleetState {
	s.mu.RLock()
	defer s.mu.RUnlock()

	busy := 0
	runnersCopy := make([]RunnerInfo, len(s.runners))
	for i, r := range s.runners {
		runnersCopy[i] = r
		if r.Status == "busy" || r.Status == "running" {
			busy++
		}
	}

	free := s.maxRunners - busy
	if free < 0 {
		free = 0
	}

	jobsCopy := make([]QueuedJob, len(s.queuedJobs))
	copy(jobsCopy, s.queuedJobs)

	prioCopy := make([]string, len(s.repoPriority))
	copy(prioCopy, s.repoPriority)

	pausedCopy := make([]string, len(s.pausedRepos))
	copy(pausedCopy, s.pausedRepos)

	return FleetState{
		Runners:            runnersCopy,
		QueuedJobs:         jobsCopy,
		BusyRunners:        busy,
		MaxRunners:         s.maxRunners,
		FreeSlots:          free,
		RepoPriority:       prioCopy,
		PausedRepos:        pausedCopy,
		RateLimitRemaining: s.rateLimitRemaining,
		RateLimitLimit:     s.rateLimitLimit,
		ActionsBilling:     s.actionsBilling,
		AutoscalerStatus:   s.autoscalerStatus,
		Version:            s.version,
	}
}

// AppendLog adds a message to the in-memory circular log buffer and emits an SSE log event.
func (s *State) AppendLog(message string) {
	s.mu.Lock()
	entry := LogEntry{
		Timestamp: newTimestamp(),
		Message:   message,
	}
	s.logs = append(s.logs, entry)
	if len(s.logs) > s.maxLogs {
		s.logs = s.logs[len(s.logs)-s.maxLogs:]
	}
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "log", Data: entry})
}

// GetLogs returns a copy of current log buffer entries.
func (s *State) GetLogs() []LogEntry {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]LogEntry, len(s.logs))
	copy(result, s.logs)
	return result
}

// SetRepoPriority updates priority steering order and paused repositories.
func (s *State) SetRepoPriority(priority []string, paused []string) {
	s.mu.Lock()
	s.repoPriority = make([]string, len(priority))
	copy(s.repoPriority, priority)
	s.pausedRepos = make([]string, len(paused))
	copy(s.pausedRepos, paused)
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "state", Data: s.GetSnapshot()})
}

// UpdateFleet updates the runner list and queued jobs, triggering an SSE state broadcast.
func (s *State) UpdateFleet(runners []RunnerInfo, jobs []QueuedJob) {
	s.mu.Lock()
	s.runners = make([]RunnerInfo, len(runners))
	copy(s.runners, runners)
	s.queuedJobs = make([]QueuedJob, len(jobs))
	copy(s.queuedJobs, jobs)
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "state", Data: s.GetSnapshot()})
}

// SetAutoscalerStatus updates the engine status string (e.g. running, paused, stopped).
func (s *State) SetAutoscalerStatus(status string) {
	s.mu.Lock()
	s.autoscalerStatus = status
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "state", Data: s.GetSnapshot()})
}

// SetMaxRunners dynamically updates the configured max runners slot capacity.
func (s *State) SetMaxRunners(max int) {
	s.mu.Lock()
	s.maxRunners = max
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "state", Data: s.GetSnapshot()})
}

// SetRateLimit sets the remaining and limit counts for GitHub API calls.
func (s *State) SetRateLimit(remaining *int, limit *int) {
	s.mu.Lock()
	s.rateLimitRemaining = remaining
	s.rateLimitLimit = limit
	s.mu.Unlock()

	s.broker.Broadcast(Event{Type: "state", Data: s.GetSnapshot()})
}
