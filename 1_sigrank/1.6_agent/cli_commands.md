# CLI Commands

The full command surface for the SigRank local agent.

---

## Command overview

```bash
sigrank init                    # initialize ~/.sigrank/
sigrank source add <type> <path>  # register a source
sigrank source list             # list configured sources
sigrank source remove <name>    # remove a source
sigrank scan [--source <name>]  # parse sources into local DB
sigrank compute --window <w>    # compute metrics for window
sigrank preview                 # show current snapshot before publish
sigrank publish                 # sign and send to API
sigrank history                 # show local publish history
sigrank verify                  # re-verify last snapshot signature
sigrank config <key> [<value>]  # get/set config values
sigrank version                 # show agent version + ruleset compat
```

---

## `sigrank init`

First-run setup.

**What it does:**
1. Creates `~/.sigrank/` directory
2. Generates ed25519 keypair → `~/.sigrank/keypair.json`
3. Prompts for codename (must be unique, 3-32 chars, alphanumeric + dash/underscore)
4. Prompts for primary platform (claude / chatgpt / gemini / pi / multi)
5. Prompts for server URL (default `https://api.sigrank.io`)
6. Initializes SQLite DB at `~/.sigrank/db.sqlite`
7. Creates `imports/`, `cache/`, `exports/` subfolders

**Output:**
```
✓ Initialized ~/.sigrank/
✓ Generated device keypair: ed25519:abc123...
✓ Codename: TransVaultOrigin
✓ Server: https://api.sigrank.io
✓ Ready. Run `sigrank source add` to point at a data source.
```

---

## `sigrank source add <type> <path>`

Register a source for the agent to read.

**Types:** `claude-code`, `chatgpt`, `cursor`, `gemini`, `codex`, `pi`, `generic-json`

**Examples:**
```bash
sigrank source add claude-code ~/.claude/projects
sigrank source add chatgpt ~/Downloads/openai-export
sigrank source add generic-json ./my-custom-exports
```

**What it does:**
1. Resolves path
2. Detects whether the adapter recognizes the path
3. Performs a dry scan to estimate session count
4. Asks for confirmation
5. Stores in `sources` table

---

## `sigrank source list`

```
NAME              TYPE          PATH                          SESSIONS  LAST SCAN
my-claude         claude-code   ~/.claude/projects            97        2026-05-14 14:00
chatgpt-export    chatgpt       ~/Downloads/openai-export     312       2026-05-12 09:00
```

---

## `sigrank scan [--source <name>] [--since <date>]`

Parse sources into the local DB.

**What it does:**
1. For each (or specified) source, run the adapter
2. Read all session files
3. Normalize to `Session` / `Message` models
4. Compute message and session features
5. Update `feature_message`, `feature_session` tables

**Options:**
- `--source <name>` — only scan one source
- `--since <date>` — only scan sessions after this date
- `--force` — re-scan even if features already computed

**Output (rich progress bar):**
```
Scanning my-claude:        [████████████████] 97/97 sessions
  Messages parsed: 12,847
  Features extracted: 12,847
  Session features: 97
  Duration: 8.2s

Scanning chatgpt-export:   [████████████████] 312/312 sessions
  ...

✓ Scan complete. Run `sigrank compute --window 30d` next.
```

---

## `sigrank compute --window <w>`

Compute metrics for a measurement window.

**Window types:** `today`, `7d`, `30d`, `90d`, `all_time`

**Examples:**
```bash
sigrank compute --window 30d
sigrank compute --window all_time
sigrank compute --window 7d --start 2026-05-08
```

**What it does:**
1. Aggregate session features over the window
2. Compute Core 5 metrics
3. Compute Background 3 metrics
4. Compute Signal Force composite
5. Store in `snapshot_local` table

**Output:**
```
Window: 30d  (2026-04-14 → 2026-05-14)

Core 5:
  Compression Ratio    : 0.9694    [TRANSMITTER]
  Prompt Complexity    :   89.0
  Cross-Thread Score   :   96
  Session Depth (avg)  :  348.9
  Token Throughput     :  1.44M tok/min

Background 3:
  Message Volume       : 7,327
  Account Age          : 119 days
  Total Messages       : 53,960

Composites:
  Signal Force         : 12.8
  (SIGNA RATE computed server-side)

Snapshot ID: 9337b23-0001
Status: ready to publish
```

---

## `sigrank preview`

Display the most recent computed snapshot in full, before publishing.

**Output:**
```
═══════════════════════════════════════════════
  SIGRANK SNAPSHOT — PREVIEW
═══════════════════════════════════════════════

Codename:    TransVaultOrigin
Device:      550e8400-...
Window:      30d  (2026-04-14 → 2026-05-14)
Platform:    claude (multi: claude-opus-4-7, claude-sonnet-4-6)
Generated:   2026-05-14 14:00:00 UTC

CORE 5
  Compression Ratio    0.9694  ████████████████████  →  TRANSMITTER
  Prompt Complexity    89.0    █████████████████░░░
  Cross-Thread         96      ███████████████████░
  Session Depth        348.9   (well above max bucket)
  Token Throughput     ~100    (log-capped)

BACKGROUND
  Message Volume       7,327
  Account Age          119 days
  Total Messages       53,960

RAW TELEMETRY
  Sessions             21
  Turns                7,327
  Total Tokens         1.12B
  Fresh Input          123,246
  Output               3.90M
  Cache Read           1.08B
  Cache Creation       34.8M

PAYLOAD HASH:  sha256:abc123...
SIGNATURE:     (will sign at publish)
RULESET:       1.0
SCHEMA:        1.0

[p]ublish  [c]ancel  [s]how raw json
```

---

## `sigrank publish`

Sign and transmit the most recent snapshot to the API.

**What it does:**
1. Load most recent unpublished snapshot from `snapshot_local`
2. Canonicalize JSON (sorted keys, no whitespace)
3. Sign with device private key (ed25519)
4. POST to `/api/v1/snapshots` with `X-Agent-Signature` header
5. Receive response, store in `publish_log`
6. Mark snapshot as `published`
7. Display server response

**Output (success):**
```
Publishing snapshot 9337b23-0001...
  Signing       ✓
  Posting       ✓ (1.2s)
  Validated     ✓

Server response:
  Submission ID:     7b3a-...
  Status:            received
  Scoring ETA:       ~30s
  Initial rank:      computing...

✓ Published. Visit https://sigrank.io/u/TransVaultOrigin in ~30s.
```

**Output (error):**
```
Publishing snapshot 9337b23-0001...
  Signing       ✓
  Posting       ✗

Server rejected:
  Reason: schema_outdated
  Detail: snapshot schema_version 1.0 not supported.
          Active versions: [1.1, 1.2]

Run `sigrank version --upgrade` to update.
```

---

## `sigrank history`

Show local publish history.

```
WHEN                 WINDOW   COMPRESSION  CLASS         RANK
2026-05-14 14:00     30d      0.9694       TRANSMITTER   #1
2026-05-07 09:00     30d      0.9512       TRANSMITTER   #1
2026-04-30 09:00     30d      0.9388       TRANSMITTER   #2
2026-04-23 09:00     30d      0.9201       TRANSMITTER   #3
```

---

## `sigrank verify`

Re-verify the signature and hash of the most recent published snapshot. Used for debugging / audit.

---

## `sigrank config <key> [<value>]`

Get or set configuration values.

```bash
sigrank config codename                    # display
sigrank config server_url https://...     # set
sigrank config publish.auto_confirm true  # set nested
sigrank config --list                      # show all
```

**Common keys:**
- `codename`
- `server_url`
- `publish.auto_confirm` (bool)
- `scan.parallelism` (int)
- `publish.require_confirm` (bool, default true)

---

## `sigrank version`

```
sigrank-agent      0.1.0
schema_version     1.0
ruleset_supported  1.0
python             3.11.4
platform           darwin / arm64
```

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General error |
| 2 | Adapter error (source unreachable / parse failed) |
| 3 | DB error (SQLite locked / corrupt) |
| 4 | Network error |
| 5 | Server rejection |
| 6 | Configuration error |
| 7 | User cancelled |

---

## Environment variables

| Variable | Purpose |
|---|---|
| `SIGRANK_HOME` | Override `~/.sigrank/` location |
| `SIGRANK_SERVER` | Override server URL |
| `SIGRANK_TIER` | Override tier (`free` / `precision`) |
| `SIGRANK_LOG_LEVEL` | `debug` / `info` / `warn` / `error` |
| `SIGRANK_NO_COLOR` | Disable rich color output |
