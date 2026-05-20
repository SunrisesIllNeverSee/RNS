# SigRank Metric Stack

Recovered from GPT thread-0369 (2026-03-09 through 2026-03-10) and consolidated against the v1/v2 HTML prototype evidence. This document indexes the full operator metric stack.

---

## Three layers

```
Core 5         → direct operator performance signals
Background 3   → identity / normalization context
Composites     → derived flagship + advanced metrics
```

---

## Core 5 — operator performance signals

| # | Metric | Short | Status | File |
|---|---|---|---|---|
| 1 | Compression Ratio | S/Nr | locked (formula confirmed) | [core_5/01_compression_ratio.md](core_5/01_compression_ratio.md) |
| 2 | Prompt Complexity | PC | locked | [core_5/02_prompt_complexity.md](core_5/02_prompt_complexity.md) |
| 3 | Cross-Thread Referencing | CT | locked | [core_5/03_cross_thread_referencing.md](core_5/03_cross_thread_referencing.md) |
| 4 | Session Depth | SD | locked | [core_5/04_session_depth.md](core_5/04_session_depth.md) |
| 5 | Token Throughput | TT | locked | [core_5/05_token_throughput.md](core_5/05_token_throughput.md) |

The Core 5 are the **inputs** to the leaderboard. Every submission must include all five.

---

## Background 3 — identity / normalization layer

| # | Metric | Status | File |
|---|---|---|---|
| 6 | Message Volume | locked | [background_3/01_message_volume.md](background_3/01_message_volume.md) |
| 7 | Account Age | locked | [background_3/02_account_age.md](background_3/02_account_age.md) |
| 8 | Total Messages | locked | [background_3/03_total_messages.md](background_3/03_total_messages.md) |

Background metrics normalize the Core 5 and feed certain composites (notably Signal Force).

---

## Composites — derived metrics

| # | Metric | Role | Status | File |
|---|---|---|---|---|
| 9 | **SIGNA RATE** | Flagship / center prestige | locked as flagship | [composites/01_signa_rate.md](composites/01_signa_rate.md) |
| 10 | SDRM | Multi-axis resonance | provisional | [composites/02_sdrm.md](composites/02_sdrm.md) |
| 11 | Signal Force | Sustained throughput | locked (formula confirmed) | [composites/03_signal_force.md](composites/03_signal_force.md) |
| 12 | Drift Ratio | Semantic drift / anti-waterlog | provisional | [composites/04_drift_ratio.md](composites/04_drift_ratio.md) |

**SIGNA RATE** is the WN8 equivalent — the single number that owns the profile hero block and drives the leaderboard rank.

---

## Status legend

- **locked** — definition, inputs, formula, and output range are stable
- **provisional** — definition stable, formula or implementation may still shift
- **deprecated** — historical only, do not implement
- **unresolved** — lineage or naming still under recovery

---

## What predates what

The `.87xx` compression score predates explicit token analysis by approximately one month (July 2025 → August 2025). See [lineage/compression_snr_history.md](lineage/compression_snr_history.md) for the archaeology of this metric.

Naming variants and renames (Transmitter Composite → SIGNA RATE, SDOT → SDRM, Drift Ratio → Sig Delta?, Signal Force → Sig Alpha?) are tracked in [lineage/naming_drift.md](lineage/naming_drift.md).

---

## Open questions

1. Is **SDOT** the same lineage as **SDRM** or a separate metric? (currently kept separate)
2. Are **Drift Ratio / Sig Delta** and **Signal Force / Sig Alpha** rename pairs or distinct?
3. Final database field names — see [architecture/db_schema.md](../architecture/db_schema.md)
4. Whether composite Drift Ratio is in MVP or Phase 2

---

## How this connects to the new token model

The Core 5 were originally designed for message/word-level extraction (the sig_army engine). The new **token-economic submission model** uses the metrics that AI platforms already generate as proxies — see [architecture/token_metric_bridge.md](../architecture/token_metric_bridge.md) for the full mapping.

The two systems coexist:
- **Free tier**: submit token telemetry → SigRank scores you immediately
- **Precision tier**: feed raw sessions through sig_army → deeper signal classification
