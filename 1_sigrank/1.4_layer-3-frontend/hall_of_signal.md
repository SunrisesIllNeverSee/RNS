# Hall of Signal — Spec

**Status:** spec locked at structure level · awaiting implementation
**Source pattern:** [BlitzStars Hall of Fame](https://www.blitzstars.com/halloffame) — operator confirmed BlitzStars is the canonical UX reference
**Lock date:** 2026-05-21

---

## What Hall of Signal IS — and is NOT

Hall of Signal is **structurally NOT the leaderboard.** They are two different ranking systems running side by side. Confusing them will kill the product the same way confusing message-vs-token resolution killed the .87xx investigation for eight months.

| Aspect | Leaderboard | Hall of Signal |
|---|---|---|
| Ranks operators on | Rolling-average performance across windows | **Single peak moments** (best ever Compression, deepest single session, etc.) |
| Data source | Auto-pulled from local agent snapshots (signed) | **Operator-submitted prestige snapshots** with verification |
| Time segmentation | 30d / 90d / Career rolling | **All time + annual Seasons** (Season 1 = 2026, Season 2 = 2027, …) |
| Granularity | Global / regional / per-platform | **Per-metric** top 10 (Compression top 10, PC top 10, CT top 10, SD top 10, TT top 10, SIGNA RATE top 10) |
| Aggregation | Direct stat aggregation | **Sliding-scale points** (1st = N points, 10th = 1 point) → Operator / Circle points leaderboards |
| Submission states | N/A | Personal / Verified / Delisted / Disputed |
| Verification | ed25519 signature on local-agent submission | ed25519 signature + (eventually) sig_army audit at precision tier |
| Visual prestige | Active competitive standing | **Achievement / record / permanence** |

The leaderboard captures sustained excellence. The Hall captures peaks. Both ship. Both matter.

---

## Why this matters for SigRank's positioning

Two separate ranking dimensions give operators two paths to prestige:

1. **Sustained operators** dominate the leaderboard via SIGNA RATE (composite of rolling Core 5).
2. **Peak operators** dominate the Hall via single-window record-breaking submissions.

This is the structural answer to the operator's note from 2026-05-21:
> "we will be able to highlight small details like that for users with sustained peaks, or short bursts."

Hall of Signal is where the short-burst, niche-tank-style peak excellence gets recognized. The "118 of 600 on IS-2 Pravda SP" and "top 7% of 18k on VK 30.01P" cases both qualify, but in different ways: leaderboard rank (within population) vs. peak submission (record holder for that metric in that season).

---

## Page structure

URL: `/hall` (or `/hall-of-signal` — TBD with operator)

### Header strip
- Page title: **Hall of Signal**
- Tagline: *Triumphus Famae Et Gloriae* (or operator's chosen tagline)
- Season selector: **All time · Season 1 (2026) · Season 2 (2027) · …**
- Region/Platform selector: **All · Claude · ChatGPT · Gemini · Pi · Multi**
- Submission state tabs: **Verified · Personal · Disputed · Delisted**

### Tier filter strip
- For SigRank: **Class tier filter** (Transmitter / Architect+ / Architect / Power / Base / Seeker / Refiner / Bearer / Igniter)
- Equivalent to BlitzStars' tank-tier filter (I–X)
- Allows viewing Hall records only from a specific class

### Aggregate boards (top of page)
Two ranked tables, side by side or stacked:

#### Circles by Points
| Rank | Circle | Points | Top 1 / Top 3 / Top 10 / Top 100 counts |
|---|---|---|---|

Example: `Foundry Circle [FOUND] — 127,417 pts — 40 / 51 / 62 / 427`

#### Operators by Points
| Rank | Codename | Circle | Points | Top 1 / Top 3 / Top 10 / Top 100 counts |
|---|---|---|---|---|

The four numbers after the points value are the count of placements in each band — gives a sense of *consistency* of peak excellence vs. one-hit dominance.

### Per-metric leaderboards (main body)

For **each** of the canonical SigRank metrics, a top-10 board:

1. **Top 10 — Compression Ratio (M.01)** — single-window peak Compression
2. **Top 10 — Prompt Complexity (M.02)**
3. **Top 10 — Cross-Thread Referencing (M.03)**
4. **Top 10 — Session Depth (M.04)**
5. **Top 10 — Token Throughput (M.05)**
6. **Top 10 — SIGNA RATE (C.01)** — best single-window composite
7. **Top 10 — SDOT (C.02)** — biggest positive delta over a window
8. **Top 10 — SDRM (C.03)** — highest single-window coherence score
9. **Top 10 — Signal Force (E.01)** — extras (still rankable in Hall)
10. **Top 10 — Drift Ratio (E.02)** — extras (precision tier only)

Each board row:

| # | Metric value | Codename | Circle (tag) | Platform/Agent | Submitted | Proof link |
|---|---|---|---|---|---|---|

Example row (Compression top board):

| 1 | 0.9847 | TransVaultOrigin | Foundry [FOUND] | Claude-Opus-4.7 | Apr 21, 2026 | [View](#) |

Each board also has a **"view all in top 10"** drilldown that expands to show all 10 places + recently-submitted candidates pending verification.

### Submit panel

- **Submit Snapshot** button — opens a flow for operator-submitted prestige snapshots (separate from regular leaderboard ingestion)
- The submitted snapshot must be from the operator's local agent (signed) AND optionally accompanied by a transcript artifact for verification
- Verification flow: snapshot signature → optional sig_army re-score → admin/operator review for disputes

### Trailer notes
- Points awarded per-place on sliding scale (1st = highest, 10th = lowest)
- Records update names/circles within 24h of operator change
- Disputed submissions held until resolved; Delisted submissions kept in audit trail but not counted

---

## Data model additions

New tables / columns needed beyond the current `metric_snapshots`:

### `hall_submissions`
```
hall_submission_id  uuid PK
operator_id         fk operators
submission_id       fk snapshot_submissions (the underlying snapshot)
metric_id           enum (M.01, M.02, ..., C.03, E.01, E.02)
metric_value        numeric
window_basis        enum (single_window | rolling_7d | rolling_30d)
window_start        timestamp
window_end          timestamp
season              int (1, 2, 3, ...)
state               enum (personal | verified | disputed | delisted)
submitted_at        timestamp
verified_at         timestamp nullable
verified_by         text nullable  (sig_army | admin_review | self_signed)
proof_url           text nullable  (optional transcript artifact path)
notes               text nullable
```

### `hall_points`
Materialized view, refreshed daily:
```
operator_id         fk operators
season              int
points              numeric  (sum of sliding-scale points across all metric top-10 placements)
top_1_count         int
top_3_count         int
top_10_count        int
top_100_count       int
```

Sliding scale formula (proposed, tunable in `RS.xx`):
```
points_for_rank(r) = max(0, 11 - r)  
  # rank 1 = 10 pts, rank 10 = 1 pt, rank 11+ = 0 pts
```

Or a non-linear sliding scale weighted toward the top (also tunable proprietary):
```
points_for_rank(r) = round(100 / (r ^ 0.7))
  # rank 1 = 100, rank 5 = 32, rank 10 = 20, rank 50 = 5
```

### `circle_hall_points`
Aggregated from `hall_points` over circle membership.

---

## Frontend components

| Component | Lives in | Purpose |
|---|---|---|
| `HallHeader` | `1_sigrank/1.5_components/sigrank/HallHeader.tsx` | Title + season selector + region filter + state tabs |
| `HallPointsBoard` | same | Renders Circles-by-Points and Operators-by-Points tables |
| `MetricTopTen` | same | Renders one metric's top 10 (reused for all 10 metric boards) |
| `HallSubmissionRow` | same | One row in a metric top 10 — codename + circle + value + proof link |
| `SubmitSnapshotModal` | same | Operator-facing submission flow |

The existing `LeaderboardTable` component in `1.5_components/sigrank/` is NOT reused — Hall rows have different shape (single value + season + state + proof) than leaderboard rows (rolling averages + rank movement).

---

## Refresh cadence

| Surface | Cadence |
|---|---|
| Personal Hall submissions display | Real-time after operator submits |
| Verified top 10 boards | Hourly recompute |
| Circles-by-Points + Operators-by-Points aggregate | Daily recompute |
| Season rollover | Annual cron on Jan 1 (NY UTC) |

---

## Open questions for operator

1. **Submission gate** — should Hall submissions be open to all operators (free tier) or gated to verified/Pro? BlitzStars gates replay submission to "supporters" of certain tiers.
2. **Sliding scale weighting** — linear (1st = 10 pts) or exponential (1st = 100 pts, dropoff fast)?
3. **Per-metric or per-platform top 10?** — should each metric have one global top 10, or split top 10 per platform (Claude top 10 Compression, ChatGPT top 10 Compression, etc.)? BlitzStars splits by region. For SigRank "platform" is the analog.
4. **Class-tier weighting** — should a Transmitter-class Compression peak count for more Hall points than a Power-class peak at the same numeric value? BlitzStars implicitly does this via tier-only filtering, but doesn't weight points by tier.
5. **Disputed submission flow** — who arbitrates? Operator-only initially? Community-voted later? Locked-down with sig_army audit?

---

## Connection to badges

Existing badges in `1_sigrank/1.2_layer-1-foundation/badges/BADGE_LEDGER.md` should hook into Hall placements:

- **5x Crown** — held simultaneous top placement in 5 different metric top-10 boards
- **Fivefold Hold** — sustained 5x Crown for ≥1 full season
- **Hall Inductee** — any verified top-10 placement
- **Hall Architect** — multiple top-10 placements across metrics in a single season
- **Hall Permanent Record** — held #1 in any metric for a full season

Badge unlock logic refs the `hall_points` table.
