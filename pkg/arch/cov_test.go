package arch

import "testing"

func TestCoverageGaps(t *testing.T) {
	if NormalizeHostArch("riscv64") != "riscv64" {
		t.Error("unknown arch should pass through")
	}
	o, err := NewNativeArchOverride("", "arm64")
	if err != nil || o.Mode != ModeOff {
		t.Errorf("empty should be off: %v %v", o, err)
	}
	o, err = NewNativeArchOverride("a/b,,c/d", "arm64")
	if err != nil || !o.Repos["a/b"] || !o.Repos["c/d"] || len(o.Repos) != 2 {
		t.Errorf("unexpected %v %v", o, err)
	}
}
