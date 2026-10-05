package state

import (
	"strings"
	"testing"
)

func TestState_LifecycleAndSnapshot(t *testing.T) {
	st := NewState(4, "v1.0.0", nil)
	if st.Broker() == nil {
		t.Fatal("expected non-nil broker")
	}

	snap := st.GetSnapshot()
	if snap.MaxRunners != 4 || snap.FreeSlots != 4 || snap.BusyRunners != 0 {
		t.Errorf("unexpected snapshot: %+v", snap)
	}
	if snap.Version != "v1.0.0" {
		t.Errorf("expected v1.0.0, got %s", snap.Version)
	}

	// Update fleet with 2 runners (1 busy, 1 idle)
	r1 := RunnerInfo{ID: "r-1", Status: "busy", TargetRepo: "org/repo"}
	r2 := RunnerInfo{ID: "r-2", Status: "idle", TargetRepo: "org/repo"}
	job := QueuedJob{ID: 101, RunID: 202, Name: "build", Repo: "org/repo"}
	st.UpdateFleet([]RunnerInfo{r1, r2}, []QueuedJob{job})

	snap2 := st.GetSnapshot()
	if snap2.BusyRunners != 1 || snap2.FreeSlots != 3 || len(snap2.QueuedJobs) != 1 {
		t.Errorf("unexpected snapshot after fleet update: %+v", snap2)
	}

	// Test free slots clamp at 0 when busy > max
	r3 := RunnerInfo{ID: "r-3", Status: "running"}
	r4 := RunnerInfo{ID: "r-4", Status: "busy"}
	r5 := RunnerInfo{ID: "r-5", Status: "busy"}
	r6 := RunnerInfo{ID: "r-6", Status: "busy"}
	r7 := RunnerInfo{ID: "r-7", Status: "busy"}
	st.UpdateFleet([]RunnerInfo{r3, r4, r5, r6, r7}, nil)
	snapOverflow := st.GetSnapshot()
	if snapOverflow.FreeSlots != 0 {
		t.Errorf("expected 0 free slots on overflow, got %d", snapOverflow.FreeSlots)
	}
}

func TestState_Mutations(t *testing.T) {
	broker := NewBroker()
	st := NewState(2, "v1.0.0", broker)

	// Repo priority
	st.SetRepoPriority([]string{"repo-a", "repo-b"}, []string{"repo-b"})
	snap := st.GetSnapshot()
	if len(snap.RepoPriority) != 2 || len(snap.PausedRepos) != 1 {
		t.Errorf("unexpected priority: %+v", snap)
	}

	// Autoscaler status
	st.SetAutoscalerStatus("paused")
	if st.GetSnapshot().AutoscalerStatus != "paused" {
		t.Errorf("expected paused status")
	}

	// Max runners
	st.SetMaxRunners(8)
	if st.GetSnapshot().MaxRunners != 8 {
		t.Errorf("expected max runners 8")
	}

	// Rate limit
	rem, lim := 4500, 5000
	st.SetRateLimit(&rem, &lim)
	snapRL := st.GetSnapshot()
	if *snapRL.RateLimitRemaining != 4500 || *snapRL.RateLimitLimit != 5000 {
		t.Errorf("unexpected rate limit: %+v", snapRL)
	}
}

func TestState_LogsAndRingBuffer(t *testing.T) {
	st := NewState(2, "v1.0.0", nil)
	st.maxLogs = 3 // small buffer to test eviction

	st.AppendLog("msg 1")
	st.AppendLog("msg 2")
	st.AppendLog("msg 3")
	st.AppendLog("msg 4")

	logs := st.GetLogs()
	if len(logs) != 3 {
		t.Fatalf("expected 3 logs, got %d", len(logs))
	}
	if logs[0].Message != "msg 2" || logs[2].Message != "msg 4" {
		t.Errorf("unexpected logs ring order: %+v", logs)
	}
}

func TestEvent_Format(t *testing.T) {
	ev := Event{Type: "test", Data: map[string]string{"foo": "bar"}}
	bytes, err := ev.Format()
	if err != nil {
		t.Fatalf("unexpected format error: %v", err)
	}
	str := string(bytes)
	if !strings.Contains(str, "event: test\n") || !strings.Contains(str, `"foo":"bar"`) {
		t.Errorf("unexpected SSE wire format: %s", str)
	}

	// Unmarshalable value (channel cannot be marshaled to JSON)
	badEv := Event{Type: "bad", Data: make(chan int)}
	_, err = badEv.Format()
	if err == nil {
		t.Error("expected error marshaling channel to JSON, got nil")
	}
}

func TestBroker_SubscribeBroadcastClose(t *testing.T) {
	broker := NewBroker()
	ch1, unsub1 := broker.Subscribe()
	ch2, _ := broker.Subscribe()

	broker.Broadcast(Event{Type: "ping", Data: "hello"})

	ev1 := <-ch1
	if ev1.Data != "hello" {
		t.Errorf("expected hello on ch1, got %v", ev1.Data)
	}
	ev2 := <-ch2
	if ev2.Data != "hello" {
		t.Errorf("expected hello on ch2, got %v", ev2.Data)
	}

	// Unsubscribe ch1
	unsub1()
	// Unsubscribing a second time should be safe
	unsub1()

	// Broadcast should only reach ch2
	broker.Broadcast(Event{Type: "ping", Data: "second"})
	ev2_2 := <-ch2
	if ev2_2.Data != "second" {
		t.Errorf("expected second on ch2, got %v", ev2_2.Data)
	}

	// Fill ch2 buffer to test non-blocking drop
	for i := 0; i < 70; i++ {
		broker.Broadcast(Event{Type: "flood", Data: i})
	}

	// Keep ch2 subscribed while closing
	broker.Close()
	// Closing already closed broker should be a no-op
	broker.Close()

	// Subscribing after close returns immediately closed channel
	chClosed, unsubClosed := broker.Subscribe()
	unsubClosed()
	_, open := <-chClosed
	if open {
		t.Error("expected closed channel when subscribing to closed broker")
	}

	// Broadcast on closed broker is a no-op
	broker.Broadcast(Event{Type: "ignored", Data: 1})
}
