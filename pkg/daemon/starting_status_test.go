package daemon

import "testing"

func TestIsStartingStatus(t *testing.T) {
	for _, v := range []string{"creating", "provisioning", "starting", "booting", "created"} {
		if !isStartingStatus(v) {
			t.Fatalf("%q should count as starting", v)
		}
	}
	for _, v := range []string{"", "stopped", "exited", "running"} {
		if isStartingStatus(v) {
			t.Fatalf("%q should not count as starting", v)
		}
	}
}
