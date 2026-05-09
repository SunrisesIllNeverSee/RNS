# RNS

Research, tools, and prototypes around **signal vs. noise** measurement in human ↔ LLM conversations — quantifying how much of an interaction is high-information signal versus repetition / drift / drag.

## What's in here

| Folder | What it is |
|--------|------------|
| `04-SDOT-SigRank/` | Research notes on **SDOT** (Signal Divergence Over Time) and **SigRank** — quantifying platform drag on high-signal users; ECC stress test and session forensics. |
| `SiGlobe/` | Global Signal Arena — TSX harness + arena UI for visualizing signal over time. |
| `SigTune/` | Buildout docs for SigTune — tuning protocol and equations. |
| `WordToken-SNR-Classifier/` | Token-level SNR classification logic — markdown spec + worked examples. |
| `sig_army/` | Python core — `signal_army.py`, `sigtoken_sys.py`, `sigsystem.py`, `thread_map.py`, `sigtoken_v2.py`. The signal-extraction engine + reference docs and session logs. |
| `signal-Areana/` | Signal Arena — full-stack web app (React + Express + Drizzle/Postgres) for interactive signal analysis. |
| `word_vault/` | Generated word-level vault — ~4,900 markdown files, one per token, with classification, signal weight, noise weight, and trajectory. |

## Status

Pre-publication. This is consolidated research material from active projects, not a polished release. Code and data dumps from analysis runs are kept locally and **excluded** from this repo (see `.gitignore`).

## Local layout (sources)

The contents of this repo are pulled from the live project tree at `~/Desktop/signal-ecosystem/`. Heavy analysis outputs (`runs/`, `chatfiles/`, `obsidian_vaults/`, `*.zip`, multi-MB CSVs) live there and stay there.

## License

No license added — copyright reserved. If you want to reuse anything, open an issue.
