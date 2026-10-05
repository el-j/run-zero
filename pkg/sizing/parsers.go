package sizing

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

var memoryRe = regexp.MustCompile(`^\s*(\d+(?:\.\d+)?)\s*([kmgt]?)i?b?\s*$`)

// ParseMemoryMiB converts memory strings like "4G", "2048M", "512MiB", "4096" to MiB.
func ParseMemoryMiB(value string) *int {
	m := memoryRe.FindStringSubmatch(strings.ToLower(value))
	if m == nil {
		return nil
	}

	num, err := strconv.ParseFloat(m[1], 64)
	if err != nil {
		return nil
	}

	unit := m[2]
	var multiplier float64
	switch unit {
	case "k":
		multiplier = 1.0 / 1024.0
	case "m", "":
		multiplier = 1.0
	case "g":
		multiplier = 1024.0
	case "t":
		multiplier = 1024.0 * 1024.0
	}

	res := int(num * multiplier)
	return &res
}

// ParseCPUs parses CPU core count string.
func ParseCPUs(value string) *int {
	s := strings.TrimSpace(value)
	if s == "" {
		return nil
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil || f <= 0 {
		return nil
	}
	c := int(f)
	if float64(c) < f {
		c++
	}
	if c < 1 {
		c = 1
	}
	return &c
}

// OversubscriptionWarnings detects configurations where runners exceed host capacity.
func OversubscriptionWarnings(cpus, memoryMiB *int, host HostCapacity, maxRunners int) []string {
	var warnings []string
	if cpus == nil {
		warnings = append(warnings, fmt.Sprintf("RUNNER_CPUS is unlimited: %d runners can claim all %d host CPUs", maxRunners, host.CPUs))
	} else if *cpus*maxRunners > host.CPUs {
		warnings = append(warnings, fmt.Sprintf("max_runners x cpus = %d x %d = %d exceeds host's %d CPUs", maxRunners, *cpus, *cpus*maxRunners, host.CPUs))
	}

	if memoryMiB != nil && host.MemoryMiB > 0 && *memoryMiB*maxRunners > host.MemoryMiB {
		warnings = append(warnings, fmt.Sprintf("max_runners x memory = %d x %d = %d MiB exceeds host's %d MiB", maxRunners, *memoryMiB, *memoryMiB*maxRunners, host.MemoryMiB))
	}
	return warnings
}
