package parity

import (
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/inspector"
	"github.com/el-j/run-zero/pkg/scheduling"
	"github.com/el-j/run-zero/pkg/sizing"
)

// EvaluateTestCase plans a scenario's job with the autoscaler's own decision
// logic (pkg/scheduling, default configuration) and compares the result with
// the scenario's expected decision.
func EvaluateTestCase(tc TestCase) (Decision, Result) {
	cfg, _ := config.LoadConfig(config.MapEnv{})
	override, _ := arch.NewNativeArchOverride(tc.ArchOverride, tc.HostArch)
	policy := scheduling.Policy{
		Backend:         cfg.RunnerBackend,
		AutoRouteVM:     cfg.AutoRouteVM,
		VMTriggerLabels: cfg.VMTriggerLabels,
		RunnerArch:      cfg.RunnerArch,
		ArchOverride:    override,
		MaxRunners:      tc.MaxRunners,
		Host:            sizing.HostCapacity{CPUs: tc.CapacityCPUs, MemoryMiB: tc.CapacityMemoryMB},
	}
	declares := inspector.JobUsesServicesOrContainer(tc.WorkflowYAML, tc.JobName)
	d := scheduling.Plan(policy, scheduling.Job{
		Repo:             tc.Repo,
		Name:             tc.JobName,
		Labels:           tc.JobLabels,
		DeclaresServices: declares != nil && *declares,
	})

	actual := Decision{
		Backend:      d.Backend,
		Arch:         d.Arch,
		RequiresVM:   d.RequiresVM(),
		TriggerMatch: d.Trigger,
		CPUs:         fmt.Sprintf("%d", d.CPUs),
		MemoryMB:     d.MemoryMiB,
	}

	res := Result{Name: tc.Name, Passed: true}
	var diffs []string
	check := func(field string, got, want any) {
		if got != want {
			diffs = append(diffs, fmt.Sprintf("%s mismatch: got %v, want %v", field, got, want))
		}
	}
	check("backend", actual.Backend, tc.Expected.Backend)
	check("arch", actual.Arch, tc.Expected.Arch)
	check("requiresVM", actual.RequiresVM, tc.Expected.RequiresVM)
	check("trigger", actual.TriggerMatch, tc.Expected.TriggerMatch)
	check("cpus", actual.CPUs, tc.Expected.CPUs)
	check("memory", actual.MemoryMB, tc.Expected.MemoryMB)

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
