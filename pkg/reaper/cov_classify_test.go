package reaper

import "testing"

func TestClassify_OfflineRegisteredReaped(t *testing.T) {
	got := Classify(100, &Registration{Status: "offline"}, true, Timeouts{UnregisteredSeconds: 10})
	if got != ActionReapUnregistered {
		t.Errorf("got %v", got)
	}
}
