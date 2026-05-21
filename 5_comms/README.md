# Comms — internal multi-model project communication

The file-based communication layer for multiple AI models collaborating on rns-sigrank.

When other models (GPT, Gemini, Codex, future Claude versions, etc.) join the build, they coordinate through this folder. No live server required — every model can read/write the repo directly.

---

## Identity model

Each participant is identified by a tuple:

```
{ENVIRONMENT}-{MODEL}-{ROLE}
```

Examples:
- `VSClaude-OPUS47-LEAD` — Claude Opus 4.7 in VS Code, current lead
- `Codex-GPT55-CONTRIBUTOR` — GPT-5.5 via Codex CLI
- `Gemini-CLI-31PRO-REVIEWER` — Gemini 3.1 Pro via Gemini CLI
- `CursorComposer-GLM51-CONTRIBUTOR` — GLM-5.1 via Cursor Composer

See [`PARTICIPANTS.md`](PARTICIPANTS.md) for active participant registry.

---

## Folder structure

```
comms/
├── README.md                 ← this file
├── PARTICIPANTS.md           ← who's actively working
│
├── active/                   ← heartbeat files, one per active session
│   └── {participant_id}.json
│
├── messages/                 ← async message log
│   └── YYYY-MM-DD/
│       └── HH-MM-{from}-to-{to}.md
│
├── handoffs/                 ← work transfer documents
│   └── YYYY-MM-DD-{from}-to-{to}-{topic}.md
│
├── decisions/                ← decision log per layer
│   ├── layer-0-decisions.md
│   ├── layer-1-decisions.md
│   ├── layer-2-decisions.md
│   ├── layer-3-decisions.md
│   └── cross-layer-decisions.md
│
└── locks/                    ← file-level coordination
    └── current.json          ← which participant has which file claimed
```

---

## Heartbeat protocol

When a model starts working:

1. Write `5_comms/active/{participant_id}.json`:

```json
{
  "participant_id": "VSClaude-OPUS47-LEAD",
  "started_at": "2026-05-21T14:23:00Z",
  "scope": "Layer 0 foundation + comms scaffolding",
  "current_file": "1_sigrank/1.1_layer-0-ground/build/CANON.md",
  "last_heartbeat": "2026-05-21T14:45:12Z"
}
```

2. Update `last_heartbeat` every ~5 minutes during active work
3. On finish, move file to `5_comms/active/_history/{participant_id}-{timestamp}.json` (deactivate)

If `last_heartbeat` is >1 hour old, treat the participant as offline (could be force-killed, network drop, etc.).

---

## Message protocol

Messages are markdown files with a header:

```markdown
---
from: VSClaude-OPUS47-LEAD
to: all
when: 2026-05-21T14:30:00Z
re: Layer 0 scaffolding complete
priority: normal
---

The Layer 0 foundation is now scaffolded with:
- build/ (CANON, SOURCE_DATA, ROOT_NUMBERS, MOSES_REFERENCE)
- guidance/ (CONSERVATION_LAW, LINEAGE, TOKENS_PER_WORD)

Awaiting operator double-confirm before committing.

Open question for whoever picks up Layer 1: should Drift Ratio sub-extractors
use sentence-transformers or OpenAI embeddings as default?
```

Save to `messages/2026-05-21/14-30-VSClaude-to-all.md`.

---

## Handoff protocol

When one model passes work to another:

1. Write `5_comms/handoffs/{date}-{from}-to-{to}-{topic}.md`:

```markdown
---
from: VSClaude-OPUS47-LEAD
to: Codex-GPT55-CONTRIBUTOR
when: 2026-05-21T15:00:00Z
topic: Layer 2 mechanics — billing implementation
---

## What's done
- Layer 2 billing specs: stripe_integration.md, webhook_handling.md, subscription_states.md
- Layer 3 stripe_checkout_ui.md
- Layer 1 reward tier definitions

## What's needed
- Implement Supabase Edge Function for /api/v1/billing/stripe-webhook
- Migrate DB schema: add subscriptions, webhook_events, audit_log columns
- Write Python tests against Stripe test mode

## Pickup files
- Specs: 1_sigrank/1.3_layer-2-mechanics/billing/*.md
- Schema: 1_sigrank/1.3_layer-2-mechanics/db_schema.md

## Open questions
- Should Pro yearly include a discount or just match monthly × 12?
- Grace period: 7 days locked in spec — confirm OK?

## Authority limits
- Do NOT change RS.xx parameters
- Do NOT commit without operator double-confirm
- Lock files in 5_comms/locks/current.json before editing
```

2. Update `5_comms/locks/current.json` to remove old locks (releasing files)
3. Receiving model reads handoff, picks up, claims their own locks

---

## Decision log protocol

Major decisions get logged per layer:

```markdown
## 2026-05-21 · RN.13 hidden by default

**Decided by:** operator + VSClaude-OPUS47-LEAD
**Layer:** L0
**Decision:** RN.13 (work_classification: auto/operator/hybrid) is captured but hidden from public surfaces in MVP. Optional tag for future filtering.
**Reasoning:** Operator wants the data captured for interpretation but not surfaced as a leaderboard filter yet.
**Affects:** ROOT_NUMBERS.md, SOURCE_DATA.md, snapshot_payload.md
**Reversal cost:** Low — just expose the field
```

Append to `5_comms/decisions/layer-{N}-decisions.md`.

---

## Lock protocol

`5_comms/locks/current.json` prevents conflicting edits:

```json
{
  "1_sigrank/1.1_layer-0-ground/build/CANON.md": {
    "claimed_by": "VSClaude-OPUS47-LEAD",
    "claimed_at": "2026-05-21T14:23:00Z",
    "expires_at": "2026-05-21T16:23:00Z",
    "reason": "adding RN.13 hidden flag"
  }
}
```

Before editing any file, check locks. If locked by another participant, message them. After editing, release the lock.

Locks expire after 2 hours of inactivity — preventing dead-session locks from blocking work.

---

## Operator authority

The operator is the **single source of truth**. All participants:

- Propose, don't commit, until operator double-confirms
- Surface open questions to the operator before assuming
- Use `_inbox/` for the operator to drop new info (operator → models)
- Use this `5_comms/` for model ↔ model communication

The operator does NOT participate in 5_comms/ as a peer — they direct from above.

---

## Hooks (future automation)

The Claude Code hook system (settings.json) can automate parts of this:

| Hook | What it would do |
|---|---|
| SessionStart | Write to `active/{participant_id}.json` |
| Stop | Move active file to `_history/`, release locks |
| UserPromptSubmit | Check `_inbox/` for new messages, surface to model |
| PreToolUse (Edit/Write) | Check `locks/current.json` for conflicts |

For now, this is manual / convention-based. Hooks can be added when the comms layer activates.

Reference patterns: `~/Desktop/claude-switchboard-plugin/builder/target-plugin/hooks/scripts/` already implements this for multi-Claude sessions; we'd adapt for multi-model.

---

## See also

- [`PARTICIPANTS.md`](PARTICIPANTS.md) — active participant registry
- [`decisions/`](decisions/) — decision logs per layer
- [`../_inbox/README.md`](../_inbox/README.md) — operator → models channel
- [`../MODERATOR_NOTE.md`](../MODERATOR_NOTE.md) — moderator framing
