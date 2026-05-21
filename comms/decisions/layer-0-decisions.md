# Layer 0 — Decision Log

Append-only record of decisions affecting the ground foundation (root numbers, canonical IDs, MO§ES reference, conservation-law guidance).

---

## 2026-05-21 · Layer scaffold model adopted

**Decided by:** operator + VSClaude-OPUS47-LEAD
**Decision:** Project organized into 4 layers (Layer 0 ground / Layer 1 foundation / Layer 2 mechanics / Layer 3 frontend) plus `comms/` + `references/` + `inbox/`.
**Reasoning:** Operator wants explicit scaffolding with Layer 0 as the unbuilt-on bedrock that everything else builds from. Mirrors the dimensional-resolution stack in CONSERVATION_LAW.md.
**Reversal cost:** Medium — would require unwinding directory moves.

---

## 2026-05-21 · Refinery ≠ rns-sigrank

**Decided by:** operator
**Decision:** This version of SigRank (rns-sigrank, token-totals resolution) is NOT canonized with Refinery. They are different dimensional layers of the same conserved signal.
**Affects:** CONSERVATION_LAW.md, LINEAGE.md, build_layers.md
**Reasoning:** Refinery operates at token-per-word resolution (SigSystem-grade). Current SigRank operates at token-total resolution. Conflating them obscures the dimensional model.
**Reversal cost:** Low — documentation only.

---

## 2026-05-21 · Operator IS OG SIGRANK

**Decided by:** operator
**Decision:** OG SIGRANK is not a separate prior product. The operator is OG SIGRANK. The originating mapping between language SNR and token telemetry was demonstrated by the operator's prior body of work.
**Affects:** LINEAGE.md, CONSERVATION_LAW.md
**Reasoning:** Validation of the conservation law is the operator's lived prior work, not a published paper or benchmark.
**Reversal cost:** N/A — identity claim, not a technical decision.

---

## 2026-05-21 · 12 root numbers locked (+ RN.13 hidden)

**Decided by:** operator
**Decision:** Locked the root number set at 12 visible + 1 hidden:
- RN.01–RN.04: Tokens (output / fresh_input / cache_read / cache_creation) — split into 4 sub-counts because they carry the most important signal
- RN.05: Messages
- RN.06: Sessions
- RN.07: Turns
- RN.08: Timestamps
- RN.09: Age (derived)
- RN.10: LOC (lines of code — hybrid automated + operator-pointed)
- RN.11: Prompt text (precision tier only)
- RN.12: Parent message id (precision tier only)
- RN.13: Work classification (auto / operator / hybrid) — HIDDEN, optional tag
**Reasoning:** Token sub-counts unlock cache hit rate, output:input ratio, throughput. LOC enables cost-per-LOC (field-crushing metric). RN.13 is metadata that interprets others; hidden for MVP.
**Reversal cost:** Medium — affects schema, agent code, multiple downstream docs.

---

## 2026-05-21 · Two reference types

**Decided by:** operator
**Decision:** Layer 0 splits into:
- `build/` — production canon (used to compute)
- `guidance/` — philosophical context (interprets the compute)
**Reasoning:** The conservation law informs interpretation; the equations drive computation. They serve different purposes and should not be conflated.
**Reversal cost:** Low — documentation only.

---

## 2026-05-21 · CANON.md location

**Decided by:** operator
**Decision:** CANON.md moved from `primary/scoring/CANON.md` to `primary/scoring/layer-0-ground/build/CANON.md`.
**Reversal cost:** Low — `git mv` preserves history.

---

## Open questions awaiting operator decision

1. Should B.03 lifetime count be computed via one-time `extract_benchmark_window.py --all-time` scan, or via continuous append-only counter?
2. Active minutes (T.08) estimation algorithm — three options listed in MOSES_REFERENCE; which do we pick?
3. Drift Ratio (C.03) alignment signal — 5 options in SOURCE_DATA.md (repetition heuristics / sentence-transformers / topic coherence / sig_army / reset heuristics) — operator hasn't picked.
4. Other metrics the operator mentioned owing — pending drop into `inbox/`.
5. Old master list documents — pending operator paths.
