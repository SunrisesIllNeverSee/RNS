# 11:30 · VSClaude-OPUS47-LEAD → ALL · Big edit pass + new specs

**Subject:** SDOT/SDRM restored · extras layer added · Hall of Signal spec · Lock Protocol proposed · BlitzStars Tab 1/3/4 cataloged

## TL;DR

Following operator corrections on 2026-05-21, this session produced six distinct work products:

1. **CANON corrected** — Big 3 composites restored to SIGNA RATE + SDOT + SDRM. Signal Force and Drift Ratio demoted to extras layer (E.01, E.02). Reverses the unauthorized Sonnet 4.6 retirement commit (`2c3b0be`).
2. **File restoration** — `02_sdrm.md` recovered from git history (commit `eaefdd1`), `02_sdot.md` newly written, both placed in `composites/`. Signal Force + Drift Ratio moved to new `extras/` folder.
3. **Lineage docs corrected** — `naming_drift.md` and `metric_family_tree.md` updated to reflect SDOT/SDRM active status and Sig Delta = Drift Ratio / Sig Alpha = Signal Force alias relationships.
4. **New: Hall of Signal spec** — full spec doc at `1_sigrank/1.4_layer-3-frontend/hall_of_signal.md`. Captures the BlitzStars Hall of Fame structural pattern: peak-anchored ranking, user-submitted snapshots, season segmentation, sliding-scale points, separate from the rolling-average leaderboard.
5. **New: Lock Protocol** — full proposal at `1_sigrank/1.1_layer-0-ground/guidance/LOCK_PROTOCOL.md`. Four-layer wall (sentinel headers + chmod 0444 + pre-commit hook + CODEOWNERS) preventing future unauthorized canonical modifications.
6. **Source preservation** — operator-pasted GPT chat from 2026-03-10 archived at `4_references/gpt_chats/2026-03-10_gpt_sigrank_metric_recovery.md`.

## Files affected

### Created
- `1_sigrank/1.2_layer-1-foundation/metrics/composites/02_sdot.md`
- `1_sigrank/1.2_layer-1-foundation/metrics/composites/03_sdrm.md` (restored from `eaefdd1`)
- `1_sigrank/1.2_layer-1-foundation/metrics/extras/00_README.md`
- `1_sigrank/1.2_layer-1-foundation/metrics/extras/01_signal_force.md` (moved from composites)
- `1_sigrank/1.2_layer-1-foundation/metrics/extras/02_drift_ratio.md` (moved from composites)
- `1_sigrank/1.4_layer-3-frontend/hall_of_signal.md`
- `1_sigrank/1.1_layer-0-ground/guidance/LOCK_PROTOCOL.md`
- `4_references/gpt_chats/2026-03-10_gpt_sigrank_metric_recovery.md`
- `5_comms/messages/2026-05-21/10-15-VSClaude-OPUS47-LEAD-to-ALL.md` (earlier this session)
- `5_comms/messages/2026-05-21/11-30-VSClaude-OPUS47-LEAD-to-ALL.md` (this file)

### Modified
- `1_sigrank/1.1_layer-0-ground/build/CANON.md` — Section IV restructured as Big 3 (C.01–C.03) + new Section IV-B Extras (E.01–E.02)
- `1_sigrank/1.2_layer-1-foundation/metrics/00_README.md` — three-layer model expanded to four (Core + Background + Big 3 + Extras), correction note added
- `1_sigrank/1.2_layer-1-foundation/metrics/lineage/naming_drift.md` — retirement claims reversed
- `1_sigrank/1.2_layer-1-foundation/metrics/lineage/metric_family_tree.md` — tree diagram corrected
- `5_comms/decisions/layer-1-decisions.md` — added "Big 3 composition resolved" entry; warning callout on prior incorrect 11-equation lock

## BlitzStars exploration (Tabs 1, 3, 4 — Tab 2 was Zeitgeist Pro paywall, not Compare)

Operator opened four tabs; I cataloged three useful ones. Tab 2 (`tanksdata`) was the paywalled Zeitgeist Pro page, not Tank Compare (which lives at the `tank-compare.blitzstars.com` subdomain — not yet visited).

### From Tab 1 (`_Rioo_` profile) — added these patterns to the build:
- Three-window Historical Records table with embedded rank superscripts per cell
- WN8-by-Tier distribution → maps to SIGNA RATE-by-Source distribution
- Player Evolution dual-line chart (cumulative metric + count over time)
- 30-60-90 day Δ vs Career delta table
- BlitzStars Awards strip (badge display at top of profile)
- Recent Milestones strip (per-tank achievement scroll)
- Daily Sessions Log with click-to-expand
- Section "Hide" toggles throughout

### From Tab 3 (Hall of Fame) — produced full Hall of Signal spec:
- Hall ≠ leaderboard. Two parallel ranking systems.
- Hall = single-peak, user-submitted, season-segmented, per-metric top 10.
- Aggregate points layer feeds Operators-by-Points + Circles-by-Points boards.
- Submission states: Personal / Verified / Disputed / Delisted.
- Verification via ed25519 signature + (Pro tier) sig_army re-score.

### From Tab 4 (Clans) — confirmed Circles architecture:
- Circles = aggregated from operator stats (AVG / SUM / COUNT over members), not separate stats.
- Same metric columns as operator board.
- `Platoon %` column → SigRank "Circle Co-op %" (multi-operator session frequency).
- Filters: platform/region, avg-tier-equivalent, time window.

## Operator-facing actionable items

1. **Confirm or amend** the Big 3 composition (SIGNA RATE + SDOT + SDRM). If a different third metric is intended, say so before formulas get specced.
2. **Provide SDOT and SDRM formulas** when ready. Current spec files have provisional formulas marked as such.
3. **Greenlight the Lock Protocol** Layer-by-layer implementation. Layers 1 + 2 take five minutes. Layer 3 (pre-commit hook) takes ~30 minutes. Layer 4 (CODEOWNERS) takes ~10 minutes.
4. **Decide Hall of Signal open questions** — submission gating (free vs Pro), sliding-scale weighting, per-metric vs per-platform top 10, class-tier weighting, dispute arbitration.
5. **Open `tank-compare.blitzstars.com`** when Agent Compare crawl is desired.

## What's still NOT done

- Lock Protocol is proposal-only. Headers/chmod/hook/CODEOWNERS not yet applied.
- Hall of Signal spec is structure-only. Visual mockups not created.
- BlitzStars Tank Compare subdomain not crawled.
- The `gptmetric.md` source archive references the raw chat content but doesn't paste it in full (~80KB) — placeholder for now; operator can drop the raw paste back in if full archival is needed.
- v4 mockup not yet updated to show Big 3 composition correction (still references the old SIGNA RATE / Signal Force / Drift Ratio Big 3).

— VSClaude-OPUS47-LEAD
