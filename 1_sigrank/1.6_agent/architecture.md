# Agent Architecture

Detailed module layout and data flow for the SigRank local agent.

---

## Module structure

```
sigrank-agent/
├── pyproject.toml
├── README.md
├── src/
│   ├── sigrank/
│   │   ├── __init__.py
│   │   ├── cli/                  # Typer/Click commands
│   │   │   ├── __init__.py
│   │   │   ├── init.py
│   │   │   ├── source.py
│   │   │   ├── scan.py
│   │   │   ├── compute.py
│   │   │   ├── preview.py
│   │   │   └── publish.py
│   │   │
│   │   ├── adapters/             # platform-specific source readers
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Adapter ABC
│   │   │   ├── claude_code.py    # parses ~/.claude/projects/*.jsonl
│   │   │   ├── chatgpt.py        # parses exported JSON / markdown
│   │   │   ├── cursor.py
│   │   │   ├── gemini.py
│   │   │   ├── codex.py
│   │   │   ├── pi.py
│   │   │   └── generic_json.py   # user-defined schema
│   │   │
│   │   ├── parsers/              # normalize → unified format
│   │   │   ├── __init__.py
│   │   │   ├── session.py        # Session model
│   │   │   ├── message.py        # Message model
│   │   │   └── normalize.py
│   │   │
│   │   ├── features/             # reusable feature extraction
│   │   │   ├── __init__.py
│   │   │   ├── message_features.py
│   │   │   ├── session_features.py
│   │   │   ├── rolling_features.py
│   │   │   └── token_features.py
│   │   │
│   │   ├── metrics/              # Core 5 + Background 3 computation
│   │   │   ├── __init__.py
│   │   │   ├── compression.py    # Compression Ratio
│   │   │   ├── prompt_complexity.py
│   │   │   ├── cross_thread.py
│   │   │   ├── session_depth.py
│   │   │   ├── token_throughput.py
│   │   │   ├── background.py     # MV, Age, Total
│   │   │   └── composites.py     # Signal Force, optional SIGNA RATE preview
│   │   │
│   │   ├── snapshots/            # canonical payload builder
│   │   │   ├── __init__.py
│   │   │   ├── builder.py
│   │   │   ├── canonicalize.py   # deterministic JSON serialization
│   │   │   └── hash.py
│   │   │
│   │   ├── publish/              # sign + transmit
│   │   │   ├── __init__.py
│   │   │   ├── sign.py           # ed25519
│   │   │   ├── http_client.py
│   │   │   └── retry.py
│   │   │
│   │   ├── db/                   # SQLite local cache
│   │   │   ├── __init__.py
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   └── store.py
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py       # operator config, server URL
│   │   │   └── keypair.py        # device keypair management
│   │   │
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── preview.py        # rich terminal preview
│   │       └── progress.py
│   │
│   └── tests/
│
└── data/
    ├── imports/                  # user drops files here
    ├── cache/                    # parsed sessions
    └── exports/                  # generated snapshots
```

---

## Data flow

### Phase 1 — Source ingestion

```
User configures source:
  $ sigrank source add claude-code ~/.claude/projects

  ↓

adapter detects platform
  → reads .jsonl files
  → normalizes into Session/Message models
  → stores raw in db.sqlite (sessions, messages tables)
```

### Phase 2 — Feature extraction

```
$ sigrank scan

  ↓

For each session:
  → extract message features (length, role, timestamp, refs)
  → extract session features (depth, complexity sub-scores, callbacks)
  → extract token features (input/output/cache split)
  → write to db.sqlite (feature_message, feature_session tables)
```

### Phase 3 — Metric computation

```
$ sigrank compute --window 30d

  ↓

For the window:
  → roll up session features
  → compute Compression Ratio
  → compute Session Depth (avg)
  → compute Prompt Complexity (composite of sub-scores)
  → compute Cross-Thread Referencing
  → compute Token Throughput
  → compute Background 3
  → write to db.sqlite (snapshot_local table)
```

### Phase 4 — Snapshot generation

```
$ sigrank preview

  ↓

Build canonical payload (per snapshot_payload.md schema)
  → display in terminal (rich formatting)
  → operator inspects metrics
  → operator confirms or cancels
```

### Phase 5 — Publish

```
$ sigrank publish

  ↓

Sign payload (ed25519 with device private key)
  → POST to /api/v1/snapshots
  → server validates + scores + ranks
  → response includes submission_id, scoring_eta, current rank
  → save local copy to data/exports/snapshots/<timestamp>.json
  → write to publish_log table
```

---

## Session normalization format

Every adapter produces this unified structure:

```python
@dataclass
class Session:
    session_id: str
    source_type: str       # claude_code, chatgpt, etc.
    platform: str          # claude, chatgpt, gemini, etc.
    started_at: datetime
    ended_at: datetime
    messages: list[Message]
    thread_refs: list[str]
    metadata: dict

@dataclass
class Message:
    message_id: str
    session_id: str
    role: str              # user, assistant, system
    content: str           # raw text (for local feature extraction)
    token_count: int
    timestamp: datetime
    parent_message_id: str | None
    references: list[str]  # other message IDs / session IDs
```

**Important:** raw `content` lives only in local SQLite. It is never serialized into the snapshot payload that goes to the server.

---

## Feature extraction layers

### Message features

Per-message, computed once at scan time:
- `length_chars`, `length_tokens`
- `role`
- `is_question`, `is_directive`
- `has_code_block`, `code_block_count`
- `references_prior_thread` (boolean)
- `instruction_layers` (count of nested asks)
- `repetition_marker` (does this echo prior content)
- `structural_markers` (count of headers, lists, ordered sections)

### Session features

Per-session aggregates:
- `message_count`, `user_message_count`, `assistant_message_count`
- `total_tokens`, `input_tokens`, `output_tokens`
- `session_depth_max` (longest chain)
- `session_depth_avg`
- `complexity_score_avg`
- `cross_thread_refs_count`, `memory_callbacks_count`
- `duration_minutes`

### Rolling features (per window)

Aggregates across multiple sessions in a time window:
- `sessions_in_window`
- `total_messages`, `total_tokens`
- `avg_session_depth`, `max_session_depth`
- `avg_complexity`, `max_complexity`
- `unique_thread_refs`
- `active_days_count`, `streak_days`

---

## Local DB schema (SQLite)

Mirrors the server schema but local-only:

```sql
-- Sources configured
CREATE TABLE sources (
  id INTEGER PRIMARY KEY,
  name TEXT,
  adapter TEXT,
  path TEXT,
  added_at DATETIME
);

-- Raw sessions
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  source_id INTEGER,
  platform TEXT,
  started_at DATETIME,
  ended_at DATETIME,
  metadata_json TEXT
);

-- Raw messages (content kept local only)
CREATE TABLE messages (
  message_id TEXT PRIMARY KEY,
  session_id TEXT,
  role TEXT,
  content TEXT,
  token_count INTEGER,
  timestamp DATETIME,
  parent_message_id TEXT
);

-- Computed message features
CREATE TABLE feature_message (
  message_id TEXT PRIMARY KEY,
  features_json TEXT,
  computed_at DATETIME
);

-- Computed session features
CREATE TABLE feature_session (
  session_id TEXT PRIMARY KEY,
  features_json TEXT,
  computed_at DATETIME
);

-- Generated snapshots (local cache before publish)
CREATE TABLE snapshot_local (
  snapshot_id TEXT PRIMARY KEY,
  window_type TEXT,
  window_start DATETIME,
  window_end DATETIME,
  payload_json TEXT,
  hash TEXT,
  created_at DATETIME,
  published BOOLEAN DEFAULT 0
);

-- Publish log
CREATE TABLE publish_log (
  id INTEGER PRIMARY KEY,
  snapshot_id TEXT,
  submission_id TEXT,
  published_at DATETIME,
  status TEXT,
  server_response_json TEXT
);

-- Settings (operator config)
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT
);
```

---

## Error handling

| Failure mode | Behavior |
|---|---|
| Adapter can't read source | Log + skip, continue with other sources |
| Parser fails on a session | Mark session as `parse_failed`, continue |
| Metric computation fails | Mark feature as null, compute others |
| Network failure on publish | Retry with backoff, queue for next attempt |
| Server rejects (signature) | Halt, surface error to operator |
| Server rejects (rate limit) | Display next-allowed-time, queue |

---

## Concurrency model

The CLI is single-threaded per command. The agent is **not** a long-running daemon. Each invocation is:

1. Open SQLite
2. Do work
3. Close cleanly

Background scheduling is left to OS cron / launchd / Task Scheduler:

```bash
# Example crontab
0 */6 * * * /usr/local/bin/sigrank scan && /usr/local/bin/sigrank publish
```

This is intentional. Daemons add complexity without value for this workload.
