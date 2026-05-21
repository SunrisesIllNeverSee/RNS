# SigRank Metric Stack

Recovered from GPT thread-0369 (2026-03-09 through 2026-03-10) and consolidated against the v1/v2 HTML prototype evidence. This document indexes the full operator metric stack.

---

## Three layers + extras

```
Core 5         → direct operator performance signals
Background 3   → identity / normalization context
Big 3          → derived composites inside the 11 core (flagship + SDOT + SDRM)
Extras         → tracked metrics outside the 11 core (Signal Force, Drift Ratio)
```

**11 core = Core 5 (5) + Background 3 (3) + Big 3 (3).** Extras live alongside but do not count toward the 11 and do not feed SIGNA RATE.

> **Corrected 2026-05-21.** Prior commit `2c3b0be` (Claude Sonnet 4.6) incorrectly retired SDOT and SDRM and demoted Sig Delta / Sig Alpha aliases. Both reversals were unauthorized. The stack below is the corrected current state.

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

Background metrics normalize the Core 5 and feed extras like Signal Force.

---

## Big 3 — composites inside the 11 core

| # | Metric | Role | Status | File |
|---|---|---|---|---|
| 9 | **SIGNA RATE** | Flagship / center prestige · composite of Core 5 | locked as flagship | [composites/01_signa_rate.md](composites/01_signa_rate.md) |
| 10 | SDOT | Signal Delta Over Time — trajectory across windows | provisional | [composites/02_sdot.md](composites/02_sdot.md) |
| 11 | SDRM | Signal Density Resonance Metric — multi-axis cohesion | provisional | [composites/03_sdrm.md](composites/03_sdrm.md) |

**SIGNA RATE** is the WN8 equivalent — the single number that owns the profile hero block and drives the leaderboard rank. **SDOT** measures how the operator's composite is changing over time. **SDRM** measures whether the Core 5 are mutually reinforcing (true Transmitter signal) vs. one metric carrying the others (gameable).

---

## Extras — outside the 11 core

Tracked, rankable, displayable — but **not** part of the 11 and **not** weighted into SIGNA RATE.

| # | Metric | Aliases | Status | File |
|---|---|---|---|---|
| E.01 | Signal Force | sigalpha, Sig Alpha, SF | locked (formula confirmed) | [extras/01_signal_force.md](extras/01_signal_force.md) |
| E.02 | Drift Ratio | sigdrift, Sig Delta, DR% | provisional · precision tier only | [extras/02_drift_ratio.md](extras/02_drift_ratio.md) |

See [extras/00_README.md](extras/00_README.md) for the rationale on why these are extras and not core.

---

## Status legend

- **locked** — definition, inputs, formula, and output range are stable
- **provisional** — definition stable, formula or implementation may still shift
- **deprecated** — historical only, do not implement
- **unresolved** — lineage or naming still under recovery

---

## What predates what

The `.87xx` compression score predates explicit token analysis by approximately one month (July 2025 → August 2025). See [lineage/compression_snr_history.md](lineage/compression_snr_history.md) for the archaeology of this metric.

Naming variants, renames, and retirements (Transmitter Composite → SIGNA RATE; SDOT and SDRM retired; Sig Delta / Sig Alpha never adopted) are tracked in [lineage/naming_drift.md](lineage/naming_drift.md).

---

## Open questions

1. Final database field names — see [architecture/db_schema.md](../architecture/db_schema.md)
2. Whether composite Drift Ratio is in MVP or Phase 2 (currently Phase 2 / precision tier only)

---

## How this connects to the new token model

The Core 5 were originally designed for message/word-level extraction (the sig_army engine). The new **token-economic submission model** uses the metrics that AI platforms already generate as proxies — see [architecture/token_metric_bridge.md](../architecture/token_metric_bridge.md) for the full mapping.

The two systems coexist:
- **Free tier**: submit token telemetry → SigRank scores you immediately
- **Precision tier**: feed raw sessions through sig_army → deeper signal classification
