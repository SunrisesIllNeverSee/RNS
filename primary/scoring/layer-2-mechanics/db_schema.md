# SigRank Database Schema

PostgreSQL-targeted schema for the SigRank leaderboard. Designed for replayability, versioning, and historical depth — never just storing final scores.

---

## Core principle

> Do not store only final scores. Store canonical submissions, reusable features, derived metrics, and cached boards.

This means every snapshot is replayable — if scoring rules change, we can recompute history from raw submissions without losing data.

---

## Tables

### `operators`

The primary identity table.

```sql
CREATE TABLE operators (
  operator_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codename           TEXT NOT NULL UNIQUE,
  display_name       TEXT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen          TIMESTAMPTZ,
  status             TEXT NOT NULL DEFAULT 'active',
                     -- active, dormant, banned, retired
  privacy_level      TEXT NOT NULL DEFAULT 'public',
                     -- public, anonymous, private
  verification_status TEXT NOT NULL DEFAULT 'unverified',
                     -- unverified, verified, audited
  primary_domain     TEXT,
                     -- which AI platform: claude, chatgpt, gemini, pi, multi
  account_age_days   INTEGER,
                     -- denormalized for fast queries
  total_messages_lifetime BIGINT DEFAULT 0
                     -- denormalized lifetime counter
);

CREATE INDEX idx_operators_codename ON operators(codename);
CREATE INDEX idx_operators_last_seen ON operators(last_seen DESC);
CREATE INDEX idx_operators_status ON operators(status);
```

---

### `devices`

Each operator may run multiple local agents (laptop, desktop, etc.).

```sql
CREATE TABLE devices (
  device_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  agent_public_key   TEXT NOT NULL,
  agent_version      TEXT NOT NULL,
  device_label       TEXT,
                     -- user-provided: "macbook", "desk linux", etc.
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen          TIMESTAMPTZ,
  trust_status       TEXT NOT NULL DEFAULT 'pending'
                     -- pending, trusted, revoked
);

CREATE INDEX idx_devices_operator ON devices(operator_id);
```

---

### `snapshot_submissions`

The raw payload from each local agent publish. Append-only, never modified.

```sql
CREATE TABLE snapshot_submissions (
  submission_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  device_id          UUID NOT NULL REFERENCES devices(device_id),
  submitted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  window_type        TEXT NOT NULL,
                     -- today, 7d, 30d, 90d, all_time
  window_start       TIMESTAMPTZ NOT NULL,
  window_end         TIMESTAMPTZ NOT NULL,
  schema_version     TEXT NOT NULL,
                     -- snapshot payload version
  ruleset_version    TEXT NOT NULL,
                     -- scoring engine version applied
  snapshot_hash      TEXT NOT NULL,
                     -- sha256 of canonical payload
  signature          TEXT NOT NULL,
                     -- agent signature
  payload_json       JSONB NOT NULL,
  status             TEXT NOT NULL DEFAULT 'received'
                     -- received, validated, rejected, scored
);

CREATE INDEX idx_submissions_operator ON snapshot_submissions(operator_id, submitted_at DESC);
CREATE INDEX idx_submissions_status ON snapshot_submissions(status);
```

---

### `session_summaries`

Per-session metrics (when the agent uploads session-level data).

```sql
CREATE TABLE session_summaries (
  session_id         UUID PRIMARY KEY,
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  submission_id      UUID NOT NULL REFERENCES snapshot_submissions(submission_id),
  source_type        TEXT NOT NULL,
                     -- claude, chatgpt, gemini, pi, generic
  started_at         TIMESTAMPTZ NOT NULL,
  ended_at           TIMESTAMPTZ,
  message_count      INTEGER NOT NULL DEFAULT 0,
  token_estimate     BIGINT DEFAULT 0,
  session_depth_avg  NUMERIC(6,2),
  prompt_complexity_score NUMERIC(5,2),
  cross_thread_score INTEGER,
  compression_ratio  NUMERIC(5,4),
  last_seen_at       TIMESTAMPTZ
);

CREATE INDEX idx_sessions_operator ON session_summaries(operator_id, started_at DESC);
```

---

### `feature_rollups_daily`

Daily aggregated features per operator. The reusable middle layer.

```sql
CREATE TABLE feature_rollups_daily (
  rollup_date        DATE NOT NULL,
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  messages_total     INTEGER NOT NULL DEFAULT 0,
  sessions_total     INTEGER NOT NULL DEFAULT 0,
  depth_avg          NUMERIC(6,2),
  depth_max          INTEGER,
  complexity_avg     NUMERIC(5,2),
  complexity_max     NUMERIC(5,2),
  cross_thread_refs  INTEGER DEFAULT 0,
  memory_callbacks   INTEGER DEFAULT 0,
  active_minutes_est INTEGER DEFAULT 0,
  streak_days        INTEGER DEFAULT 0,
  feature_json       JSONB,
                     -- bag of additional features for replay
  PRIMARY KEY (rollup_date, operator_id)
);

CREATE INDEX idx_rollups_operator ON feature_rollups_daily(operator_id, rollup_date DESC);
```

---

### `metric_snapshots`

The board-grade scored metrics. The leaderboard reads from here.

```sql
CREATE TABLE metric_snapshots (
  metric_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  snapshot_date      DATE NOT NULL,
  window_type        TEXT NOT NULL,

  -- Core 5
  compression_ratio  NUMERIC(5,4),
  prompt_complexity  NUMERIC(5,2),
  cross_thread       INTEGER,
  session_depth      NUMERIC(6,2),
  token_throughput   BIGINT,

  -- Background 3
  message_volume     INTEGER,
  account_age_days   INTEGER,
  total_messages     BIGINT,

  -- Composites
  signa_rate         NUMERIC(5,2),
  signal_force       NUMERIC(10,2),
  drift_ratio        NUMERIC(5,2),

  -- Class assignment
  class_tier         TEXT,

  -- Activity
  last_seen          TIMESTAMPTZ,
  recency_modifier   NUMERIC(3,2),
  live_signa_rate    NUMERIC(5,2),

  -- Movement
  movement_24h       INTEGER,
  movement_7d        INTEGER,

  generated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  ruleset_version    TEXT NOT NULL,

  UNIQUE (operator_id, snapshot_date, window_type)
);

CREATE INDEX idx_metric_snapshots_signa ON metric_snapshots(signa_rate DESC);
CREATE INDEX idx_metric_snapshots_class ON metric_snapshots(class_tier, signa_rate DESC);
CREATE INDEX idx_metric_snapshots_date ON metric_snapshots(snapshot_date DESC);
```

---

### `rank_history`

Per-metric historical ranks for trend charts.

```sql
CREATE TABLE rank_history (
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  snapshot_date      DATE NOT NULL,
  global_rank        INTEGER,
  class_rank         INTEGER,
  compression_rank   INTEGER,
  depth_rank         INTEGER,
  volume_rank        INTEGER,
  complexity_rank    INTEGER,
  cross_thread_rank  INTEGER,
  percentile         NUMERIC(5,2),
  PRIMARY KEY (operator_id, snapshot_date)
);

CREATE INDEX idx_rank_history_global ON rank_history(snapshot_date, global_rank);
```

---

### `badges` and `operator_badges`

```sql
CREATE TABLE badges (
  badge_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  badge_name         TEXT NOT NULL UNIQUE,
  badge_type         TEXT NOT NULL,
                     -- structural, event, prestige
  criteria_json      JSONB NOT NULL,
  rarity             TEXT NOT NULL DEFAULT 'common',
                     -- common, rare, epic, legendary
  icon_url           TEXT
);

CREATE TABLE operator_badges (
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  badge_id           UUID NOT NULL REFERENCES badges(badge_id),
  awarded_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_snapshot_id UUID REFERENCES metric_snapshots(metric_snapshot_id),
  source_note        TEXT,
  PRIMARY KEY (operator_id, badge_id, awarded_at)
);
```

**Initial badge catalog** (see naming_drift.md for the full list):
- 5x Crown — held all five Core metrics simultaneously
- Transmitter-Class — sustained Compression ≥ 0.85
- Architect Lock — sustained Architect+ for 14+ days
- Crossweaver — elite CT continuity
- Deep Channel — exceptional Session Depth
- Compression Forge — high Compression sustained through heavy MV
- Audit Verified — manually confirmed metrics
- Ghost Return — reactivation after dormancy
- Lightning Strike — largest 24h rise
- Quiet Giant — low MV, elite Compression
- Iron Streak — sustained active streak
- Fivefold Hold — held all five Core crowns simultaneously

---

### `circles` (team/clan equivalent)

```sql
CREATE TABLE circles (
  circle_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name               TEXT NOT NULL,
  tag                TEXT NOT NULL UNIQUE,
  visibility         TEXT NOT NULL DEFAULT 'public',
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  owner_operator_id  UUID NOT NULL REFERENCES operators(operator_id)
);

CREATE TABLE circle_members (
  circle_id          UUID NOT NULL REFERENCES circles(circle_id),
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  joined_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  role               TEXT NOT NULL DEFAULT 'member',
                     -- owner, officer, member
  status             TEXT NOT NULL DEFAULT 'active',
  PRIMARY KEY (circle_id, operator_id)
);

CREATE TABLE circle_metric_snapshots (
  circle_id          UUID NOT NULL REFERENCES circles(circle_id),
  snapshot_date      DATE NOT NULL,
  avg_compression    NUMERIC(5,4),
  avg_depth          NUMERIC(6,2),
  avg_complexity     NUMERIC(5,2),
  avg_cross_thread   NUMERIC(6,2),
  total_volume       BIGINT,
  avg_signa_rate     NUMERIC(5,2),
  global_rank        INTEGER,
  PRIMARY KEY (circle_id, snapshot_date)
);
```

**Circles status:** Phase 2. Not required for MVP.

---

### `leaderboards_cached`

Precomputed leaderboard tables. The web app reads from here, not from live joins.

```sql
CREATE TABLE leaderboards_cached (
  leaderboard_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  board_type         TEXT NOT NULL,
                     -- global, compression, depth, complexity, cross_thread, volume,
                     -- circle_global, class_transmitter, etc.
  scope              TEXT NOT NULL,
                     -- global, region, platform, class
  scope_value        TEXT,
                     -- e.g. "claude", "north_america", "transmitter"
  window_type        TEXT NOT NULL,
                     -- 24h, 7d, 30d, 90d, all_time
  generated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  ruleset_version    TEXT NOT NULL,
  payload_json       JSONB NOT NULL,
                     -- ordered array of {rank, operator_id, score, ...}
  expires_at         TIMESTAMPTZ
);

CREATE INDEX idx_leaderboards_lookup ON leaderboards_cached(board_type, scope, scope_value, window_type, generated_at DESC);
```

---

### `audit_records` (precision tier)

When operators opt into the precision tier (sig_army audit), audit findings are recorded here.

```sql
CREATE TABLE audit_records (
  audit_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id        UUID NOT NULL REFERENCES operators(operator_id),
  audit_date         TIMESTAMPTZ NOT NULL DEFAULT now(),
  auditor            TEXT NOT NULL,
                     -- sig_army_v1, manual_review, etc.
  finding_type       TEXT NOT NULL,
                     -- score_verified, score_revised, anomaly_flagged
  finding_summary    TEXT,
  audit_payload      JSONB,
  status             TEXT NOT NULL DEFAULT 'active',
  confidence         NUMERIC(3,2)
);
```

---

### `rulesets`

Versioned scoring rule sets so we can replay history.

```sql
CREATE TABLE rulesets (
  ruleset_version    TEXT PRIMARY KEY,
  effective_from     TIMESTAMPTZ NOT NULL,
  effective_to       TIMESTAMPTZ,
  formula_json       JSONB NOT NULL,
                     -- the full scoring formula as JSON
  threshold_json     JSONB NOT NULL,
                     -- class tier thresholds
  weight_json        JSONB NOT NULL,
                     -- composite weights
  notes              TEXT
);
```

---

## Read-pattern overview

| User action | Tables hit |
|---|---|
| View leaderboard | `leaderboards_cached` only |
| View operator profile | `operators` + `metric_snapshots` (latest) + `rank_history` |
| Operator drilldown — sessions | `session_summaries` |
| Operator drilldown — daily history | `feature_rollups_daily` + `rank_history` |
| Submit snapshot | INSERT `snapshot_submissions`; scoring job populates rest |
| Score replay (ruleset change) | Read `snapshot_submissions` + `rulesets`, regenerate `metric_snapshots` |

---

## Write-pattern overview

| Action | Tables affected |
|---|---|
| Agent publishes snapshot | `snapshot_submissions` (raw), `session_summaries` (parsed) |
| Daily scoring job | `feature_rollups_daily`, `metric_snapshots`, `rank_history`, `leaderboards_cached` |
| Badge award | `operator_badges` |
| Audit completion | `audit_records`, possibly revise `metric_snapshots` |
| Circle creation | `circles`, `circle_members` |
