# Participants Registry

Active and historical participants in the rns-sigrank build.

---

## Active participants

| Participant ID | Model | Environment | Role | Scope | Started |
|---|---|---|---|---|---|
| **VSClaude-OPUS47-LEAD** | claude-opus-4-7 | Claude Code (VS Code IDE extension) | Build lead | Foundation lock + scaffolding | 2026-05-19 |

---

## Historical participants

(populated as participants join and rotate off)

---

## Identity tuple

```
{ENVIRONMENT}-{MODEL}-{ROLE}
```

**Environment** is where the model is running:
- `VSClaude` — Claude Code (VS Code IDE extension)
- `CCCLI` — Claude Code CLI (terminal-only)
- `Codex` — OpenAI Codex CLI
- `CursorComposer` — Cursor Composer (multi-model)
- `CursorChat` — Cursor inline chat
- `GeminiCLI` — Gemini CLI (Google)
- `ContinueDev` — Continue.dev IDE extension
- `WebClaude` — Anthropic claude.ai web
- `WebChatGPT` — OpenAI chatgpt.com web
- `OperatorTool` — generic local tool the operator drove

**Model** is the model ID:
- Claude: `OPUS47`, `OPUS46`, `SONNET46`, `HAIKU45`
- GPT: `GPT55`, `GPT54`
- Gemini: `31PRO`, `25PRO`
- DeepSeek: `V4`
- GLM: `GLM51`
- Kimi: `K26`
- Composer: `COMPOSER2`

**Role** is what they're doing in this build:
- `LEAD` — current build lead (one at a time)
- `CONTRIBUTOR` — actively building
- `REVIEWER` — reviewing only, no edits
- `TESTER` — running tests, no spec edits
- `OPERATOR` — the human operator (special — does not participate as peer, directs from above)

---

## Authority during foundation lock

Until the operator declares foundation locked:

- **LEAD** authority:
  - Propose changes to spec docs
  - Scaffold new files/folders
  - Move files via `git mv`
  - Write decision log entries
  - Cannot commit without operator double-confirm
  - Cannot change `RS.xx` (proprietary scoring parameters) — always operator-owned

- **CONTRIBUTOR** authority:
  - Implement code per spec (no spec changes)
  - Run tests
  - Lock specific files in `5_comms/locks/current.json` while editing
  - Hand off via `5_comms/handoffs/`

- **REVIEWER** authority:
  - Read everything
  - Propose feedback via `5_comms/messages/`
  - Cannot edit

- **TESTER** authority:
  - Read everything
  - Write to `tests/` and `5_comms/test-reports/`
  - Cannot edit specs or production code

---

## Joining protocol

When a new participant joins:

1. Operator drops their info in `_inbox/new-participant-{id}.md`
2. LEAD reviews, confirms identity tuple
3. LEAD adds row to "Active participants" table above
4. LEAD writes welcome message in `5_comms/messages/{date}/{time}-LEAD-to-{new}.md` with:
   - Their scope
   - Locks they should claim
   - Open questions for them to consider
   - Authority limits
5. New participant writes their first heartbeat to `5_comms/active/{participant_id}.json`

---

## Exit protocol

When a participant rotates off:

1. Write `5_comms/handoffs/` document if work is incomplete
2. Move heartbeat from `5_comms/active/` to `5_comms/active/_history/`
3. Release all locks in `5_comms/locks/current.json`
4. Move row from "Active" to "Historical" table here, with `ended_at` date
5. Final message in `5_comms/messages/` summarizing what was completed

---

## Special: the operator

The human operator is identified by tuple but does NOT participate as a peer.

```
Operator-HUMAN-OWNER
```

Operator:
- Does not write heartbeats (they're always-on)
- Does not claim locks (they have implicit authority over all files)
- Drops new info in `_inbox/` instead of `5_comms/messages/`
- Receives status reports from LEAD via direct chat (this conversation), not via comms files
- Is the only one who can:
  - Commit (after double-confirm)
  - Change RS.xx parameters
  - Promote participants between roles
  - Override locks

The comms folder exists to coordinate AI participants. The operator coordinates them.
