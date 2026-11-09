/**
 * Formats the time remaining until a Unix epoch reset time as `HH:MM:SS`.
 *
 * @param resetEpoch - Reset time in epoch seconds.
 * @returns `--:--:--` when no reset time is known, otherwise the zero-padded countdown.
 */
export function formatReset(resetEpoch?: number | null): string {
  if (!resetEpoch) return "--:--:--";
  const remainingSec = Math.max(0, Math.floor(resetEpoch - Date.now() / 1000));
  const h = Math.floor(remainingSec / 3600);
  const m = Math.floor((remainingSec % 3600) / 60);
  const s = remainingSec % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

/**
 * Formats the elapsed time since an ISO timestamp (`45s`, `3m 12s`, `2h 5m`).
 *
 * @param isoTime - ISO-8601 start timestamp.
 * @returns `active` when the timestamp is missing or invalid.
 */
export function formatDuration(isoTime?: string | null): string {
  if (!isoTime) return "active";
  const created = new Date(isoTime).getTime();
  if (isNaN(created)) return "active";
  const diffSec = Math.max(0, Math.floor((Date.now() - created) / 1000));
  const m = Math.floor(diffSec / 60);
  const s = diffSec % 60;
  if (m === 0) return `${s}s`;
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  return `${m}m ${s}s`;
}

/**
 * Escapes HTML special characters so untrusted text can be embedded in markup.
 *
 * @param str - Raw text.
 * @returns The escaped string, or an empty string for falsy input.
 */
export function escapeHtml(str: string): string {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Compares two sort keys: numerically for numbers, otherwise with a natural, case-insensitive locale comparison.
 */
export function compareValues(a: string | number, b: string | number): number {
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), undefined, { sensitivity: "base", numeric: true });
}

/**
 * Normalizes a search query (trimmed, lower-cased) for filtering.
 */
export function normalizeFilter(value: string): string {
  return value.trim().toLowerCase();
}

/**
 * Tests whether the lower-cased, space-joined fields contain the query.
 *
 * @param fields - Searchable values; nullish entries are ignored.
 * @param query - Normalized query. An empty query matches everything.
 */
export function includesFilter(
  fields: Array<string | number | undefined | null>,
  query: string,
): boolean {
  const haystack = fields
    .map((f) => (f === undefined || f === null ? "" : String(f).toLowerCase()))
    .join(" ");
  return haystack.includes(query);
}

/**
 * Escapes a log line and wraps well-known `[Tag]` markers in colored badge spans.
 */
export function formatLogMessage(msg: string): string {
  let safe = escapeHtml(msg);
  safe = safe.replace(
    /\[(Autoscaler|Reconciler|DockerDriver|OrbStackDriver|WSL2Driver|MultipassDriver|Go Engine)\]/g,
    '<span class="log-tag tag-cyan">[$1]</span>',
  );
  safe = safe.replace(
    /\[(Spawn|ScaleUp|Ready|Started)\]/gi,
    '<span class="log-tag tag-emerald">[$1]</span>',
  );
  safe = safe.replace(
    /\[(ScaleDown|Prune|Terminated|Stopped)\]/gi,
    '<span class="log-tag tag-amber">[$1]</span>',
  );
  safe = safe.replace(
    /\[(Error|Failed|Exception|Timeout|❌)\]/gi,
    '<span class="log-tag tag-crimson">[$1]</span>',
  );
  safe = safe.replace(
    /\[(Bridge|VM|Routing|🚀)\]/gi,
    '<span class="log-tag tag-purple">[$1]</span>',
  );
  return safe;
}
