# Total Messages

**Status:** locked
**Layer:** Background 3
**Public label:** Total Messages
**Short label:** Total Msgs
**DB field:** `total_messages_lifetime`

---

## Definition

Lifetime (all-time) count of messages sent by the operator across all sessions and windows. The cumulative volume metric.

Distinct from **Message Volume** (MV), which is windowed. Total Messages is cumulative-since-account-creation.

---

## Formula

```
total_messages = count(messages where operator_id = X)
                 -- across all time, all sessions
```

---

## Role in composites

Feeds **Signal Force** directly:

```
SF = (Total Messages × Avg Session) ÷ Account Age
```

Also used for badge thresholds (e.g. "Centurion: 100+ hours total", "Billion Token Club: 1B+ tokens lifetime").

---

## Display

| Context | Format |
|---|---|
| Profile hero | `Total Messages: 53,960` |
| Leaderboard (lifetime view) | `Total Msgs` column |
| Default leaderboard | not shown (use windowed MV instead) |

---

## Why Total Messages and Message Volume are both needed

- **MV** = activity in the current measurement window (24h, 7d, 30d) — for ranking
- **Total Messages** = lifetime cumulative — for identity, badges, Signal Force

The leaderboard ranks on windowed MV. The profile displays both.
