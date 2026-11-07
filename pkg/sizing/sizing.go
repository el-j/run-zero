package sizing

const (
	// ReserveCPUs is the CPU count kept free for the host.
	ReserveCPUs = 1
	// ReserveMemoryMiB is the memory (MiB) kept free for the host.
	ReserveMemoryMiB = 2048
	// MinMemoryMiB is the smallest memory (MiB) a runner may be given.
	MinMemoryMiB = 1024
)

// HostCapacity represents available CPU cores and physical memory in MiB.
type HostCapacity struct {
	CPUs      int
	MemoryMiB int
}

// RunnerSizing describes resource limits allocated per runner.
type RunnerSizing struct {
	CPUs       *int
	MemoryMiB  *int
	Source     string
	Host       HostCapacity
	MaxRunners int
	Warnings   []string
}

// DeriveSizing computes equal share of host resources per runner after safety reserves.
func DeriveSizing(host HostCapacity, maxRunners int) (int, int) {
	runners := max(maxRunners, 1)
	availCPUs := max(host.CPUs-ReserveCPUs, 1)
	availMem := max(host.MemoryMiB-ReserveMemoryMiB, MinMemoryMiB)
	return max(availCPUs/runners, 1), max(availMem/runners, MinMemoryMiB)
}

// ResolveSizing resolves effective sizing from configuration and host metrics.
func ResolveSizing(cpusCfg, memCfg string, maxRunners int, host HostCapacity) RunnerSizing {
	if maxRunners < 1 {
		maxRunners = 4
	}

	derivedCPUs, derivedMem := DeriveSizing(host, maxRunners)
	cpus := ParseCPUs(cpusCfg)
	mem := ParseMemoryMiB(memCfg)

	source := "configured"
	if cpus == nil && mem == nil {
		source = "derived"
	}

	if cpus == nil {
		cpus = &derivedCPUs
	}
	if mem == nil {
		mem = &derivedMem
	}

	warnings := OversubscriptionWarnings(cpus, mem, host, maxRunners)

	return RunnerSizing{
		CPUs:       cpus,
		MemoryMiB:  mem,
		Source:     source,
		Host:       host,
		MaxRunners: maxRunners,
		Warnings:   warnings,
	}
}
