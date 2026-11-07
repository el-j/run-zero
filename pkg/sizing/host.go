package sizing

import (
	"os"
	"runtime"
	"strconv"
	"strings"
)

// DetectHostCapacity reports this machine's CPU count and, where
// /proc/meminfo exists (Linux, including the daemon's container), its total
// memory. MemoryMiB is 0 (unknown) elsewhere.
func DetectHostCapacity() HostCapacity {
	return detectHostCapacity(runtime.NumCPU(), os.ReadFile)
}

func detectHostCapacity(cpus int, readFile func(string) ([]byte, error)) HostCapacity {
	host := HostCapacity{CPUs: cpus}
	data, err := readFile("/proc/meminfo")
	if err != nil {
		return host
	}
	for _, line := range strings.Split(string(data), "\n") {
		if f := strings.Fields(line); len(f) >= 2 && f[0] == "MemTotal:" {
			if kib, err := strconv.Atoi(f[1]); err == nil {
				host.MemoryMiB = kib / 1024
			}
		}
	}
	return host
}
