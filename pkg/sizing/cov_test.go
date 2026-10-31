package sizing

import (
	"strings"
	"testing"
)

func TestCoverageGaps(t *testing.T) {
	if ParseMemoryMiB("1"+strings.Repeat("0", 400)) != nil {
		t.Error("overflow should be nil")
	}
	if v := ParseMemoryMiB("2048k"); v == nil || *v != 2 {
		t.Errorf("k unit: %v", v)
	}
	cpus, mem := DeriveSizing(HostCapacity{CPUs: 4, MemoryMiB: 8192}, 1000)
	if cpus != 1 || mem != MinMemoryMiB {
		t.Errorf("got %d %d", cpus, mem)
	}
	r := ResolveSizing("", "", 0, HostCapacity{CPUs: 16, MemoryMiB: 65536})
	if r.MaxRunners != 4 {
		t.Errorf("max runners %d", r.MaxRunners)
	}
}
