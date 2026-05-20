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

## SDOT and SDRM — RETIRED

**Status: removed from active stack**

| Term | What it tried to be | Resolution |
|---|---|---|
| SDOT | Signal Delta Over Time — slope/delta concept | retired |
| SDRM | Signal Density Resonance Metric — multi-axis | retired |

Both were under recovery in GPT thread-0369. Neither had a confirmed formula. Neither was in any active prototype. They were "system constructions" from GPT outputs that never landed as locked metrics.

**Decision (locked):** Both retired. Not implemented. Not in the database. Not in the snapshot payload. If a real multi-axis resonance metric is needed later, it'll be designed fresh with a clear formula — not resurrected from undefined GPT-era branches.

---

## Drift Ratio (Sig Delta hypothesis — resolved)

The earlier theory: "drift ratio became sig delta to match signal force as sig alpha."

That rename **never materialized**. No prototype uses Sig Delta. No spec uses Sig Delta. The original name **Drift Ratio (DR%)** stands as canonical.

**Decision (locked):** Drift Ratio is the canonical name. "Sig Delta" was a possible rename that never happened — drop the alias from active vocabulary.

---

## Signal Force (Sig Alpha hypothesis — resolved)

Same pattern. The hypothesized rename to "Sig Alpha" never landed. No prototype uses Sig Alpha. The v2 Signal Codex shipped with **Signal Force (SF)**.

**Decision (locked):** Signal Force is the canonical name. "Sig Alpha" was a possible rename that never happened — drop the alias.

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
