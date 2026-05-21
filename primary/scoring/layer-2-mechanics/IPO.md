# SigRank Processing System — Input · Process · Output

The complete data pipeline from operator's local machine to public leaderboard, decomposed into discrete steps. Each step has:
- **Step ID** (S.xx) — referenced from CANON.md
- **Owner** — which system runs it
- **Runtime** — where it executes (local, edge, worker, modal, frontend)
- **Status** — 🟢 LOCKED / 🟡 PROVISIONAL / 🔴 OPEN
- **Inputs** — typed by canonical ID (T.xx, M.xx, B.xx, C.xx, K.xx, R.xx, RS.xx)
- **Process** — what the code does
- **Outputs** — typed by canonical ID
- **Implementation path** — where the code lives

> If a step doesn't appear here, it doesn't exist in the spec. If a value flows through the pipeline without an ID, it's a hallucination.

---

## Pipeline overview

```
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 1 — AGENT (operator's machine, Python CLI)                 │
│ S.01 → S.02 → S.03 → S.04 → S.05 → S.06 → S.07 → S.08            │
│ Source → Parse → Features → Core 5 → Background 3 → Snapshot →   │
│ Sign → Publish                                                   │
└──────────────────────────────────────────────────────────────────┘
                                  ↓ HTTPS
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 2 — INGEST (Supabase Edge Function, Deno)                  │
│ S.09 → S.10 → S.11 → S.12 → S.13                                 │
│ Verify sig → Validate schema → Rate limit → Insert → NOTIFY      │
└──────────────────────────────────────────────────────────────────┘
                                  ↓ Postgres LISTEN
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 3 — SCORING WORKER (Railway, private Python FastAPI)       │
│ S.14 → S.15 → S.16 → S.17 → S.18 → S.19 → S.20 → S.21 → S.22     │
│ Pickup → Normalize Core 5 → Composites → Class → Recency →       │
│ Movement → Persist → Cache → Badges                              │
└──────────────────────────────────────────────────────────────────┘
                                  ↓ (opt-in upgrade)
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 4 — PRECISION AUDIT (Modal, private Python sig_army)       │
│ S.23 → S.24 → S.25 → S.26 → S.27 → S.28                          │
│ Request → sig_army → Exact scores → Audit log → Update → Badge   │
└──────────────────────────────────────────────────────────────────┘
                                  ↓ Postgres reads
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 5 — FRONTEND (Vercel, Next.js)                             │
│ S.29 → S.30 → S.31 → S.32                                        │
│ Request → Read cache → Realtime subscribe → Render              │
└──────────────────────────────────────────────────────────────────┘
```

---

# PHASE 1 — Agent Pipeline (Operator's Machine)

The local Python CLI does all the heavy lifting. Conversations stay on device.

## `S.01` — Source Ingestion

| | |
|---|---|
| **Owner** | Local Agent / Platform Adapter |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED (Claude Code adapter) · 🔴 OPEN (other platforms) |
| **Inputs** | Local files (e.g. `~/.claude/projects/*/*.jsonl` for Claude Code) |
| **Process** | Adapter scans configured source path, lists session files. Each adapter implements: `detect()`, `list_sessions()`, `parse_session()`, `estimate_token_quality()` |
| **Outputs** | List of `Path` objects pointing to session files + `quality_estimate` enum (`excellent`/`good`/`medium`/`low`) |
| **Implementation** | `sigrank-agent/src/adapters/` (per platform) |

## `S.02` — Parse + Normalize

| | |
|---|---|
| **Owner** | Local Agent / Parser |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED |
| **Inputs** | Session file paths from S.01 |
| **Process** | Each session file → unified `Session` model with `messages[]`, `thread_refs[]`, `started_at`, `ended_at`. Per platform: Claude Code reads `.jsonl` line-by-line; ChatGPT export reads mapping tree; etc. |
| **Outputs** | Normalized `Session` and `Message` objects stored in local SQLite (`sessions`, `messages` tables). Raw content stays local-only. |
| **Implementation** | `sigrank-agent/src/parsers/` |

## `S.03` — Feature Extraction

| | |
|---|---|
| **Owner** | Local Agent / Feature Engine |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED |
| **Inputs** | Normalized `Session`/`Message` objects from S.02 |
| **Process** | Extracts reusable primitives per message and per session: length, role, timestamp, references, instruction layers, repetition markers, structural markers, code blocks, callbacks. Also rolling features per window (24h, 7d, 30d, 90d, lifetime). |
| **Outputs** | Populated `feature_message`, `feature_session`, `feature_rollups_daily` (local SQLite) |
| **Implementation** | `sigrank-agent/src/features/` |

## `S.04` — Compute Core 5 (Agent-side, free tier proxies)

| | |
|---|---|
| **Owner** | Local Agent / Metric Engine |
| **Runtime** | Operator's machine |
| **Status** | 🟡 PROVISIONAL (M.02 needs sig_army for exact) |
| **Inputs** | T.01 output_tokens · T.02 fresh_input_tokens · T.03 cache_read · T.04 cache_creation · T.06 sessions_count · T.07 turns_total · T.08 active_minutes_est · prompt text (precision only) |
| **Process** | Compute proxy formulas: <br>• M.01 = T.01 / (T.01 + T.02) <br>• M.03 = (T.03 / (T.03 + T.04 + T.02)) × 100 <br>• M.04 raw = T.07 / T.06 <br>• M.05 raw = T.01 / T.08 <br>• M.02 = weak estimate from input volume (free tier) OR sig_army call (precision tier) |
| **Outputs** | M.01 [0,1] · M.02 [0,100] + confidence · M.03 [0,100] · M.04 raw · M.05 raw |
| **Implementation** | `sigrank-agent/src/metrics/{compression,prompt_complexity,cross_thread,session_depth,token_throughput}.py` |

## `S.05` — Compute Background 3

| | |
|---|---|
| **Owner** | Local Agent |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED · 🟡 (T.11 lifetime requires full-history scan) |
| **Inputs** | T.09 message_volume · T.10 account_age_days · T.11 total_messages_lifetime |
| **Process** | Direct counts and timestamp arithmetic. No transformation. |
| **Outputs** | B.01 value · B.02 value · B.03 value |
| **Implementation** | `sigrank-agent/src/metrics/background.py` |

## `S.06` — Build Canonical Snapshot Payload

| | |
|---|---|
| **Owner** | Local Agent / Snapshot Builder |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED |
| **Inputs** | M.01-M.05 (from S.04) · B.01-B.03 (from S.05) · T.12 window_type · T.13 window_start · T.14 window_end · T.15 platform · T.16 models |
| **Process** | Assemble JSON per Schema v1.0 (`snapshot_payload.md`). Canonicalize: sort keys, no whitespace, UTF-8. Compute T.20 snapshot_hash = SHA-256(canonical_json). |
| **Outputs** | Canonical JSON payload + T.20 snapshot_hash |
| **Implementation** | `sigrank-agent/src/snapshots/builder.py` + `canonicalize.py` |

## `S.07` — Sign Payload (ed25519)

| | |
|---|---|
| **Owner** | Local Agent / Signer |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED |
| **Inputs** | Canonical JSON from S.06 · Device private key (from `~/.sigrank/keypair.json`) |
| **Process** | Compute ed25519 signature of canonical bytes. Attach T.18 signature + T.17 agent.public_key + T.19 agent.ruleset_version. |
| **Outputs** | Signed payload ready for transmission |
| **Implementation** | `sigrank-agent/src/publish/sign.py` |

## `S.08` — Publish to Ingest API

| | |
|---|---|
| **Owner** | Local Agent / HTTP Client |
| **Runtime** | Operator's machine |
| **Status** | 🟢 LOCKED |
| **Inputs** | Signed payload from S.07 · Server URL (config) |
| **Process** | POST to `/api/v1/snapshots` with `X-Agent-Signature` header. Retry with exponential backoff on transient failures. Log to local `publish_log` table. |
| **Outputs** | HTTP response: `{submission_id, status, scoring_eta_seconds}` OR rejection reason |
| **Implementation** | `sigrank-agent/src/publish/http_client.py` |

---

# PHASE 2 — Ingest Pipeline (Supabase Edge Function)

Server-side gate. Validates and parks the submission. No scoring happens here.

## `S.09` — Verify Signature

| | |
|---|---|
| **Owner** | Supabase Edge Function (Deno) |
| **Runtime** | Edge |
| **Status** | 🟢 LOCKED |
| **Inputs** | Incoming POST body · `X-Agent-Signature` header · T.17 agent.public_key from payload |
| **Process** | (1) Lookup `devices` table by `device_id`; verify `agent_public_key` matches T.17. (2) Recompute canonical JSON. (3) Verify ed25519 signature against canonical bytes. (4) Verify T.20 snapshot_hash matches recomputed hash. |
| **Outputs** | OK → continue · FAIL → 401 `{reason: signature_invalid}` |
| **Implementation** | `supabase/functions/snapshots/index.ts` |

## `S.10` — Validate Schema

| | |
|---|---|
| **Owner** | Supabase Edge Function |
| **Runtime** | Edge |
| **Status** | 🟢 LOCKED |
| **Inputs** | Verified payload from S.09 |
| **Process** | (1) Check `schema_version` is supported. (2) Validate every required T.xx field present + correct type + within domain. (3) Check window_end > window_start, window_end ≤ now. (4) Check `ruleset_version` is active. |
| **Outputs** | OK → continue · FAIL → 400 `{reason: schema_outdated / validation_failed, detail}` |
| **Implementation** | Same edge function · Zod schema validation |

## `S.11` — Rate Limit Check

| | |
|---|---|
| **Owner** | Supabase Edge Function |
| **Runtime** | Edge |
| **Status** | 🟢 LOCKED |
| **Inputs** | `device_id` from payload · Recent submission history |
| **Process** | Lookup last 24h of submissions for this device. Enforce: max 1 per 24h (default) configurable to 1 per 6h for trusted devices. |
| **Outputs** | OK → continue · FAIL → 429 `{reason: rate_limit, next_allowed_at}` |
| **Implementation** | Same edge function · Postgres count + threshold |

## `S.12` — Insert snapshot_submissions

| | |
|---|---|
| **Owner** | Supabase Edge Function → Postgres |
| **Runtime** | Edge → DB |
| **Status** | 🟢 LOCKED |
| **Inputs** | Validated, verified payload |
| **Process** | INSERT row into `snapshot_submissions` table with `status='received'`. Append-only. Returns new `submission_id` UUID. |
| **Outputs** | `submission_id` UUID written to DB |
| **Implementation** | `db_schema.md` table `snapshot_submissions` |

## `S.13` — Notify Scoring Worker

| | |
|---|---|
| **Owner** | Postgres trigger |
| **Runtime** | DB |
| **Status** | 🟢 LOCKED |
| **Inputs** | New `snapshot_submissions` row from S.12 |
| **Process** | `NOTIFY new_submission, '{submission_id}'` |
| **Outputs** | Postgres notification fires to any LISTEN consumer (S.14). Edge function returns 200 to agent with `{submission_id, status: received, scoring_eta_seconds: ~30}` |
| **Implementation** | Postgres trigger function |

---

# PHASE 3 — Scoring Worker (Railway, Private)

THE MOAT. Implements every proprietary parameter. Lives in `sigrank-scoring-worker` private repo.

## `S.14` — LISTEN Consumer Picks Up Submission

| | |
|---|---|
| **Owner** | Scoring Worker (FastAPI + asyncio listener) |
| **Runtime** | Railway worker process |
| **Status** | 🟢 LOCKED |
| **Inputs** | `NOTIFY new_submission` from S.13 |
| **Process** | Worker holds persistent Postgres LISTEN connection. On notification, fetch row from `snapshot_submissions` by `submission_id`. Mark `status='processing'`. |
| **Outputs** | Submission record in memory ready for scoring |
| **Implementation** | `sigrank-scoring-worker/src/workers/listener.py` |

## `S.15` — Normalize Core 5 to [0, 100] Scores

| | |
|---|---|
| **Owner** | Scoring Worker / Algo Library |
| **Runtime** | Railway |
| **Status** | 🟢 LOCKED (M.01, M.05) · 🟡 PROVISIONAL (M.04 bucket curve = RS.02) |
| **Inputs** | M.01 (raw [0,1]) · M.02 (raw [0,100]) · M.03 (raw [0,100]) · M.04 (raw turns/session) · M.05 (raw tokens/min) |
| **Process** | • M.01_score = M.01 × 100 <br>• M.02_score = pass through (already normalized in S.04) <br>• M.03_score = pass through <br>• M.04_score = apply RS.02 bucket curve (proprietary) <br>• M.05_score = min(100, 20·log₁₀(T.05 + 1)) |
| **Outputs** | 5 normalized scores ∈ [0,100] |
| **Implementation** | `sigrank-scoring-worker/src/scoring/normalize.py` |

## `S.16` — Compute SIGNA RATE Composite

| | |
|---|---|
| **Owner** | Scoring Worker / Composite Engine |
| **Runtime** | Railway |
| **Status** | 🟡 PROVISIONAL (RS.01 tunable) |
| **Inputs** | 5 normalized Core 5 scores from S.15 · RS.01 (proprietary weights) |
| **Process** | C.01 = w₁·M.01_score + w₂·M.04_score + w₃·M.02_score + w₄·M.03_score + w₅·M.05_score (where w₁..w₅ = RS.01) |
| **Outputs** | C.01 SIGNA RATE ∈ [0, 100] |
| **Implementation** | `sigrank-scoring-worker/src/scoring/signa_rate.py` |

## `S.17` — Compute Auxiliary Composites

| | |
|---|---|
| **Owner** | Scoring Worker |
| **Runtime** | Railway |
| **Status** | 🟢 LOCKED (C.02) · 🟡 PROVISIONAL (C.03 precision only) |
| **Inputs** | B.03 (T.11) · M.04 raw · B.02 (T.10) |
| **Process** | • C.02 raw = (B.03 × M.04_raw) / B.02 <br>• C.02 score = min(100, 20·log₁₀(C.02_raw + 1)) <br>• C.03: skip in free tier; populated by S.25 if precision audit run |
| **Outputs** | C.02 raw + score · C.03 (null in free, computed if precision) |
| **Implementation** | `sigrank-scoring-worker/src/scoring/composites.py` |

## `S.18` — Apply Recency Modifier → LIVE_SIGNA_RATE

| | |
|---|---|
| **Owner** | Scoring Worker |
| **Runtime** | Railway |
| **Status** | 🟡 PROVISIONAL (RS.03 tunable) |
| **Inputs** | C.01 from S.16 · operator's `last_seen` timestamp · RS.03 (proprietary curve) |
| **Process** | LIVE_C.01 = C.01 × RS.03(now - last_seen). Tiered modifier per RS.03. |
| **Outputs** | LIVE_C.01 = effective rank score |
| **Implementation** | `sigrank-scoring-worker/src/scoring/recency.py` |

## `S.19` — Assign Class Tier

| | |
|---|---|
| **Owner** | Scoring Worker |
| **Runtime** | Railway |
| **Status** | 🟢 LOCKED · 🟡 PROVISIONAL (RS.07 cycle count) |
| **Inputs** | M.01 (Compression) · C.01 (SIGNA RATE) · prior 3 cycles of class assignments (for promotion stickiness RS.07) |
| **Process** | Apply `assign_class(M.01, C.01)` from `class_tiers.md`. For promotion to higher class, verify RS.07 consecutive cycles met. Demotions immediate. |
| **Outputs** | One of K.01-K.09 |
| **Implementation** | `sigrank-scoring-worker/src/scoring/class_assignment.py` |

## `S.20` — Compute Movement Deltas

| | |
|---|---|
| **Owner** | Scoring Worker |
| **Runtime** | Railway |
| **Status** | 🟢 LOCKED |
| **Inputs** | Current rank from cache · prior 24h rank · prior 7d rank (from `rank_history`) |
| **Process** | movement_24h = current - 24h_ago · movement_7d = current - 7d_ago. Negative = moved up. |
| **Outputs** | `movement_24h`, `movement_7d` integers |
| **Implementation** | `sigrank-scoring-worker/src/scoring/movement.py` |

## `S.21` — Write metric_snapshots + rank_history

| | |
|---|---|
| **Owner** | Scoring Worker → Postgres |
| **Runtime** | Railway → DB |
| **Status** | 🟢 LOCKED |
| **Inputs** | All computed values from S.15-S.20 |
| **Process** | Single transaction: INSERT into `metric_snapshots` (one row per operator per snapshot_date). Also INSERT/UPDATE `rank_history` with daily snapshot. Tag both with `ruleset_version`. Mark submission `status='scored'`. |
| **Outputs** | Rows persisted |
| **Implementation** | `sigrank-scoring-worker/src/db/store.py` |

## `S.22` — Regenerate leaderboards_cached

| | |
|---|---|
| **Owner** | Scoring Worker / Cache Generator |
| **Runtime** | Railway (cron + on-write) |
| **Status** | 🟢 LOCKED |
| **Inputs** | Latest `metric_snapshots` rows for all active operators |
| **Process** | For each leaderboard variant (global × window × class × platform), SELECT top N + sort. Write JSONB into `leaderboards_cached.payload_json`. Runs every 5 minutes via cron + immediately on top-N change. |
| **Outputs** | Materialized leaderboard rows ready for frontend reads |
| **Implementation** | `sigrank-scoring-worker/src/workers/cache_rebuild.py` |

## `S.23` — Evaluate Badge Criteria

| | |
|---|---|
| **Owner** | Scoring Worker / Badge Engine |
| **Runtime** | Railway (per scoring cycle) |
| **Status** | 🟡 PROVISIONAL (3-5 badges for MVP, full catalog Phase 2) |
| **Inputs** | Current + historical metric_snapshots · existing `operator_badges` |
| **Process** | For each badge in catalog, evaluate `criteria_json` against operator's state. If criteria met and badge not yet awarded, INSERT into `operator_badges`. |
| **Outputs** | Zero or more new `operator_badges` rows |
| **Implementation** | `sigrank-scoring-worker/src/scoring/badge_engine.py` |

---

# PHASE 4 — Precision Audit (Modal, Opt-In)

The upsell tier. Replaces free-tier proxies with sig_army exact analysis.

## `S.24` — Audit Request Received

| | |
|---|---|
| **Owner** | Supabase Edge Function → Modal trigger |
| **Runtime** | Edge → Modal |
| **Status** | 🟡 PROVISIONAL |
| **Inputs** | Operator's audit request (after Stripe payment confirmed) · Raw session uploads OR consent to use submitted telemetry |
| **Process** | Edge function validates payment, queues a Modal job with operator_id + submission_ids to audit. Modal scales up worker. |
| **Outputs** | Modal job ID in queue |
| **Implementation** | `supabase/functions/audit-request/` + Modal trigger |

## `S.25` — Run sig_army Classifier

| | |
|---|---|
| **Owner** | sig_army on Modal |
| **Runtime** | Modal (scales to zero between audits) |
| **Status** | 🔴 OPEN (not yet built · 4,900-token word_vault exists locally) |
| **Inputs** | Raw conversation text (uploaded for audit) · word_vault classifier |
| **Process** | For each session, classify every token as signal vs noise per word_vault. Aggregate signal_tokens and noise_tokens per window. Extract PC sub-scores: instruction_layers, recursion_logic, system_entities, constraint_density, symbolic_precision, response_shaping_directives. |
| **Outputs** | `signal_tokens`, `noise_tokens` (for exact M.01) · PC sub-scores (for exact M.02 via RS.04 weights) · semantic alignment vector (for C.03) |
| **Implementation** | `sigrank-sig-army/src/classifier/` + `sigrank-sig-army/src/audit/` |

## `S.26` — Compute Exact M.01, M.02, C.03

| | |
|---|---|
| **Owner** | sig_army on Modal |
| **Runtime** | Modal |
| **Status** | 🔴 OPEN |
| **Inputs** | sig_army outputs from S.25 |
| **Process** | • M.01_exact = signal_tokens / (signal_tokens + noise_tokens) <br>• M.02_exact = RS.04-weighted sub-score composite <br>• C.03 = aligned_messages / total_messages |
| **Outputs** | Exact M.01, M.02, C.03 values |
| **Implementation** | `sigrank-sig-army/src/scoring/` |

## `S.27` — Write audit_records

| | |
|---|---|
| **Owner** | sig_army → Postgres |
| **Runtime** | Modal → DB |
| **Status** | 🟡 PROVISIONAL |
| **Inputs** | Exact scores from S.26 |
| **Process** | INSERT into `audit_records` with `auditor='sig_army_v1'`, finding_type, payload. If audit revises a score significantly, finding_type='score_revised'. |
| **Outputs** | Audit record persisted |
| **Implementation** | `db_schema.md` table `audit_records` |

## `S.28` — Update metric_snapshots with Verified Scores

| | |
|---|---|
| **Owner** | sig_army → Postgres |
| **Runtime** | Modal → DB |
| **Status** | 🟡 PROVISIONAL |
| **Inputs** | Exact scores from S.26 · existing `metric_snapshots` row |
| **Process** | UPDATE the operator's most recent metric_snapshots row with verified M.01, M.02, C.03 values. Trigger S.16-S.22 to recompute SIGNA RATE with exact inputs. |
| **Outputs** | Updated metric_snapshots row + new audit-revised SIGNA RATE |
| **Implementation** | `sigrank-sig-army/src/scoring/persist.py` |

## `S.29` — Award Audit Verified Badge

| | |
|---|---|
| **Owner** | Badge Engine |
| **Runtime** | Railway |
| **Status** | 🟡 PROVISIONAL |
| **Inputs** | `audit_records` row from S.27 |
| **Process** | If audit complete and verified (no revision needed OR operator paid for revised score), INSERT `operator_badges` with `badge_id=audit_verified`. |
| **Outputs** | "Audit Verified" badge visible on profile |
| **Implementation** | `sigrank-scoring-worker/src/scoring/badge_engine.py` (special case) |

---

# PHASE 5 — Frontend Reads (Vercel)

Pure read path. Fast. Cached.

## `S.30` — Operator Requests Page

| | |
|---|---|
| **Owner** | Next.js (Vercel) |
| **Runtime** | Vercel Edge / Serverless |
| **Status** | 🟢 LOCKED |
| **Inputs** | HTTP GET `/leaderboard?metric=signa_rate&window=30&class=transmitter&platform=claude` |
| **Process** | Next.js route handler parses query params. |
| **Outputs** | Validated query params for S.31 |
| **Implementation** | `sigrank-web/app/leaderboard/page.tsx` |

## `S.31` — Read leaderboards_cached

| | |
|---|---|
| **Owner** | Supabase Postgres |
| **Runtime** | DB |
| **Status** | 🟢 LOCKED |
| **Inputs** | Query params from S.30 |
| **Process** | SELECT from `leaderboards_cached` WHERE board_type + scope + window + class match. NO live JOINs. Just read materialized payload. |
| **Outputs** | Pre-computed ordered array of operator rows |
| **Implementation** | Supabase client with RLS-respected query |

## `S.32` — Realtime Subscribe (Optional)

| | |
|---|---|
| **Owner** | Supabase Realtime |
| **Runtime** | Edge / Browser |
| **Status** | 🟢 LOCKED |
| **Inputs** | Browser-side subscription to `leaderboards_cached` and `metric_snapshots` |
| **Process** | Supabase Realtime pushes changes to subscribed clients via WebSocket. Frontend re-renders affected rows on update event. |
| **Outputs** | Live UI updates (rank movement, new entries, class changes) |
| **Implementation** | `sigrank-web/lib/realtime.ts` |

## `S.33` — Render with Components

| | |
|---|---|
| **Owner** | Next.js / React |
| **Runtime** | Browser |
| **Status** | 🟢 LOCKED |
| **Inputs** | Leaderboard data from S.31 · realtime updates from S.32 |
| **Process** | Pass data to `components/sigrank/` components (`LeaderboardTable`, `ProfilePanel`, etc.) which render the UI. |
| **Outputs** | Rendered HTML/CSS in browser |
| **Implementation** | `sigrank-web/app/` + `components/sigrank/` |

---

# Cross-cutting concerns

These don't belong to a single step but cut across the pipeline.

## `S.X.01` — Ruleset Versioning Replay

| | |
|---|---|
| **Owner** | Scoring Worker |
| **Status** | 🟢 LOCKED |
| **Trigger** | New `ruleset_version` deployed (e.g., v1.0 → v1.1) |
| **Process** | Background job re-runs S.15-S.22 on every historical `snapshot_submissions` row under the new ruleset. Old `metric_snapshots` rows retained for audit. New rows tagged with new ruleset_version. |

## `S.X.02` — Anti-Gaming Detection (Phase 2)

| | |
|---|---|
| **Owner** | Scoring Worker / Anti-Gaming Module |
| **Status** | 🔴 OPEN (RS.06 currently disabled for MVP) |
| **Trigger** | Each scoring cycle (after S.15) |
| **Process** | Pattern-match against RS.06 rules: spam (MV spike + Comp drop), redundancy (high repeated_chunks ratio), synthetic inflation (PC spike without CT rise). On detection, apply RS.06 penalty in S.16 composite. Flag in admin dashboard. |

## `S.X.03` — Audit Trail Logging

| | |
|---|---|
| **Owner** | All workers |
| **Status** | 🟡 PROVISIONAL |
| **Trigger** | Every state-changing operation |
| **Process** | Append-only `audit_log` table records: submission_id, step_id (S.xx), input_hash, output_hash, timestamp, ruleset_version. Enables full replay + dispute resolution. |

---

# Step ↔ ID matrix

Quick reference: which canonical IDs each step touches.

| Step | Reads | Writes | Owner |
|---|---|---|---|
| S.01 | — | session files | Agent |
| S.02 | session files | Session, Message | Agent |
| S.03 | Session, Message | feature_message, feature_session | Agent |
| S.04 | T.01-T.04, T.06-T.08 | M.01-M.05 | Agent |
| S.05 | T.09-T.11 | B.01-B.03 | Agent |
| S.06 | M.01-M.05, B.01-B.03, T.12-T.16 | canonical JSON, T.20 | Agent |
| S.07 | canonical JSON | T.17, T.18, T.19 | Agent |
| S.08 | signed JSON | HTTP POST | Agent |
| S.09 | T.17, T.18, T.20 | verification status | Ingest |
| S.10 | all T.xx | validation result | Ingest |
| S.11 | device_id history | rate limit decision | Ingest |
| S.12 | full payload | snapshot_submissions row | Ingest |
| S.13 | row from S.12 | NOTIFY | Ingest |
| S.14 | NOTIFY | submission in memory | Worker |
| S.15 | M.01-M.05 raw, RS.02 | M.01-M.05 scored | Worker |
| S.16 | M.01-M.05 scored, RS.01 | C.01 | Worker |
| S.17 | B.03, M.04, B.02 | C.02 (C.03 deferred) | Worker |
| S.18 | C.01, RS.03 | LIVE C.01 | Worker |
| S.19 | M.01, C.01, RS.07 | K.01-K.09 | Worker |
| S.20 | rank_history | movement deltas | Worker |
| S.21 | all above | metric_snapshots, rank_history | Worker |
| S.22 | metric_snapshots | leaderboards_cached | Worker |
| S.23 | metric_snapshots, history | operator_badges | Worker |
| S.24 | payment confirmed | Modal job | Edge |
| S.25 | raw text, word_vault | signal/noise classes, PC sub-scores | sig_army |
| S.26 | S.25 outputs | M.01_exact, M.02_exact, C.03 | sig_army |
| S.27 | exact scores | audit_records | sig_army |
| S.28 | exact scores | updated metric_snapshots | sig_army |
| S.29 | audit_records | Audit Verified badge | Worker |
| S.30 | URL params | query | Frontend |
| S.31 | leaderboards_cached | result set | Frontend |
| S.32 | realtime subscribe | live updates | Frontend |
| S.33 | data | rendered UI | Frontend |

---

# Summary status

| Phase | Locked steps | Provisional steps | Open steps |
|---|---|---|---|
| 1 Agent | S.01* S.02 S.03 S.05 S.06 S.07 S.08 | S.04 | (none) |
| 2 Ingest | S.09 S.10 S.11 S.12 S.13 | (none) | (none) |
| 3 Worker | S.14 S.20 S.21 S.22 | S.15 S.16 S.17 S.18 S.19 S.23 | (none) |
| 4 Precision | (none) | S.24 S.27 S.28 S.29 | S.25 S.26 |
| 5 Frontend | S.30-S.33 | (none) | (none) |
| Cross-cutting | S.X.01 | S.X.03 | S.X.02 |

*S.01 locked for Claude Code only; other platform adapters Phase 2.

See `primary/scoring/GREENING.md` for the path to all-🟢.
