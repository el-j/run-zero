package sizing

import (
	"testing"
)

func TestParseMemoryMiB(t *testing.T) {
	cases := []struct {
		input    string
		expected *int
	}{
		{"4G", intPtr(4096)},
		{"2048M", intPtr(2048)},
		{"512MiB", intPtr(512)},
		{"4096", intPtr(4096)},
		{"1T", intPtr(1048576)},
		{"invalid", nil},
		{"", nil},
	}

	for _, c := range cases {
		got := ParseMemoryMiB(c.input)
		if c.expected == nil && got != nil {
			t.Errorf("expected nil for %s, got %v", c.input, *got)
		} else if c.expected != nil && (got == nil || *got != *c.expected) {
			t.Errorf("expected %v for %s, got %v", *c.expected, c.input, got)
		}
	}
}

func TestParseCPUs(t *testing.T) {
	cases := []struct {
		input    string
		expected *int
	}{
		{"4", intPtr(4)},
		{"2.5", intPtr(3)},
		{"0", nil},
		{"-1", nil},
		{"bad", nil},
		{"", nil},
	}

	for _, c := range cases {
		got := ParseCPUs(c.input)
		if c.expected == nil && got != nil {
			t.Errorf("expected nil for %s, got %v", c.input, *got)
		} else if c.expected != nil && (got == nil || *got != *c.expected) {
			t.Errorf("expected %v for %s, got %v", *c.expected, c.input, got)
		}
	}
}

func TestDeriveAndResolveSizing(t *testing.T) {
	host := HostCapacity{CPUs: 10, MemoryMiB: 32768}

	// Derived
	sizing := ResolveSizing("", "", 4, host)
	if sizing.Source != "derived" {
		t.Errorf("expected derived source, got %s", sizing.Source)
	}
	if *sizing.CPUs != 2 || *sizing.MemoryMiB != 7680 {
		t.Errorf("unexpected derived sizing: %+v", sizing)
	}
	if len(sizing.Warnings) != 0 {
		t.Errorf("unexpected warnings: %v", sizing.Warnings)
	}

	// Configured with warnings
	sizingOver := ResolveSizing("8", "16G", 4, host)
	if sizingOver.Source != "configured" {
		t.Errorf("expected configured source")
	}
	if len(sizingOver.Warnings) < 2 {
		t.Errorf("expected at least 2 oversubscription warnings, got: %v", sizingOver.Warnings)
	}

	// Small host clamp
	smallHost := HostCapacity{CPUs: 1, MemoryMiB: 512}
	cpus, mem := DeriveSizing(smallHost, 0)
	if cpus != 1 || mem != MinMemoryMiB {
		t.Errorf("expected 1 CPU and MinMemoryMiB, got %d, %d", cpus, mem)
	}
}

func TestParseLabelSizing(t *testing.T) {
	labelsCustom := []string{"ubuntu-latest", "8cpu-32gb"}
	cpus, mem := ParseLabelSizing(labelsCustom)
	if cpus == nil || *cpus != 8 || mem == nil || *mem != 32768 {
		t.Errorf("unexpected custom sizing: %v, %v", cpus, mem)
	}

	tiers := []struct {
		label string
		cpus  int
		mem   int
	}{
		{"xlarge", 8, 16384},
		{"large", 4, 8192},
		{"medium", 2, 4096},
		{"small", 1, 2048},
	}
	for _, tier := range tiers {
		c, m := ParseLabelSizing([]string{tier.label})
		if c == nil || *c != tier.cpus || m == nil || *m != tier.mem {
			t.Errorf("expected %s: %d, %d; got: %v, %v", tier.label, tier.cpus, tier.mem, c, m)
		}
	}

	labelsHighmem := []string{"highmem"}
	_, mem = ParseLabelSizing(labelsHighmem)
	if mem == nil || *mem != 32768 {
		t.Errorf("unexpected highmem memory: %v", mem)
	}

	labelsNone := []string{"ubuntu-latest"}
	cpus, mem = ParseLabelSizing(labelsNone)
	if cpus != nil || mem != nil {
		t.Errorf("expected nil for non-matching labels")
	}

	// Test unlimited warnings
	warns := OversubscriptionWarnings(nil, nil, HostCapacity{CPUs: 4, MemoryMiB: 8192}, 2)
	if len(warns) == 0 {
		t.Errorf("expected warning for unlimited cpus")
	}
}

func intPtr(i int) *int {
	return &i
}
