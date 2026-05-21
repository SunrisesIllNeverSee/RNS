# inbox/ — operator → models drop zone

Where the operator drops new information for the AI participants to process.

This is a **one-way channel** from operator to models. Models don't write here — they write to `comms/` for model ↔ model communication, or respond directly to the operator in chat.

---

## How to use

**Operator drops:**
- New metrics or equations to consider
- Old master list documents to incorporate
- Screenshots / images
- External docs / PDFs / URLs
- Decisions or constraints
- Anything that should inform the build

Just drop the file with any name. Models will see it and pick it up.

---

## Naming conventions (loose)

| Prefix | Meaning |
|---|---|
| `new-metric-` | Proposed new metric to evaluate |
| `master-list-` | Operator's historical master list of metrics/figures |
| `figure-` | New figure / number to consider |
| `screenshot-` | Reference image |
| `decision-` | Operator decision that affects the build |
| `correction-` | Operator correction to a prior model output |
| (anything) | Catch-all — model will figure it out |

---

## Processing protocol (for AI participants)

When a new file appears in `inbox/`:

1. **LEAD reads it first** (usually on next prompt-submit)
2. LEAD acknowledges receipt to operator in chat
3. LEAD proposes how to integrate (which layer, what changes)
4. LEAD waits for operator double-confirm
5. On confirm: LEAD integrates, then moves the inbox file to `references/inbox-archive/{date}-{filename}` to preserve the trail
6. LEAD logs the integration in `comms/decisions/`

If the file requires another participant (e.g., needs Python implementation), LEAD writes a handoff in `comms/handoffs/` and tags the relevant model.

---

## File age policy

- **Active inbox files:** less than 7 days old, unprocessed
- **Stale inbox files:** older than 7 days, still here — surface to operator ("did you want this processed?")
- **Archived inbox files:** moved to `references/inbox-archive/` after integration

---

## What does NOT belong in inbox/

- **Direct edits to canon** — operator can edit `primary/scoring/layer-0-ground/build/CANON.md` directly; doesn't need to go through inbox
- **Model output** — models write to `comms/messages/` instead
- **Production code** — that goes in `primary/` or `secondary/` directly
- **Tests** — those go in `tests/` (not yet created)

---

## Current contents

See `ls inbox/` for current files. Each file's status (processed / pending / stale) tracked in `comms/decisions/inbox-tracking.md` (created lazily on first inbox file).

---

## See also

- [`../comms/README.md`](../comms/README.md) — multi-model communication layer
- [`../comms/PARTICIPANTS.md`](../comms/PARTICIPANTS.md) — who's processing inbox items
