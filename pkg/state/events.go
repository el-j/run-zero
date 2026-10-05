package state

import (
	"encoding/json"
	"sync"
)

// Event represents a Server-Sent Event message.
type Event struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

// Format returns SSE wire format bytes.
func (e Event) Format() ([]byte, error) {
	dataBytes, err := json.Marshal(e.Data)
	if err != nil {
		return nil, err
	}
	out := "event: " + e.Type + "\ndata: " + string(dataBytes) + "\n\n"
	return []byte(out), nil
}

// Broker distributes real-time events to active HTTP SSE clients.
type Broker struct {
	mu          sync.RWMutex
	subscribers map[chan Event]struct{}
	closed      bool
}

// NewBroker initializes an event distribution hub.
func NewBroker() *Broker {
	return &Broker{
		subscribers: make(map[chan Event]struct{}),
	}
}

// Subscribe registers a new SSE listener channel and returns an unregister function.
func (b *Broker) Subscribe() (chan Event, func()) {
	b.mu.Lock()
	defer b.mu.Unlock()

	ch := make(chan Event, 64)
	if b.closed {
		close(ch)
		return ch, func() {}
	}

	b.subscribers[ch] = struct{}{}

	unsubscribe := func() {
		b.mu.Lock()
		defer b.mu.Unlock()
		if _, exists := b.subscribers[ch]; exists {
			delete(b.subscribers, ch)
			close(ch)
		}
	}

	return ch, unsubscribe
}

// Broadcast sends an event to all connected subscriber channels.
func (b *Broker) Broadcast(event Event) {
	b.mu.RLock()
	defer b.mu.RUnlock()

	if b.closed {
		return
	}

	for ch := range b.subscribers {
		select {
		case ch <- event:
		default:
			// Non-blocking drop if client buffer is saturated
		}
	}
}

// Close shuts down the broker and terminates all subscriber channels.
func (b *Broker) Close() {
	b.mu.Lock()
	defer b.mu.Unlock()

	if b.closed {
		return
	}
	b.closed = true
	for ch := range b.subscribers {
		delete(b.subscribers, ch)
		close(ch)
	}
}
