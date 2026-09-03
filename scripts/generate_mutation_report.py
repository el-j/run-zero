#!/usr/bin/env python3
"""Generate mutation test summaries and a rolling weekly trend report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return int(value)
    return default


def read_stats(stats_path: Path) -> dict[str, int]:
    raw = json.loads(stats_path.read_text(encoding="utf-8"))
    killed = _as_int(raw.get("killed"))
    survived = _as_int(raw.get("survived"))
    timeout = _as_int(raw.get("timeout", raw.get("timeouts", 0)))
    suspicious = _as_int(raw.get("suspicious"))
    skipped = _as_int(raw.get("skipped"))
    no_tests = _as_int(raw.get("no_tests"))

    total = _as_int(raw.get("total", raw.get("total_mutants", 0)))
    if total <= 0:
        total = killed + survived + timeout + suspicious + skipped + no_tests

    return {
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "suspicious": suspicious,
        "skipped": skipped,
        "no_tests": no_tests,
        "total": total,
    }


def read_status_counts(results_path: Path | None) -> dict[str, int]:
    if results_path is None or not results_path.exists():
        return {}

    counters: Counter[str] = Counter()
    for line in results_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        status = line.split(":", 1)[1].strip().lower()
        if status:
            counters[status] += 1
    return dict(sorted(counters.items(), key=lambda kv: (-kv[1], kv[0])))


def load_history(history_path: Path) -> list[dict[str, object]]:
    if not history_path.exists():
        return []
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    return []


def save_history(history_path: Path, history: list[dict[str, object]]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


def build_markdown(
    current: dict[str, int],
    status_counts: dict[str, int],
    history: list[dict[str, object]],
    history_window: int,
) -> str:
    total = current["total"]
    killed = current["killed"]
    survived = current["survived"]
    timeout = current["timeout"]

    mutation_score = (killed / total * 100.0) if total else 0.0
    survival_rate = (survived / total * 100.0) if total else 0.0

    lines: list[str] = []
    lines.append("# Mutation Weekly Trend Dashboard")
    lines.append("")
    lines.append("## Latest Snapshot")
    lines.append("")
    lines.append(f"- Total mutants: **{total}**")
    lines.append(f"- Killed: **{killed}** ({mutation_score:.1f}%)")
    lines.append(f"- Survived: **{survived}** ({survival_rate:.1f}%)")
    lines.append(f"- Timeout: **{timeout}**")
    lines.append(f"- Suspicious: **{current['suspicious']}**")
    lines.append(f"- Skipped: **{current['skipped']}**")
    lines.append(f"- No tests: **{current['no_tests']}**")
    lines.append("")

    if status_counts:
        lines.append("## Current Mutant Status Breakdown")
        lines.append("")
        lines.append("| Status | Count |")
        lines.append("|---|---:|")
        for status, count in status_counts.items():
            lines.append(f"| {status} | {count} |")
        lines.append("")

    lines.append(f"## Recent History (last {history_window})")
    lines.append("")
    lines.append("| Date (UTC) | Total | Killed | Survived | Timeout |")
    lines.append("|---|---:|---:|---:|---:|")
    for entry in history[-history_window:]:
        date = str(entry.get("date", "unknown"))
        e_total = _as_int(entry.get("total"))
        e_killed = _as_int(entry.get("killed"))
        e_survived = _as_int(entry.get("survived"))
        e_timeout = _as_int(entry.get("timeout"))
        lines.append(f"| {date} | {e_total} | {e_killed} | {e_survived} | {e_timeout} |")

    lines.append("")
    lines.append("## Triage Guidance")
    lines.append("")
    lines.append("- Prioritize `survived` mutants in control-flow heavy modules first.")
    lines.append("- Treat string-literal and logging-only mutations with the equivalent-mutant policy.")
    lines.append("- Keep this report attached to each weekly mutation workflow run for drift tracking.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate mutation trend artifacts from mutmut output.")
    parser.add_argument("--stats", required=True, help="Path to mutmut-cicd-stats.json")
    parser.add_argument("--results", help="Optional path to raw `mutmut results` output")
    parser.add_argument("--history", default="reports/mutation/history.json", help="Rolling history JSON output")
    parser.add_argument("--output", default="reports/mutation/latest.md", help="Markdown dashboard output")
    parser.add_argument("--window", type=int, default=12, help="Number of history points shown in markdown")
    args = parser.parse_args()

    stats_path = Path(args.stats)
    if not stats_path.exists():
        raise FileNotFoundError(f"Missing stats file: {stats_path}")

    current = read_stats(stats_path)
    status_counts = read_status_counts(Path(args.results) if args.results else None)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = load_history(Path(args.history))

    new_entry: dict[str, object] = {"date": today, **current}
    if history and history[-1].get("date") == today:
        history[-1] = new_entry
    else:
        history.append(new_entry)

    save_history(Path(args.history), history)

    markdown = build_markdown(current, status_counts, history, max(1, args.window))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown + "\n", encoding="utf-8")

    summary_path = Path("reports/mutation/latest-summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps({"current": current, "status_counts": status_counts, "history_entries": len(history)}, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote dashboard markdown: {output_path}")
    print(f"Wrote trend history: {args.history}")
    print(f"Latest totals: total={current['total']} killed={current['killed']} survived={current['survived']} timeout={current['timeout']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
