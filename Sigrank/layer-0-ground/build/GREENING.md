# Greening Roadmap — Path to All 🟢

Every value, parameter, and step that isn't 🟢 LOCKED today, what's blocking it, what acceptance criteria flips it to green, and which sprint owns it.

> **Rule:** Don't promote anything to 🟢 until the acceptance criteria are met. No shortcuts.

---

## Greening summary

**Today's status snapshot:**
- 🟢 LOCKED: ~70% of canon entries
- 🟡 PROVISIONAL: ~20% (mostly Ruleset RS.xx parameters and free-tier estimates)
- 🔴 OPEN: ~10% (precision tier sig_army + anti-gaming)

**Target:** all 🟢 within ~12 weeks of build work, sequenced through the build_layers.md milestones.

---

# 🟡 PROVISIONAL — Concept locked, value/curve tunable

## Telemetry inputs

### T.08 `active_minutes_est` — wall-time estimation

**Blocker**: No standard for computing active minutes from session timestamps.

**Acceptance criteria to 🟢**:
- [ ] Define algorithm: e.g., sum of intervals between adjacent messages within a session, gaps > 5 min excluded
- [ ] Document edge cases (single-message sessions, abandoned sessions)
- [ ] Implement in `sigrank-agent/src/features/session_features.py`
- [ ] Verify against MO§ES R.15 (1.84 min/task) — agent computation should produce comparable wall time

**Owner**: Agent build (S.03)
**Sprint**: Sprint 4 (Local Agent build)

---

## Core 5 metrics

### M.02 `Prompt Complexity` — needs sig_army for exact

**Blocker**: PC sub-extractors (instruction_layers, recursion_logic, system_entities, constraint_density, symbolic_precision, response_shaping_directives) require actual prompt analysis. Free-tier estimate is low-confidence.

**Acceptance criteria to 🟢 (for precision tier)**:
- [ ] Build sig_army on Modal (`sigrank-sig-army` private repo)
- [ ] Train/configure word_vault classifier on the 4,900-token reference set
- [ ] Implement each sub-extractor as a separate function
- [ ] Apply RS.04 weighted composite
- [ ] Run against MO§ES sessions → produce R.xx PC reference value
- [ ] Validate against 10+ operator audits (cross-check sub-scores manually)

**Owner**: sig_army build (S.25, S.26)
**Sprint**: Sprint 11 (Pro Tier launch)

**Acceptance criteria to 🟢 (for free-tier estimate)**:
- [ ] Acknowledge: free-tier M.02 stays 🟡 forever (estimate, not exact). That's the upsell driver.
- [ ] Document the confidence flag: `prompt_complexity_confidence: low` in payload
- [ ] Frontend renders `~92*` with the asterisk pattern to make it visible

**Owner**: Confidence flagging
**Sprint**: Sprint 2 (Algo + Scoring)

---

### M.04 `Session Depth` — bucket curve is RS.02

**Blocker**: Score normalization from raw turns/session to [0,100] uses proprietary bucket curve.

**Acceptance criteria to 🟢**:
- [ ] Lock RS.02 bucket breakpoints in Ruleset v1.0 server-side config
- [ ] Validate against MO§ES R.11 (348.9 turns/session → expected score)
- [ ] Run sensitivity analysis: what happens at 10 turns? 30? 100? 300?
- [ ] Implement in `sigrank-scoring-worker/src/scoring/normalize.py`

**Owner**: Scoring worker build (S.15)
**Sprint**: Sprint 2

---

## Background 3

### B.03 `Total Messages` — no MO§ES reference value

**Blocker**: MO§ES R.xx doesn't have B.03 because the poster window was 7d, not all-time.

**Acceptance criteria to 🟢 (for the MO§ES reference)**:
- [ ] Run `extract_benchmark_window.py` with `--all-time` against full Claude Code session history
- [ ] Sum `turn` counts across every session file ever
- [ ] Record as new canonical ID `R.23` in CANON.md
- [ ] Cite source path and computation

**Owner**: Reference data extraction
**Sprint**: Sprint 1 (Foundation)

---

## Composites

### C.01 `SIGNA RATE` — RS.01 weights + RS.03 recency curve tunable

**Blocker**: The structure is locked but the exact weights are subject to tuning across rulesets.

**Acceptance criteria to 🟢 (for current Ruleset v1.0)**:
- [ ] Commit RS.01 = `[0.30, 0.20, 0.20, 0.15, 0.15]` (Comp / SD / PC / CT / TT) in server-side ruleset config
- [ ] Validate: feed MO§ES R.xx inputs → produce a SIGNA RATE → manually verify reasonableness
- [ ] Commit RS.03 recency curve: `<24h→1.00, <72h→0.97, <168h→0.94, <336h→0.88, <720h→0.80, >720h→0.65`
- [ ] Tag Ruleset v1.0 as deployed in `rulesets` DB table

**Owner**: Scoring worker build (S.16, S.18)
**Sprint**: Sprint 2

**Note**: After v1.0 launches, RS.01 may be tuned based on real operator distribution. Each tuning = new ruleset version = full historical replay (S.X.01).

---

### C.02 `Signal Force` — no MO§ES reference

**Blocker**: B.03 lifetime not yet computed for MO§ES (same as B.03 above).

**Acceptance criteria to 🟢**:
- [ ] B.03 computed for MO§ES (see B.03 row above)
- [ ] Compute C.02 raw = (B.03_moses × M.04_moses_avg) / B.02_moses (119d)
- [ ] Apply log normalization → C.02 score
- [ ] Record as new canonical ID `R.24` in CANON.md

**Owner**: Reference data extraction
**Sprint**: Sprint 1 (depends on B.03 greening)

---

### C.03 `Drift Ratio` — precision tier only, alignment scoring open

**Blocker**: Requires semantic embedding or custom vector model for alignment scoring.

**Acceptance criteria to 🟢 (decision)**:
- [ ] Decide: use semantic embeddings (e.g., sentence-transformers) OR build custom vector model with word_vault?
- [ ] Document decision in `metrics/composites/03_drift_ratio.md`
- [ ] Define `aligned_messages` operationally (e.g., cosine similarity to session vector > threshold X)

**Acceptance criteria to 🟢 (implementation)**:
- [ ] Implement in sig_army (`sigrank-sig-army/src/drift_detection/`)
- [ ] Run against MO§ES sessions → produce R.xx Drift reference value
- [ ] Validate: manually drift-rate 5+ sessions and compare to algorithm

**Owner**: sig_army build (S.26)
**Sprint**: Sprint 11

---

# 🟡 RS.xx — Proprietary Ruleset Parameters

These are server-side scoring engine constants. Tunable across ruleset versions but locked within each version.

## RS.01 — SIGNA RATE weights

**Status**: 🟡 PROVISIONAL (locked in v1.0 but tunable in future versions)

**Proposed v1.0**:
- M.01 (Compression) — 0.30
- M.04 (Session Depth) — 0.20
- M.02 (Prompt Complexity) — 0.20
- M.03 (Cross-Thread) — 0.15
- M.05 (Token Throughput) — 0.15
- Sum = 1.0

**Acceptance criteria to 🟢 (v1.0 lock)**:
- [ ] Commit values to server-side ruleset config (NOT public)
- [ ] Validate: feed MO§ES inputs, compute SIGNA RATE, sanity-check against current `96.4` reference
- [ ] Document rationale: Why 0.30 for Compression? (it's the moat) Why equal weights for SD/PC? Etc.

**Owner**: Scoring worker config
**Sprint**: Sprint 2

---

## RS.02 — Session Depth bucket curve

**Status**: 🟡 PROVISIONAL

**Proposed v1.0**:
- 30+ → 100
- 25-29 → 92
- 20-24 → 84
- 15-19 → 72
- 10-14 → 58
- 5-9 → 42
- < 5 → 25

**Note**: These are RAW chain-length tiers, NOT turn-count tiers. With proxy (turns/session), MO§ES at 348.9 turns/session → after divide-by-2-conversion-factor or similar, still likely maxes at 100. Need to determine the proxy→raw conversion factor.

**Acceptance criteria to 🟢**:
- [ ] Decide: should free-tier proxy SD use the same bucket curve as exact SD?
- [ ] If different, document both curves (one for proxy, one for exact)
- [ ] Run validation: feed 10+ sample SD inputs → bucketed score → sanity check
- [ ] Commit to server-side config

**Owner**: Scoring worker
**Sprint**: Sprint 2

---

## RS.03 — Recency modifier curve

**Status**: 🟡 PROVISIONAL

**Proposed v1.0**:
- < 24h → 1.00
- < 72h (3d) → 0.97
- < 168h (7d) → 0.94
- < 336h (14d) → 0.88
- < 720h (30d) → 0.80
- > 720h → 0.65

**Acceptance criteria to 🟢**:
- [ ] Validate that the decay isn't so steep it eliminates serious-but-busy operators (e.g., 14d off vacation → score halved? Probably too aggressive)
- [ ] Validate that it's steep enough to prevent fossilized #1 entrenchment (someone who scored once 2 years ago and never returned shouldn't keep top rank)
- [ ] Commit to server-side config

**Owner**: Scoring worker config
**Sprint**: Sprint 2

---

## RS.04 — PC sub-score weights

**Status**: 🟡 PROVISIONAL (requires sig_army)

**Proposed v1.0**:
- instruction_layers — 0.25
- recursion_logic — 0.20
- system_entities — 0.20
- constraint_density — 0.15
- symbolic_precision — 0.10
- response_shaping_directives — 0.10
- Sum = 1.0

**Acceptance criteria to 🟢**:
- [ ] sig_army built (S.25)
- [ ] Each sub-extractor produces a [0, 100] output
- [ ] Validate weighted composite produces sensible PC scores on test cases
- [ ] Commit weights to ruleset config

**Owner**: sig_army
**Sprint**: Sprint 11

---

## RS.05 — Class threshold exact breakpoints

**Status**: 🟢 LOCKED (qualitative cuts in K.01-K.09 match numerical values)

This one is essentially done — the qualitative ranges in the K.xx table ARE the numerical breakpoints. No additional work needed unless we decide to tighten/loosen any tier boundary.

---

## RS.06 — Anti-gaming penalty rules

**Status**: 🔴 OPEN (disabled for MVP)

**Proposed Phase 2**:
- **Spam penalty**: if MV spikes >40% above 7d avg AND Compression drops >10% AND SD drops >15% → -5 to -25 penalty
- **Redundancy penalty**: if `repeated_chunks / total_chunks` > threshold X → mild/moderate/severe penalty
- **Synthetic inflation**: if PC rises but CT does not → flag for manual review

**Acceptance criteria to 🟢**:
- [ ] Decide if anti-gaming is MVP or Phase 2 (currently Phase 2)
- [ ] Implement detection patterns in `sigrank-scoring-worker/src/scoring/anti_gaming.py`
- [ ] Add admin dashboard view to surface flagged operators
- [ ] Define penalty thresholds and resolution flow
- [ ] Validate against synthetic gaming attempts (simulate 5+ patterns)

**Owner**: Scoring worker / anti-gaming module
**Sprint**: Sprint 12+ (post-MVP)

---

## RS.07 — Class promotion stickiness

**Status**: 🟡 PROVISIONAL

**Proposed v1.0**: 3 consecutive scoring cycles required for promotion. Demotion immediate.

**Acceptance criteria to 🟢**:
- [ ] Validate: 3 cycles = appropriate stickiness? Too long? Too short? Depends on cycle duration (daily? hourly?)
- [ ] Define cycle duration explicitly (daily snapshots = 3 days for promotion)
- [ ] Implement in S.19 (class assignment)
- [ ] Test: simulate operator at threshold, verify promotion fires on day 3 not day 1

**Owner**: Scoring worker
**Sprint**: Sprint 2

---

# 🔴 OPEN — Not yet built / not yet decided

## Operator and submission counts (used throughout mockup hero stats)

**Not in CANON yet** — but referenced as `*` placeholders in the mockup hero.

**Acceptance criteria to add to canon (and 🟢)**:
- [ ] Define new IDs:
  - `O.01` total_operators (count of `operators` table)
  - `O.02` operators_active_24h (last_seen within 24h)
  - `O.03` snapshots_today (submitted today)
  - `O.04` operators_by_class (count per K.01-K.09)
- [ ] Add to CANON.md Section II.5 or new Section X
- [ ] Implement aggregation in scoring worker cron
- [ ] Cache in a `system_stats` table (or expose via `leaderboards_cached`)

**Owner**: Stats aggregation
**Sprint**: Sprint 7 (Frontend Core)

---

## S.25 / S.26 — sig_army classifier and exact M.01/M.02/C.03

**Status**: 🔴 OPEN — biggest single greening blocker

**What's needed**:
- [ ] Set up Modal account + private repo `sigrank-sig-army`
- [ ] Port the word_vault from `Sigrank/word_vault/words_user/` (4,900 token files) into the classifier
- [ ] Build the classifier: token → signal/noise binary classification
- [ ] Build sub-score extractors for PC (instruction_layers, recursion_logic, etc.)
- [ ] Build drift detection (semantic vector deviation)
- [ ] Build the audit pipeline (S.25-S.28)
- [ ] Validate against MO§ES sessions
- [ ] Promote M.01_exact, M.02_exact, C.03 to 🟢 with MO§ES reference values

**Owner**: sig_army build
**Sprint**: Sprint 11

---

## S.X.02 — Anti-Gaming Detection Module

Already covered above under RS.06. Same priority.

---

## Active platform adapters beyond Claude Code (S.01)

**Status**: 🔴 OPEN for all non-Claude platforms

**Acceptance criteria per adapter**:
- [ ] Document source path / export format
- [ ] Implement `Adapter` ABC (`detect()`, `list_sessions()`, `parse_session()`)
- [ ] Token telemetry quality estimate (excellent/good/medium/low)
- [ ] Validate against operator with that platform

**Per-platform sprints**:
- Claude Code: 🟢 Sprint 4 (priority 1)
- ChatGPT: 🟡 Sprint 9 (priority 2)
- Cursor: 🟡 Sprint 9 (priority 2)
- Gemini: 🔴 Sprint 12 (priority 3)
- Codex: 🔴 Sprint 12 (priority 3)
- Pi: 🔴 Sprint 12+ (priority 4)
- Generic JSON: 🟡 Sprint 9 (always-available catch-all)

---

# Path to 🟢 — Sprint-by-sprint

Tied to `architecture/build_layers.md` sprint sequence.

## Sprint 1: Foundation
- 🟢 Greening targets: **B.03 MO§ES reference (R.23)**, **C.02 MO§ES reference (R.24)**
- Acceptance: re-run extraction with `--all-time`, log values into CANON.md

## Sprint 2: Algo + Scoring Engine
- 🟢 Greening targets: **RS.01, RS.02, RS.03, RS.07** all locked in v1.0
- Acceptance: ruleset config committed, scoring worker passes MO§ES inputs → SIGNA RATE 96.4
- 🟢 M.04, C.01, C.02 all green (formulas validated against MO§ES)

## Sprint 3: Backend Pipeline
- 🟢 Greening targets: **S.14-S.22** all green (worker operational)
- 🟢 S.09-S.13 ingest pipeline green

## Sprint 4: Local Agent
- 🟢 Greening targets: **S.01 (Claude Code), S.02-S.08** all green
- 🟢 T.08 active_minutes_est defined and implemented

## Sprint 7: Frontend Core
- 🟢 Greening targets: **O.01-O.04** operator counts implemented
- 🟢 S.30-S.33 frontend green
- All hero stat placeholders replaced with real aggregates

## Sprint 9: Adapters
- 🟢 Greening targets: **ChatGPT, Cursor, Generic JSON adapters** green
- Multi-platform support live

## Sprint 11: Precision Tier
- 🟢 Greening targets: **S.25, S.26, S.27, S.28, S.29** all green
- 🟢 M.02_exact, M.01_exact, C.03 all green with MO§ES reference
- 🟢 RS.04 (PC sub-score weights) locked

## Sprint 12+: Anti-Gaming and Other Platforms
- 🟡→🟢 RS.06 implemented and enabled
- 🟢 S.X.02 anti-gaming module operational
- 🟢 Gemini, Codex, Pi adapters

---

# Greening checklist (top of every sprint review)

Each sprint review, run this checklist:

- [ ] Are there new `*` placeholder values in any mockup that should now be real?
- [ ] Are there new ruleset parameters not yet in RS.xx?
- [ ] Are there new metric values not yet in CANON.md tables?
- [ ] Has the MO§ES reference data been refreshed since last sprint?
- [ ] Have any 🟡 items met their acceptance criteria?
- [ ] Have any 🔴 items been built?
- [ ] Does the IPO.md still reflect the actual pipeline?
- [ ] Does the DATA_LEDGER.md still reflect what's in the mockup?

If any answer is "I don't know" — pause and audit before proceeding.

---

# When you change ruleset_version

Critical: any change to RS.xx parameters requires a new ruleset version.

Process:
1. Update RS.xx value(s) in this document
2. Increment `current_ruleset_version` in scoring worker config (e.g., 1.0 → 1.1)
3. Add row to CANON.md Section IX "Change log"
4. Deploy scoring worker with new version
5. Run replay job (S.X.01): re-score every historical `snapshot_submissions` row
6. Compare new `metric_snapshots` to old; flag operators whose class or rank changed materially
7. Notify affected operators (notification service, S.X.??)
8. Promote new ruleset to active; old version stays in `rulesets` table for replay safety

---

# Bottom line

**To go from today's state to all-🟢**: roughly 12 sprints (≈ 12-18 weeks) of focused build work, sequenced through the build_layers milestones. The biggest single greening blocker is **sig_army on Modal** (Phase 4 of the IPO pipeline) — without it, M.02, C.03, and the precision tier upsell stay 🟡.

**The fastest path to "leaderboard live with one real operator (MO§ES)"** is Sprints 1-6 (~6 weeks): foundation → algo → backend pipeline → local agent → frontend core. After that you have a functioning free-tier leaderboard with the operator who built it as the first ranked entry.

Everything else (precision tier, anti-gaming, multi-platform adapters) is post-MVP work that promotes the remaining 🟡 / 🔴 rows to 🟢.
