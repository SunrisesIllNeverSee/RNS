# Snapshot Payload Schema

The canonical JSON payload submitted by a local agent to `POST /api/v1/snapshots`. Versioned, signed, replayable.

---

## Schema version 1.0

```json
{
  "schema_version": "1.0",
  "codename": "TransVaultOrigin",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "submitted_at": "2026-05-14T14:00:00Z",

  "window": {
    "type": "30d",
    "start": "2026-04-14T00:00:00Z",
    "end": "2026-05-14T00:00:00Z"
  },

  "platform": {
    "primary": "claude",
    "models": ["claude-opus-4-7", "claude-sonnet-4-6"]
  },

  "core_metrics": {
    "compression_ratio": 0.87,
    "prompt_complexity": 92.4,
    "cross_thread_score": 37,
    "session_depth_avg": 26.1,
    "token_throughput": 18450
  },

  "background_metrics": {
    "message_volume": 1170,
    "account_age_days": 119,
    "total_messages_lifetime": 53960
  },

  "composites": {
    "signa_rate": 96.4,
    "signal_force": 12.8,
    "sdrm_score": null,
    "drift_ratio": null
  },

  "raw_telemetry": {
    "sessions_count": 21,
    "turns_total": 7327,
    "tokens_total": 1123252011,
    "tokens_input_fresh": 123246,
    "tokens_output": 3902803,
    "tokens_cache_read": 1084399183,
    "tokens_cache_creation": 34826779,
    "active_minutes_est": 2700
  },

  "tier": "free",

  "agent": {
    "version": "0.1.0",
    "ruleset_version": "1.0",
    "snapshot_hash": "sha256:abc123...",
    "public_key": "ed25519:..."
  }
}
```

---

## Field definitions

### Top-level

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | Snapshot schema version |
| `codename` | string | yes | Operator's public codename |
| `device_id` | UUID | yes | Identifier of the submitting device |
| `submitted_at` | ISO 8601 | yes | When the agent created the payload |

### `window`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `today` \| `7d` \| `30d` \| `90d` \| `all_time` |
| `start` | ISO 8601 | yes | Window start (inclusive) |
| `end` | ISO 8601 | yes | Window end (exclusive) |

### `platform`

| Field | Type | Required | Description |
|---|---|---|---|
| `primary` | enum | yes | `claude` \| `chatgpt` \| `gemini` \| `pi` \| `multi` \| `other` |
| `models` | array | no | List of specific model identifiers used |

### `core_metrics` (all required for free tier ranking)

| Field | Type | Range | Description |
|---|---|---|---|
| `compression_ratio` | float | `[0, 1]` | See [../metrics/core_5/01_compression_ratio.md](../metrics/core_5/01_compression_ratio.md) |
| `prompt_complexity` | float | `[0, 100]` | See [../metrics/core_5/02_prompt_complexity.md](../metrics/core_5/02_prompt_complexity.md) |
| `cross_thread_score` | int | `[0, 100]` | See [../metrics/core_5/03_cross_thread_referencing.md](../metrics/core_5/03_cross_thread_referencing.md) |
| `session_depth_avg` | float | `[0, ∞)` | See [../metrics/core_5/04_session_depth.md](../metrics/core_5/04_session_depth.md) |
| `token_throughput` | int | `[0, ∞)` | See [../metrics/core_5/05_token_throughput.md](../metrics/core_5/05_token_throughput.md) |

### `background_metrics`

| Field | Type | Required | Description |
|---|---|---|---|
| `message_volume` | int | yes | Messages in current window |
| `account_age_days` | int | yes | Days since account creation |
| `total_messages_lifetime` | int | yes | All-time message count |

### `composites` (optional — agent may pre-compute or leave to server)

| Field | Type | Required | Description |
|---|---|---|---|
| `signa_rate` | float | no | If agent computed it; server will recompute regardless |
| `signal_force` | float | no | If agent computed |
| `sdrm_score` | float | no | Provisional metric |
| `drift_ratio` | float | no | Precision tier only |

### `raw_telemetry`

Token-level telemetry from the AI platform. Used for verification, audit, and bridge calculations. See [token_metric_bridge.md](token_metric_bridge.md).

| Field | Type | Required | Description |
|---|---|---|---|
| `sessions_count` | int | yes | Sessions in window |
| `turns_total` | int | yes | Conversation turns |
| `tokens_total` | int | yes | All tokens (in + out + cache) |
| `tokens_input_fresh` | int | yes | Non-cached input tokens |
| `tokens_output` | int | yes | Output tokens |
| `tokens_cache_read` | int | yes | Cache hits (read) |
| `tokens_cache_creation` | int | yes | Cache writes |
| `active_minutes_est` | int | yes | Estimated active wall time |

### `tier`

| Value | Meaning |
|---|---|
| `free` | Token-telemetry only submission |
| `precision` | Includes sig_army audit hooks |

### `agent`

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | string | yes | Agent version |
| `ruleset_version` | string | yes | Scoring ruleset the agent was built against |
| `snapshot_hash` | string | yes | SHA-256 of canonicalized payload |
| `public_key` | string | yes | Agent's ed25519 public key |

---

## Signing

The HTTP header `X-Agent-Signature` carries an ed25519 signature of the canonical JSON payload (sorted keys, no whitespace, UTF-8 encoded).

Verification on server:
1. Parse `agent.public_key`
2. Lookup `devices` table by `device_id` to confirm registered key matches
3. Verify signature against canonical payload
4. Verify `snapshot_hash` matches re-computed hash

If any step fails → `status: "rejected", reason: "signature_invalid"`.

---

## Validation rules

| Rule | Action on failure |
|---|---|
| All `core_metrics` present | reject |
| `compression_ratio` in `[0, 1]` | reject |
| `window.end > window.start` | reject |
| `window.end <= now()` | reject |
| `schema_version` is supported | reject (with allowed versions in response) |
| `ruleset_version` is active | reject (with active versions in response) |
| Codename does not exist | server creates new `operators` row |
| Same window already submitted | accept latest, mark previous as superseded |

---

## Canonical example — MO§ES 7-day window

```json
{
  "schema_version": "1.0",
  "codename": "MOSES",
  "device_id": "00000000-0000-0000-0000-000000000001",
  "submitted_at": "2026-05-14T15:00:00Z",
  "window": {
    "type": "7d",
    "start": "2026-05-08T00:00:00Z",
    "end": "2026-05-14T23:59:59Z"
  },
  "platform": {
    "primary": "claude",
    "models": ["claude-opus-4-7", "claude-sonnet-4-6"]
  },
  "core_metrics": {
    "compression_ratio": 0.9694,
    "prompt_complexity": 89.0,
    "cross_thread_score": 96,
    "session_depth_avg": 348.9,
    "token_throughput": 1444112
  },
  "background_metrics": {
    "message_volume": 7327,
    "account_age_days": 119,
    "total_messages_lifetime": 53960
  },
  "composites": {
    "signa_rate": 96.4,
    "signal_force": 12.8
  },
  "raw_telemetry": {
    "sessions_count": 21,
    "turns_total": 7327,
    "tokens_total": 1123252011,
    "tokens_input_fresh": 123246,
    "tokens_output": 3902803,
    "tokens_cache_read": 1084399183,
    "tokens_cache_creation": 34826779,
    "active_minutes_est": 2700
  },
  "tier": "free",
  "agent": {
    "version": "0.1.0",
    "ruleset_version": "1.0",
    "snapshot_hash": "sha256:...",
    "public_key": "ed25519:..."
  }
}
```
