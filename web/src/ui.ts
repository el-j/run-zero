import { dom } from "./dom";

/**
 * Shows a transient toast notification that fades out after a few seconds.
 *
 * @param message - Text to display.
 * @param isError - Renders the toast with an error border when true.
 */
export function showToast(message: string, isError = false) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) {
    toast.style.borderColor = "var(--crimson)";
  }
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/**
 * Updates the header connection badge and label.
 */
export function setConnectionStatus(status: "connecting" | "online" | "error", text: string) {
  const { connectionBadge, connectionText } = dom;
  if (!connectionText || !connectionBadge) return;
  connectionText.textContent = text;
  connectionBadge.className = "badge badge-pulse";
  if (status === "connecting") {
    connectionBadge.classList.add("connecting");
  } else if (status === "error") {
    connectionBadge.classList.add("error");
  }
}
