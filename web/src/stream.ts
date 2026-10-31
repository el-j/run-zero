import { BuildImagesModal } from "./components/BuildImagesModal";
import { client } from "./api/client";
import { appendLog } from "./terminal";
import { loadCacheStats, refreshState } from "./data";
import { renderState } from "./render/state";
import { setConnectionStatus } from "./ui";

/** Loads the buffered server log history into the terminal. Failures are logged, not thrown. */
export async function loadInitialLogs(): Promise<void> {
  try {
    const res = await fetch("/api/logs");
    if (res.ok) {
      const data = await res.json();
      if (data.logs && Array.isArray(data.logs)) {
        data.logs.forEach((l: { message: string; timestamp?: string }) =>
          appendLog(l.message, l.timestamp),
        );
      }
    }
  } catch (err) {
    console.warn("Could not load initial logs:", err);
  }
}

/**
 * Subscribes to the server-sent event stream and starts the background polling timers.
 *
 * @param imagesModal - Receives image build progress events and periodic refreshes.
 */
export function startStreams(imagesModal: BuildImagesModal): void {
  client.subscribeSSE({
    onFleet: (newState) => {
      setConnectionStatus("online", "LIVE OBSERVABILITY");
      renderState(newState);
    },
    onActivity: (msg) => {
      appendLog(msg);
    },
    onBuildProgress: (progress) => {
      imagesModal.handleProgressEvent(progress);
    },
    onError: () => {
      setConnectionStatus("error", "RECONNECTING...");
    },
  });

  // Background refresh every 10s for state, 20s for cache, 15s for image status
  window.setInterval(refreshState, 10000);
  window.setInterval(loadCacheStats, 20000);
  window.setInterval(() => imagesModal.refresh(), 15000);
}
