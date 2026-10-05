package parity

import (
	"strings"
	"testing"
)

func TestBaselineScenarios_100PercentParity(t *testing.T) {
	cases := BaselineScenarios()
	results := RunAllParity(cases)

	for _, r := range results {
		if !r.Passed {
			t.Errorf("Parity test failed for scenario %s: %s", r.Name, r.DiffMsg)
		}
	}
}

func TestEvaluateTestCase_MismatchReporting(t *testing.T) {
	tc := TestCase{
		Name:             "mismatched-case",
		Repo:             "el-j/run-zero",
		WorkflowYAML:     "name: T\njobs:\n  t:\n    runs-on: self-hosted\n",
		JobName:          "t",
		JobLabels:        []string{"self-hosted"},
		HostArch:         "arm64",
		ArchOverride:     "off",
		CapacityCPUs:     4,
		CapacityMemoryMB: 4096,
		MaxRunners:       1,
		Expected: Decision{
			Backend:    "orbstack-vm", // actual will be docker
			Arch:       "amd64",       // actual will be arm64
			RequiresVM: true,          // actual will be false
			CPUs:       "99",          // actual will be 3
			MemoryMB:   9999,          // actual will be 3276
		},
	}

	actual, res := EvaluateTestCase(tc)
	if res.Passed {
		t.Fatalf("expected mismatch failure, but passed: %+v", actual)
	}
	if !strings.Contains(res.DiffMsg, "backend mismatch") ||
		!strings.Contains(res.DiffMsg, "arch mismatch") ||
		!strings.Contains(res.DiffMsg, "requiresVM mismatch") ||
		!strings.Contains(res.DiffMsg, "cpus mismatch") ||
		!strings.Contains(res.DiffMsg, "memory mismatch") {
		t.Fatalf("diff message missing expected errors: %s", res.DiffMsg)
	}
}
