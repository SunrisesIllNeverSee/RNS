# Session Depth (SD)

**Status:** locked
**Layer:** Core 5
**Public label:** Session Depth
**Short label:** SD (or Depth)
**DB field:** `session_depth_avg`

---

## Definition

The average **reply-chain length** per session. Measures sustained conversational depth — how deep the operator goes in a single sitting rather than bouncing across shallow exchanges.

SD is the **sustained reasoning** metric.

---

## Formula

```
SD = avg(max_reply_chain_length per session) across window
```

Where `max_reply_chain_length` = the longest unbroken conversational thread within a single session.

---

## Score normalization

For leaderboard scoring, raw SD is normalized to a bounded score:

```
30+ avg depth → 100
25 – 29       → 92
20 – 24       → 84
15 – 19       → 72
10 – 14       → 58
5  – 9        → 42
< 5           → 25
```

---

## Inputs required

Per session:
- message timestamps
- reply-to / parent relationships
- session boundaries

**Token-proxy path:** use `turns_per_session` from token telemetry (e.g. MO§ES benchmark shows 348.9 turns/session in 7-day window). See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## Output

- Raw SD: float (avg messages per chain)
- Normalized SD score: `[0, 100]` integer

---

## Why SD matters

Sustained continuity matters more than chatter. Two operators can have identical message volume but radically different SD — the high-SD operator is doing real work, the low-SD operator is shallow-prompting in many short bursts.

SD also serves as a sanity check on Compression Ratio: a high Compression with very low SD often indicates short curated answers rather than real sustained signal density.

---

## Display

- Profile hero: `Avg Depth: 24.6`
- Leaderboard column: `Depth (Session Depth)` — keep the parenthetical for clarity
- Mobile: `Depth`
