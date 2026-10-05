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
	tVal := true
	cache.SetJobResult("job-key", &tVal)
	res, ok := cache.GetJobResult("job-key")
	if !ok || res == nil || *res != true {
		t.Errorf("expected hit true on job-key")
	}

	cache.Clear()
	if _, ok := cache.GetWorkflow("key-1"); ok {
		t.Errorf("expected miss after clear")
	}
}
