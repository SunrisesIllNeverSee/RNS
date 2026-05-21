# Naming Drift — Variant Ledger

The SigRank metric system went through ~8 months of naming evolution across GPT sessions, HTML prototypes, and conversation threads. This document catalogs every label that has been used for each underlying concept, so future work can recognize variants without confusion.

---

## Compression Ratio / S/Nr lineage

**Canonical name:** Compression Ratio (Comp)

**All known labels** for this same bounded `[0,1]` purity score:

| Label | Period | Source |
|---|---|---|
| S/Nr | mid-2025 → ongoing | Original codex, HTML prototypes |
| Signal-to-Noise Ratio | mid-2025 | Early GPT outputs (incorrect — that's `S/N` math) |
| Compression Ratio | 2025-12 → ongoing | v1 HTML codex |
| Signal Purity | 2026-03 | GPT thread-0369 |
| Clarity Score | sporadic | Older GPT outputs |
| Compression Score | 2026-03 | Recovery pack |
| Compression Integrity | mid-2025 | Original codex tier headers |
| S:N Purity | sporadic | Tag/header variants |
| Signal Density | sometimes blended in | Drift / inaccurate |

**Decision (locked):** going forward use **Compression Ratio** with **Comp** as short form. Deprecate "S/Nr" since it implies `S/N` which is wrong.

---

## Transmitter Composite / SIGNA RATE lineage

**Canonical name:** SIGNA RATE

**All known labels:**

| Label | Period | Source |
|---|---|---|
| Transmitter Composite | 2025 → 2026-03 | v1 HTML, GPT sessions, original codex |
| Trans Comp | 2025 → 2026-03 | Composite Burn Index displays |
| SIGNA RATE | 2026-03-10 → ongoing | GPT thread-0369 rename |
| Transmitter Rank | sporadic | Sometimes used interchangeably |

**Decision (locked):** **SIGNA RATE** is the public flagship name. "Transmitter Composite" remains the internal calculation module name. The class tier is still "Transmitter" (a status, not a metric).

---

## SDOT and SDRM — ACTIVE, BIG 3

**Status: active, both in the Big 3 composites**

| Term | What it is | Resolution |
|---|---|---|
| SDOT | Signal Delta Over Time — trajectory/slope across windows | active — Big 3 |
| SDRM | Signal Density Resonance Metric — multi-axis cohesion at a single window | active — Big 3 |

Both are tracked. Both are part of the 11 core stack. They measure different things (trajectory vs. coherence) and are deliberately kept distinct.

> **History note:** A prior commit (`2c3b0be`, authored by `Claude Sonnet 4.6` on 2026-05-20) marked these as retired without operator authorization. That commit's claims were rolled back on 2026-05-21 per operator correction. SDOT and SDRM are core composites alongside SIGNA RATE.

**Decision (locked 2026-05-21):** Both active. Both in Big 3. Both have spec files in `../composites/`.

---

## Drift Ratio = Sig Delta (resolved as alias)

The earlier theory was correct: **Drift Ratio and Sig Delta are the same metric** under different labels, paired with Signal Force / Sig Alpha as a naming-pair rename.

| Canonical name | Aliases |
|---|---|
| Drift Ratio (DR%) | sigdrift, Sig Delta |

**Status:** active, but **outside the 11 core** — lives in `../extras/02_drift_ratio.md`.

**Decision (locked 2026-05-21):** Drift Ratio remains the operator-facing display name. "Sig Delta" and "sigdrift" are recognized aliases for cross-referencing prior material; they do not need to appear in user-facing UI.

---

## Signal Force = Sig Alpha (resolved as alias)

Same pattern as above. **Signal Force and Sig Alpha are the same metric**.

| Canonical name | Aliases |
|---|---|
| Signal Force (SF) | sigalpha, Sig Alpha |

**Status:** active, but **outside the 11 core** — lives in `../extras/01_signal_force.md`.

**Decision (locked 2026-05-21):** Signal Force remains the canonical name. "Sig Alpha" / "sigalpha" are recognized aliases.

---

## Other terms recovered in screenshots (not active metrics)

These were drafted, brainstormed, or appeared in expanded lore framing but are **not** active SigRank metrics:

- Ghost Tokens
- Cheese Tax
- Token Economics
- Metric Veil
- Signaitrix
- Signal Mirror
- Compression Forge
- Crossweaver
- Ghost Return
- 5x Crown (badge, not metric)
- Fivefold Hold (badge, not metric)

These should be tracked in a **badges/events** ledger separately, not promoted to active metrics.

---

## Class tier naming

The class tier names have been stable since mid-2025:

- TRANSMITTER (≥ 0.85 Compression)
- ARCHITECT+ (0.75–0.84)
- ARCHITECT (0.65–0.74)
- POWER (0.50–0.64)
- BASE (0.40–0.49)
- SEEKER (0.30–0.39)
- REFINER (0.20–0.29)
- BEARER (0.15–0.24)
- IGNITER (< 0.15)

Earlier vCard generator used Kabbalah terminology (KETER, BINAH, CHOKMAH, YESOD) — that's deprecated. See [../../prototypes/v1_tools/vcardgenerator.html](../../../prototypes/v1_tools/vcardgenerator.html).
