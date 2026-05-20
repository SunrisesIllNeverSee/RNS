# SDRM (Signal Density Resonance Metric)

**Status:** provisional — definition stable, formula still under recovery
**Layer:** Composite (advanced)
**Public label:** SDRM
**Short label:** SDRM
**DB field:** `sdrm_score`

---

## Definition

A multi-axis resonance/density metric measuring how cohesively the Core 5 hold together over time. SDRM detects when an operator's metrics are **mutually reinforcing** (real Transmitter behavior) vs. when one metric is propping up the others (gaming).

SDRM is the **internal coherence detector**.

---

## Lineage notes — IMPORTANT

SDRM is **NOT** the same as SDOT. Both are tracked.

- **SDOT** (Signal Delta Over Time) — earlier time-evolution / slope concept
- **SDRM** (Signal Density Resonance Metric) — later multi-axis form

The exact relationship between them is unresolved. They may share a lineage but they are recorded as separate metrics until archive recovery confirms.

See [../lineage/naming_drift.md](../lineage/naming_drift.md).

---

## Provisional formula

The conversation never locked an exact SDRM formula. Working hypothesis:

```
SDRM = (Compression × (SD + PC)) × Thread_Rate
```

Where `Thread_Rate = CT / Total_Messages` (the cross-thread density).

This formula came from the v2 `signal_codex_basic.html` prototype. Treat it as a placeholder until recovery confirms or replaces.

---

## What SDRM tries to detect

A real Transmitter has:
- High Compression
- High SD
- High PC
- High CT
- Reasonable TT

A gaming operator typically has **one** high metric and lower correlated metrics. SDRM penalizes that asymmetry.

A high SDRM means "your metrics resonate together." A low SDRM means "one of your metrics is doing all the work."

---

## Status

- **MVP:** not required
- **Phase 2:** recommended
- **Display:** internal analytics initially; may surface in Pro tier

---

## Open questions

1. Is the v2 prototype formula correct or a placeholder?
2. What is the actual mathematical relationship to SDOT?
3. Should SDRM penalize asymmetry directly (variance among the Core 5) or measure resonance positively (correlation among them)?
4. Is SDRM windowed or rolling?
