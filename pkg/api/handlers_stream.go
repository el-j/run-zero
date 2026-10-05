package api

import (
	"net/http"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

func handleSSEStream(st *state.State, heartbeatInterval time.Duration) http.HandlerFunc {
	if heartbeatInterval <= 0 {
		heartbeatInterval = 5 * time.Second
	}

	return func(w http.ResponseWriter, r *http.Request) {
		flusher, ok := w.(http.Flusher)
		if !ok {
			writeError(w, http.StatusInternalServerError, "Streaming unsupported")
			return
		}

		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")
		w.Header().Set("X-Accel-Buffering", "no")
		w.WriteHeader(http.StatusOK)

		// Emit initial snapshot event
		initialEvent := state.Event{
			Type: "state",
			Data: st.GetSnapshot(),
		}
		if bytes, err := initialEvent.Format(); err == nil {
			_, _ = w.Write(bytes)
			flusher.Flush()
		}

		events, unsubscribe := st.Broker().Subscribe()
		defer unsubscribe()

		ticker := time.NewTicker(heartbeatInterval)
		defer ticker.Stop()

		ctx := r.Context()
		for {
			select {
			case <-ctx.Done():
				return
			case ev, open := <-events:
				if !open {
					return
				}
				bytes, err := ev.Format()
				if err != nil {
					continue
				}
				if _, err := w.Write(bytes); err != nil {
					return
				}
				flusher.Flush()
			case <-ticker.C:
				if _, err := w.Write([]byte(": ping\n\n")); err != nil {
					return
				}
				flusher.Flush()
			}
		}
	}
}
