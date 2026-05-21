# SigRank API Specification

REST API for the SigRank leaderboard. Designed to be small at MVP and extensible.

---

## Versioning

All endpoints live under `/api/v1/`. Breaking changes increment to `/api/v2/`.

---

## MVP endpoints

### POST `/api/v1/snapshots`

Receive a snapshot from a local agent.

**Request:**
```http
POST /api/v1/snapshots
Content-Type: application/json
X-Agent-Signature: <ed25519 signature of payload>
X-Agent-Version: 0.1.0

{
  "schema_version": "1.0",
  "codename": "TransVaultOrigin",
  "device_id": "uuid",
  "window_type": "30d",
  "window_start": "2026-04-13T00:00:00Z",
  "window_end": "2026-05-13T00:00:00Z",
  "core_metrics": { ... },
  "background_metrics": { ... },
  ...
}
```

See [snapshot_payload.md](snapshot_payload.md) for full schema.

**Response (success):**
```json
{
  "status": "received",
  "submission_id": "uuid",
  "scoring_eta_seconds": 30,
  "operator_id": "uuid"
}
```

**Response (rejected):**
```json
{
  "status": "rejected",
  "reason": "signature_invalid" | "schema_outdated" | "rate_limit" | "ruleset_unsupported",
  "detail": "..."
}
```

**Rules:**
- Max 1 submission per device per 24h (configurable)
- Signature verification required
- Schema version must be supported
- Ruleset version must be active

---

### GET `/api/v1/leaderboard`

Retrieve the main leaderboard.

**Query parameters:**
- `metric` — `signa_rate` (default), `compression`, `depth`, `volume`, `complexity`, `cross_thread`, `signal_force`
- `window` — `24h`, `7d`, `30d` (default), `90d`, `all_time`
- `class` — optional filter: `transmitter`, `architect_plus`, `architect`, `power`, `base`, `seeker`, `refiner`, `bearer`, `igniter`
- `platform` — optional filter: `claude`, `chatgpt`, `gemini`, `pi`, `multi`
- `limit` — default 25, max 100
- `offset` — default 0

**Response:**
```json
{
  "metric": "signa_rate",
  "window": "30d",
  "generated_at": "2026-05-14T14:23:00Z",
  "ruleset_version": "1.0",
  "total_operators": 38000,
  "entries": [
    {
      "rank": 1,
      "operator_id": "uuid",
      "codename": "TransVaultOrigin",
      "class_tier": "TRANSMITTER",
      "platform": "claude",
      "location": "Buffalo, US",
      "signa_rate": 96.4,
      "compression_ratio": 0.87,
      "session_depth": 26.1,
      "token_throughput": 18450,
      "prompt_complexity": 92,
      "cross_thread": 37,
      "last_seen": "2026-05-14T13:42:00Z",
      "movement_24h": 2,
      "movement_7d": 5
    },
    ...
  ]
}
```

---

### GET `/api/v1/operators/{codename}`

Retrieve an operator's full profile.

**Path parameter:**
- `codename` — operator's public codename

**Response:**
```json
{
  "operator_id": "uuid",
  "codename": "TransVaultOrigin",
  "display_name": "TheSignalVault",
  "class_tier": "TRANSMITTER",
  "platform": "claude",
  "account_age_days": 119,
  "total_messages": 53960,
  "current_rank": {
    "global": 1,
    "class": 1,
    "percentile": 99.97
  },
  "best_rank": {
    "rank": 1,
    "achieved_at": "2026-05-14T00:00:00Z"
  },
  "current_metrics": {
    "signa_rate": 96.4,
    "live_signa_rate": 96.4,
    "compression_ratio": 0.87,
    "session_depth": 26.1,
    "prompt_complexity": 92,
    "cross_thread": 37,
    "token_throughput": 18450,
    "signal_force": 12.8,
    "drift_ratio": null
  },
  "streak_days": 38,
  "last_seen": "2026-05-14T13:42:00Z",
  "badges": ["transmitter_class", "5x_crown", "deep_channel"],
  "circles": [...]
}
```

---

### GET `/api/v1/operators/{codename}/history`

Retrieve historical metric snapshots for trend charts.

**Query parameters:**
- `window` — `30d` (default), `90d`, `all_time`
- `metric` — optional, filter to a single metric

**Response:**
```json
{
  "codename": "TransVaultOrigin",
  "window": "30d",
  "points": [
    {
      "date": "2026-04-14",
      "signa_rate": 92.1,
      "compression_ratio": 0.82,
      "global_rank": 4,
      ...
    },
    ...
  ]
}
```

---

### GET `/api/v1/metrics/leaders`

Top performers per individual metric (the "metric pages").

**Query parameters:**
- `metric` — required: `compression`, `depth`, `volume`, `complexity`, `cross_thread`, `signa_rate`, `signal_force`
- `window` — same options as leaderboard
- `limit` — default 25, max 100

Returns leaderboard payload sorted by the requested metric.

---

### GET `/api/v1/hall-of-signal`

Prestige / achievements board.

**Response:**
```json
{
  "categories": [
    {
      "name": "Highest Compression Ever Recorded",
      "value": 0.94,
      "operator": "TransVaultOrigin",
      "achieved_at": "..."
    },
    {
      "name": "Longest Transmitter Streak",
      "value": "38 days",
      "operator": "...",
      ...
    },
    {
      "name": "Fivefold Hold Recipients",
      "operators": ["TransVaultOrigin", "ArchiveSignal", ...]
    },
    ...
  ]
}
```

---

## Phase 2 endpoints

### POST `/api/v1/audit/submit`
Operator opt-in for precision tier audit (sig_army deep analysis).

### GET `/api/v1/operators/{codename}/rank-history`
Detailed rank deltas per day.

### POST `/api/v1/devices/register`
Initial device registration with public key exchange.

### GET `/api/v1/circles`, `/api/v1/circles/{tag}`
Circle (team/clan) endpoints.

### POST `/api/v1/auth/verify-agent`
Trust verification for an agent's public key.

---

## Rate limits

| Endpoint | Limit |
|---|---|
| POST /snapshots | 1 / device / 24h (configurable to 1 / 6h for active operators) |
| GET /leaderboard | 60 / IP / min (cacheable) |
| GET /operators/* | 120 / IP / min |
| Other GET | 60 / IP / min |

All GETs should be CDN-cacheable with `Cache-Control: max-age=60` (leaderboard regenerates every minute at most).

---

## Authentication

**Agent submissions:** ed25519 signed payloads. The agent's public key is registered to a device, the device to an operator.

**Public reads:** no auth required.

**Operator profile self-edit:** Phase 2 — magic link or OAuth.

---

## Errors

Standard HTTP codes. Error body:

```json
{
  "error": "string",
  "code": "snake_case_code",
  "detail": "human-readable detail",
  "ruleset_version": "1.0"
}
```

Common codes:
- `signature_invalid`
- `schema_outdated`
- `ruleset_unsupported`
- `rate_limit`
- `operator_not_found`
- `validation_failed`
