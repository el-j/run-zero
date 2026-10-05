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
