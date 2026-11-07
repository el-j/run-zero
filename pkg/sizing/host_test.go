package sizing

import (
	"errors"
	"testing"
)

func TestDetectHostCapacity(t *testing.T) {
	meminfo := func(text string, err error) func(string) ([]byte, error) {
		return func(path string) ([]byte, error) {
			if path != "/proc/meminfo" {
				t.Errorf("unexpected path %s", path)
			}
			return []byte(text), err
		}
	}
	if h := detectHostCapacity(8, meminfo("MemFree: 1 kB\nMemTotal:       16777216 kB\n", nil)); h != (HostCapacity{CPUs: 8, MemoryMiB: 16384}) {
		t.Fatalf("got %+v", h)
	}
	if h := detectHostCapacity(8, meminfo("", errors.New("no procfs"))); h != (HostCapacity{CPUs: 8}) {
		t.Fatalf("without procfs: got %+v", h)
	}
	if h := detectHostCapacity(8, meminfo("MemTotal: lots kB\n", nil)); h.MemoryMiB != 0 {
		t.Fatalf("unparsable memory: got %+v", h)
	}
	if h := DetectHostCapacity(); h.CPUs < 1 {
		t.Fatalf("expected at least one CPU, got %+v", h)
	}
}
