package inspector

import (
	"sync"
)

// WorkflowCache caches fetched workflow YAMLs and parsed job inspection results.
type WorkflowCache struct {
	mu         sync.RWMutex
	workflows  map[string]string
	jobResults map[string]*bool
}

// NewWorkflowCache creates an in-memory workflow cache.
func NewWorkflowCache() *WorkflowCache {
	return &WorkflowCache{
		workflows:  make(map[string]string),
		jobResults: make(map[string]*bool),
	}
}

// GetWorkflow retrieves cached workflow YAML text.
func (c *WorkflowCache) GetWorkflow(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.workflows[key]
	return val, ok
}

// SetWorkflow caches workflow YAML text for a key.
func (c *WorkflowCache) SetWorkflow(key, content string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.workflows[key] = content
}

// GetJobResult retrieves cached service/container declaration boolean.
func (c *WorkflowCache) GetJobResult(key string) (*bool, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.jobResults[key]
	return val, ok
}

// SetJobResult caches the service/container declaration boolean.
func (c *WorkflowCache) SetJobResult(key string, res *bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.jobResults[key] = res
}

// Clear flushes all cached workflows and job results.
func (c *WorkflowCache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.workflows = make(map[string]string)
	c.jobResults = make(map[string]*bool)
}
