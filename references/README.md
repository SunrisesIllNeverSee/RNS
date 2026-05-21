# references/ — material we used to build, not needed at runtime

This folder holds everything that informed the SigRank build but **is not part of the production site or scoring system**. Source material, historical prototypes, benchmark artifacts, competitor analysis, archived research.

**If it's referenced by `primary/` or `comms/`, it stays here.** If it's not, it can be archived externally.

---

## Contents

### `blitzstars/`
Firecrawl export of [blitzstars.com](https://www.blitzstars.com/) homepage + key pages, captured 2026-03-11.
- 10 JSON files of scraped page content (home, top players, top tanks, clans, hall of fame, community, etc.)
- One markdown export of a player profile
- **Why it's here:** BlitzStars is the canonical UX reference. SigRank's site_architecture.md is mapped 1:1 from this source.

### `v1_leaderboard_site/`
Original December 2025 working leaderboard prototype.
- `index.html` + `main.js` + `styles.css` (complete static site)
- Multiple variant pages (final, table, codex popup)
- **Why it's here:** First proof that the SigRank concept rendered as a site. Source of design DNA.

### `v2_board_of_leaders/`
Most recent pre-repo build (2026, K2 reports).
- `board_of_leaders.html` — Avg User vs Avg AI comparison
- `signal_codex_basic.html` — formula definitions in HTML form
- **Why it's here:** The codex page is the precursor to CANON.md.

### `v1_tools/`
- `vcardgenerator.html` — original Signal vCard Generator (manual submission form)
- `composite_burn_index.html` — early aggregated index display
- `leaderboard_v2.html` — v2 iteration

### `benchmark_assets/`
MO§ES benchmark visual assets (PDF poster, metric cards, HTML poster).
- `MOSES_BENCHMARK_POSTER.pdf` — the field-comparison document
- Per-metric cards (card_01 cache, card_02 outin, etc.)
- `poster.html` — interactive version

### `benchmark_export/`
Raw `summary.json` output from `extract_benchmark_window.py` — 97 sessions of real Claude Code telemetry for the MO§ES reference window (2026-05-08 → 2026-05-14).
- **Why it's here:** Verification source for MO§ES R.xx reference values. Re-runnable to update reference data.

### `field_comparison/`
ArtificialAnalysis.ai scraped data on competitor coding agents.
- Used to construct the MO§ES benchmark comparison table.

### `extract_benchmark_window.py`
The script that produced `benchmark_export/summary.json`. Reads Claude Code `.jsonl` session files and aggregates token telemetry per window.
- **Pattern reference:** This is the model for what the production agent's adapter should do at scale.

### `moses_stats_raw.md`, `03_moses_5_benchmarks.md`
Working notes from the MO§ES benchmark construction. The "raw" before things got formalized into CANON / MOSES_REFERENCE.

### `04-SDOT-SigRank/`
Research notes on SDOT (Signal Delta Over Time) — a metric that was under consideration but retired during the build (see LINEAGE.md). Preserved for archaeological completeness.

---

## What does NOT belong here

- Production canon (lives in `primary/scoring/layer-0-ground/build/`)
- Production guidance (lives in `primary/scoring/layer-0-ground/guidance/`)
- Active mockups (live in `primary/scoring/layer-3-frontend/v4_mockup/`)
- Components used at runtime (live in `components/sigrank/`)
- Active spec documents (live in `primary/scoring/layer-{1,2,3}-*/`)
- Multi-model coordination (lives in `comms/`)
- Operator-dropped new info (lives in `inbox/`)

---

## When to move things in or out

**Move INTO `references/` when:**
- A doc was used as inspiration but isn't operative anymore
- An old prototype is superseded by a newer one
- A research note is no longer part of the active build

**Move OUT of `references/` when:**
- A reference doc gets promoted to canon (move to `layer-0-ground/`)
- A historical metric gets re-activated (move to `layer-1-foundation/metrics/`)

When moving, use `git mv` to preserve history.

---

## See also

- [`../primary/scoring/layer-0-ground/guidance/LINEAGE.md`](../primary/scoring/layer-0-ground/guidance/LINEAGE.md) — historical context for what's in this folder
- [`../primary/scoring/layer-0-ground/build/MOSES_REFERENCE.md`](../primary/scoring/layer-0-ground/build/MOSES_REFERENCE.md) — canon row that ties back to `benchmark_export/summary.json` here
