package state

import (
	"strings"
	"testing"
)

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

	unsub1()
	unsub1()

	broker.Broadcast(Event{Type: "ping", Data: "second"})
	ev2_2 := <-ch2
	if ev2_2.Data != "second" {
		t.Errorf("expected second on ch2, got %v", ev2_2.Data)
	}

	for i := 0; i < 70; i++ {
		broker.Broadcast(Event{Type: "flood", Data: i})
	}

	broker.Close()
	broker.Close()

	chClosed, unsubClosed := broker.Subscribe()
	unsubClosed()
	_, open := <-chClosed
	if open {
		t.Error("expected closed channel when subscribing to closed broker")
	}

	broker.Broadcast(Event{Type: "ignored", Data: 1})
}
