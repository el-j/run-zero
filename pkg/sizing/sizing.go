package sizing

const (
	ReserveCPUs      = 1
	ReserveMemoryMiB = 2048
	MinMemoryMiB     = 1024
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
	runners := maxRunners
	if runners < 1 {
		runners = 1
	}

	availCPUs := host.CPUs - ReserveCPUs
	if availCPUs < 1 {
		availCPUs = 1
	}
	cpus := availCPUs / runners
	if cpus < 1 {
		cpus = 1
	}

	availMem := host.MemoryMiB - ReserveMemoryMiB
	if availMem < MinMemoryMiB {
		availMem = MinMemoryMiB
	}
	mem := availMem / runners
	if mem < MinMemoryMiB {
		mem = MinMemoryMiB
	}

	return cpus, mem
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
