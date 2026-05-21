# Layer 1 — Decision Log

Append-only record of decisions affecting the foundation layer (11 equations, class tiers, badges, rewards).

---

## 2026-05-20 · 11-equation set locked

**Decided by:** operator + VSClaude-OPUS47-LEAD
**Decision:** Active metric set is 11 total:
- Core 5: M.01 Compression Ratio · M.02 Prompt Complexity · M.03 Cross-Thread · M.04 Session Depth · M.05 Token Throughput
- Background 3: B.01 Message Volume · B.02 Account Age · B.03 Total Messages Lifetime
- Composites 3: C.01 SIGNA RATE · C.02 Signal Force · C.03 Drift Ratio
**Retired:** SDOT, SDRM (no confirmed formulas)
**Renamed:** Transmitter Composite → SIGNA RATE (C.01)
**Reversal cost:** High — would unwind multiple specs.

---

## 2026-05-21 · Badges added to Layer 1

**Decided by:** operator
**Decision:** Badges and rewards belong in Layer 1 (foundation), not Layer 2.
**Reasoning:** Badge definitions and reward catalog are canonical reference data (same nature as metric definitions). The badge evaluation engine + reward fulfillment is Layer 2 mechanics.
**Affects:** `1.2_layer-1-foundation/badges/BADGE_LEDGER.md`, `1.2_layer-1-foundation/rewards/REWARD_TIERS.md`
**Reversal cost:** Low — documentation organization.

---

## 2026-05-21 · 16 badges in initial catalog

**Decided by:** VSClaude-OPUS47-LEAD (pending operator review)
**Decision:** Initial badge catalog has 16 entries (BG.01–BG.16). Categories: Structural, Event, Prestige, Audit, Patron.
**Rarity targets:** Common >10%, Rare 1-10%, Epic 0.1-1%, Legendary <0.1%
**Affects:** `1.2_layer-1-foundation/badges/BADGE_LEDGER.md`
**Reversal cost:** Low — catalog can be edited freely.

---

## 2026-05-21 · Candidate metrics surfaced from ChatGPT System_Maturation_Recognition session

**Decided by:** operator (flagged for review) · captured by VSClaude-OPUS47-LEAD
**Source:** `4_references/System_Maturation_Recognition/02_Turns_Structured.md` (turns 39–56)
**Status:** PROPOSED — awaiting operator decision on each item.

Reading the ChatGPT session, four token-side concepts emerged that aren't yet first-class in CANON. Recommendation per item:

### 1. Cache I/O as a derived bridge metric
**What it is:** Bidirectional cache traffic = `RN.03 cache_read + RN.04 cache_creation`. GPT framed it as a TT+CT split metric.
**Already covered?** Partially. RN.03 + RN.04 exist as root numbers; the *ratio* and the *flow direction* aren't surfaced as a published metric.
**Proposal:** Add as a derived display metric on the profile page, not a new Core/Composite. Possible ID: `D.01 Cache I/O` (new `D.xx` derived-display family) or fold under M.05 Throughput as a sub-row.
**Decision needed:** Promote, fold, or skip.

### 2. Raw Input vs Fresh Input distinction
**What it is:** GPT (turn 41 / 48) split operator effort into two:
- Raw Input = total operator-authored tokens (effort proxy)
- Fresh Input = continuity reconstruction cost (re-explaining ontology after a context reset)
**Already covered?** Root numbers currently track `RN.02 fresh_input` only. "Raw Input" as a separate count is implicit but not split out.
**Proposal:** Either (a) add `RN.02b raw_input` as a sibling root number, or (b) treat raw_input as a derived field computed from RN.02 + cache-rebuild signal. The distinction affects M.01 Compression Ratio precision.
**Decision needed:** Add as RN sibling, or compute as derived?

### 3. Output : Fresh Input ratio as a clean SNR proxy
**What it is:** GPT's "Output:Fresh Input" ratio (8.3:1 in MO§ES R-window) reads as a mechanical proxy for M.01 Compression Ratio. Clean root merge claim, 85% match.
**Already covered?** M.01 Compression Ratio uses `signal_tokens / (signal_tokens + noise_tokens)` from sig_army audit (precision tier). Output:Fresh Input would give a free-tier-only computable approximation.
**Proposal:** Add as `M.01-free` or a "Compression (telemetry)" estimate displayed on free-tier profiles, with a note that the precision-tier value differs.
**Decision needed:** Promote as a published metric, or keep as internal-only proxy?

### 4. Continuity Economics as guidance/framework concept
**What it is:** GPT (turn 54–58) framed continuity itself as having measurable economic value — context reconstruction costs tokens, drift costs time, ontology collapse reduces throughput. Becomes the investor-facing why-this-matters layer.
**Already covered?** CONSERVATION_LAW.md covers the dimensional layers but not the economic framing explicitly.
**Proposal:** Add `1.1_layer-0-ground/guidance/CONTINUITY_ECONOMICS.md` capturing the framework. Distinct from CONSERVATION_LAW which is about signal preservation across resolution layers.
**Decision needed:** Add the guidance doc, or fold into existing CONSERVATION_LAW?

### 5. (Operator-flagged) Three-Layer Separation Model — Mechanical / Semantic / Philosophical
**What it is:** GPT (turn 55–56) proposed splitting the metric stack itself into three evidentiary types: directly measurable (Layer 1), inference from patterns (Layer 2), symbolic/faith-influenced (Layer 3).
**Already covered?** Our existing Layer 0/1/2/3 architecture is *delivery layers* (ground/foundation/mechanics/frontend), not *evidentiary types*. Different axis entirely.
**Proposal:** This is a separate cross-cutting model. Could live as `1.1_layer-0-ground/guidance/EVIDENTIARY_LAYERS.md` if operator wants it documented. Operator already corrected GPT on the "objectivity" framing (turn 57) — the right framing is "evidentiary type."
**Decision needed:** Document or skip — and if documented, where?

**Reversal cost:** Low until any of these get embedded into schema / scoring. Documentation-only at this stage.

---

## Open questions

1. Should BG.07 (Audit Verified) require minimum Compression threshold, or any successful audit qualifies?
2. BG.10 (Quiet Giant) — "bottom 50% MV" is currently the threshold. Operator should confirm this is the right cutoff.
3. Should Hall of Signal records be tracked retroactively from existing data, or only forward from launch?
4. Class promotion stickiness (3 consecutive cycles) — confirmed in CANON RS.07 — but should we visualize the "pending promotion" state to operators (e.g., "2 of 3 cycles confirmed")?
5. Each of the five candidates above (per the 2026-05-21 entry).
