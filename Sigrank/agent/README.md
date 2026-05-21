# SigRank Local Agent

The on-device collector that reads an operator's local AI platform exports, computes Core 5 metrics, generates a signed snapshot, and publishes to the SigRank API.

> **The leaderboard ingests summaries, proofs, and rankable metrics — not whole private chat archives.**

---

## Design principle

The local agent does the heavy lifting on the operator's machine. The server only receives:

- leaderboard metrics
- snapshot timestamps
- codename / profile id
- class tier
- proof hash
- optional badge / audit metadata

The server does **not** require:

- raw full chats
- raw personal content
- entire archives
- thread dumps

This is a **privacy-preserving telemetry framework**, not a transcript marketplace.

---

## Architecture overview

```
Local source                      (exports, .jsonl files, drop folders)
    ↓
adapters/                         (per-platform: claude, chatgpt, gemini, pi)
    ↓
parsers/                          (normalize → unified session format)
    ↓
features/                         (extract reusable primitives)
    ↓
metrics/                          (compute Core 5 + Background 3)
    ↓
snapshots/                        (build canonical payload)
    ↓
publish/                          (sign + transmit)
    ↓
SigRank API                       (server receives)
    ↓
Server scoring + ranking          (composite, class, leaderboard)
```

See [architecture.md](architecture.md) for the detailed module breakdown.

---

## Supported platforms (planned)

| Platform | Status | Source format |
|---|---|---|
| Claude Code | priority 1 | `.claude/projects/*/*.jsonl` (native) |
| ChatGPT | priority 2 | exported JSON / markdown |
| Cursor | priority 2 | session logs |
| Gemini CLI | priority 3 | session logs |
| Codex | priority 3 | session logs |
| Pi (Inflection) | priority 4 | exported chats |
| Generic JSON | always | user-provided schema |

See [collectors_map.md](collectors_map.md) for adapter specifications.

---

## Implementation choice — Python CLI first

Best MVP path from GPT thread-0369:

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| CLI framework | Typer or Click |
| Schemas | Pydantic |
| Local DB | SQLite |
| Folder monitoring | watchdog |
| HTTP | httpx |
| Terminal UX | rich |
| Crypto signing | pynacl (ed25519) |

**Why Python CLI before Electron / desktop GUI:**
- Lowest friction for technical operators (the priority adopters)
- No installer complexity
- Pipx installable: `pipx install sigrank-agent`
- GUI wrapper can come later via Tauri

---

## Quick start (planned UX)

```bash
# Install
pipx install sigrank-agent

# Initialize (creates ~/.sigrank/ with config, db, keypair)
sigrank init

# Point at a source
sigrank source add claude-code ~/.claude/projects

# Scan and compute
sigrank scan
sigrank compute --window 30d

# Preview before publishing
sigrank preview

# Publish to leaderboard
sigrank publish
```

See [cli_commands.md](cli_commands.md) for the full command spec.

---

## What lives on the operator's machine

```
~/.sigrank/
├── config.yml                    # operator config, codename, server URL
├── keypair.json                  # device public/private key (ed25519)
├── db.sqlite                     # local cache: sessions, features, snapshots
├── imports/                      # drop folder for source files
├── cache/                        # parsed sessions, computed features
└── exports/
    ├── snapshots/                # generated payloads (timestamped)
    └── reports/                  # local PDF reports if enabled
```

**Nothing in this folder leaves the machine** except the signed snapshot payload, which contains only the metrics defined in [../scoring/architecture/snapshot_payload.md](../scoring/architecture/snapshot_payload.md).

---

## What the agent does NOT do

- Does not upload raw conversation text
- Does not require platform API keys
- Does not run continuously in the background (cron-triggered or manual)
- Does not store telemetry on the server beyond what's in `snapshot_payload`
- Does not auto-submit without operator confirmation (default config)

---

## Trust model

1. Operator runs `sigrank init` → generates local ed25519 keypair
2. First snapshot publish registers the public key with the server (creates a `devices` row)
3. Subsequent publishes are signed with the private key — server verifies against the registered public key
4. Operator can revoke a device via the web app
5. Multi-device operators register each agent separately (one per machine)

See [../scoring/architecture/api_spec.md](../scoring/architecture/api_spec.md) for the authentication flow.

---

## Open questions

1. Where does the Python CLI live in this repo long-term? `Sigrank/agent/` or its own subpackage?
2. Should we ship Claude Code as a built-in adapter from day one (it's the obvious starting point)?
3. Do we want a Codex / Cursor CLI extension before or after the Python CLI is stable?
4. Public key registration — auto-trust on first submission or require email verification?

---

## Status

**Not yet implemented.** This is the specification document set. Implementation begins after:

1. Components are reviewed (ultrareview)
2. Architecture is approved
3. The scoring engine spec is locked

The HTML prototypes in [../prototypes/](../prototypes/) provide visual reference. The components in [../../Sigrank/components/sigrank/](../../Sigrank/components/sigrank/) provide the UI building blocks.
