# Message Volume (MV)

**Status:** locked
**Layer:** Background 3
**Public label:** Message Volume
**Short label:** MV
**DB field:** `message_volume`

---

## Definition

Total messages sent by the operator in the measurement window. Raw activity count — both user messages and assistant replies.

MV is a **volume / engagement** background metric. It does not by itself indicate quality.

---

## Formula

```
MV = count(messages where operator_id = X within window)
```

No normalization at the raw layer. Normalization happens when MV is fed into composites.

---

## Score normalization for leaderboard contexts

When MV is used in scoring, apply log normalization:

```
MV_score = min(100, 20 × log10(message_count + 1))
```

This prevents volume-only operators from owning the leaderboard.

---

## Inputs required

- raw message count (per window)
- window definition

---

## Output

- Raw MV: integer
- Normalized MV_score: `[0, 100]`

---

## Why MV is "background"

MV is necessary context but a weak signal alone. It's promoted to the Background layer because:

1. It anchors other metrics (TT, SD interact with MV)
2. It detects gaming attempts (sudden MV spikes with no Compression change = spam)
3. Public leaderboards expect to show "Total Messages" as identity context

But MV alone is not Transmitter-defining. A 10,000-message account with `Compression = 0.45` is a Power-class spammer, not a Transmitter.

---

## Anti-gaming role

When MV rises sharply (>40% above 7d avg) while Compression drops (>10%) and SD drops (>15%), trigger a spam penalty on the operator's composite scores. See [../../architecture/scoring_formula.md](../../architecture/scoring_formula.md) for penalty logic.
