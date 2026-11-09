// Package scheduling decides where and how a queued job runs: which backend
// (container or VM), which architecture, and how much CPU and memory its runner
// gets. It is pure, so the autoscaler and the `runzero parity` self-check share
// exactly the same decisions.
package scheduling

import (
	"fmt"
	"strings"
	"unicode"

	"github.com/el-j/run-zero/pkg/arch"
	"github.com/el-j/run-zero/pkg/sizing"
)

// Default runner size when neither job labels, configuration nor host
// capacity say otherwise.
const (
	DefaultCPUs      = 3
	DefaultMemoryMiB = 4096
)

// Policy is the operator configuration a decision depends on.
type Policy struct {
	// Backend is RUNNER_BACKEND; "" or "auto" lets the job decide.
	Backend         string
	AutoRouteVM     bool
	VMTriggerLabels []string
	// RunnerArch is RUNNER_ARCH: "arm64", "amd64", or "both"/"" (job decides).
	RunnerArch   string
	ArchOverride *arch.NativeArchOverride
	// HostArch is the host's CPU ("arm64" or "amd64"); a job without an arch
	// label runs on it natively. Empty means unknown, which falls back to amd64.
	HostArch     string
	RunnerCPUs   int
	RunnerMemory string
	// Unlimited (RUNNER_SIZING=unlimited) drops CPU/memory limits; sizes a
	// job requests through its labels still apply.
	Unlimited  bool
	MaxRunners int
	// Host is the machine's capacity; zero means unknown.
	Host sizing.HostCapacity
}

// Job is what is known about a queued job when it is scheduled.
type Job struct {
	Repo         string
	Name         string
	WorkflowName string
	Labels       []string
	// VMReason is why the job's workflow needs a VM rather than a container
	// runner (an inspector.Reason* value: services, docker-compose, ...), or "".
	VMReason string
}

// Decision is where and how a job runs.
type Decision struct {
	Backend string
	Arch    string
	// Trigger explains a VM routing: the workflow's VM reason (e.g.
	// "services", "docker-compose"), "label:<l>", "name:<t>" or
	// "workflow:<t>"; empty when the job runs in a container.
	Trigger   string
	CPUs      int
	MemoryMiB int
}

// RequiresVM reports whether the decision runs the job in a VM.
func (d Decision) RequiresVM() bool { return d.Backend != "docker" }

// Plan decides backend, architecture and size for job under policy.
func Plan(p Policy, job Job) Decision {
	backend, trigger := Backend(p, job)
	cpus, mem := Size(p, job.Labels)
	return Decision{Backend: backend, Arch: Arch(p, job), Trigger: trigger, CPUs: cpus, MemoryMiB: mem}
}

// Backend picks the runner backend. A configured RUNNER_BACKEND wins; with
// "auto" and AUTO_ROUTE_VM, a job is routed to an OrbStack VM when its
// workflow needs one (services, docker compose, bind mounts, ...; see
// inspector.JobVMReason), or a VM trigger matches its labels, name or
// workflow name. The trigger says which.
func Backend(p Policy, job Job) (backend, trigger string) {
	if p.Backend != "" && p.Backend != "auto" {
		return p.Backend, ""
	}
	if p.AutoRouteVM {
		if job.VMReason != "" {
			return "orbstack", job.VMReason
		}
		if t := vmTrigger(job, p.VMTriggerLabels); t != "" {
			return "orbstack", t
		}
	}
	return "docker", ""
}

// vmTrigger returns the first VM trigger matching the job's labels, name or
// workflow name (as "label:", "name:" or "workflow:" plus the token), or "".
func vmTrigger(job Job, triggers []string) string {
	set := make(map[string]bool, len(triggers))
	for _, t := range triggers {
		if tt := strings.ToLower(strings.TrimSpace(t)); tt != "" {
			set[tt] = true
		}
	}
	if len(set) == 0 {
		return ""
	}
	for _, label := range job.Labels {
		for _, token := range tokenizeLower(label) {
			if set[token] {
				return "label:" + token
			}
		}
	}
	for _, src := range []struct{ kind, text string }{{"name", job.Name}, {"workflow", job.WorkflowName}} {
		for _, token := range tokenizeLower(src.text) {
			if set[token] {
				return src.kind + ":" + token
			}
		}
	}
	return ""
}

func tokenizeLower(input string) []string {
	return strings.FieldsFunc(strings.ToLower(input), func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsDigit(r)
	})
}

// Arch picks the runner architecture: RUNNER_ARCH when it names one, else
// the job's arch label (arm64/aarch64/arm or amd64/x64/x86_64), else the
// host's own arch, so unlabelled jobs run natively. The native arch override
// may then run an amd64 job natively on an arm64 host.
func Arch(p Policy, job Job) string {
	jobArch := p.HostArch
	if jobArch == "" {
		jobArch = "amd64"
	}
	if p.RunnerArch != "both" && p.RunnerArch != "" {
		jobArch = p.RunnerArch
	} else if labelled := labelArch(job.Labels); labelled != "" {
		jobArch = labelled
	}
	if p.ArchOverride != nil {
		return p.ArchOverride.ArchFor(jobArch, job.Labels, job.Repo)
	}
	return jobArch
}

// labelArch is the architecture a job's labels ask for, or "".
func labelArch(labels []string) string {
	for _, l := range labels {
		switch strings.ToLower(l) {
		case "arm64", "aarch64", "arm":
			return "arm64"
		case "amd64", "x64", "x86_64":
			return "amd64"
		}
	}
	return ""
}

// Size returns the runner's CPUs and memory (MiB). Sizes requested through job
// labels (e.g. "4cpu-8gb", "large", "highmem") win over RUNNER_CPUS and
// RUNNER_MEMORY, which win over an equal share of the host's capacity (after
// a reserve) per MAX_RUNNERS, or DefaultCPUs/DefaultMemoryMiB when the host's
// capacity is unknown.
func Size(p Policy, labels []string) (cpus, memMiB int) {
	if p.Unlimited {
		return labelSize(0, 0, labels)
	}
	cpus, memMiB = DefaultCPUs, DefaultMemoryMiB
	if p.Host.CPUs > 0 {
		cpus, _ = sizing.DeriveSizing(p.Host, p.MaxRunners)
	}
	if p.Host.MemoryMiB > 0 {
		_, memMiB = sizing.DeriveSizing(p.Host, p.MaxRunners)
	}
	if p.RunnerCPUs > 0 {
		cpus = p.RunnerCPUs
	}
	if p.RunnerMemory != "" {
		if m := sizing.ParseMemoryMiB(p.RunnerMemory); m != nil {
			memMiB = *m
		}
	}
	return labelSize(cpus, memMiB, labels)
}

// labelSize applies the sizes requested through job labels over cpus/memMiB.
func labelSize(cpus, memMiB int, labels []string) (int, int) {
	labelCPUs, labelMem := sizing.ParseLabelSizing(labels)
	if labelCPUs != nil {
		cpus = *labelCPUs
	}
	if labelMem != nil {
		memMiB = *labelMem
	}
	return cpus, memMiB
}

// SizingSummary describes the per-runner size for a job without sizing labels,
// with warnings when MAX_RUNNERS such runners oversubscribe the host.
func SizingSummary(p Policy) (summary string, warnings []string) {
	cpus, mem := Size(p, nil)
	var cpusPtr, memPtr *int
	cpuText, memText := "unlimited CPU", "unlimited memory"
	if cpus > 0 {
		cpusPtr, cpuText = &cpus, fmt.Sprintf("%d CPU", cpus)
	}
	if mem > 0 {
		memPtr, memText = &mem, fmt.Sprintf("%d MiB", mem)
	}
	summary = fmt.Sprintf("%s / %s per runner, up to %d runners", cpuText, memText, p.MaxRunners)
	if p.Host.CPUs > 0 {
		summary += fmt.Sprintf(" (host: %d CPU / %d MiB)", p.Host.CPUs, p.Host.MemoryMiB)
		warnings = sizing.OversubscriptionWarnings(cpusPtr, memPtr, p.Host, p.MaxRunners)
	}
	return summary, warnings
}
