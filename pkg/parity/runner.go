package parity

import (
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/inspector"
	"github.com/el-j/run-zero/pkg/sizing"
)

// EvaluateTestCase evaluates a single parity test scenario against Go engine packages.
func EvaluateTestCase(tc TestCase) (Decision, Result) {
	declaresServices := inspector.JobUsesServicesOrContainer(tc.WorkflowYAML, tc.JobName)
	reqVM, trigger := inspector.JobNeedsVM(tc.JobLabels, tc.JobName, declaresServices)

	backend := "docker"
	if reqVM {
		backend = "orbstack-vm"
	}

	initialArch := "arm64"
	for _, l := range tc.JobLabels {
		if strings.EqualFold(l, "amd64") || strings.EqualFold(l, "x64") || strings.EqualFold(l, "x86_64") {
			initialArch = "amd64"
			break
		}
	}

	override, _ := arch.NewNativeArchOverride(tc.ArchOverride, tc.HostArch)
	effectiveArch := override.ArchFor(initialArch, tc.JobLabels, tc.Repo)

	sizingRes := sizing.ResolveSizing("", "", tc.MaxRunners, sizing.HostCapacity{
		CPUs:      tc.CapacityCPUs,
		MemoryMiB: tc.CapacityMemoryMB,
	})

	cpus := ""
	if sizingRes.CPUs != nil {
		cpus = fmt.Sprintf("%d", *sizingRes.CPUs)
	}
	mem := 0
	if sizingRes.MemoryMiB != nil {
		mem = *sizingRes.MemoryMiB
	}

	actual := Decision{
		Backend:      backend,
		Arch:         effectiveArch,
		RequiresVM:   reqVM,
		TriggerMatch: trigger,
		CPUs:         cpus,
		MemoryMB:     mem,
	}

	res := Result{Name: tc.Name, Passed: true}
	var diffs []string

	if actual.Backend != tc.Expected.Backend {
		diffs = append(diffs, fmt.Sprintf("backend mismatch: got %s, want %s", actual.Backend, tc.Expected.Backend))
	}
	if actual.Arch != tc.Expected.Arch {
		diffs = append(diffs, fmt.Sprintf("arch mismatch: got %s, want %s", actual.Arch, tc.Expected.Arch))
	}
	if actual.RequiresVM != tc.Expected.RequiresVM {
		diffs = append(diffs, fmt.Sprintf("requiresVM mismatch: got %v, want %v", actual.RequiresVM, tc.Expected.RequiresVM))
	}
	if actual.CPUs != tc.Expected.CPUs {
		diffs = append(diffs, fmt.Sprintf("cpus mismatch: got %s, want %s", actual.CPUs, tc.Expected.CPUs))
	}
	if actual.MemoryMB != tc.Expected.MemoryMB {
		diffs = append(diffs, fmt.Sprintf("memory mismatch: got %d, want %d", actual.MemoryMB, tc.Expected.MemoryMB))
	}

	if len(diffs) > 0 {
		res.Passed = false
		res.DiffMsg = strings.Join(diffs, "; ")
	}

	return actual, res
}

// RunAllParity evaluates all given test scenarios.
func RunAllParity(cases []TestCase) []Result {
	results := make([]Result, len(cases))
	for i, tc := range cases {
		_, res := EvaluateTestCase(tc)
		results[i] = res
	}
	return results
}
