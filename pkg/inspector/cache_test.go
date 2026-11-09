package inspector

import (
	"testing"
)

func TestWorkflowCache(t *testing.T) {
	cache := NewWorkflowCache()

	// Workflow YAML cache
	if _, ok := cache.GetWorkflow("key-1"); ok {
		t.Errorf("expected miss on key-1")
	}
	cache.SetWorkflow("key-1", "workflow content")
	val, ok := cache.GetWorkflow("key-1")
	if !ok || val != "workflow content" {
		t.Errorf("expected hit on key-1, got %s", val)
	}

	// Job result cache
	if _, ok := cache.GetJobResult("job-key"); ok {
		t.Errorf("expected miss on job-key")
	}
	cache.SetJobResult("job-key", ReasonSystemd)
	if res, ok := cache.GetJobResult("job-key"); !ok || res != ReasonSystemd {
		t.Errorf("expected hit %q on job-key, got %q", ReasonSystemd, res)
	}

	cache.Clear()
	if _, ok := cache.GetWorkflow("key-1"); ok {
		t.Errorf("expected miss after clear")
	}
	if _, ok := cache.GetJobResult("job-key"); ok {
		t.Errorf("expected job result miss after clear")
	}
}
