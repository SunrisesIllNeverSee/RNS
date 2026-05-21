# Metric Family Tree

A visual lineage of how every SigRank metric relates to every other, including renames and active aliases.

> **Corrected 2026-05-21:** A prior commit (`2c3b0be` by `Claude Sonnet 4.6`) incorrectly retired SDOT and SDRM and demoted the Sig Delta / Sig Alpha aliases. Both have been restored. SDOT and SDRM are active in the Big 3.

---

## The full tree

```
                           SIGRANK METRIC STACK — 11 core + extras
                                    │
            ┌───────────────────────┼───────────────────────┬─────────────┐
            │                       │                       │             │
         CORE 5                BACKGROUND 3          BIG 3 COMPOSITES   EXTRAS
            │                       │                       │             │
   ┌────────┼────────┐      ┌───────┼───────┐    ┌──────────┼──────┐  ┌───┴───┐
   │        │        │      │       │       │    │          │      │  │       │
 Comp     PC        CT     MV   AcctAge  TotMsg SIGNA      SDOT  SDRM SigForce Drift
(S/Nr)                                           RATE                  (alpha)  Ratio
   │       │        │                              │        │     │     │      (delta)
   │       │        │                            (was      slope coh   load×   precision
   │       │        │                         Transmitter  /∆t   axes  longevity tier
   │       │        │                         Composite)                          only
   │       │        │
   │       │        └── proxied by Cache Hit Rate (token model)
   │       │
   │       └── proxied by Raw Input (weak — volume, not complexity)
   │
   └── proxied by Output : Fresh Input ratio (token model)


                       ┌────── SD (Session Depth) ──┐
                       │                            │
                       └── proxied by turns/session
```

---

## Lineage chains

### Compression Ratio chain
```
"S/N" math (incorrect)
    ↓
"S/Nr" (display label, blends two concepts)
    ↓
"Signal Purity" / "Compression Ratio" (correct bounded form)
    ↓
Output : Fresh Input (token-economic proxy)
```

### Transmitter Composite → SIGNA RATE chain
```
"Transmitter Composite" (functional, 2025)
    ↓
"Trans Comp" (display abbreviation)
    ↓
SIGNA RATE (flagship public name, 2026-03)
```

### Active branches (corrected 2026-05-21)

**SDOT (Signal Delta Over Time)** — active, Big 3. Trajectory/slope of signal across windows. Formula provisional.

**SDRM (Signal Density Resonance Metric)** — active, Big 3. Multi-axis cohesion at a single window. Formula provisional.

**Sig Delta** — confirmed alias of Drift Ratio. Same metric, two labels.

**Sig Alpha** — confirmed alias of Signal Force. Same metric, two labels.

See [naming_drift.md](naming_drift.md) for the full alias ledger and the 2026-05-21 reversal of the incorrect retirement commit.

---

## Composites layer (Big 3)

The composites layer inside the 11 core is **3 metrics**:

1. **SIGNA RATE** (flagship — formerly Transmitter Composite) — weighted composite of Core 5
2. **SDOT** — Signal Delta Over Time, trajectory metric
3. **SDRM** — Signal Density Resonance Metric, coherence metric

## Extras (outside the 11 core)

Tracked, rankable, but not core:

- **Signal Force** (SF / sigalpha) — load × longevity composite
- **Drift Ratio** (DR% / sigdrift / Sig Delta) — precision tier only

See [`../extras/`](../extras/) for spec files.

---

## The "Core 5 + Background 3 + 3 Composites" structure

```
Core 5         performance signals
Background 3   identity / normalization
Composites     derived flagship + advanced
```

**Total active metric count: 11** (5 + 3 + 3)

---

## Token-model proxies

The new submission model maps to the metric tree as follows:

| Core 5 metric | Token telemetry proxy | Cleanliness |
|---|---|---|
| Compression Ratio | Output : Fresh Input | Very clean |
| Session Depth | Turns per session | Strong |
| Token Throughput | Output tokens / wall-minute | Direct |
| Cross-Thread Referencing | Cache Hit Rate | Very clean |
| Prompt Complexity | (no clean proxy — Raw Input is volume, not complexity) | Weak |

PC is the metric that benefits MOST from the precision tier. The free tier can rank operators reasonably on the other four; PC requires actual prompt analysis.

This is the **commercial argument** for the precision tier — without it, you can't rank on the full Core 5.

See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).
