package state

import (
	"strings"
	"testing"
)

func TestCompletedJobHistoryAndRunnerLogs(t *testing.T) {
	s := NewState(2, "v", nil)
	if got, ok := s.GetRunnerLog("none"); ok || got != "" {
		t.Fatalf("missing log = %q,%v", got, ok)
	}
	s.SetRunnerLog("", "ignored")
	s.SetRunnerLog("runner", "")
	if _, ok := s.GetRunnerLog("runner"); ok {
		t.Fatal("empty runner log should be ignored")
	}
	large := strings.Repeat("x", maxRunnerLogBytes+17)
	s.SetRunnerLog("runner", large)
	if got, ok := s.GetRunnerLog("runner"); !ok || len(got) != maxRunnerLogBytes || got != large[17:] {
		t.Fatalf("stored log length/content %d %v", len(got), ok)
	}
	// Updating does not duplicate its FIFO entry; the next new name is evicted at capacity.
	s.SetRunnerLog("runner", "updated")
	for i := 0; i < maxRunnerLogs; i++ {
		s.SetRunnerLog("r"+strings.Repeat("a", i+1), "line")
	}
	if _, ok := s.GetRunnerLog("runner"); ok {
		t.Fatal("oldest log was not evicted")
	}
	if got, ok := s.GetRunnerLog("r" + strings.Repeat("a", maxRunnerLogs)); !ok || got != "line" {
		t.Fatal("newest log missing")
	}

	runner := "r100"
	s.SetRunnerLog(runner, "retained")
	jobs := make([]CompletedJob, MaxCompletedJobs+1)
	for i := range jobs {
		jobs[i].ID = int64(i)
	}
	jobs[0].RunnerName = &runner
	s.SetCompletedJobs(jobs)
	snap := s.GetSnapshot()
	if len(snap.CompletedJobs) != MaxCompletedJobs || !snap.CompletedJobs[0].HasRunnerLog {
		t.Fatalf("history snapshot %+v", snap)
	}
	jobs[0].ID = -1
	if s.GetSnapshot().CompletedJobs[0].ID != 0 {
		t.Fatal("history slice was not copied")
	}
	s.SetCompletedJobs(nil)
	if got := s.GetSnapshot().CompletedJobs; len(got) != 0 {
		t.Fatalf("empty history not stored: %d", len(got))
	}
}

func TestHistoryRefreshAndActionsBilling(t *testing.T) {
	s := NewState(1, "v", nil)
	if s.ConsumeHistoryRefresh() {
		t.Fatal("refresh should initially be clean")
	}
	s.RequestHistoryRefresh()
	if !s.ConsumeHistoryRefresh() || s.ConsumeHistoryRefresh() {
		t.Fatal("refresh signal should be consumed once")
	}
	billing := &ActionsBilling{IncludedMinutes: 10, TotalMinutesUsed: 3}
	s.SetActionsBilling(billing)
	if got := s.GetSnapshot().ActionsBilling; got == nil || got.TotalMinutesUsed != 3 {
		t.Fatalf("billing = %+v", got)
	}
	s.SetActionsBilling(nil)
	if s.GetSnapshot().ActionsBilling != nil {
		t.Fatal("billing should clear")
	}
}

func TestSnapshotCloudAndRunnerStates(t *testing.T) {
	s := NewState(3, "v", nil)
	s.UpdateFleet([]RunnerInfo{
		{ID: "cloud", IsCloud: true, Status: "busy", State: "running"},
		{ID: "running", State: "running"},
		{ID: "up", Status: "UP 2m"},
		{ID: "idle", Status: "idle"},
	}, nil)
	snap := s.GetSnapshot()
	if snap.BusyRunners != 2 || snap.FreeSlots != 1 {
		t.Fatalf("busy=%d free=%d", snap.BusyRunners, snap.FreeSlots)
	}
}
