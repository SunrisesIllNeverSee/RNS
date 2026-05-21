# SDOT (Signal Delta Over Time)

**Status:** 🟢 LOCKED (structure) · 🟡 PROVISIONAL (formula — operator to lock later)
**Layer:** Composite (Big 3, inside the 11 core)
**Public label:** SDOT
**Short label:** SDOT
**DB field:** `sdot_score`
**Locked 2026-05-21 by:** operator (chat directive: "lock in sdot and sdrm i'll do the math later")

---

## Definition

A time-evolution / slope metric measuring how an operator's signal output changes across windows. SDOT detects:

- whether the operator's signal output is accelerating or decelerating
- whether high-Core-5 readings are sustained or a single-window spike
- whether the system itself is "phase-transitioning" relative to baseline (the prior 04-SDOT-SigRank framing: signal output outpacing the system's learning)

SDOT is the **temporal trajectory detector**. SDRM is the **internal coherence detector** at a single point in time. They are deliberately tracked as distinct metrics.

---

## Lineage notes — IMPORTANT

SDOT is **NOT** the same as SDRM. Both are tracked in the Big 3 alongside SIGNA RATE.

- **SDOT** (Signal Delta Over Time) — slope / time-evolution
- **SDRM** (Signal Density Resonance Metric) — multi-axis cohesion at a single window

The operator confirmed on 2026-05-21 that these are separate and both belong in the Big 3. Prior retirement (by `Claude Sonnet 4.6` in commit `2c3b0be`) was incorrect and has been reversed.

See [../lineage/naming_drift.md](../lineage/naming_drift.md) and [../../../../../../4_references/04-SDOT-SigRank/](../../../../../../4_references/04-SDOT-SigRank/) for the historical reference material.

---

## Provisional formula (not locked)

Working hypothesis based on prior framing:

```
SDOT(t) = d(SIGNA_RATE) / dt   (rolling window slope)
```

Or in discrete terms:

```
SDOT(window_n) = SIGNA_RATE(window_n) - SIGNA_RATE(window_n-1)
```

A positive SDOT means the operator's composite signal is *rising* across windows. A flat near-zero SDOT means sustained signal. A negative SDOT means decay.

This is a placeholder. The original SDOT framing in `4_references/04-SDOT-SigRank/` was about signal output outpacing the *system's* learning, which is a different (and more interesting) framing — it would require comparing the operator's trajectory against a population/model baseline trajectory, not just self-delta.

---

## What SDOT tries to detect

- sustained operator (flat-high SDOT) vs. one-window spike (rising-then-falling SDOT)
- phase transitions where the operator's pace exceeds the model's natural absorption rate
- decline signals that wouldn't show in a single-window SIGNA RATE reading

---

## Status

- **MVP:** not required (Big 3 may ship with placeholders until formulas locked)
- **Phase 2:** required
- **Display:** internal initially; may surface in Pro tier as trajectory chart

---

## Open questions

1. Self-delta only (operator vs. their own prior windows), or population-relative (operator vs. model baseline)?
2. Window size — 24h, 7d, 30d, or all of them with separate values?
3. Should SDOT be a scalar or a vector of per-window deltas?
4. Relationship to Drift Ratio (extra, outside core) — DR% measures within-session drift; SDOT measures across-session evolution. Confirm they're not measuring the same thing in different windows.
