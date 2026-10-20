package provider

import (
	"context"
	"sync"

	"github.com/el-j/run-zero/pkg/state"
)

// Manager coordinates multiple CI providers (GitHub, GitLab SaaS, GitLab Self-Hosted).
type Manager struct {
	mu        sync.RWMutex
	providers map[string]CIProvider
	order     []string
}

// NewManager creates an empty multi-provider registry.
func NewManager() *Manager {
	return &Manager{
		providers: make(map[string]CIProvider),
		order:     make([]string, 0),
	}
}

// Register adds or updates a provider instance.
func (m *Manager) Register(p CIProvider) {
	m.mu.Lock()
	defer m.mu.Unlock()
	id := p.ID()
	if _, exists := m.providers[id]; !exists {
		m.order = append(m.order, id)
	}
	m.providers[id] = p
}

// Get returns a registered provider by its ID.
func (m *Manager) Get(id string) (CIProvider, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	p, ok := m.providers[id]
	return p, ok
}

// All returns all registered providers in registration order.
func (m *Manager) All() []CIProvider {
	m.mu.RLock()
	defer m.mu.RUnlock()
	res := make([]CIProvider, len(m.order))
	for i, id := range m.order {
		res[i] = m.providers[id]
	}
	return res
}

// FetchAllRemoteRunners concurrently collects remote and cloud runners from all registered providers.
func (m *Manager) FetchAllRemoteRunners(ctx context.Context) ([]state.RunnerInfo, []error) {
	providers := m.All()
	if len(providers) == 0 {
		return nil, nil
	}

	type result struct {
		runners []state.RunnerInfo
		err     error
	}

	results := make(chan result, len(providers))
	var wg sync.WaitGroup

	for _, p := range providers {
		wg.Add(1)
		go func(prov CIProvider) {
			defer wg.Done()
			runners, err := prov.FetchRemoteRunners(ctx)
			results <- result{runners: runners, err: err}
		}(p)
	}

	wg.Wait()
	close(results)

	var allRunners []state.RunnerInfo
	var errs []error

	for res := range results {
		if res.err != nil {
			errs = append(errs, res.err)
		} else {
			allRunners = append(allRunners, res.runners...)
		}
	}

	return allRunners, errs
}

// MergeRunners combines locally discovered runners (from Docker / OrbStack) with remote/cloud runners.
// If a runner is present in both local and remote discovery, local execution details are preserved.
func MergeRunners(localRunners, remoteRunners []state.RunnerInfo) []state.RunnerInfo {
	seenLocal := make(map[string]bool)
	result := make([]state.RunnerInfo, 0, len(localRunners)+len(remoteRunners))

	// 1. Add all local runners (they have live runtime stats like JobID, RunID, logs)
	for _, lr := range localRunners {
		seenLocal[lr.Name] = true
		seenLocal[lr.ID] = true
		origin := "local"
		if lr.Origin == nil {
			lr.Origin = &origin
		}
		result = append(result, lr)
	}

	// 2. Add remote/cloud runners that are not already tracked locally
	for _, rr := range remoteRunners {
		if seenLocal[rr.Name] || seenLocal[rr.ID] {
			continue
		}
		result = append(result, rr)
	}

	return result
}
