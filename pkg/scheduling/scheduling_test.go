package scheduling

import (
	"testing"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/sizing"
)

var triggers = []string{"vm", "browser", "e2e", "postgres", "db", "dind"}

func TestBackend(t *testing.T) {
	auto := Policy{AutoRouteVM: true, VMTriggerLabels: triggers}
	cases := []struct {
		name          string
		policy        Policy
		job           Job
		backend, trig string
	}{
		{"configured backend wins", Policy{Backend: "docker", AutoRouteVM: true, VMTriggerLabels: triggers}, Job{Labels: []string{"vm"}}, "docker", ""},
		{"label", auto, Job{Name: "unit-tests", Labels: []string{"self-hosted", "vm"}}, "orbstack", "label:vm"},
		{"job name", auto, Job{Name: "Matrix — E2E (mock auth)", Labels: []string{"self-hosted"}}, "orbstack", "name:e2e"},
		{"workflow name", auto, Job{Name: "Matrix — CI", WorkflowName: "E2E"}, "orbstack", "workflow:e2e"},
		{"services", auto, Job{Name: "lint", DeclaresServices: true}, "orbstack", "services"},
		{"no match", auto, Job{Name: "lint", WorkflowName: "Lint & Unit Tests", Labels: []string{"amd64"}}, "docker", ""},
		{"routing off", Policy{VMTriggerLabels: triggers}, Job{Labels: []string{"vm"}, DeclaresServices: true}, "docker", ""},
		{"blank triggers", Policy{AutoRouteVM: true, VMTriggerLabels: []string{"", "  "}}, Job{Name: "e2e"}, "docker", ""},
		{"no triggers", Policy{AutoRouteVM: true}, Job{Name: "e2e"}, "docker", ""},
	}
	for _, c := range cases {
		if b, tr := Backend(c.policy, c.job); b != c.backend || tr != c.trig {
			t.Errorf("%s: got %s/%q, want %s/%q", c.name, b, tr, c.backend, c.trig)
		}
	}
}

func TestArch(t *testing.T) {
	override, _ := arch.NewNativeArchOverride("all", "arm64")
	cases := []struct {
		name   string
		policy Policy
		labels []string
		want   string
	}{
		{"default amd64", Policy{RunnerArch: "both"}, nil, "amd64"},
		{"arm label", Policy{}, []string{"self-hosted", "ARM64"}, "arm64"},
		{"configured arch", Policy{RunnerArch: "arm64"}, []string{"amd64"}, "arm64"},
		{"native override", Policy{ArchOverride: override}, []string{"amd64"}, "arm64"},
		{"emulation label keeps amd64", Policy{ArchOverride: override}, []string{"amd64", "rosetta"}, "amd64"},
	}
	for _, c := range cases {
		if got := Arch(c.policy, Job{Repo: "o/r", Labels: c.labels}); got != c.want {
			t.Errorf("%s: got %s, want %s", c.name, got, c.want)
		}
	}
}

func TestSize(t *testing.T) {
	host := sizing.HostCapacity{CPUs: 9, MemoryMiB: 18432}
	cases := []struct {
		name      string
		policy    Policy
		labels    []string
		cpus, mem int
	}{
		{"defaults when host unknown", Policy{}, nil, DefaultCPUs, DefaultMemoryMiB},
		{"derived from host", Policy{Host: host, MaxRunners: 2}, nil, 4, 8192},
		{"cpus known, memory unknown", Policy{Host: sizing.HostCapacity{CPUs: 9}, MaxRunners: 2}, nil, 4, DefaultMemoryMiB},
		{"config wins over host", Policy{Host: host, MaxRunners: 2, RunnerCPUs: 2, RunnerMemory: "6g"}, nil, 2, 6144},
		{"unparsable memory keeps default", Policy{RunnerMemory: "lots"}, nil, DefaultCPUs, DefaultMemoryMiB},
		{"labels win over config", Policy{RunnerCPUs: 2, RunnerMemory: "6g"}, []string{"4cpu-8gb"}, 4, 8192},
		{"memory-only label", Policy{RunnerCPUs: 2}, []string{"highmem"}, 2, 32768},
	}
	for _, c := range cases {
		if cpus, mem := Size(c.policy, c.labels); cpus != c.cpus || mem != c.mem {
			t.Errorf("%s: got %d/%d, want %d/%d", c.name, cpus, mem, c.cpus, c.mem)
		}
	}
}

func TestPlan(t *testing.T) {
	d := Plan(Policy{AutoRouteVM: true, VMTriggerLabels: triggers}, Job{Name: "browser tests", Labels: []string{"arm64", "large"}})
	want := Decision{Backend: "orbstack", Arch: "arm64", Trigger: "name:browser", CPUs: 4, MemoryMiB: 8192}
	if d != want || !d.RequiresVM() {
		t.Fatalf("got %+v, want %+v", d, want)
	}
	if (Decision{Backend: "docker"}).RequiresVM() {
		t.Fatal("docker must not require a VM")
	}
}
