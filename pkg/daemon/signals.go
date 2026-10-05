package daemon

import (
	"context"
	"os"
	"os/signal"
	"syscall"
)

// SignalContext returns a context canceled when SIGINT or SIGTERM is intercepted.
func SignalContext(parent context.Context) (context.Context, context.CancelFunc) {
	return signal.NotifyContext(parent, syscall.SIGINT, syscall.SIGTERM)
}

// DefaultSignals returns the standard termination signals.
func DefaultSignals() []os.Signal {
	return []os.Signal{syscall.SIGINT, syscall.SIGTERM}
}
