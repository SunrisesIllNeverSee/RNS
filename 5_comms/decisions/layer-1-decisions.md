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
**Affects:** `layer-1-foundation/badges/BADGE_LEDGER.md`, `layer-1-foundation/rewards/REWARD_TIERS.md`
**Reversal cost:** Low — documentation organization.

---

## 2026-05-21 · 16 badges in initial catalog

**Decided by:** VSClaude-OPUS47-LEAD (pending operator review)
**Decision:** Initial badge catalog has 16 entries (BG.01–BG.16). Categories: Structural, Event, Prestige, Audit, Patron.
**Rarity targets:** Common >10%, Rare 1-10%, Epic 0.1-1%, Legendary <0.1%
**Affects:** `layer-1-foundation/badges/BADGE_LEDGER.md`
**Reversal cost:** Low — catalog can be edited freely.

---

## Open questions

1. Should BG.07 (Audit Verified) require minimum Compression threshold, or any successful audit qualifies?
2. BG.10 (Quiet Giant) — "bottom 50% MV" is currently the threshold. Operator should confirm this is the right cutoff.
3. Should Hall of Signal records be tracked retroactively from existing data, or only forward from launch?
4. Class promotion stickiness (3 consecutive cycles) — confirmed in CANON RS.07 — but should we visualize the "pending promotion" state to operators (e.g., "2 of 3 cycles confirmed")?
