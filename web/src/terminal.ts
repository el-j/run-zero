import { dom } from "./dom";
import { escapeHtml, formatLogMessage } from "./format";
import { state } from "./state";

/**
 * Clamps a terminal height in pixels to the bounds allowed by the workspace column.
 */
export function clampTerminalHeight(px: number): number {
  const { workspaceMainColumn } = dom;
  if (!workspaceMainColumn) return px;
  const maxAllowed = Math.max(120, workspaceMainColumn.clientHeight - 220);
  return Math.min(maxAllowed, Math.max(96, Math.round(px)));
}

/**
 * Applies (and persists) the terminal panel height as the `--terminal-height` CSS variable.
 */
export function applyTerminalHeight(px: number) {
  const { workspaceMainColumn } = dom;
  if (!workspaceMainColumn) return;
  state.terminalHeightPx = clampTerminalHeight(px);
  workspaceMainColumn.style.setProperty("--terminal-height", `${state.terminalHeightPx}px`);
  localStorage.setItem("runzero_terminal_height_px", String(state.terminalHeightPx));
}

/**
 * Wires the drag splitter that resizes the bottom terminal and re-applies the height on window resize.
 */
export function initTerminalSplitter() {
  const { workspaceMainColumn, mainTerminalSplitter, panelTerminal } = dom;
  if (!workspaceMainColumn || !mainTerminalSplitter || !panelTerminal) return;

  applyTerminalHeight(state.terminalHeightPx);

  let startY = 0;
  let startHeight = 0;

  // Listeners are attached only for the duration of a drag.
  const onMove = (ev: MouseEvent) => {
    const delta = startY - ev.clientY;
    applyTerminalHeight(startHeight + delta);
  };

  const stopDrag = () => {
    mainTerminalSplitter.classList.remove("dragging");
    window.removeEventListener("mousemove", onMove);
    window.removeEventListener("mouseup", stopDrag);
  };

  mainTerminalSplitter.addEventListener("mousedown", (ev) => {
    ev.preventDefault();
    startY = ev.clientY;
    startHeight = panelTerminal.getBoundingClientRect().height;
    mainTerminalSplitter.classList.add("dragging");
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", stopDrag);
  });

  window.addEventListener("resize", () => applyTerminalHeight(state.terminalHeightPx));
}

/**
 * Toggles the terminal between its collapsed and expanded presets and updates the toggle button.
 */
export function toggleTerminal() {
  const { btnTerminalExpandIcon, btnTerminalExpandText } = dom;
  state.terminalExpanded = !state.terminalExpanded;
  applyTerminalHeight(state.terminalExpanded ? 320 : 180);
  if (btnTerminalExpandIcon) btnTerminalExpandIcon.textContent = state.terminalExpanded ? "▼" : "▲";
  if (btnTerminalExpandText)
    btnTerminalExpandText.textContent = state.terminalExpanded ? "COLLAPSE" : "EXPAND";
}

/**
 * Appends a log line to the terminal, capping it at 500 lines and honoring auto-scroll.
 *
 * @param text - Log message.
 * @param timestamp - Optional timestamp label; defaults to the local time.
 */
export function appendLog(text: string, timestamp?: string) {
  const { logTerminal, autoScrollToggle, terminalLineCount } = dom;
  if (!logTerminal) return;
  state.totalLogLines++;
  if (terminalLineCount) terminalLineCount.textContent = `${state.totalLogLines} lines`;
  const ts = timestamp || new Date().toLocaleTimeString();
  const lineEl = document.createElement("div");
  lineEl.className = "log-line";
  lineEl.innerHTML = `<span class="log-ts font-mono">[${escapeHtml(ts)}]</span> <span class="log-content">${formatLogMessage(text)}</span>`;
  logTerminal.appendChild(lineEl);
  if (logTerminal.children.length > 500) {
    logTerminal.removeChild(logTerminal.firstChild!);
  }
  if (autoScrollToggle && autoScrollToggle.checked) {
    logTerminal.scrollTop = logTerminal.scrollHeight;
  }
}
