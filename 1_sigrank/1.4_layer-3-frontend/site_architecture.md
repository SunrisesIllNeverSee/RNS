# Site Architecture — BlitzStars Model

SigRank's site structure mirrors BlitzStars deliberately. BlitzStars is the gold standard for stat ecosystems, and the operator (who has played thousands of hours of WoT Blitz) knows that game intuitively. The structural map below is locked from GPT thread-0369 (2026-03-10).

> "BlitzStars and SIGRANK are both 'basic inputs → custom derived metrics → rich leaderboard surface.' That is the real shared cloth."

---

## Top-level concept mapping

| BlitzStars | SigRank | Why |
|---|---|---|
| Players | **Operators** | The people being ranked |
| Clans | **Circles** | Teams / groups |
| Tanks | **Metrics** | The dimensions of performance |
| Tank Compare | **Operator Compare** | Side-by-side analysis |
| Zeitgeist Pro | **Signalgeist Pro** | Premium analytics layer |
| Hall of Fame | **Hall of Signal** | Records / prestige |
| Community | **Community** | Forums / submissions / discussion |
| Tank tiers (I–X) | **Class hierarchy** (IGNITER → TRANSMITTER) | Hierarchical performance bands |
| Regions (EU/NA/ASIA/RU) | **Platforms** (Claude/ChatGPT/Gemini/Pi/Multi) | Source / domain segmentation |

---

## Page-by-page architecture

### Homepage (`/`)

The single most important page. BlitzStars puts the most signal here. SigRank does the same.

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER NAV                                                       │
│   ◈ SIGRANK                                                      │
│   Operators │ Circles │ Metrics │ Compare │                      │
│   Signalgeist Pro │ Hall of Signal │ Community                   │
│   [search: operators/circles]                          [Login]   │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ HERO                                                             │
│   ◈ SIGRANK                                                      │
│   Detailed operator & signal statistics for human                │
│   performance across AI systems                                  │
│                                                                  │
│   Platform selector: [Global] [Claude] [ChatGPT] [Gemini] [Pi]   │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ FEATURED — Signal Supporters / Featured Operators                │
│   (BlitzStars equivalent: Clan Supporters strip)                 │
│   Horizontal scrolling card row of featured operators            │
└──────────────────────────────────────────────────────────────────┘
┌────────────────────────────┬─────────────────────────────────────┐
│ TODAY'S SIGNAL LEADERS     │ TODAY'S SIGNAL EVENTS               │
│ (BlitzStars: Today's       │ (BlitzStars: Today's Hero Battles)  │
│  Supporters)                │                                     │
│                            │ Top performances grouped by class:   │
│ Last 24h ranking by daily  │   TRANSMITTER tier                  │
│ signal points              │     • TransVaultOrigin               │
│                            │       Comp 0.94 / SR 96.4 / 16h ago  │
│ Operator   │ Today │ Total │   ARCHITECT+ tier                   │
│ TVO        │  180  │ 2,700 │     • ArchiveSignal                  │
│ ArchPlus   │  154  │ 2,210 │       Comp 0.82 / SR 89 / 2h ago    │
│ XW         │  142  │ 1,988 │   ARCHITECT tier                    │
│ ...                        │     • ...                            │
└────────────────────────────┴─────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ SIGNALGEIST — 90-day stats slices                                │
│ (BlitzStars: Tank Zeitgeist)                                     │
│                                                                  │
│ ┌──────────────┬──────────────┬──────────────┬──────────────┐    │
│ │ Highest      │ Most         │ Most Active  │ Deepest      │    │
│ │ Compression  │ Improved SNR │ (Volume)     │ Channels     │    │
│ ├──────────────┼──────────────┼──────────────┼──────────────┤    │
│ │ TVO 0.94     │ Ghost +0.08  │ TVO 18,450   │ DC 31        │    │
│ │ Quiet 0.92   │ Deep +0.06   │ XW 14,320    │ TVO 26       │    │
│ │ XW 0.88      │ Arch +0.05   │ Ghost 10,880 │ XW 24        │    │
│ └──────────────┴──────────────┴──────────────┴──────────────┘    │
│                                                                  │
│ ┌──────────────┬──────────────┐                                  │
│ │ Most Complex │ Most         │                                  │
│ │ Prompts      │ Cross-Thread │                                  │
│ ├──────────────┼──────────────┤                                  │
│ │ Promplex 94  │ XW 41        │                                  │
│ │ TVO 92       │ TVO 37       │                                  │
│ │ XW 88        │ Arch 31      │                                  │
│ └──────────────┴──────────────┘                                  │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ OPERATORS ACTIVE — LIVE                                          │
│ (BlitzStars: Players Online — Live)                              │
│                                                                  │
│ Global: 1,847    Claude: 612    ChatGPT: 798    Gemini: 287      │
│ Pi: 88    Multi: 62                                              │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ ACTIVITY PULSE — Hourly chart                                    │
│ (BlitzStars: Players Online — Hourly)                            │
│                                                                  │
│ [stacked area chart: operators active per hour, last 7d,         │
│  color-coded by platform]                                        │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ WEEKLY SIGNAL PULSE — max & avg                                  │
│ (BlitzStars: Players Online — Weekly)                            │
│                                                                  │
│ [line chart: weekly active operators, peak vs average, by        │
│  ruleset version on x-axis instead of game patches]              │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ RECENTLY VIEWED                                                  │
│                                                                  │
│ Operators  │ Circles  │ Featured Supporters                      │
│ • TVO      │ • Foundry│ • TransVaultOrigin                       │
│ • XW       │ • Deep   │ • ArchiveSignal                          │
│ ...        │ ...      │ ...                                      │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ FOOTER                                                           │
│   SIGRANK © | v1.0                                               │
│   Signal data derived from operator-submitted telemetry          │
│   Not affiliated with OpenAI, Anthropic, Google, xAI, Inflection │
│   Privacy │ Terms │ Methodology │ Support │ Contact              │
└──────────────────────────────────────────────────────────────────┘
```

---

### Operators page (`/operators`)

The main ranked list. Equivalent to BlitzStars' Players page.

**Controls (top bar):**
- Platform filter: Global / Claude / ChatGPT / Gemini / Pi / Multi
- Window: Today / 7d / 30d / 90d / All-time
- Class filter: All / Transmitter / Architect+ / Architect / Power / Base / Seeker / Refiner / Bearer / Igniter
- Sort by: SIGNA RATE (default) / Compression / Depth / Volume / Complexity / Cross-Thread / Signal Force
- Search

**Table columns (the LeaderboardTable component we built):**

```
#  │ Class    │ Operator (location)        │ SIGNA  │ Comp  │ SD    │ TT     │ PC   │ CT  │ SF    │ Age  │ Last Seen
1  │ TRANS    │ TransVaultOrigin (US)      │ 96.4   │ 0.87  │ 26.1  │ 18,450 │  92  │ 37  │ 12.8  │ 14d  │ 16h ago
2  │ ARCH+    │ ArchiveSignal (DE)         │ 89.7   │ 0.82  │ 22.1  │ 14,320 │  88  │ 41  │  9.4  │ 7mo  │  2h ago
3  │ ARCH+    │ Arch+:24-00971 (CA)        │ 87.3   │ 0.81  │ 19.6  │ 12,107 │  79  │ 24  │  7.1  │ 21d  │ 18h ago
...
```

**Pagination:** Top 25 by default. Next 25 / Next 100 / Show All.

---

### Circles page (`/circles`)

Equivalent to BlitzStars' Clans page.

**Controls:** Platform filter, window, search

**Table columns:**
```
#  │ Circle Tag │ Name              │ Members │ Avg SIGNA │ Avg Comp │ Total TT  │ Active │ Crown Cnt
1  │ [-TVO-]    │ Foundry Circle    │   42    │   78.4    │   0.79   │ 1.2M      │  38    │   12
2  │ [DC]       │ Deep Channel      │   28    │   76.1    │   0.81   │ 0.9M      │  24    │    8
```

**Each row clickable → `/circles/{tag}`** showing the circle's roster, leaderboard rank, recent activity.

---

### Metrics page (`/metrics`)

Equivalent to BlitzStars' Tanks page — but instead of tanks, it shows per-metric leaderboards.

**Sub-pages / tabs:**
- `/metrics/compression` — Top operators by Compression Ratio
- `/metrics/depth` — Top by Session Depth
- `/metrics/volume` — Top by Token Throughput
- `/metrics/complexity` — Top by Prompt Complexity
- `/metrics/cross-thread` — Top by Cross-Thread Referencing
- `/metrics/signa-rate` — Top by SIGNA RATE (the flagship board)
- `/metrics/signal-force` — Top by Signal Force

Each is a metric-focused leaderboard table.

---

### Operator profile (`/operators/{codename}`)

The single most important page after the homepage. Equivalent to a BlitzStars player profile.

```
┌──────────────────────────────────────────────────────────────────┐
│ IDENTITY HEADER                                                  │
│   ◈ TransVaultOrigin                                             │
│   Platform: Claude    Class: TRANSMITTER    Member: 119d         │
│   Status: ● Active    Last seen: 16h ago                         │
│   Verified: ✓ (audit_verified)                                   │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ HERO — CENTER PRESTIGE METRIC                                    │
│                                                                  │
│              ┌──────────────────────────┐                        │
│              │                          │                        │
│              │      ⭐ 96.4 ⭐           │                        │
│              │                          │                        │
│              │       SIGNA RATE         │                        │
│              │                          │                        │
│              │   Rank #1 Global         │                        │
│              │   Rank #1 Class          │                        │
│              │   99.97th percentile     │                        │
│              │                          │                        │
│              │   24h: ↑ +2              │                        │
│              │   7d:  ↑ +5              │                        │
│              │   Best: #1 (2026-05-14)  │                        │
│              └──────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ TIME-WINDOW SELECTOR                                             │
│   [Today] [7d] [30d] [90d] [All-time]                            │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ CORE METRICS GRID                                                │
│                                                                  │
│ Compression Ratio    0.87  ████████████████████░░  TRANSMITTER   │
│ Prompt Complexity    92    █████████████████░░░░░                │
│ Cross-Thread         37    ███████████████░░░░░░░                │
│ Session Depth        26.1  ████████████░░░░░░░░░░                │
│ Token Throughput     18.4k █████████████████░░░░░                │
│                                                                  │
│ Background:                                                      │
│   Message Volume   3,864     Account Age   14d                   │
│   Total Messages   53,960                                        │
│                                                                  │
│ Composites:                                                      │
│   Signal Force       12.8                                        │
│   Drift Ratio        — (precision tier)                          │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ ANALYTICS DASHBOARD                                              │
│                                                                  │
│ ┌────────────┬────────────────────┬────────────────────┐         │
│ │ Performance│ Activity Heatmap   │ Score Trends       │         │
│ │ Overview   │ (16 weeks)         │ (last 12 windows)  │         │
│ │ (Radar)    │ [...green grid...] │ [...line chart...] │         │
│ └────────────┴────────────────────┴────────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ DRILLDOWN A — SNAPSHOT HISTORY                                   │
│ (BlitzStars equivalent: daily stats history)                     │
│                                                                  │
│ Date        SIGNA  Comp   SD    PC   CT  TT     Class       Rank │
│ 2026-05-14  96.4   0.87  26.1  92   37  18.4k  TRANS       #1   │
│ 2026-05-13  95.2   0.86  25.8  91   36  17.9k  TRANS       #1   │
│ 2026-05-07  92.1   0.82  22.4  87   31  15.2k  TRANS       #1   │
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ DRILLDOWN B — SESSION / THREAD LOG                               │
│ (BlitzStars equivalent: per-tank performance)                    │
│                                                                  │
│ Thread / Session     Last       Msgs   SD   Comp  TT     PC      │
│ moses-build          2h ago    1,327  18.4 0.94  187k   89      │
│ commitment-theory    20h ago    821  16.2 0.92   89k   84      │
│ application-hub      18h ago    785  14.9 0.85   82k   76      │
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ BADGE CASE                                                       │
│                                                                  │
│ ⭐ 5x Crown           Held all 5 Core metrics                    │
│ ◈ Transmitter         SNR ≥ 0.85                                 │
│ ⚡ Lightning Strike   Largest 24h rise (2026-05-10)              │
│ 🛡 Audit Verified     Manually confirmed metrics                │
│ ❄ Quiet Giant         Low MV, elite SNR                         │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ COMPARE / EXPORT / SHARE                                         │
│                                                                  │
│ [Compare to another operator] [Compare to Top 50 avg]            │
│ [Export profile data] [Share signed vCard]                       │
└──────────────────────────────────────────────────────────────────┘
```

**Above is the heart of the system.** It mirrors a BlitzStars profile page structure exactly, with SigRank metrics substituted in.

---

### Operator Compare page (`/compare`)

Equivalent to BlitzStars' Tank Compare.

```
┌──────────────────────────────────────────────────────────────────┐
│ Operator A: [TransVaultOrigin ▾]    vs    [ArchiveSignal ▾] : B  │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ Metric              │  A         │  B         │  Δ              │
├─────────────────────┼────────────┼────────────┼─────────────────┤
│ SIGNA RATE          │  96.4 ✓    │  89.7      │  +6.7           │
│ Compression Ratio   │  0.87 ✓    │  0.82      │  +0.05          │
│ Session Depth       │  26.1 ✓    │  22.1      │  +4.0           │
│ Token Throughput    │  18,450 ✓  │  14,320    │  +4,130         │
│ Prompt Complexity   │  92 ✓      │  88        │  +4             │
│ Cross-Thread        │  37        │  41 ✓      │  −4             │
│ Signal Force        │  12.8 ✓    │   9.4      │  +3.4           │
│ Account Age         │  14d       │  7mo ✓     │  N/A            │
│ Total Messages      │  53,960 ✓  │  31,200    │  +22,760        │
└─────────────────────────────────────────────────────────────────┘
[Compare radar overlay chart]
```

Also supports:
- Operator vs Top 50 avg
- Operator vs class average
- Operator vs platform median

---

### Signalgeist Pro (`/pro`)

Equivalent to BlitzStars' Zeitgeist Pro — the **paid analytics tier**.

Features:
- 30/90/365-day trends per metric
- Class migration history (when did this operator change class)
- Badge history timeline
- Score decomposition (which sub-scores drove SIGNA RATE)
- Rank delta history
- Session density analytics
- Lineage strip (which models / platforms over time)
- Drift Ratio detection (precision tier only)
- Private operator dashboard
- Export to CSV / API access

**This is the upsell page.** Funnels operators from free tier to paid.

---

### Hall of Signal (`/hall`)

Equivalent to BlitzStars' Hall of Fame. Prestige records.

```
┌──────────────────────────────────────────────────────────────────┐
│ HALL OF SIGNAL                                                   │
│                                                                  │
│ Highest Compression Ever Recorded                                │
│   TransVaultOrigin — 0.94 (2026-05-14)                           │
│                                                                  │
│ Deepest Single Session Depth                                     │
│   DeepChannel — 31.0 (2026-04-22)                                │
│                                                                  │
│ Most Cross-Thread Continuity                                     │
│   CrossWeaver — 41 (2026-05-10)                                  │
│                                                                  │
│ Longest Transmitter Streak                                       │
│   TransVaultOrigin — 38 days (current)                           │
│                                                                  │
│ Largest 24h Rank Climb                                           │
│   GhostRelay — +47 (2026-04-15)                                  │
│                                                                  │
│ Fivefold Hold Recipients                                         │
│   • TransVaultOrigin (2026-05-14)                                │
│   • ArchiveSignal (2026-04-22)                                   │
│   • CrossWeaver (2026-03-08)                                     │
│                                                                  │
│ First Verified Transmitter                                       │
│   TransVaultOrigin (2025-07-26)                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### Community (`/community`)

Equivalent to BlitzStars' Community section.

- Operator spotlights
- Daily snapshot drops (PDF archive)
- Methodology updates
- Changelog
- Ruleset versioning notes
- Discussion (off-platform forum link initially; embedded later)
- Support / feedback
- Become a Signal Supporter (donation / sponsor link)

---

### Submit (`/submit`)

The action page — how operators get on the leaderboard.

```
1. Install the agent:    pipx install sigrank-agent
2. Initialize:           sigrank init
3. Add your source:      sigrank source add claude-code ~/.claude/projects
4. Scan + compute:       sigrank scan && sigrank compute --window 30d
5. Preview:              sigrank preview
6. Publish:              sigrank publish
```

Plus an **inline web submission form** (the vCard generator equivalent) for operators who don't want to run the CLI — manual entry of metrics for a basic rank (with reduced confidence indicator).

---

## Search (top nav)

```
[search]   "known operators, known circles"
```

Type-ahead with results split into:
- **Operators** (autocomplete on codename)
- **Circles** (autocomplete on tag or name)
- **Metrics** (jump to leaderboard for that metric)

Same UX pattern as BlitzStars search.

---

## Platform / domain selector (everywhere)

Just like BlitzStars' region selector (EU/NA/ASIA/RU), SigRank shows the platform/domain filter prominently at top of every leaderboard page:

```
[ Global ] [ Claude ] [ ChatGPT ] [ Gemini ] [ Pi ] [ Multi ]
```

Defaults to Global. Operators can compare cross-platform or filter to their own.

---

## Routing structure (Next.js)

```
app/
├── page.tsx                            (homepage)
├── operators/
│   ├── page.tsx                        (operators list)
│   └── [codename]/
│       ├── page.tsx                    (operator profile)
│       ├── history/page.tsx            (full historical drilldown)
│       └── sessions/page.tsx           (session/thread log expanded)
├── circles/
│   ├── page.tsx
│   └── [tag]/page.tsx
├── metrics/
│   ├── page.tsx                        (metrics overview)
│   ├── compression/page.tsx
│   ├── depth/page.tsx
│   ├── complexity/page.tsx
│   ├── cross-thread/page.tsx
│   ├── volume/page.tsx
│   ├── signa-rate/page.tsx
│   └── signal-force/page.tsx
├── compare/
│   └── page.tsx                        (with query params for A / B)
├── pro/
│   └── page.tsx                        (Signalgeist Pro pitch + features)
├── hall/
│   └── page.tsx                        (Hall of Signal)
├── community/
│   └── page.tsx
├── submit/
│   ├── page.tsx                        (CLI instructions + web form)
│   └── manual/page.tsx                 (vCard generator)
└── api/
    └── (proxy routes to Supabase if needed)
```

---

## Component mapping (existing → routes)

| Component | Used on |
|---|---|
| `LeaderboardTable` | `/operators`, `/metrics/{metric}` |
| `ProfilePanel` | `/operators/{codename}` (hero block) |
| `AnalyticsDashboard` | `/operators/{codename}` (analytics row) |
| `K2IndexSnapshot` | `/` (homepage class distribution snapshot) |
| `WrappedStats` | `/operators/{codename}/wrapped` (annual / period summary) |
| `CrossPlatformLeaderboard` | `/` hero secondary view |
| `SignalSystemBoard` | `/operators/{codename}` (vs avg comparison) |
| `MetricTabs` | Inside `LeaderboardTable` |
| `SignalClassBadge` | Everywhere class is displayed |

All 12 components map to at least one page. None are orphans.

---

## What we deliberately copy from BlitzStars

1. **Stat surface over disciplined pipeline** — the website is the last step, not the system
2. **Profile depth as the heart** — not the leaderboard, the profile is where users identify
3. **Multi-region / multi-platform selector everywhere**
4. **Precomputed cached pages, not live joins** — fast at scale
5. **Today's leaders + Today's events side-by-side**
6. **90-day "geist" slices** with multiple cuts (best, most improved, most active)
7. **Live activity counter at fold**
8. **Recently viewed module** (drives return engagement)
9. **Search prominent in nav, type-ahead with category split**
10. **Hall of Fame for prestige** — single records, badges of distinction
11. **Pro tier as paid upsell with deeper analytics** — same monetization model
12. **Supporters program** — operators can sponsor / support the project

## What we deliberately do NOT copy

1. **Tank-specific data structures** — our "tanks" are metrics, which are flatter
2. **Battle-by-battle replay** — we don't have battles; we have sessions
3. **Wargaming brand attachment** — SigRank is platform-agnostic
4. **Hero Battles' single-event focus** — replaced with class-tier event leaders

---

## Summary

The BlitzStars structural map is the locked frontend architecture. Every page on SigRank has a clear BlitzStars analog. The components are already built to fit this structure. The data model already supports it. The deployment topology supports the precompute pattern that makes it fast.

When in doubt during the build, ask: **what would BlitzStars do?** That's the answer.
