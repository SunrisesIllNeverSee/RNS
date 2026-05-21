# RNS — rns-sigrank

Research, tools, and the active **SigRank** build — quantifying signal vs. noise in human ↔ LLM conversations via token telemetry. The headline product is **SigRank**: a privacy-preserving leaderboard that infers operator interaction quality from token-level telemetry, without requiring raw transcripts.

Operator: Deric McHenry (OG SIGRANK). Build lead participant: VSClaude-OPUS47-LEAD.

---

## Repo layout (top level)

Sorted for navigation. Numbers prefix the folder name so they sort in build order; `_inbox/` sorts to the top with the underscore.

| Folder | What it is |
|---|---|
| `_inbox/` | Operator → models drop zone. New metrics, screenshots, decisions land here. One-way channel; models don't write here. |
| `1_sigrank/` | **The primary build.** Production canon, equations, mechanics, and frontend mockups. See layered structure below. |
| `2_secondary/` | Related projects that aren't the SigRank build: `sig_army/`, `word_vault/`, `WordToken-SNR-Classifier/`, `SiGlobe/`, `SigTune/`, `signal-Areana/`. |
| `3_outliers/` | Off-pattern research notes. |
| `4_references/` | Source material that informed the build but isn't part of runtime: BlitzStars crawl, formatted conversations, benchmark assets, competitor analysis. |
| `5_comms/` | Multi-model coordination: decision logs, handoffs, participant registry, lock state. |
| `raw/` | Source-of-truth dump of routed inbox files. Untracked locally; not part of the GitHub repo. |
| `MODERATOR_NOTE.md` | Project orientation: who's who, build rules, layer model, authority limits. **Read this first.** |

## `1_sigrank/` layered structure

```text
1_sigrank/
├── 1.1_layer-0-ground/       — bedrock: CANON, ROOT_NUMBERS, MO§ES_REFERENCE, CONSERVATION_LAW
├── 1.2_layer-1-foundation/   — Core 5 + Background 3 + Composites, class tiers, badges, rewards
├── 1.3_layer-2-mechanics/    — db schema, scoring formula, snapshot payload, billing, refresh cadences
├── 1.4_layer-3-frontend/     — site architecture, v3/v4 mockups, Stripe checkout UI
├── 1.5_components/           — TSX components (LeaderboardTable, ProfilePanel, etc.)
└── 1.6_agent/                — local telemetry agent design
```

Layer 0 is the bedrock — every higher layer cites canonical IDs (`M.01`, `B.02`, `C.03`, `R.04`, `RS.xx`) defined there.

## Canonical ID scheme

| Prefix | Meaning | Lives in |
|---|---|---|
| `RN.xx` | Root number (raw telemetry input) | `1.1_layer-0-ground/build/ROOT_NUMBERS.md` |
| `T.xx` | Telemetry shape | CANON.md |
| `M.xx` | Core 5 metric | CANON.md |
| `B.xx` | Background 3 metric | CANON.md |
| `C.xx` | Composite metric (SIGNA RATE, Signal Force, DR%) | CANON.md |
| `K.xx` | Class tier (TRANSMITTER → IGNITER) | CANON.md |
| `R.xx` | MO§ES reference value | `MOSES_REFERENCE.md` |
| `RS.xx` | Proprietary scoring parameter (HIDDEN) | scoring engine |
| `BG.xx` / `RW.xx` | Badge / reward | `1.2_layer-1-foundation/badges,rewards/` |

Every number in any mockup or doc either has a canonical ID or is marked `*` as placeholder.

## SigRank in 30 seconds

- **Free tier** uses token telemetry (output / fresh_input / cache_read / cache_creation / messages / sessions / turns / age / LOC) to compute 9 of 11 metrics.
- **Pro tier** adds `sig_army` word-level audit for the remaining 2 (Drift Ratio, refined Compression).
- **Leaderboard** organized BlitzStars-style: Operators · Circles · Metrics · Operator Compare · Signalgeist Pro · Hall of Signal — with platform toggle (Claude / ChatGPT / Gemini / Pi / Multi).
- **Refresh cadences** are tiered: live (30–60s) for top-10 boards, 5min for full leaderboards, hourly for percentile bands, daily for badges and Hall of Signal.
- **Score breakdown** is black-boxed in the UI: inputs → sealed "Scoring Engine" → result. Exact weights (`RS.01`) and class thresholds (`RS.05`) are proprietary.

## Status

Pre-launch. Schema is locked at v1.0 (11 metrics + 13 root numbers + 9 class tiers). Mockups in `1.4_layer-3-frontend/v4_mockup/`. Next.js production build pending operator green-light.

## License

No license — copyright reserved. Open an issue if you want to reuse anything.
