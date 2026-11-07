package scheduling

import (
	"strings"
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

func TestSize_Unlimited(t *testing.T) {
	p := Policy{Unlimited: true, RunnerCPUs: 4, RunnerMemory: "8g", Host: sizing.HostCapacity{CPUs: 9, MemoryMiB: 18432}, MaxRunners: 2}
	if cpus, mem := Size(p, nil); cpus != 0 || mem != 0 {
		t.Fatalf("unlimited must drop limits, got %d/%d", cpus, mem)
	}
	if cpus, mem := Size(p, []string{"large"}); cpus != 4 || mem != 8192 {
		t.Fatalf("labels still size an unlimited fleet, got %d/%d", cpus, mem)
	}
}

func TestSizingSummary(t *testing.T) {
	host := sizing.HostCapacity{CPUs: 9, MemoryMiB: 18432}
	summary, warnings := SizingSummary(Policy{Host: host, MaxRunners: 2})
	if summary != "4 CPU / 8192 MiB per runner, up to 2 runners (host: 9 CPU / 18432 MiB)" || len(warnings) != 0 {
		t.Fatalf("derived: %q %v", summary, warnings)
	}
	_, warnings = SizingSummary(Policy{Host: host, MaxRunners: 4, RunnerCPUs: 4})
	if len(warnings) != 1 || !strings.Contains(warnings[0], "exceeds host's 9 CPUs") {
		t.Fatalf("oversubscription: %v", warnings)
	}
	summary, warnings = SizingSummary(Policy{Unlimited: true, Host: host, MaxRunners: 2})
	if !strings.HasPrefix(summary, "unlimited CPU / unlimited memory per runner") || len(warnings) != 1 {
		t.Fatalf("unlimited: %q %v", summary, warnings)
	}
	if summary, warnings = SizingSummary(Policy{MaxRunners: 3}); summary != "3 CPU / 4096 MiB per runner, up to 3 runners" || warnings != nil {
		t.Fatalf("unknown host: %q %v", summary, warnings)
	}
}
