#!/usr/bin/env python3
"""
MO§ES™ — Benchmark Window Extractor
Extracts full token data + transcripts from ~/.claude/projects/
for a given date range (default: May 8–14 2026).

Usage:
  python3 extract_benchmark_window.py
  python3 extract_benchmark_window.py --from 2026-05-08 --to 2026-05-14
  python3 extract_benchmark_window.py --transcript   # also dump full conversation text
  python3 extract_benchmark_window.py --out ~/Desktop/stats/benchmark_export
"""

import json, os, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ── CONFIG ──────────────────────────────────────────────────────────────────
CLAUDE_DIR   = Path.home() / ".claude" / "projects"
DEFAULT_FROM = "2026-05-08"
DEFAULT_TO   = "2026-05-14"
OUT_DIR      = Path.home() / "Desktop" / "stats" / "benchmark_export"

# ── ARGS ─────────────────────────────────────────────────────────────────────
p = argparse.ArgumentParser()
p.add_argument("--from",  dest="from_date", default=DEFAULT_FROM)
p.add_argument("--to",    dest="to_date",   default=DEFAULT_TO)
p.add_argument("--out",   dest="out_dir",   default=str(OUT_DIR))
p.add_argument("--transcript", action="store_true", help="Also write full conversation transcripts")
args = p.parse_args()

from_ts = datetime.strptime(args.from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
to_ts   = datetime.strptime(args.to_date,   "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
to_ts  += 86399  # include full last day

out = Path(args.out_dir)
out.mkdir(parents=True, exist_ok=True)

print(f"\n MO§ES™ Benchmark Window Extractor")
print(f" Window : {args.from_date} → {args.to_date}")
print(f" Source : {CLAUDE_DIR}")
print(f" Output : {out}\n")

# ── FIND FILES ───────────────────────────────────────────────────────────────
all_files = list(CLAUDE_DIR.rglob("*.jsonl"))
window_files = []
for f in all_files:
    mtime = f.stat().st_mtime
    if from_ts <= mtime <= to_ts:
        window_files.append(f)

window_files.sort(key=lambda f: f.stat().st_mtime)
print(f" Found {len(window_files)} .jsonl files in window\n")

# ── EXTRACT ──────────────────────────────────────────────────────────────────
totals = defaultdict(int)
sessions = []
all_turns = []

for fpath in window_files:
    project = fpath.parts[-3] if "subagents" in str(fpath) else fpath.parts[-2]
    project = project.replace("-Users-dericmchenry-Desktop-", "").replace("-Users-dericmchenry-", "~/")

    session_data = {
        "file": str(fpath),
        "project": project,
        "session_id": fpath.stem,
        "is_subagent": "subagent" in str(fpath),
        "mtime": datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(),
        "turns": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read": 0,
        "cache_creation_5m": 0,
        "cache_creation_1h": 0,
        "models": set(),
        "transcript": []
    }

    try:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                role = obj.get("type", "")
                msg  = obj.get("message", {})
                ts   = obj.get("timestamp", "")

                # ── TOKEN COUNTS (assistant turns only) ──
                if role == "assistant" and isinstance(msg, dict):
                    usage = msg.get("usage", {})
                    if usage:
                        inp  = usage.get("input_tokens", 0) or 0
                        out_ = usage.get("output_tokens", 0) or 0
                        cr   = usage.get("cache_read_input_tokens", 0) or 0
                        cc   = usage.get("cache_creation_input_tokens", 0) or 0
                        cc5  = (usage.get("cache_creation", {}) or {}).get("ephemeral_5m_input_tokens", 0) or 0
                        cc1h = (usage.get("cache_creation", {}) or {}).get("ephemeral_1h_input_tokens", 0) or 0

                        session_data["turns"]            += 1
                        session_data["input_tokens"]     += inp
                        session_data["output_tokens"]    += out_
                        session_data["cache_read"]       += cr
                        session_data["cache_creation_5m"] += cc5
                        session_data["cache_creation_1h"] += cc1h

                        totals["turns"]            += 1
                        totals["input_tokens"]     += inp
                        totals["output_tokens"]    += out_
                        totals["cache_read"]       += cr
                        totals["cache_creation_5m"] += cc5
                        totals["cache_creation_1h"] += cc1h

                        model = msg.get("model", "")
                        if model:
                            session_data["models"].add(model)

                    # ── TRANSCRIPT (assistant) ──
                    if args.transcript:
                        content = msg.get("content", "")
                        text = ""
                        if isinstance(content, str):
                            text = content
                        elif isinstance(content, list):
                            parts = []
                            for block in content:
                                if isinstance(block, dict):
                                    if block.get("type") == "text":
                                        parts.append(block.get("text", ""))
                                    elif block.get("type") == "thinking":
                                        pass  # skip thinking blocks
                            text = "\n".join(parts)
                        if text.strip():
                            session_data["transcript"].append({
                                "role": "assistant", "ts": ts, "text": text[:4000]
                            })

                # ── TRANSCRIPT (user) ──
                elif role == "user" and args.transcript:
                    msg_content = msg.get("content", "") if isinstance(msg, dict) else ""
                    text = ""
                    if isinstance(msg_content, str):
                        text = msg_content
                    elif isinstance(msg_content, list):
                        parts = []
                        for block in msg_content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                parts.append(block.get("text", ""))
                        text = "\n".join(parts)
                    if text.strip() and not text.startswith("This session is being continued"):
                        session_data["transcript"].append({
                            "role": "user", "ts": ts, "text": text[:2000]
                        })

    except Exception as e:
        print(f"  ⚠ Error reading {fpath.name}: {e}")
        continue

    if session_data["turns"] > 0:
        session_data["models"] = list(session_data["models"])
        sessions.append(session_data)

# ── TOTALS ───────────────────────────────────────────────────────────────────
total_cache_create = totals["cache_creation_5m"] + totals["cache_creation_1h"]
total_tokens = (totals["input_tokens"] + totals["output_tokens"] +
                totals["cache_read"] + total_cache_create)
denom = totals["input_tokens"] + totals["cache_read"] + total_cache_create
cache_hit_rate = (totals["cache_read"] / denom * 100) if denom > 0 else 0
out_in_ratio = (totals["output_tokens"] / totals["input_tokens"]) if totals["input_tokens"] > 0 else 0

# ── WRITE SUMMARY ────────────────────────────────────────────────────────────
summary = {
    "window": {"from": args.from_date, "to": args.to_date},
    "files_found": len(window_files),
    "sessions_with_turns": len(sessions),
    "totals": {
        "turns": totals["turns"],
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
        "cache_read": totals["cache_read"],
        "cache_creation_5m": totals["cache_creation_5m"],
        "cache_creation_1h": totals["cache_creation_1h"],
        "cache_creation_total": total_cache_create,
        "total_tokens": total_tokens,
    },
    "derived": {
        "cache_hit_rate_pct": round(cache_hit_rate, 4),
        "output_to_input_ratio": round(out_in_ratio, 2),
    },
    "sessions": [
        {k: v for k, v in s.items() if k != "transcript"}
        for s in sorted(sessions, key=lambda s: s["turns"], reverse=True)
    ]
}

summary_path = out / "summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

# ── WRITE MARKDOWN REPORT ────────────────────────────────────────────────────
md_lines = [
    f"# MO§ES™ — Benchmark Window Extract",
    f"_Window: {args.from_date} → {args.to_date}_\n",
    f"## Totals",
    f"| Metric | Value |",
    f"|--------|------:|",
    f"| Files | {len(window_files)} |",
    f"| Sessions (w/ turns) | {len(sessions)} |",
    f"| Turns | {totals['turns']:,} |",
    f"| Input (fresh) | {totals['input_tokens']:,} |",
    f"| Output | {totals['output_tokens']:,} |",
    f"| Cache Read | {totals['cache_read']:,} |",
    f"| Cache Create (5m) | {totals['cache_creation_5m']:,} |",
    f"| Cache Create (1h) | {totals['cache_creation_1h']:,} |",
    f"| **Total Tokens** | **{total_tokens:,}** |",
    f"| **Cache Hit Rate** | **{cache_hit_rate:.4f}%** |",
    f"| **Output:Input** | **{out_in_ratio:.1f}×** |",
    f"",
    f"## Sessions (by turn count)",
    f"| Project | Session | Turns | Input | Output | Cache Read | Models |",
    f"|---------|---------|------:|------:|-------:|-----------:|--------|",
]
for s in sorted(sessions, key=lambda s: s["turns"], reverse=True):
    md_lines.append(
        f"| {s['project'][:40]} | {s['session_id'][:12]}… | "
        f"{s['turns']} | {s['input_tokens']:,} | {s['output_tokens']:,} | "
        f"{s['cache_read']:,} | {', '.join(s['models'])[:40]} |"
    )

md_path = out / "report.md"
with open(md_path, "w") as f:
    f.write("\n".join(md_lines))

# ── WRITE TRANSCRIPTS ────────────────────────────────────────────────────────
if args.transcript:
    tx_path = out / "transcripts"
    tx_path.mkdir(exist_ok=True)
    for s in sessions:
        if not s.get("transcript"):
            continue
        safe_name = s["project"].replace("/", "_").replace(" ", "_")[:60]
        fname = tx_path / f"{safe_name}__{s['session_id'][:12]}.md"
        with open(fname, "w") as f:
            f.write(f"# {s['project']}\n")
            f.write(f"_Session: {s['session_id']} · {s['mtime']}_\n\n")
            for turn in s["transcript"]:
                role_label = "**You**" if turn["role"] == "user" else "**Claude**"
                f.write(f"### {role_label} `{turn['ts']}`\n\n{turn['text']}\n\n---\n\n")

# ── PRINT SUMMARY ────────────────────────────────────────────────────────────
print(f"{'═'*56}")
print(f"  WINDOW : {args.from_date} → {args.to_date}")
print(f"  FILES  : {len(window_files)} jsonl files")
print(f"  SESS   : {len(sessions)} sessions with turns")
print(f"  TURNS  : {totals['turns']:,}")
print(f"{'─'*56}")
print(f"  Input (fresh)      : {totals['input_tokens']:>15,}")
print(f"  Output             : {totals['output_tokens']:>15,}")
print(f"  Cache Read         : {totals['cache_read']:>15,}")
print(f"  Cache Create (5m)  : {totals['cache_creation_5m']:>15,}")
print(f"  Cache Create (1h)  : {totals['cache_creation_1h']:>15,}")
print(f"  Total Tokens       : {total_tokens:>15,}")
print(f"{'─'*56}")
print(f"  Cache Hit Rate     : {cache_hit_rate:>14.4f}%")
print(f"  Output:Input       : {out_in_ratio:>14.1f}×")
print(f"{'═'*56}")
print(f"\n  Output:")
print(f"  → {summary_path}")
print(f"  → {md_path}")
if args.transcript:
    print(f"  → {tx_path}/")
print()
