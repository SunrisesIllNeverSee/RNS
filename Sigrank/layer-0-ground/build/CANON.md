# SigRank Canon — Foundation Data Sheet

**The single source-of-truth for every equation, variable, threshold, and reference value in SigRank. This is the document you build concrete around.**

If you need a number for a build decision, get it from here. If a value isn't in this document, it's either a placeholder or hasn't been decided yet — do not assume.

Last reviewed: 2026-05-20 · Ruleset version: **1.0**

---

## Legend

- 🟢 **LOCKED** — value is fixed, source-cited, build-safe
- 🟡 **PROVISIONAL** — concept is fixed, exact value may still tune
- 🔴 **OPEN** — not yet decided / awaiting implementation
- `[SLOT]` — variable slot, fill from telemetry or scoring engine
- `[TBD]` — unfilled, needs a decision

---

## ID Scheme — every value has a primary key

**Every number that appears anywhere in SigRank must reference one of these canonical IDs.** If you see a value without an ID, it's a hallucination — flag it.

| Prefix | Domain | Example |
|---|---|---|
| `T.xx` | **Telemetry inputs** — raw fields the agent submits | `T.01` = output_tokens |
| `M.xx` | **Core 5 metrics** | `M.01` = Compression Ratio |
| `B.xx` | **Background 3 metrics** | `B.01` = Message Volume |
| `C.xx` | **Composites** | `C.01` = SIGNA RATE |
| `K.xx` | **Class tiers (1-9)** | `K.01` = TRANSMITTER |
| `R.xx` | **Reference operator (MO§ES) verified values** | `R.04` = Output tokens 3,902,803 |
| `RS.xx` | **Ruleset parameters (server-side, proprietary)** | `RS.01` = SIGNA RATE weights |
| `S.xx` | **Scoring pipeline steps** | `S.05` = Compute Core 5 |

Every ID maps to:
- A row in this document
- A DB column or scoring-engine constant
- A spec doc under `Sigrank/layer-0-ground/build/`

**Rule:** If a value isn't `[ID]`-tagged in this document, do NOT use it for build decisions.

---

# I. Token Telemetry Input Schema

The payload every snapshot must contain. This is what the local agent submits.

| ID | Field | Type | Range | Source | Status |
|---|---|---|---|---|---|
| **T.01** | `output_tokens` | int | `[0, ∞)` | platform `usage.output_tokens` | 🟢 |
| **T.02** | `fresh_input_tokens` | int | `[0, ∞)` | platform `usage.input_tokens` (non-cached) | 🟢 |
| **T.03** | `cache_read` | int | `[0, ∞)` | platform `usage.cache_read_input_tokens` | 🟢 |
| **T.04** | `cache_creation` | int | `[0, ∞)` | platform `usage.cache_creation_input_tokens` | 🟢 |
| **T.05** | `total_tokens` | int | `[0, ∞)` | sum of T.01–T.04 | 🟢 |
| **T.06** | `sessions_count` | int | `[0, ∞)` | count of session files in window | 🟢 |
| **T.07** | `turns_total` | int | `[0, ∞)` | sum of turns across sessions | 🟢 |
| **T.08** | `active_minutes_est` | int | `[0, ∞)` | wall-time estimate | 🟡 |
| **T.09** | `message_volume` | int | `[0, ∞)` | total messages in window | 🟢 |
| **T.10** | `account_age_days` | int | `[0, ∞)` | `now - first_seen / 86400` | 🟢 |
| **T.11** | `total_messages_lifetime` | int | `[0, ∞)` | lifetime cumulative | 🟢 |
| **T.12** | `window_type` | enum | `daily / 30 / 60 / 90 / all_time` | operator choice | 🟢 |
| **T.13** | `window_start` | ISO 8601 | — | inclusive start | 🟢 |
| **T.14** | `window_end` | ISO 8601 | — | exclusive end | 🟢 |
| **T.15** | `platform.primary` | enum | `claude / chatgpt / gemini / pi / multi / other` | adapter detected | 🟢 |
| **T.16** | `platform.models` | string[] | — | model IDs used | 🟢 |
| **T.17** | `agent.public_key` | string | ed25519 | device keypair | 🟢 |
| **T.18** | `agent.signature` | string | ed25519 sig of canonical payload | sign at publish | 🟢 |
| **T.19** | `agent.ruleset_version` | string | matches active ruleset | from server | 🟢 |
| **T.20** | `agent.snapshot_hash` | string | SHA-256 of canonical JSON | computed at publish | 🟢 |

See `architecture/snapshot_payload.md` for the full schema.

---

# II. The Core 5 Metrics

These are the per-operator performance signals. All five are required for a leaderboard rank.

## `M.01` — Compression Ratio (Comp)

| Field | Value |
|---|---|
| **Canonical ID** | **M.01** |
| **DB column** | `metric_snapshots.compression_ratio` |
| **Formula (exact, precision tier)** | `signal_tokens / (signal_tokens + noise_tokens)` |
| **Formula (proxy, free tier)** | `T.01 / (T.01 + T.02)` |
| **Domain** | `[0.0, 1.0]` |
| **Status** | 🟢 LOCKED |
| **Class cuts** | see V (K.01–K.09) |
| **Required inputs** | T.01, T.02 (free) · signal_tokens, noise_tokens (precision) |
| **MO§ES reference** | R.09 = `3,902,803 / (3,902,803 + 123,246) = 0.9694` ← from poster 7d window |
| **Spec doc** | `metrics/core_5/01_compression_ratio.md` |

## `M.02` — Prompt Complexity (PC)

| Field | Value |
|---|---|
| **Canonical ID** | **M.02** |
| **DB column** | `metric_snapshots.prompt_complexity` |
| **Formula** | weighted composite of: instruction_layers, recursion_logic, system_entities, constraint_density, symbolic_precision, response_shaping_directives |
| **Sub-score weights** | **RS.04** = `[PROPRIETARY]` — locked in Ruleset v1.0 server-side |
| **Domain** | `[0, 100]` |
| **Status** | 🟡 PROVISIONAL — sub-extractors require sig_army |
| **Free-tier estimate** | `min(100, log₁₀(unique_prompts + 1) × 20 × length_factor)` — low confidence |
| **Required inputs** | raw prompt text (precision) · prompt count + avg length (free estimate) |
| **MO§ES reference** | `[NOT COMPUTED]` ← sig_army not yet run |
| **Spec doc** | `metrics/core_5/02_prompt_complexity.md` |

## `M.03` — Cross-Thread Referencing (CT)

| Field | Value |
|---|---|
| **Canonical ID** | **M.03** |
| **DB column** | `metric_snapshots.cross_thread` |
| **Formula (exact)** | `min(100, 8 × unique_thread_refs + 4 × memory_linked_callbacks)` |
| **Formula (proxy)** | `(T.03 / (T.03 + T.04 + T.02)) × 100` |
| **Domain** | `[0, 100]` |
| **Status** | 🟢 LOCKED |
| **Required inputs** | thread ref count, callback count (precision) · T.03, T.04, T.02 (free) |
| **MO§ES reference** | R.10 = `1,084,399,183 / 1,119,349,208 = 0.9688 → 96.88%` ← from poster |
| **Spec doc** | `metrics/core_5/03_cross_thread_referencing.md` |

## `M.04` — Session Depth (SD)

| Field | Value |
|---|---|
| **Canonical ID** | **M.04** |
| **DB column** | `metric_snapshots.session_depth` |
| **Formula (exact)** | `avg(max_reply_chain_length per session)` |
| **Formula (proxy)** | `T.07 / T.06` |
| **Normalization to score** | bucketed `[0, 100]` per **RS.02** — `[PROPRIETARY]` exact curve |
| **Domain (raw)** | `[0, ∞)` |
| **Domain (score)** | `[0, 100]` |
| **Status** | 🟢 LOCKED (formula) · 🟡 PROVISIONAL (bucket curve RS.02) |
| **Required inputs** | reply-parent graph (precision) · T.07, T.06 (free) |
| **MO§ES reference** | R.11 = `7,327 / 21 = 348.9` raw turns/session (poster window) |
| **Spec doc** | `metrics/core_5/04_session_depth.md` |

## `M.05` — Token Throughput (TT)

| Field | Value |
|---|---|
| **Canonical ID** | **M.05** |
| **DB column** | `metric_snapshots.token_throughput` |
| **Formula (raw)** | `T.01 / T.08` |
| **Formula (score)** | `min(100, 20 × log₁₀(T.05 + 1))` |
| **Domain (raw)** | `[0, ∞)` |
| **Domain (score)** | `[0, 100]` |
| **Status** | 🟢 LOCKED |
| **Required inputs** | T.01, T.08 |
| **MO§ES reference** | R.15 = `1.84 min/task · ` R.07 = `1.12B total tokens · 7d window` ← from poster |
| **Spec doc** | `metrics/core_5/05_token_throughput.md` |

---

# III. Background 3

Identity / normalization context. Required for composites but not direct leaderboard sort keys.

## `B.01` — Message Volume (MV)

| Field | Value |
|---|---|
| **Canonical ID** | **B.01** |
| **DB column** | `metric_snapshots.message_volume` |
| **Formula** | `count(messages where operator_id = X, window)` |
| **Score normalization** | `min(100, 20 × log₁₀(T.09 + 1))` when used in composites |
| **Domain** | `[0, ∞)` raw · `[0, 100]` score |
| **Status** | 🟢 LOCKED |
| **Required input** | T.09 |
| **MO§ES reference** | R.02 = `7,327` (7d window) |
| **Spec doc** | `metrics/background_3/01_message_volume.md` |

## `B.02` — Account Age

| Field | Value |
|---|---|
| **Canonical ID** | **B.02** |
| **DB column** | `metric_snapshots.account_age_days` |
| **Formula** | `floor((now - first_seen) / 86400)` |
| **Domain** | `[0, ∞)` days |
| **Status** | 🟢 LOCKED |
| **Required input** | T.10 |
| **MO§ES reference** | R.18 = `119 days` |
| **Spec doc** | `metrics/background_3/02_account_age.md` |

## `B.03` — Total Messages (Lifetime)

| Field | Value |
|---|---|
| **Canonical ID** | **B.03** |
| **DB column** | `metric_snapshots.total_messages` |
| **Formula** | `count(messages where operator_id = X, all time)` |
| **Domain** | `[0, ∞)` |
| **Status** | 🟢 LOCKED |
| **Required input** | T.11 |
| **MO§ES reference** | `[TBD]` ← not in poster, requires cumulative count from all session files |
| **Spec doc** | `metrics/background_3/03_total_messages.md` |

---

# IV. Composites

Derived metrics. The flagship plus two advanced.

## `C.01` — SIGNA RATE (the flagship)

| Field | Value |
|---|---|
| **Canonical ID** | **C.01** |
| **DB column** | `metric_snapshots.signa_rate` |
| **Formula structure** | `w₁·M.01_score + w₂·M.04_score + w₃·M.02_score + w₄·M.03_score + w₅·M.05_score` |
| **Composite weights** | **RS.01** = `[PROPRIETARY]` — locked in Ruleset v1.0 server-side · sum = 1.0 |
| **Domain** | `[0, 100]` |
| **Live score** | `LIVE_SIGNA_RATE = C.01 × RS.03` |
| **Recency curve** | **RS.03** = `[PROPRIETARY]` — tiered by `last_seen` age |
| **Status** | 🟢 LOCKED (structure) · 🟡 PROVISIONAL (RS.01 and RS.03 tunable across rulesets) |
| **MO§ES reference** | `[NOT COMPUTED]` ← requires server scoring engine to be built |
| **Spec doc** | `metrics/composites/01_signa_rate.md` |

## `C.02` — Signal Force (SF)

| Field | Value |
|---|---|
| **Canonical ID** | **C.02** |
| **DB column** | `metric_snapshots.signal_force` |
| **Formula (raw)** | `(B.03 × M.04_raw) / B.02` |
| **Formula (score)** | `min(100, 20 × log₁₀(C.02_raw + 1))` |
| **Domain (raw)** | `[0, ∞)` · **Domain (score)** `[0, 100]` |
| **Status** | 🟢 LOCKED |
| **Required inputs** | B.03, M.04, B.02 |
| **MO§ES reference** | `[TBD]` ← needs B.03 (lifetime totals); partial inputs available |
| **Spec doc** | `metrics/composites/02_signal_force.md` |

## `C.03` — Drift Ratio (DR%)

| Field | Value |
|---|---|
| **Canonical ID** | **C.03** |
| **DB column** | `metric_snapshots.drift_ratio` |
| **Formula** | `(aligned_messages / total_messages) × 100` |
| **Alignment scoring** | requires semantic vector analysis — `[PROPRIETARY]` |
| **Domain** | `[0, 100]` percentage |
| **Status** | 🟡 PROVISIONAL — precision tier only · no free-tier proxy |
| **Tier** | Precision tier (sig_army) ONLY |
| **MO§ES reference** | `[NOT COMPUTED]` ← sig_army not yet run |
| **Spec doc** | `metrics/composites/03_drift_ratio.md` |

---

# V. Class Thresholds

The 9-tier hierarchy. Class is the more restrictive of Compression OR SIGNA RATE.

| ID | Class | Glyph | Compression cut (qualitative) | SIGNA RATE cut (qualitative) | Status |
|---|---|---|---|---|---|
| **K.01** | TRANSMITTER | ◈ | ≥ 0.85 | ≥ 85 | 🟢 |
| **K.02** | ARCHITECT+ | ▲ | 0.75 – 0.84 | 75 – 84 | 🟢 |
| **K.03** | ARCHITECT | ▽ | 0.65 – 0.74 | 65 – 74 | 🟢 |
| **K.04** | POWER | ⬡ | 0.50 – 0.64 | 50 – 64 | 🟢 |
| **K.05** | BASE | ↓ | 0.40 – 0.49 | — | 🟢 |
| **K.06** | SEEKER | ◎ | 0.30 – 0.39 | — | 🟢 |
| **K.07** | REFINER | ⟳ | 0.20 – 0.29 | — | 🟢 |
| **K.08** | BEARER | ◇ | 0.15 – 0.24 | — | 🟢 |
| **K.09** | IGNITER | · | < 0.15 | — | 🟢 |

> Exact numerical breakpoints (vs the qualitative cuts above) live server-side as **RS.05** = `[PROPRIETARY]`. The class names + ordering + glyphs are public.

**Promotion stickiness:** Promotion to a higher class requires sustained threshold for **RS.07** = 3 consecutive scoring cycles (proposed, tunable). Demotions take effect immediately. Exact rule is **RS.07** server-side.

See `architecture/class_tiers.md` for full color tokens and population distribution targets.

---

# VI. Scoring Pipeline

The order of operations from raw snapshot to final live rank.

```
Snapshot Submission
        ↓
1. Validate + verify ed25519 signature                    🟢 LOCKED
        ↓
2. Verify schema_version + ruleset_version supported     🟢 LOCKED
        ↓
3. Insert raw to snapshot_submissions                    🟢 LOCKED
        ↓
4. Compute Background 3 (MV, AcctAge, TotalMsgs)         🟢 LOCKED
        ↓
5. Compute Core 5 (Comp, PC, CT, SD, TT)                🟢 LOCKED
   - Free tier uses proxies (II.1-II.5 proxy formulas)
   - Precision tier uses exact + sig_army audit
        ↓
6. Normalize Core 5 to [0,100] scores                    🟡 PROVISIONAL
   - Comp_score = Comp × 100
   - SD_score = bucketization curve [PROPRIETARY]
   - PC_score = sub-score composite [PROPRIETARY weights]
   - CT_score = already [0,100]
   - TT_score = log normalization
        ↓
7. Compute SIGNA RATE composite                          🟡 PROVISIONAL (weights)
   = w₁·Comp + w₂·SD + w₃·PC + w₄·CT + w₅·TT
        ↓
8. Apply recency_modifier → LIVE_SIGNA_RATE              🟡 PROVISIONAL (curve)
        ↓
9. Assign class tier (V)                                 🟢 LOCKED
        ↓
10. Compute auxiliary composites                         🟡 PROVISIONAL
    - Signal Force (formula locked, value derives)
    - Drift Ratio (precision tier only)
        ↓
11. Compute movement deltas (24h, 7d rank diff)          🟢 LOCKED
        ↓
12. Write to metric_snapshots + rank_history             🟢 LOCKED
        ↓
13. Regenerate leaderboards_cached                       🟢 LOCKED
```

---

# VII. Reference Operator — MO§ES (Concrete Anchor)

The only operator with fully verified real data. Use as ground truth when testing scoring engine or seeding the leaderboard.

## Window definition
- **R.00** Window: 2026-05-08 → 2026-05-14 (7 days)
- **Source:** `Evaluation Metrics Tracing/stats/extract_benchmark_window.py` output → `benchmark_export/summary.json`

## Raw telemetry (from `summary.json` poster cuts)

| ID | Field | Value | Source |
|---|---|---|---|
| **R.01** | Files found | 98 | `summary.json` |
| **R.01a** | Sessions with turns (full summary) | 97 | `summary.json` |
| **R.02** | Turns total (poster top sessions) | 7,327 | poster |
| **R.02a** | Turns total (full summary) | 9,332 | `summary.json` |
| **R.03** | Fresh input tokens (poster) | 123,246 | poster |
| **R.04** | Output tokens (poster) | 3,902,803 | poster |
| **R.05** | Cache read (poster) | 1,084,399,183 | poster |
| **R.06** | Cache creation (poster) | 34,826,779 | poster |
| **R.07** | Total tokens (poster) | 1,123,252,011 | poster |
| **R.08** | Sessions (poster) | 21 | poster |

## Derived metrics

| ID | Metric | Value | Computation |
|---|---|---|---|
| **R.09** | Compression Ratio (proxy for M.01) | **0.9694** | R.04 / (R.04 + R.03) |
| **R.10** | Cross-Thread (proxy for M.03) | **96.88%** | R.05 / (R.05 + R.06 + R.03) |
| **R.11** | Session Depth raw (input for M.04) | **348.9** | R.02 / R.08 |
| **R.12** | Output : Input ratio (7d) | **31.7×** | R.04 / R.03 |
| **R.13** | Output : Input ratio (30d) | **42.5×** | poster |
| **R.14** | Output : Input ratio (90d) | **22.1×** | poster |
| **R.15** | Time / task | **1.84 min** | ~45 hr / 1,465 tasks |
| **R.16** | Cost / LOC (plan basis) | **$0.0007** | $23.33 / 35,242 |
| **R.16a** | Cost / LOC (API equiv) | **$0.0444** | $1,564.47 / 35,242 |
| **R.17** | LOC shipped | **35,242** | wc -l verified |

## Operator metadata

| ID | Field | Value |
|---|---|---|
| **R.18** | Account age (input for B.02) | 119 days |
| **R.19** | Top model | Claude Opus 4.7 |
| **R.20** | Primary platform (T.15) | Claude (Claude Code) |
| **R.21** | Codename (public) | TransVaultOrigin |
| **R.21a** | Codename (internal) | MOSES / MO§ES |
| **R.22** | Active project mix | application-hub, Commitment-Theory, CIVITAE, Thread-Workspace, GPT-WorkFlow, rns, mcp-eval, kd, Pickle-AI |

## What's NOT computed for MO§ES yet

- SIGNA RATE (requires scoring engine implementation)
- Class assignment (requires class engine)
- PC sub-scores (requires sig_army)
- Drift Ratio (requires sig_army)
- Signal Force (formula known, lifetime totals needed)
- Badge awards (requires badge engine)
- Rank position (no leaderboard to rank in yet)

---

# VIII. Open Questions / Proprietary Parameters (RS.xx)

Server-side scoring engine constants. All marked `[PROPRIETARY]` — never exposed publicly. Each ID maps to a configuration row in the Railway scoring worker.

| ID | Parameter | Proposed value (internal only) | Status |
|---|---|---|---|
| **RS.01** | SIGNA RATE weights | `0.30 / 0.20 / 0.20 / 0.15 / 0.15` (M.01 / M.04 / M.02 / M.03 / M.05) — sum = 1.0 | 🟡 Locked in Ruleset v1.0, tunable |
| **RS.02** | SD bucketization curve | tiered: 30+→100, 25-29→92, 20-24→84, 15-19→72, 10-14→58, 5-9→42, <5→25 | 🟡 Provisional |
| **RS.03** | Recency modifier curve | <24h→1.00, <72h→0.97, <168h→0.94, <336h→0.88, <720h→0.80, >720h→0.65 | 🟡 Provisional |
| **RS.04** | PC sub-score weights | `0.25 / 0.20 / 0.20 / 0.15 / 0.10 / 0.10` (instruction_layers / recursion / entities / constraints / symbolic_precision / response_shaping) | 🟡 Provisional |
| **RS.05** | Class threshold exact breakpoints | matches K.01-K.09 qualitative cuts numerically | 🟢 Locked v1.0 |
| **RS.06** | Anti-gaming penalty rules | disabled for MVP. Pattern: MV spike >40% + Comp drop >10% + SD drop >15% → spam_penalty | 🔴 Open · MVP off |
| **RS.07** | Class promotion stickiness cycles | 3 consecutive cycles required for promotion. Demotion immediate. | 🟡 Provisional |

## Other open questions (not yet ID'd because no decision made)

| Topic | Status |
|---|---|
| Free-tier PC estimate quality | needs empirical validation against precision-tier audits |
| Drift Ratio alignment scoring approach | semantic embeddings vs custom vector model — open |
| Active minutes estimation method | how to compute T.08 cleanly from session timestamps — currently `[ESTIMATE]` |
| MO§ES Total Messages lifetime (R.??) | full cumulative count from all session files not yet computed → B.03 has no MO§ES reference |
| Drift Ratio composite weight in SIGNA RATE | C.03 currently NOT in C.01 composite — should it be? |

---

# IX. Ruleset v1.0 — Locked Status

Effective: 2026-05-14 onwards (date placeholder until first real scoring run).

## What v1.0 locks

- The set of 11 active metrics (Core 5 + Background 3 + 3 Composites)
- The structure of SIGNA RATE as a weighted Core 5 composite
- The 9-class hierarchy and qualitative thresholds
- The Compression Ratio formula (signal / signal+noise)
- The Token Throughput log normalization shape
- The Cross-Thread cache-hit proxy mapping
- The snapshot payload schema (v1.0)
- The deployment topology (Supabase + Railway + Vercel + Modal)
- The free-tier / precision-tier split
- Ed25519 signing requirement

## What v1.0 does NOT lock (subject to change in v1.1+)

- Exact SIGNA RATE weights
- Exact SD bucketization curve
- Exact recency modifier curve
- Exact class threshold breakpoints (numerical, vs the qualitative ranges in V)
- PC sub-score weights
- Anti-gaming penalty thresholds
- Promotion stickiness cycle count

## Change log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-05-14 | Initial locked ruleset |

---

# X. How to use this document

### When you need a value for a build decision:
1. Find it in this document
2. If marked 🟢 — use it
3. If marked 🟡 — use it but flag the assumption
4. If marked 🔴 or `[TBD]` — STOP, decide, then update this document
5. If marked `[PROPRIETARY]` — the value exists server-side in the scoring engine, request it from the engine team

### When you generate a real value for the first time:
1. Add a row in the relevant section
2. Cite the source (file path, computation, sig_army run ID, etc.)
3. Promote from 🔴/🟡 to 🟢
4. Update the Ruleset change log if it affects locked structure

### When you change a `[PROPRIETARY]` value:
1. Increment ruleset version in `IX`
2. Add change log entry
3. Re-run scoring engine against all historical snapshots
4. Verify replay produces consistent ranks within tolerance

### When you spot a placeholder in code or mockup:
1. Check this document for the real value
2. If not here, mark with `*` in mockup OR `[PLACEHOLDER]` in code
3. Add to "Open Questions" if it's a real decision needed

---

# Appendix A — File index

The complete spec set this document references:

```
Sigrank/layer-0-ground/build/
├── CANON.md                                  ← THIS FILE
├── extract_benchmark_window.py               ← MO§ES extraction script
├── 03_moses_5_benchmarks.md                  ← MO§ES 5 categories
├── benchmark_export/summary.json             ← real session data
├── field_comparison/                         ← ArtificialAnalysis competitor data
├── benchmark_assets/                         ← poster + cards
├── metrics/
│   ├── 00_README.md                          ← metric stack overview
│   ├── core_5/
│   │   ├── 01_compression_ratio.md
│   │   ├── 02_prompt_complexity.md
│   │   ├── 03_cross_thread_referencing.md
│   │   ├── 04_session_depth.md
│   │   └── 05_token_throughput.md
│   ├── background_3/
│   │   ├── 01_message_volume.md
│   │   ├── 02_account_age.md
│   │   └── 03_total_messages.md
│   ├── composites/
│   │   ├── 01_signa_rate.md
│   │   ├── 02_signal_force.md
│   │   └── 03_drift_ratio.md
│   └── lineage/
│       ├── compression_snr_history.md
│       ├── metric_family_tree.md
│       └── naming_drift.md
└── architecture/
    ├── api_spec.md
    ├── build_layers.md
    ├── class_tiers.md
    ├── db_schema.md
    ├── deployment_topology.md
    ├── scoring_formula.md
    ├── site_architecture.md
    ├── snapshot_payload.md
    └── token_metric_bridge.md
```

---

**Bottom line:** if a number isn't in this document and isn't traceable to a file in Appendix A, it doesn't exist yet. Don't pour concrete around it.
