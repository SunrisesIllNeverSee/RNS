# Metric Family Tree

A visual lineage of how every SigRank metric relates to every other, including renames and retired branches.

---

## The full tree

```
                           SIGRANK METRIC STACK
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
         CORE 5                BACKGROUND 3            COMPOSITES
            │                       │                       │
   ┌────────┼────────┐      ┌───────┼───────┐      ┌───────┼───────┐
   │        │        │      │       │       │      │       │       │
 Comp      PC       CT     MV    AcctAge  TotMsg  SIGNA  Signal  Drift
(S/Nr)                                            RATE   Force   Ratio
   │       │       │                                │     │      │
   │       │       │                            (was     SF      DR%
   │       │       │                          Transmitter        precision
   │       │       │                          Composite)         tier only
   │       │       │                              │              │
   │       │       │                              └── weighted   └── no clean
   │       │       │                                  Core 5         token proxy
   │       │       │
   │       │       └── proxied by Cache Hit Rate (token model)
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

### Retired branches

**SDOT (Signal Delta Over Time)** — retired. Never had a confirmed formula. Not implemented.

**SDRM (Signal Density Resonance Metric)** — retired. No active prototype. Not implemented.

**Sig Delta** — never adopted. Drift Ratio remains canonical.

**Sig Alpha** — never adopted. Signal Force remains canonical.

See [naming_drift.md](naming_drift.md) for the full retirement notes.

---

## Composites layer

The composites layer is **3 metrics**:

1. **SIGNA RATE** (flagship — formerly Transmitter Composite)
2. **Signal Force** (SF)
3. **Drift Ratio** (DR%) — precision tier only

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
