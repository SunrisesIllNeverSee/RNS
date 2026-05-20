# Account Age

**Status:** locked
**Layer:** Background 3
**Public label:** Account Age
**Short label:** Age (or `Acct Age` in tables)
**DB field:** `account_age_days`

---

## Definition

Number of days since the operator first interacted with the underlying AI system (or first registered with SigRank, whichever is earlier and verifiable).

Account Age is **identity context**, not performance.

---

## Formula

```
account_age_days = floor((now - first_seen) / 86400)
```

Display format: humanized — `14d`, `2mo`, `1y 3mo`.

---

## Role in composites

Account Age feeds two specific composites:

1. **Signal Force**: `SF = (Total Msgs × Avg Session) ÷ Account Age` — older accounts produce a lower SF for the same throughput, rewarding new operators who hit high signal fast
2. **Recency decay** (anti-fossilization): see [../../architecture/scoring_formula.md](../../architecture/scoring_formula.md)

---

## Display

| Context | Format |
|---|---|
| Leaderboard column | `14d`, `2mo`, `7mo`, `1y 3mo` |
| Profile hero | `Member: 119 days` |
| Compact | `14d`, `2mo` |

---

## Edge cases

- Day 0 (just joined): show as `0d` or `< 1d`, not as null
- Verified-from-other-platform older accounts: show the older date only after verification
- Anonymous operators without verifiable history: derive from first SigRank snapshot submission
