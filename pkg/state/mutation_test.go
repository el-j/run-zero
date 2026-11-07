package state

import (
	"fmt"
	"testing"
)

func TestSetRunnerLog_KeepsExactlyMaxRunnerLogs(t *testing.T) {
	s := NewState(1, "t", nil)
	for i := 0; i < maxRunnerLogs; i++ {
		s.SetRunnerLog(fmt.Sprintf("r%d", i), "log")
	}
	if _, ok := s.GetRunnerLog("r0"); !ok {
		t.Fatal("the oldest log must be kept while there are exactly maxRunnerLogs")
	}
	s.SetRunnerLog("one-more", "log")
	if _, ok := s.GetRunnerLog("r0"); ok {
		t.Fatal("the oldest log must be evicted past maxRunnerLogs")
	}
}
