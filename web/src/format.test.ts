import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  compareValues,
  escapeHtml,
  formatDuration,
  formatLogMessage,
  formatReset,
  includesFilter,
  normalizeFilter,
} from "./format";

describe("format", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-01-01T00:00:00Z"));
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("formatReset", () => {
    const now = Date.now() / 1000;
    expect(formatReset()).toBe("--:--:--");
    expect(formatReset(null)).toBe("--:--:--");
    expect(formatReset(now + 3725)).toBe("01:02:05");
    expect(formatReset(now - 100)).toBe("00:00:00");
  });

  it("formatDuration", () => {
    const ago = (s: number) => new Date(Date.now() - s * 1000).toISOString();
    expect(formatDuration()).toBe("active");
    expect(formatDuration(null)).toBe("active");
    expect(formatDuration("nope")).toBe("active");
    expect(formatDuration(ago(45))).toBe("45s");
    expect(formatDuration(ago(192))).toBe("3m 12s");
    expect(formatDuration(ago(7500))).toBe("2h 5m");
    expect(formatDuration(new Date(Date.now() + 5000).toISOString())).toBe("0s");
  });

  it("escapeHtml", () => {
    expect(escapeHtml("")).toBe("");
    expect(escapeHtml(`<a href="x">'&'</a>`)).toBe(
      "&lt;a href=&quot;x&quot;&gt;&#039;&amp;&#039;&lt;/a&gt;",
    );
  });

  it("compareValues", () => {
    expect(compareValues(1, 3)).toBe(-2);
    expect(compareValues("a10", "a9")).toBeGreaterThan(0);
    expect(compareValues("A", "a")).toBe(0);
    expect(compareValues(1, "1")).toBe(0);
  });

  it("normalizeFilter", () => {
    expect(normalizeFilter("  FoO ")).toBe("foo");
  });

  it("includesFilter", () => {
    expect(includesFilter(["a"], "")).toBe(true);
    expect(includesFilter(["Alpha", undefined, null, 42], "42")).toBe(true);
    expect(includesFilter(["Alpha", undefined, null], "beta")).toBe(false);
    expect(includesFilter(["Alpha", "Beta"], "alpha beta")).toBe(true);
  });

  it("formatLogMessage badges known tags and escapes html", () => {
    const html = formatLogMessage(
      "[Autoscaler] [spawn] [ScaleDown] [error] [Bridge] [Unknown] <b>",
    );
    expect(html).toContain('<span class="log-tag tag-cyan">[Autoscaler]</span>');
    expect(html).toContain('<span class="log-tag tag-emerald">[spawn]</span>');
    expect(html).toContain('<span class="log-tag tag-amber">[ScaleDown]</span>');
    expect(html).toContain('<span class="log-tag tag-crimson">[error]</span>');
    expect(html).toContain('<span class="log-tag tag-purple">[Bridge]</span>');
    expect(html).toContain("[Unknown] &lt;b&gt;");
  });
});
