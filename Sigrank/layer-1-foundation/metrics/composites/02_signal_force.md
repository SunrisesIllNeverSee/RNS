# Signal Force (SF)

**Status:** locked — formula confirmed from v2 Signal Codex
**Layer:** Composite (advanced)
**Public label:** Signal Force
**Short label:** SF (or `SigForce` in DB)
**DB field:** `signal_force`

---

## Definition

Sustained throughput and resilience over time. Measures the operator's ability to maintain meaningful output **per day of account life**.

Signal Force is the **sustained productivity** composite. It rewards operators who consistently produce signal over long periods rather than burning out after one streak.

---

## Confirmed formula

From the v2 `signal_codex_basic.html` prototype:

```
SF = (Total Messages × Average Session Depth) ÷ Account Age (days)
```

Or in DB field terms:

```
signal_force = (total_messages_lifetime × session_depth_avg) / account_age_days
```

---

## Example calibration

| Operator | Total Msgs | Avg SD | Age | SF |
|---|---:|---:|---:|---:|
| A (newer, intense) | 8,700 | 4.6 | 14 | 2,858 |
| B (steady, year+) | 53,960 | 5.0 | 365 | 739 |
| C (volume, shallow) | 30,000 | 1.8 | 90 | 600 |
| D (Transmitter sustained) | 18,450 | 26 | 90 | 5,330 |

---

## Lineage notes

Signal Force may have been renamed to **Sig Alpha** in later sessions (paired with Drift Ratio → Sig Delta). Lineage unresolved.

For now, **Signal Force / SF** is the canonical name.

See [../lineage/naming_drift.md](../lineage/naming_drift.md).

---

## Inputs required

- `total_messages_lifetime` (background metric)
- `session_depth_avg` (Core 5 — SD)
- `account_age_days` (background metric)

All three are required. No fallback.

---

## Output

- Raw SF: float (can be very large for prolific operators)
- Display: rounded to nearest integer
- Range: theoretically `[0, ∞)`, practically `[0, 10000]` for most operators

---

## Display

| Context | Format |
|---|---|
| Cross-Platform Leaderboard | `Signal Force` column with raw value |
| Profile metric block | `SF: 12.8` (normalized — see below) |
| Mobile compact | `SF` |

**Normalized SF score** for leaderboard display (so values stay in a comparable range):

```
SF_score = min(100, 20 × log10(SF + 1))
```

This puts SF into `[0, 100]` for ranking. Raw SF is preserved for analytics.

---

## Why account age divisor matters

Without dividing by age, Signal Force would just favor old accounts. With age in the denominator, a 2-week-old operator with intense sustained signal can match or beat a year-old operator's SF.

This is the metric that **rewards new operators who arrive hot**.
