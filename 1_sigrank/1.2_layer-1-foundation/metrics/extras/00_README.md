# Extras — outside the 11 core

Metrics that are tracked and rankable but **not part of the 11 core** (Core 5 + Background 3 + Big 3). Per operator on 2026-05-21:

> "DR or sigdrift and sigalpha were added outside of the 11 core."

Where:
- **sigdrift = Drift Ratio** (alias)
- **sigalpha = Signal Force** (alias)

These are still valid SigRank metrics. They appear on profiles and may drive badges. They just don't sit inside the 11-core canonical stack and they don't feed SIGNA RATE.

| # | File | Metric | Aliases | Status |
|---|---|---|---|---|
| 01 | [01_signal_force.md](01_signal_force.md) | Signal Force | sigalpha, SF | locked formula |
| 02 | [02_drift_ratio.md](02_drift_ratio.md) | Drift Ratio | sigdrift, Sig Delta, DR% | provisional |

## Why these are extras, not core

- **Signal Force** is a load × longevity composite (`B.03 × M.04 / B.02`) — it's a *derived consequence* of other metrics, not an independent signal axis.
- **Drift Ratio** is a precision-tier-only metric (requires `sig_army` audit). It can't be fairly compared across operators without word-level analysis, so it can't sit in the universally-computed core.

The Big 3 (SDOT, SDRM, SIGNA RATE) are different: each measures a distinct independent property of the operator's signal — trajectory, coherence, composite quality. The extras layer is for *derived metrics* and *precision-tier-only metrics*.
