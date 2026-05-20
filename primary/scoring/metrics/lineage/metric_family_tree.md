# Metric Family Tree

A visual lineage of how every SigRank metric relates to every other, including renames, splits, and unresolved branches.

---

## The full tree

```
                           SIGRANK METRIC STACK
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
         CORE 5                BACKGROUND 3            COMPOSITES
            │                       │                       │
   ┌────────┼────────┐      ┌───────┼───────┐      ┌────────┼────────┐
   │        │        │      │       │       │      │        │        │
Comp     PC      CT       MV    AcctAge  TotMsg  SIGNA    SDRM   Signal
(S/Nr)                                            RATE             Force
   │     │       │                                  │                │
   │     │       │                                (was              (may be
   │     │       │                              Transmitter         Sig Alpha?)
   │     │       │                              Composite)
   │     │       │                                  │
   │     │       │                                  └── derived from Core 5
   │     │       │
   │     │       └── proxied by Cache Hit Rate (token model)
   │     │
   │     └── proxied by Raw Input (weak — volume, not complexity)
   │
   └── proxied by Output:Fresh_Input ratio (token model)


                              ┌────── SD (Session Depth) ──┐
                              │                              │
                              └── proxied by turns/session  │
                                                              │
                                              ┌── Drift Ratio (DR%)
                                              │     (may be Sig Delta?)
                                              │
                                              └── precision tier only
                                                  no clean token proxy
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

### Transmitter Composite chain
```
"Transmitter Composite" (functional, 2025)
    ↓
"Trans Comp" (display abbreviation)
    ↓
SIGNA RATE (flagship public name, 2026-03)
```

### SDOT branch (unresolved)
```
SDOT (Signal Delta Over Time)
    │
    ├── may have evolved into SDRM
    │
    └── may have remained distinct
         (both currently tracked separately)
```

### Drift / Force branch (unresolved)
```
Drift Ratio (DR%) ──── may be ────► Sig Delta
                │
Signal Force (SF) ──── may be ────► Sig Alpha
                       (paired rename hypothesis)
```

---

## The "Big 3" composites concept

The composites layer was sometimes called the "Big 3":

1. **SIGNA RATE** (formerly Transmitter Composition / T)
2. **SDRM** (Signal Density Resonance Metric)
3. **Signal Force** (SF)

Drift Ratio joined as a 4th composite later. The composites layer is now **4 metrics**, not 3.

---

## The "Core 5 + Background 3" structure

This naming convention came from the v2 Signal Codex prototype. It's stable:

- **Core 5** = performance signals
- **Background 3** = identity / normalization
- **Composites** = derived flagship + advanced

**Total active metric count: 12** (5 + 3 + 4)

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
