package inspector

import (
	"testing"
)

func TestJobUsesServicesOrContainer(t *testing.T) {
	yamlContent := `
jobs:
  unit:
    name: "Unit Tests"
    steps: []
  e2e:
    name: "E2E Tests"
    services:
      redis:
        image: redis
`

	// Match by rendered name
	res := JobUsesServicesOrContainer(yamlContent, "Unit Tests")
	if res == nil || *res != false {
		t.Errorf("expected false for Unit Tests, got %v", res)
	}

	// Match by ID
	resE2E := JobUsesServicesOrContainer(yamlContent, "e2e")
	if resE2E == nil || *resE2E != true {
		t.Errorf("expected true for e2e, got %v", resE2E)
	}

	// Match with matrix suffix
	resMatrix := JobUsesServicesOrContainer(yamlContent, "E2E Tests (shard-1, shard-2)")
	if resMatrix == nil || *resMatrix != true {
		t.Errorf("expected true for matrix E2E Tests, got %v", resMatrix)
	}

	// Non-matching job
	if resMissing := JobUsesServicesOrContainer(yamlContent, "Non Existent"); resMissing != nil {
		t.Errorf("expected nil for non existent job, got %v", resMissing)
	}

	// Empty inputs
	if resEmpty := JobUsesServicesOrContainer("", "test"); resEmpty != nil {
		t.Errorf("expected nil for empty yaml")
	}
	if resEmptyJob := JobUsesServicesOrContainer(yamlContent, ""); resEmptyJob != nil {
		t.Errorf("expected nil for empty job name")
	}
	if resNoJobs := JobUsesServicesOrContainer("name: test", "test"); resNoJobs != nil {
		t.Errorf("expected nil when no jobs parsed")
	}
}
