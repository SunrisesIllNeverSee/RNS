# Token Throughput (TT)

**Status:** locked
**Layer:** Core 5
**Public label:** Token Throughput
**Short label:** TT
**DB field:** `token_throughput`

---

## Definition

Sustained transmission rate — total tokens generated per unit of active time. Measures the operator's bandwidth: how much actual signal output flows through the system during productive use.

TT is the **transmission velocity** metric.

---

## Formula

```
TT = total_output_tokens / active_minutes
```

Or as a session-normalized score:

```
TT_score = min(100, 20 × log10(total_tokens + 1))
```

Log scale prevents whale skew (someone with 10M tokens shouldn't crush someone with 100K by 100×).

**Calibration:**
- 100 tokens     ≈ 40
- 1,000 tokens   ≈ 60
- 10,000 tokens  ≈ 80
- 100,000+ tokens → 100 cap

---

## Inputs required

- output token count (per window)
- active time in minutes (wall clock during sessions)

**Token-proxy path:** map directly to `output_tokens / wall_minutes` from token telemetry. The MO§ES benchmark shows 1.84 min/task vs field average 11.54 min — this is TT velocity. See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## Output

- Raw TT: integer tokens/min
- Normalized TT_score: `[0, 100]`

---

## Relationship to other metrics

| Metric | Relationship |
|---|---|
| Message Volume | TT measures tokens, MV measures messages — related but distinct |
| Compression Ratio | High TT × high Compression = real Transmitter signal. High TT × low Compression = volume noise |
| Session Depth | TT and SD interact — sustained depth requires throughput, but not all throughput is deep |

A high TT alone is not impressive. A high TT × high Compression × high CT is the Transmitter profile.

---

## Why log scale matters

Without log normalization, the leaderboard becomes a contest of who has the most tokens, which is gameable through volume alone. Log scale ensures TT rewards sustained meaningful throughput without making volume the deciding factor.

---

## Confusion with Message Volume

TT counts tokens. MV counts messages. They can diverge:
- Long messages → high TT, lower MV
- Short messages → lower TT, higher MV

Keep them separate in the schema.
