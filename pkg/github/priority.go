package github

import (
	"strings"
	"sync"
)

// PriorityManager manages repository ordering weights and pause states, persisted to JSON.
type PriorityManager struct {
	filePath string
	mu       sync.RWMutex
	priority []string
	paused   map[string]bool
}

// NewPriorityManager loads or creates a priority manager file.
func NewPriorityManager(filePath string, initialPriority, initialPaused []string) (*PriorityManager, error) {
	pm := &PriorityManager{
		filePath: filePath,
		priority: make([]string, 0),
		paused:   make(map[string]bool),
	}

	for _, p := range initialPriority {
		if strings.TrimSpace(p) != "" {
			pm.priority = append(pm.priority, strings.TrimSpace(p))
		}
	}
	for _, p := range initialPaused {
		if strings.TrimSpace(p) != "" {
			pm.paused[strings.TrimSpace(p)] = true
		}
	}

	if filePath != "" {
		_ = pm.Load()
	}

	return pm, nil
}

// IsPaused reports whether repo is currently paused from runner allocation.
func (pm *PriorityManager) IsPaused(repo string) bool {
	pm.mu.RLock()
	defer pm.mu.RUnlock()
	return pm.paused[repo]
}

// SortRepos reorders repos so that priority repos appear first in priority order.
func (pm *PriorityManager) SortRepos(repos []string) []string {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	prioMap := make(map[string]int)
	for idx, name := range pm.priority {
		prioMap[name] = idx
	}

	result := make([]string, len(repos))
	copy(result, repos)

	for i := 0; i < len(result)-1; i++ {
		for j := i + 1; j < len(result); j++ {
			p1, ok1 := prioMap[result[i]]
			p2, ok2 := prioMap[result[j]]

			if ok1 && ok2 {
				if p2 < p1 {
					result[i], result[j] = result[j], result[i]
				}
			} else if !ok1 && ok2 {
				result[i], result[j] = result[j], result[i]
			}
		}
	}
	return result
}

// GetState returns current priority and paused repository slices.
func (pm *PriorityManager) GetState() ([]string, []string) {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	prio := make([]string, len(pm.priority))
	copy(prio, pm.priority)

	paused := make([]string, 0, len(pm.paused))
	for p := range pm.paused {
		paused = append(paused, p)
	}
	return prio, paused
}
