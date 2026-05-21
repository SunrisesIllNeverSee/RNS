# Drift Ratio (DR%)

**Status:** provisional — definition stable, integration pending
**Layer:** Composite (advanced)
**Public label:** Drift Ratio
**Short label:** DR%
**DB field:** `drift_ratio`

---

## Definition

The percentage of operator messages that remain **aligned with the session's signal vector** vs. the percentage that drift into noise, tangent, or topic collapse.

Drift Ratio is the **anti-waterlog metric** — it detects when sessions decay into noise even if total volume stays high.

---

## Formula (provisional)

```
DR% = (aligned_messages / total_messages) × 100
```

Where `aligned_messages` = messages that maintain the session's signal vector (don't drift to off-topic, redundant, or low-coherence content).

**Equivalent inverse form:**

```
DR% = 100 - drift_percentage
```

---

## Inputs required

Per session:
- semantic alignment score per message (from sig_army or vector coherence check)
- total message count

**Token-proxy path:** no direct token equivalent yet. DR% is one of the metrics that strongly favors the **precision tier** (sig_army audit) over the **free tier** (token telemetry only). Potential proxies: `wasted_token_count`, `context_reset_count`, `entropy_growth_per_session` — but none are clean. See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## Output

- Range: `[0, 100]` (percentage)
- Precision: 1 decimal place

---

## Lineage notes

May have been renamed to **Sig Delta** in later GPT sessions (paired with Signal Force → Sig Alpha rename). Lineage unresolved.

**Drift Ratio / DR%** is the canonical name for now.

See [../lineage/naming_drift.md](../lineage/naming_drift.md).

---

## Why Drift Ratio matters

Most existing AI metrics measure **what happened**. Drift Ratio measures **what should have happened but didn't**. It's the metric that catches:

- Sessions that started strong and decayed
- Operators who lose the thread mid-session
- High-volume operators with low semantic coherence

A Transmitter has both high Compression AND low Drift. Architects can have high Compression with moderate Drift. Power-class often has high Compression on short bursts but high Drift on longer sessions.

---

## Status decisions

**MVP:** not required (free tier ships without it)
**Phase 2:** required (precision tier core)
**Display:**
- Free tier: not surfaced
- Precision tier: profile detail + leaderboard secondary column
- Internal: always computed when raw sessions are available
