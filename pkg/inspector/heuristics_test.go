package inspector

import (
	"testing"
)

func TestJobNeedsVM(t *testing.T) {
	// Declared services true
	declared := true
	needsVM, reason := JobNeedsVM(nil, "simple-job", &declared)
	if !needsVM || reason != "services" {
		t.Errorf("expected services reason, got %v (%s)", needsVM, reason)
	}

	// Label trigger
	notDeclared := false
	needsVM, reason = JobNeedsVM([]string{"ubuntu-latest", "postgres"}, "simple-job", &notDeclared)
	if !needsVM || reason != "label:postgres" {
		t.Errorf("expected label:postgres reason, got %v (%s)", needsVM, reason)
	}

	// Name token trigger
	needsVM, reason = JobNeedsVM([]string{"ubuntu-latest"}, "run-e2e-suite", nil)
	if !needsVM || reason != "name:e2e" {
		t.Errorf("expected name:e2e reason, got %v (%s)", needsVM, reason)
	}

	// Simple job - container
	needsVM, reason = JobNeedsVM([]string{"ubuntu-latest"}, "lint-code", &notDeclared)
	if needsVM || reason != "container" {
		t.Errorf("expected container, got %v (%s)", needsVM, reason)
	}
}
