# Refresh Cadences — when each surface updates

BlitzStars pattern: different surfaces refresh at different cadences. Cheap things stay fresh; expensive things update on a schedule. The site reads precomputed views — no surface is computed on page load.

This document defines the cadence for every surface in the SigRank site.

---

## Cadence tiers

| Tier | Frequency | Use case | Job runner |
|---|---|---|---|
| **Live** | Every 30s – 1min | Counters, current-rank ping | Lightweight cron / Realtime subscription |
| **Near-live** | Every 5min | Live leaderboard, recent submissions | Scoring engine post-submit + 5min cron |
| **Hourly** | Every 60min | Activity histograms, recent rank deltas | Hourly cron on Railway worker |
| **Daily** | 00:00 UTC | Signalgeist 90d, Hall of Signal, badge eval | Daily cron |
| **On-demand** | When triggered | Profile pages (lazy hydration on view) | Cache-aside pattern |
| **On-submit** | Every new snapshot | Operator's own profile, their rank | Triggered by scoring engine completion |

---

## Per-surface cadence table

### Homepage

| Surface | Cadence | Materialized view |
|---|---|---|
| Hero stats counters (operators ranked, active, snapshots today, Transmitters) | Live (60s) | `homepage_stats` (single row) |
| Featured Signal Supporters carousel | Daily | `featured_supporters_cached` |
| Today's Signal Leaders (24h) | Near-live (5min) | `today_leaders_24h` |
| Today's Signal Events (top performances 24h) | Near-live (5min) | `today_events_24h` |
| Signalgeist 6-card 90d grid | Daily | `signalgeist_90d` |
| Operators Active counter (per platform) | Live (30s) | `active_counters` |
| Activity Pulse hourly chart | Hourly | `activity_hourly` |
| Weekly Signal Pulse chart (with ruleset markers) | Daily | `activity_weekly` |
| Recently viewed | Per-session (browser localStorage + occasional sync) | Client-side primarily |
| Top 10 daily across 5 metrics | Daily | `top10_by_metric` × 5 |

### Leaderboard (`/leaderboard`)

| Surface | Cadence |
|---|---|
| Top 25 ranked list (default window: 30d) | Near-live (5min) — `leaderboards_cached` |
| Window toggle (Daily / 30 / 60 / 90 / All time) | Each is its own cached view, refreshed per cadence |
| Metric sort toggle (SIGNA / Comp / SD / TT / PC / CT / SF) | Pre-computed per metric, cached |
| Class filter | Filter applied on cached view |
| Platform filter | Filter applied on cached view |
| Pagination | Page-cached |

### Operator Profile (`/operators/{codename}`)

| Surface | Cadence |
|---|---|
| Profile header (codename, class, last seen) | On-submit when own profile · Hourly otherwise |
| SIGNA RATE hero | On-submit own · Near-live others |
| Core 5 grid | Same |
| Analytics dashboard (radar, heatmap, trends) | Daily (heatmap), Hourly (trends), On-submit (radar) |
| Snapshot history drilldown | On-submit own · Daily others |
| Session breakdown drilldown | On-submit own · Daily others |
| Badge case | Daily evaluation, immediate on award |
| Rank tiles | Near-live |

### Hall of Signal (`/hall`)

| Surface | Cadence |
|---|---|
| All-time records | Daily |
| Recipient lists | Daily |
| Hall page itself | Cache 1hr, stale-while-revalidate |

### Pro Dashboard (`/pro`)

| Surface | Cadence |
|---|---|
| Subscription state | On-webhook from Stripe |
| Audit history | On-submit + on-audit-complete |
| Drift Ratio trends | Daily (audit jobs run nightly) |
| Score decomposition | On-submit |

---

## Job orchestration

```
Railway scoring worker
├── Background process: LISTEN on 'new_submission' (continuous)
│   └── On NOTIFY: score submission, write metric_snapshots, update operator's own profile cache
│
├── Cron: every 30s
│   └── Refresh active_counters
│
├── Cron: every 60s
│   └── Refresh homepage_stats
│
├── Cron: every 5min
│   └── Refresh leaderboards_cached (per metric, per window, per class filter)
│   └── Refresh today_leaders_24h
│   └── Refresh today_events_24h
│
├── Cron: every 60min
│   └── Refresh activity_hourly
│   └── Refresh per-operator trends for actively-viewed profiles
│
├── Cron: 00:00 UTC daily
│   └── Refresh signalgeist_90d
│   └── Refresh hall_records
│   └── Run badge engine evaluation
│   └── Refresh top10_by_metric × 5
│   └── Refresh featured_supporters_cached
│   └── Refresh activity_weekly
│   └── Reconcile Stripe subscriptions
│
└── Cron: weekly Sunday 00:00 UTC
    └── Backup snapshot of metric_snapshots
    └── Audit ruleset version coverage
    └── Reconcile subscriptions
```

---

## Cache invalidation triggers

In addition to time-based refresh, certain events trigger invalidation:

| Event | Invalidates |
|---|---|
| New snapshot submitted | Operator's profile cache, their leaderboard rank position |
| Class assignment changed | Operator's profile + leaderboard row, possibly featured carousel |
| Badge awarded | Operator's profile + Hall of Signal if applicable |
| Ruleset version change (RS.xx update) | EVERYTHING (full replay) |
| Subscription state change | Operator's profile (RW.xx display), pro dashboard |
| Manual admin override | Affected operator + audit_log entry |

---

## Patch markers / Ruleset markers (BlitzStars-style)

The weekly chart on the homepage shows operators-active counts with **vertical line markers at each ruleset version change**, just like BlitzStars marks WoT patches (11.4, 11.5, 11.6...).

```
2026-02 ────────── 2026-03 ────────── 2026-04 ────────── 2026-05
                      │                                    │
                      │ v1.0 launched                      │ v1.1 (RS.01 weights tuned)
                      │                                    │
```

This is the trust mechanism. Operators can see exactly when scoring changes happened relative to their rank trajectory.

Stored as:

```sql
CREATE TABLE ruleset_versions (
  version TEXT PRIMARY KEY,
  effective_from TIMESTAMPTZ NOT NULL,
  changelog TEXT NOT NULL,
  changed_params JSONB NOT NULL  -- which RS.xx params changed
);
```

Each chart that supports markers reads this table and overlays vertical lines.

---

## What doesn't get cached

- **Per-snapshot scoring** is not cached — happens once at submit, stored in `metric_snapshots`
- **Auth state** — not cached (Supabase Auth handles)
- **Real-time chat / notifications** (Phase 2) — Supabase Realtime
- **Stripe webhooks** — processed immediately, not cached

---

## Cost rationale

Cheap things (counters, activity pings) run every 30-60s — they're 1-row queries.

Expensive things (Signalgeist 90d, Hall, badge evaluation) run daily — they're large window aggregations.

The leaderboard is the hot path. Refreshing every 5min means up to 5 min stale, which is acceptable. Refreshing on every submission would melt the cache.

For operators viewing their own profile, the on-submit invalidation gives sub-second feedback. For others viewing that operator's profile, they see the 5min-cached version, which is fine.

---

## See also

- [`deployment_topology.md`](deployment_topology.md) — Railway worker hosting
- [`db_schema.md`](db_schema.md) — table definitions
- [`scoring_formula.md`](scoring_formula.md) — what scoring engine does on-submit
