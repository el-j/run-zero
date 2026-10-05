package driver

import (
	"sync"

	"github.com/el-j/run-zero/pkg/state"
)

// InstanceStore maintains active runner instances and reconciles state.
type InstanceStore struct {
	mu        sync.RWMutex
	filePath  string
	instances map[string]state.RunnerInfo
}

// NewInstanceStore creates an in-memory or persisted instance store.
func NewInstanceStore(filePath string) *InstanceStore {
	store := &InstanceStore{
		filePath:  filePath,
		instances: make(map[string]state.RunnerInfo),
	}
	if filePath != "" {
		_ = store.Load()
	}
	return store
}

// Register adds or updates a runner instance in the store.
func (s *InstanceStore) Register(info state.RunnerInfo) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.instances[info.ID] = info
	_ = s.saveLocked()
}

// Unregister removes a runner instance from the store.
func (s *InstanceStore) Unregister(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.instances, id)
	_ = s.saveLocked()
}

// Get retrieves a runner instance by ID.
func (s *InstanceStore) Get(id string) (state.RunnerInfo, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	info, ok := s.instances[id]
	return info, ok
}

// List returns a copy of all tracked runner instances.
func (s *InstanceStore) List() []state.RunnerInfo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	res := make([]state.RunnerInfo, 0, len(s.instances))
	for _, v := range s.instances {
		res = append(res, v)
	}
	return res
}

// UpdateStatus updates the status and state strings for an instance.
func (s *InstanceStore) UpdateStatus(id, status, runState string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	info, ok := s.instances[id]
	if !ok {
		return false
	}
	info.Status = status
	info.State = runState
	s.instances[id] = info
	_ = s.saveLocked()
	return true
}

// Reconcile compares stored instances with live discovered instances to identify dead and orphaned runners.
func (s *InstanceStore) Reconcile(discovered []state.RunnerInfo) (deadIDs []string, orphans []state.RunnerInfo) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	discoveredMap := make(map[string]bool)
	for _, d := range discovered {
		discoveredMap[d.ID] = true
	}

	for id := range s.instances {
		if !discoveredMap[id] {
			deadIDs = append(deadIDs, id)
		}
	}

	for _, d := range discovered {
		if _, ok := s.instances[d.ID]; !ok {
			orphans = append(orphans, d)
		}
	}

	return deadIDs, orphans
}
