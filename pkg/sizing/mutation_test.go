package sizing

import "testing"

func TestDetectHostCapacity_MemTotalWithoutUnit(t *testing.T) {
	h := detectHostCapacity(2, func(string) ([]byte, error) { return []byte("MemTotal: 2097152\n"), nil })
	if h.MemoryMiB != 2048 {
		t.Fatalf("got %+v", h)
	}
}

func TestParseLabelSizing_RejectsZeroSizes(t *testing.T) {
	for _, l := range []string{"0cpu-8gb", "4cpu-0gb"} {
		if c, m := ParseLabelSizing([]string{l}); c != nil || m != nil {
			t.Errorf("%s must not size a runner, got %v %v", l, c, m)
		}
	}
}

func TestOversubscriptionWarnings_LimitsAndMessages(t *testing.T) {
	host := HostCapacity{CPUs: 8, MemoryMiB: 8192}
	four, mem := 4, 4096
	if w := OversubscriptionWarnings(&four, &mem, host, 2); len(w) != 0 {
		t.Fatalf("exactly filling the host is fine, got %v", w)
	}
	five, mem5 := 5, 5000
	w := OversubscriptionWarnings(&five, &mem5, host, 2)
	if len(w) != 2 ||
		w[0] != "max_runners x cpus = 2 x 5 = 10 exceeds host's 8 CPUs" ||
		w[1] != "max_runners x memory = 2 x 5000 = 10000 MiB exceeds host's 8192 MiB" {
		t.Fatalf("unexpected warnings %q", w)
	}
	if w := OversubscriptionWarnings(&four, &mem5, HostCapacity{CPUs: 8}, 2); len(w) != 0 {
		t.Fatalf("unknown host memory must not warn, got %v", w)
	}
}

func TestResolveSizing_KeepsOneRunner(t *testing.T) {
	if r := ResolveSizing("", "", 1, HostCapacity{CPUs: 9, MemoryMiB: 18432}); r.MaxRunners != 1 || *r.CPUs != 8 {
		t.Fatalf("got %+v", r)
	}
	if r := ResolveSizing("", "", 0, HostCapacity{CPUs: 9, MemoryMiB: 18432}); r.MaxRunners != 4 {
		t.Fatalf("0 runners must default to 4, got %d", r.MaxRunners)
	}
}
