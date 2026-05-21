# BlitzStars Canonical Profile + Tank-Detail Page Structure

**Captured:** 2026-05-21 from live BlitzStars site, signed-in as DBrass57 (na)
**URL inspected:** `https://www.blitzstars.com/player/com/DBrass57/tank/4449` (IS-2 Pravda SP)
**Purpose:** Canonical reference for how BlitzStars structures the player profile AND the per-tank drilldown. Do not re-crawl. Treat as authoritative for SigRank's equivalent design.

> "Looks so easy simple basic yet not mindblowing until you try to build it and realize holy fuck how did he do this."

The depth comes from layered density. There's nothing flashy. Every section is a tight, focused information unit. But there are ~27 distinct sections on one page, all interlinked, all filterable, all clickable.

---

## URL pattern

```
/player/{region}/{codename}              ← player profile (top tanks + tank table)
/player/{region}/{codename}/tank/{tank_id}  ← player profile + tank-detail overlay
/halloffame                              ← global hall of fame
/topplayers                              ← top players leaderboard
/toptanks                                ← top tanks leaderboard
/tanksdata                               ← Zeitgeist Pro
/clan/{region}/{clan_id}                 ← clan profile
/supporters                              ← supporter page (Stripe checkout)
```

Regions: `com` (NA), `eu`, `asia`, `ru`

---

## CRITICAL ARCHITECTURAL INSIGHT

**The tank-detail page is the player profile PLUS a modal-like card overlaying it.** Both contents exist on the same DOM. The card has:
- `prev` / `close` / `next` navigation (ref_10696, 10697, 10698)
- URL updates to reflect the current tank (`/tank/{id}`)
- Underlying player profile stays loaded — keeps context

So tank detail is a **stateful overlay**, not a separate page. You can flip through tanks (prev/next) without losing the player context underneath.

**For SigRank:** When operator clicks a session row in the Session Log, open it as an overlay with prev/next nav, NOT a full page navigation. Faster, preserves context.

---

## Section-by-section catalog (27 sections)

### Persistent across every player page (1-12)

1. **Top Banner** — "Become a BlitzStars Supporter! Go ad-free + more" — links to `/supporters`
2. **Advertisement slot 1** (top)
3. **Player Identity Header**
   - Codename + clan tag (`[III]`, `[HAIRY]`, etc.)
   - Region badge `(na)`, `(eu)`, etc.
   - Currency totals: gold 💰 (3,529), silver 💵 (45,698,809), and a third value (438,353 — XP?)
   - "Last battle 3y 263d 1h 58m ago" — staleness indicator
4. **Medal/Achievement Row** (icons + counts):
   - Rassenay Medals (7 kills)
   - Pool Medals (6 kills)
   - Radley Walters Medals (5 kills) — 162 earned
   - High Caliber (Most Damage)
   - Top Gun (Most Kills on Team 4+) — 1,148
   - Win alone vs 3
   - Scout Medals — 572
   - Supporter Medals — 3,020
   - Mastery Aces — 250/451 (55%)
   - Link: "Show Achievement / Medal details"
5. **Career stats overview** — headline numbers
   - Winrate 56.98% (in platoon: 7.15%)
   - Tier wins distribution chart (III/VII/VIII most won)
   - Battles 43,581
   - Avg Tier 8.07
   - Avg Damage 1,603
   - WN8 2,152 (Great)
   - Survival 37.1%
   - Spot Rate 1.27
   - Kill Ratio 1.50
   - Damage Ratio 1.20
6. **Period Stats table** (Historical Records)
   - Columns: Statistic / 30 days / 60 days / 90 days / Career
   - Rows: Winrate, in platoon, Battles, Avg Tier, Avg Dmg, WN8 (with grade), WN7 (with grade), Dmg ratio, Kills/deaths, Spots, Survival, Dmg/tier
   - Grade labels: Very Bad / Bad / Below Average / Average / Above Average / Good / Very Good / Great / Unicum
   - Footnote: "Rankings are regional. Tanks tier 6+ only counted... 5,000 battles minimum all time. Top 5,000 places."
   - Hide button
7. **WN8 by Tier** matrix
   - Toggles: "Show %" / "Show tier weight"
   - Per-tier (I-X) breakdown — percentage of battles in each WN8 bracket
   - Footnote: "WN8 tier data is weighted by battle count, just as the combined WN8 'overall' value is."
8. **Stats by Tier** chart
   - Sortable Tier button + Sortable secondary metric button (Winrate by default)
   - Stacked bar chart: Wins / Losses / Draws + winrate line overlay
   - Y-axis: 2000 → 14000 (battle count), winrate 52-61%
9. **Show more statistics / Show WN8 Legend** links (expand for deeper detail)
10. **Lifetime Statistics** (massive grid):
    - **Account**: ID, Creation date, Total battle time (83d 9h 27m)
    - **Battles**: Wins 24,833, Win & survive 15,589 (35.77%), Draws 149, Losses 18,599
    - **Aim**: Shots 327,918, Hits 280,871, Hit rate 85.65%
    - **Lethality**: Damage dealt 69,873,156, Damage received 58,002,621, DPB 1,603, KPB 0.94
    - **Mortality**: Kills 40,976, Deaths 27,404, Survived 16,177, Survival 37.12%
    - **Honours**: Raseiniai count, Pool count, Radley Walters count, Top gun count
    - **Vision**: Spots 55,486, Spots/battle 1.27
    - **Platoon**: Platoon wins 1,775, % of wins in platoon 7.15%
    - **Tanks**: Played 451, Mastered 250, Mastery % 55.43%
    - **MISC**: Total XP 38,373,999, Capture points 7,971, Dropped capture points 16,765, Avg battle length 2m 45s
11. **Player Evolution** chart
    - Empty for this player ("No Data")
    - Cost-optimization note: **"Player history is recorded for all profiles VIEWED in the last 30 days. If profile not viewed for 30 days, history STOPS being recorded."**
    - Hide button
12. **Daily sessions log** table
    - Headers: Last / Tier / WN8 / WN7 / Tanks / Battles / Winrate / DR / KDR / Damage / KPB / Spots / Survival / XP
    - "Click row to view tanks played in session"
    - "Sessions end at 05:00 hrs the next morning, from the date shown"
    - Signature textbox (Supporter feature)

### Player-level tank tables (13-15)

13. **Top Tanks (min 100 battles)** with featured tank card
    - Tank stats recorded every ~25 battles / 24 hours
    - One tank's deep card shown (auto-rotates? or sort default):
      - Winrate, Damage ratio, DPM, KPM, KDR, Battles, Total battle time
    - Sortable secondary list with 13 items (top tanks)
14. **Tanks full table**
    - Filter controls:
      - Tier checkboxes (I, II, III, IV, V, VI, VII, VIII, IX, X) — multi-select
      - Premium toggle: Show / Hide / Only
      - Battles Custom Period — Min/Max numeric inputs
      - Columns link (show/hide columns)
      - Time window labels: Today / 30 day / 60 day / 90 day / All time
      - Show tank averages checkbox
      - Clear / Clear all
    - Stat percentiles key: "Each colour indicates a percentile band. Based on players who have at least 10*tier, minimum 40, battles"
    - Columns (22): Tank / Tier / Rank / WN8 / WN7 / Battles / Winrate / KDR / DPB / KPB / Spots / HPB / ShotEff / Hit rate / WPM / DPM / KPM / aXP / mXP / Survival / Last Played
    - Footnotes: 'Today' filter logic, Rank requirements (min 1,000 WN8, min 30/50/100 battles, min 5k lifetime)
15. **Advertisement slot 2**

### Tank-Detail Card Overlay (16-23) — visible when on /tank/{id}

16. **Card Navigation**: prev / close / next (flip through tanks without page reload)
17. **Tank Header Card**:
    - Mastery Class 1 Badge (best mastery achieved on this tank)
    - DBrass57 (codename, again)
    - Region (na)
    - **#118** rank position on this tank
    - "Last battle 3y 349d 45m ago" (per-tank, different from player level)
    - **WN8: 2,240 (Great)** — for THIS TANK
    - **IS-2 Pravda SP** heading (tank name)
    - **JAPAN** (nation)
    - **Tier 7**
18. **Stats Comparison Table** (Tank-specific, with reference baseline):
    - Columns: Average / Player / Diff
    - Rows (15): Battles, Winrate, Damage Ratio, KDR, Damage per battle, Kills per battle, Hits per battle, Spots per battle, Wins per minute, Damage per minute, Kills per minute, Survival rate, Hit rate, Dmg / hit, Shot Efficiency
    - Player's values are colored by percentile band (legend below)
    - Note: "Shot Efficiency compares the damage per hit to the top 100 players' damage per hit."
19. **Percentiles Legend**:
    - "Each colour represents a percentile band. For example, dark blue (80+) would indicate a stat higher than 80% of players who have played this tank."
    - "IS-2 Pravda SP averages and percentiles based on data from 3,801 random players."
20. **Masteries section**:
    - Mastery Class 1 Badge (highest)
    - Mastery Class 2 Badge × 20 (earned 20 times)
    - Mastery Class 3 Badge × 34 (earned 34 times)
21. **History chart** for this tank:
    - Sortable Y-axis: Winrate / Battles
    - Sortable X-axis: Date (default)
    - Data points with date stamps (2022-06-07 etc.)
    - "History shown since tracking began. See table below for all sessions."
    - **"Load more history"** button (Supporter feature — image: Supporter badge)
22. **30-60-90 day averages** table (tank-specific):
    - Columns: Stat / Period / 30 days / 60 days / 90 days
    - Rows: Rank/Position, Winrate, Battles, Damage per battle, Damage ratio, KDR, Spots, WN8, WN7
    - Footnote: "Rankings are regional, by WN8, for 30, 90 and career stats. Required battles: 30/50/100"
23. **Tank Totals** (lifetime totals on this specific tank):
    - **Damage**: Dealt 163,513 / Received 117,306
    - **Mortality**: Kills 121 / Deaths
    - **Aim & Vision**: Shots 637 / Hits 544 / Spots 151
    - **Misc**: Avg XP 886 / Max XP 1,875 / Total XP 94,819 / Max kills / Avg battle time 2m 44s / Total battle time 4h 53m
    - Per-battle/session table: Date / Btl / Winrate / WN8 / WN7 / DPB / KPB / KDR / Spots / Hit Rate / Survival
    - **"Load More History"** (Supporter feature)

### Tank-Level Tools + Rankings (24-26)

24. **Armour Inspector** section
    - Link: "Show Armour Inspector" (external 3D armor visualization tool)
25. **Hall of Fame for {tank}** section (tank-specific HoF):
    - Heading: "Hall of Fame for IS-2 Pravda SP" with link to `/halloffame`
    - **Season dropdown** (All time / Season 1 / 2 / 3 / 4 / 5 / 6 / Season 7 [current])
    - Per-season top performers list with player/clan links + score:
      - Animisk [808S] (na) — 3,148
      - Janzmeister [__Z__] (na) — 3,049 (pliego — map name?)
      - Janzmeister [__Z__] (na) — 3,028 (port — map name)
    - "Visit the [Hall of Fame] to submit & view replays."
26. **Blitz Stars regional rankings for {tank}**:
    - Heading: "All time IS-2 Pravda SP"
    - Time toggle: 30 days / All time
    - **Regional** checkbox (filter to same region as viewed player)
    - Columns: Player / Btl / Winrate / WN8 / WN7 / DPB / KDR / Spots
    - Top 10 (NA regional, all-time, IS-2 Pravda SP):
      ```
      Wicked_Lord_Shingan         100b  72.00%  WN8 3355  WN7 2222  DPB 1953  KDR 3.54
      soviet2021 [FKR]            276b  70.29%  WN8 3328  WN7 2112  DPB 2017  KDR 3.09
      _Tactical [-NOX-]           125b  69.60%  WN8 3305  WN7 2087  DPB 1931  KDR 2.83
      Nagatoro_Hayase [T0MA]      139b  69.78%  WN8 3298  WN7 2115  DPB 1932  KDR 3.25
      Jhonie_Ang [DEF_6]          106b  71.70%  WN8 3262  WN7 2062  DPB 2018  KDR 3.09
      skibidi_sneasler [U_S]      122b  71.31%  WN8 3198  WN7 2080  DPB 1930  KDR 4.04
      Zsef [GETTO]                147b  68.71%  WN8 3126  WN7 2011  DPB 1998  KDR 3.42
      Sanka_Rea                   103b  74.76%  WN8 3095  WN7 2003  DPB 1958  KDR 3.40
      alan456_sniper              197b  68.02%  WN8 3080  WN7 2014  DPB 1891  KDR 3.48
      InvaderTak                  994b  68.71%  WN8 3035  WN7 2016  DPB 1956  KDR 2.82
      ```
    - Footnote: "Min battles to qualify. By WN8. 100"
    - "Click 'Blitz Stars' text for full IS-2 Pravda SP stats. Updated daily."

### Site-wide tail (27)

27. **Recently viewed / Supporters / Footer**:
    - Recently viewed Players list (last 6)
    - Recently viewed Clans list (last 6)
    - BlitzStars supporters (random) — 6 highlighted
    - Clan supporters carousel — same 7 clans top + 7 bottom (logos × 14)
    - Footer: BlitzStars © | v1.5
    - "Raw stats data sourced from Wargaming's public API"
    - "Not affiliated with Wargaming or World of Tanks: Blitz"
    - "Wargaming content © Wargaming.net. All rights reserved."
    - Wargaming Support / Privacy Policy / Manage Cookie Settings
    - Theme selector: Default / Pale
    - Contact info (email + forum links)
    - Support BlitzStars CTA
    - WoT Console stats cross-link
    - Log in via Wargaming modal (region selector EU/NA/ASIA)
    - Advertisement slot 3 (footer)

---

## Engineering insights

### 1. No SVG/Canvas charts
**"The page does not contain any chart canvas or SVG visualization elements."**

All charts in BlitzStars are built with **HTML divs + CSS**, not D3 / Chart.js / canvas. This is a deliberate engineering choice:
- Lower bundle size
- No client-side rendering library required
- Accessibility-tree-readable
- Server-renderable

**For SigRank:** Consider HTML/CSS charts for the simpler views (sparklines, bar comparisons). Use SVG only for radar charts and complex visualizations.

### 2. Cost optimization: lazy history recording
> "Player history is recorded for all profiles that have been VIEWED in the last 30 days. If a player profile is not viewed for 30 days or more, history will stop being recorded."

Smart cost-control: only spend compute/storage on profiles people care about. Inactive operators stop accruing trend history.

**For SigRank:** Same pattern. Profile views trigger trend recording. After 30d of no views, freeze the trend recording for that operator.

### 3. Mastery Class system
- **Class 1** = highest mastery (top X% of damage/XP in a battle in this tank)
- **Class 2** = next tier (earned 20 times for DBrass57 on IS-2 Pravda SP)
- **Class 3** = third tier (earned 34 times)
- **Mastery Ace** = top 1% (separate accolade, shown in medal row)

**For SigRank:** This maps to BG.xx badge categories. Earnable multiple times. Aggregated count shown × N.

### 4. Per-entity Hall of Fame
The Hall of Fame isn't just global — every tank has its own HoF section embedded in the tank-detail card. With **per-season filtering**.

**For SigRank:** Hall of Signal per metric (compression / depth / continuity), per platform, per ruleset version. Embedded into operator-relative views, not just a separate page.

### 5. Comparative percentile bands
The Stats Comparison table colors each player value by percentile relative to all players on that tank. Dark blue = top 80%+.

**For SigRank:** Color-code Core 5 values by percentile relative to operator's class. TRANSMITTER who's bottom of their class shows yellow/red on weak metrics.

### 6. Supporter-gated features
- "Load more history" requires supporter badge
- Extended trend periods (60d, 90d) may be supporter-only on some tables
- Custom signature on session log

**For SigRank:** Same pattern — free tier gets 30d, Pro tier gets unlimited history depth.

### 7. The card-overlay-on-profile pattern
Tank detail is a card overlay on top of the player profile. Same DOM. Prev/Close/Next nav. URL updates.

**For SigRank:** Apply this pattern to session detail on operator profile. Same DOM, overlay card with prev/close/next session nav.

### 8. Three-way comparison pattern
Stats Comparison: **Average / Player / Diff**. This is the canonical comparison table format.

**For SigRank:** Apply to session-vs-operator-vs-class-average. Three columns. Diff column shows delta.

---

## SigRank equivalents — locked mapping

| BlitzStars section | SigRank equivalent | Layer |
|---|---|---|
| Player identity header | Operator profile header (codename, class, last seen) | L3 |
| Medal row | Badge case (BG.xx counts) | L1 + L3 |
| Career stats overview | SIGNA RATE hero + Core 5 grid | L3 |
| Period stats table (30/60/90/Career) | Window selector + Core 5 + Background 3 | L3 |
| WN8 by Tier matrix | Class-quality matrix per session-tier | L3 |
| Stats by Tier chart | Stats by class chart | L3 |
| Lifetime Statistics grid | Operator lifetime totals (B.xx, derived) | L3 |
| Player Evolution chart | SIGNA RATE trend line chart | L3 |
| Daily sessions log | Daily sessions log (same name!) | L3 |
| Top Tanks (min 100) | Top Sessions (min N messages) | L3 |
| Tanks full table | Sessions/Threads full table | L3 |
| Tank detail header card | Session detail header card | L3 |
| Stats Comparison (Avg/Player/Diff) | Session vs Operator vs Class Avg comparison | L3 |
| Percentiles Legend | Percentile coloring on Core 5 cells | L3 |
| Masteries section | Per-session badge tier counts | L1 + L3 |
| History chart (per-tank) | Session metric history chart | L3 |
| 30-60-90 day averages | Per-session window averages | L3 |
| Tank Totals (Damage/Mortality/Aim/Misc) | Session Totals (Output/Continuity/Complexity/Misc) | L3 |
| Armour Inspector link | Tooling integration link (e.g. "View in MCP Inspector") | L3 |
| Hall of Fame for tank | Hall of Signal for metric/session-type | L1 + L3 |
| Per-tank Top 10 regional | Per-thread Top 10 platform-regional | L3 |
| Recently viewed | Recently viewed operators/sessions/badges | L3 |
| Supporter carousel | Patron carousel (×2 placements) | L3 |
| Footer with regional login | Footer with platform selector | L3 |

---

## What this confirms for the SigRank build

1. **The session-detail overlay is mandatory.** Operators expect prev/next nav to flip between sessions.
2. **Mastery tiers per session.** Each session can earn Class 1, 2, 3 badges based on its Core 5 against operator's history.
3. **Per-metric Hall of Signal.** Not just global rankings — Hall sub-sections embedded into per-metric leaderboard pages.
4. **Color-coded percentile bands.** Operator's values colored relative to class average. Visual signal density.
5. **Three-way comparison table is canonical.** Operator / Class Avg / Diff is THE comparison format.
6. **Show More History is the Pro tier moat.** Free tier shows recent; Pro tier unlimited depth.
7. **Lazy history recording.** Inactive operators stop accruing trend history at 30d.
8. **Charts built with HTML/CSS, not canvas.** Consider this for our chart components.
9. **Regional / Platform toggle is everywhere.** It's not just on the homepage; it's on every leaderboard sub-section.
10. **Custom Period date range filter.** Operators want to slice by arbitrary date windows.

---

## What to grab next (operator's call)

Still to crawl on BlitzStars (if useful):
- **Hall of Fame** (`/halloffame`) — see global HoF format
- **Top Players** (`/topplayers`) — the actual ranked leaderboard
- **Tank Compare** (`/compare/...`) — compare engine UX
- **Zeitgeist Pro** (`/tanksdata`) — the paid analytics page
- **Supporters page** (`/supporters`) — Stripe checkout UI for inspiration
- **Clan page** (`/clan/...`) — for Circle structural reference

This document is enough to build the operator profile + session detail + tanks/sessions table at full BlitzStars-equivalent depth. The other pages above would extend it.

---

## End of canonical reference. Build accordingly.
