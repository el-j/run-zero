package inspector

import (
	"testing"
)

func TestParseWorkflowJobs(t *testing.T) {
	yamlContent := `
name: CI
on: [push]

jobs:
  lint:
    name: "Code Lint"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
    steps:
      - run: make test

  container-job:
    name: 'Container Build'
    container:
      image: node:18
    steps:
      - run: npm test
`

	jobs := ParseWorkflowJobs(yamlContent)
	if len(jobs) != 3 {
		t.Fatalf("expected 3 jobs, got %d", len(jobs))
	}

	if jobs[0].JobID != "lint" || jobs[0].JobName != "Code Lint" || jobs[0].HasServices {
		t.Errorf("unexpected job 0: %+v", jobs[0])
	}
	if jobs[1].JobID != "test" || !jobs[1].HasServices {
		t.Errorf("unexpected job 1: %+v", jobs[1])
	}
	if jobs[2].JobID != "container-job" || jobs[2].JobName != "Container Build" || !jobs[2].HasServices {
		t.Errorf("unexpected job 2: %+v", jobs[2])
	}
}

func TestParseWorkflowJobs_EdgeCases(t *testing.T) {
	if unquote("plain") != "plain" {
		t.Errorf("expected plain")
	}

	if jobs := ParseWorkflowJobs("no jobs section"); jobs != nil {
		t.Errorf("expected nil for missing jobs section")
	}

	malformed := `
jobs:
  # comment
  key with spaces:
    steps: []
  - invalid list under jobs
  valid:
    steps: []
`
	jobs := ParseWorkflowJobs(malformed)
	if len(jobs) != 1 || jobs[0].JobID != "valid" {
		t.Errorf("unexpected jobs: %+v", jobs)
	}

	// Test MatrixBase
	if MatrixBase("Build (matrix-1, opt)") != "Build" {
		t.Errorf("expected matrix base 'Build', got '%s'", MatrixBase("Build (matrix-1, opt)"))
	}
	if MatrixBase("Simple") != "Simple" {
		t.Errorf("expected 'Simple', got '%s'", MatrixBase("Simple"))
	}
}
