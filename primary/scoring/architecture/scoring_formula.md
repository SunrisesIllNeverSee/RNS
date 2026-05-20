# Scoring Formula

The complete SigRank scoring pipeline. From raw submission → final live rank.

---

## The pipeline

```
Snapshot Submission
        ↓
Validate + Verify Signature
        ↓
Normalize Core 5 → individual [0,100] scores
        ↓
Compute SIGNA RATE composite
        ↓
Apply Recency Modifier → LIVE_SIGNA_RATE
        ↓
Assign Class Tier (uses Compression + SIGNA RATE)
        ↓
Compute Auxiliary Composites (Signal Force, SDRM, Drift)
        ↓
Write to metric_snapshots
        ↓
Update rank_history
        ↓
Regenerate leaderboards_cached
```

---

## Step 1 — Normalize Core 5 to `[0, 100]`

### Compression score
Compression Ratio is already `[0, 1]`. Multiply by 100:

```
COMPRESSION_SCORE = compression_ratio × 100
```

(Already bounded — no further normalization needed.)

### Session Depth score
Apply tiered bucket mapping:

```
function depth_score(sd) {
  if (sd >= 30) return 100
  if (sd >= 25) return 92
  if (sd >= 20) return 84
  if (sd >= 15) return 72
  if (sd >= 10) return 58
  if (sd >= 5)  return 42
  return 25
}
```

### Token Throughput score
Log scale to prevent volume gaming:

```
TT_SCORE = min(100, 20 × log10(total_tokens + 1))
```

### Prompt Complexity score
PC is computed directly to `[0, 100]` — no further normalization.

```
PC_SCORE = prompt_complexity   // already 0-100
```

### Cross-Thread score
Already bounded `[0, 100]`:

```
CT_SCORE = cross_thread_score   // already 0-100
```

---

## Step 2 — Compute SIGNA RATE

```
SIGNA_RATE = 0.30 × COMPRESSION_SCORE
           + 0.20 × DEPTH_SCORE
           + 0.20 × PC_SCORE
           + 0.15 × CT_SCORE
           + 0.15 × TT_SCORE
```

Output range: `[0, 100]`. See [../metrics/composites/01_signa_rate.md](../metrics/composites/01_signa_rate.md).

---

## Step 3 — Apply Recency Modifier

```
function recency_modifier(last_seen_at) {
  const hours_since = (now - last_seen_at) / 3600

  if (hours_since < 24)   return 1.00
  if (hours_since < 72)   return 0.97
  if (hours_since < 168)  return 0.94    // 7d
  if (hours_since < 336)  return 0.88    // 14d
  if (hours_since < 720)  return 0.80    // 30d
  return 0.65
}

LIVE_SIGNA_RATE = SIGNA_RATE × recency_modifier(last_seen)
```

The leaderboard ranks on `LIVE_SIGNA_RATE`, not raw `SIGNA_RATE`. Profile pages display both — the raw composite for identity, the live score for current rank.

---

## Step 4 — Assign class tier

See [class_tiers.md](class_tiers.md) — `assign_class(compression_ratio, signa_rate)`.

---

## Step 5 — Compute auxiliary composites

### Signal Force
```
SF = (total_messages_lifetime × session_depth_avg) / account_age_days
SF_SCORE = min(100, 20 × log10(SF + 1))   // for display
```

### SDRM (provisional)
```
THREAD_RATE = cross_thread_score / message_volume
SDRM = (compression_ratio × (session_depth_avg + prompt_complexity / 10)) × THREAD_RATE × 100
```

(SDRM formula remains under recovery — this is a working placeholder.)

### Drift Ratio (precision tier only)
```
DR = (aligned_messages / total_messages) × 100
```

Requires sig_army analysis. Free tier leaves this `null`.

---

## Step 6 — Movement deltas

```
movement_24h = current_global_rank - global_rank_24h_ago
movement_7d  = current_global_rank - global_rank_7d_ago
```

Negative values = moved up. Positive = moved down. Display arrows accordingly.

---

## Anti-gaming layer (Phase 2)

The original GPT thread proposed a penalty layer but the user explicitly chose to defer it: *"Number two can be put in parenthesis... not concerned about penalizing right now... the measurements should handle everything."*

When penalties are eventually added:

### Spam penalty
```
if (message_volume > prior_7d_avg × 1.4
    && compression < prior_7d_avg × 0.9
    && session_depth < prior_7d_avg × 0.85) {
  SPAM_PENALTY = -5 to -25 depending on severity
}
```

### Redundancy penalty
```
REDUNDANCY_RATIO = repeated_chunks / total_chunks
if (REDUNDANCY_RATIO > threshold) apply -5 / -10 / -20 penalty
```

### Synthetic inflation
```
if (prompt_complexity rises but cross_thread does not) flag for review
```

**For MVP:** No penalties. Pure measurement.

---

## Replay-ability

Every metric_snapshots row records `ruleset_version`. If scoring rules change:

1. New `rulesets` row added with `effective_from`
2. New scoring job recomputes against historical `snapshot_submissions`
3. Old `metric_snapshots` retained for audit
4. New `metric_snapshots` created with new `ruleset_version`

This is non-negotiable. Without ruleset versioning, leaderboard history is unreliable.

---

## Worked example — MO§ES 7-day window

**Inputs:**
- compression_ratio: 0.9694
- session_depth_avg: 348.9 (turns/session)
- prompt_complexity: 89.0
- cross_thread_score: 96 (high cache reuse → near max)
- total_tokens: 1,123,252,011

**Step 1 — Normalize:**
- COMPRESSION_SCORE: 96.94
- DEPTH_SCORE: 100 (>>30)
- PC_SCORE: 89.0
- CT_SCORE: 96
- TT_SCORE: 100 (1.12B tokens × log = capped at 100)

**Step 2 — SIGNA RATE:**
```
SIGNA_RATE = 0.30(96.94) + 0.20(100) + 0.20(89.0) + 0.15(96) + 0.15(100)
           = 29.08 + 20.00 + 17.80 + 14.40 + 15.00
           = 96.28
```

**Step 3 — Recency:** last_seen < 24h → modifier 1.00 → LIVE_SIGNA_RATE = 96.28

**Step 4 — Class:** Compression 0.9694 ≥ 0.85 AND SIGNA RATE 96.28 ≥ 85 → **TRANSMITTER**

**Output:** `MO§ES` ranks Transmitter-class, LIVE_SIGNA_RATE = `96.3`.

That matches the SignalSystemBoard image where the user value was `96.4` — the difference is within rounding.

---

## Rule lock — Ruleset v1.0

Effective from: `2026-05-14T00:00:00Z`

Weights:
```
Compression: 0.30
Session Depth: 0.20
Prompt Complexity: 0.20
Cross-Thread: 0.15
Token Throughput: 0.15
```

Recency tiers as above.

Class thresholds as in `class_tiers.md`.

Penalties: none.

**Locked.** Any change increments to v1.1.
