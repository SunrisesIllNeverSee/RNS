# v4 Mockup — Data Ledger

**Read this before building anything in concrete around the mockup.**

The v4 mockup pages (`intro.html`, `index.html`, `profile.html`) contain a mix of:
- 🟢 **CONCRETE** — real values traceable to a verified source
- 🟡 **STRUCTURAL** — the system concept is real, but the specific number is illustrative
- 🔴 **PLACEHOLDER** — purely fabricated for visual demonstration

**Do not architect decisions around 🔴 PLACEHOLDER values.** If a number is needed for a real build decision, get it from the source listed in the 🟢 CONCRETE rows.

---

## 🟢 CONCRETE — Hardwired, sourced, build-safe

### Repo + spec
| What | Value | Source |
|---|---|---|
| Core 5 metric names | Compression Ratio, Prompt Complexity, Cross-Thread, Session Depth, Token Throughput | `1_sigrank/1.2_layer-1-foundation/metrics/00_README.md` |
| Background 3 metrics | Message Volume, Account Age, Total Messages | spec |
| Big 3 (composites inside the 11 core) | SIGNA RATE, SDOT, SDRM | spec (corrected 2026-05-21 — SDOT/SDRM restored) |
| Extras (outside the 11 core) | Signal Force (E.01 · sigalpha), Drift Ratio (E.02 · sigdrift / Sig Delta) | spec |
| Total active metrics | 11 core + 2 extras | spec |
| 9 class tier names | TRANSMITTER, ARCHITECT+, ARCHITECT, POWER, BASE, SEEKER, REFINER, BEARER, IGNITER | v1 codex + spec |
| Compression formula concept | `Signal / (Signal + Noise)` bounded [0,1] | screenshot arithmetic |
| Compression example: 703,944 / 822,902 = 0.8554 | Real arithmetic | screenshot in GPT thread-0369 |
| TRANSMITTER class cut | Compression ≥ 0.85 | v1 codex |
| Codename "TransVaultOrigin" | Real | K2 reports + GPT thread |
| Codename "MOSES" / "MO§ES" | Real | Evaluation Metrics Tracing |
| Signing scheme | Ed25519 | spec |

### MO§ES 7-day benchmark (verified from `summary.json`)
| What | Value | Source |
|---|---|---|
| Window | 2026-05-08 → 2026-05-14 | `summary.json` |
| Files found | 98 | `summary.json` |
| Sessions with turns | 97 | `summary.json` |
| Total turns | 9,332 (full export) / **7,327** (top sessions in poster) | `summary.json` totals |
| Fresh input tokens | 331,214 (full) / **123,246** (poster window) | `summary.json` |
| Output tokens | 5,935,260 (full) / **3,902,803** (poster window) | `summary.json` / poster |
| Cache read | 1,425,781,478 (full) / **1,084,399,183** (poster) | `summary.json` |
| Cache creation | 80,029,869 (full) / **34,826,779** (poster) | `summary.json` |
| Total tokens | 1,512,077,821 (full) / **1.12B** (poster) | `summary.json` |
| Cache hit rate (poster window) | 96.88% | `extract_benchmark_window.py` |
| Output : Fresh Input ratio | 31.7× (7d window in poster) | poster |
| Cost / LOC | $0.0007 (plan) / $0.044 (API) | poster |
| LOC shipped | 35,242 | poster (wc -l verified) |
| Time / task | 1.84 min | poster |
| 30-day Output:Input ratio | 42.5× | poster |
| 90-day Output:Input ratio | 22.1× | poster |
| Account age (operator) | 119 days | poster |
| Top model | Claude Opus 4.7 | poster |
| Sessions count (top sessions) | 21 | poster |

### Real session/project names (from `summary.json`)
The threads shown in profile.html "Session Breakdown" are pulled from actual Claude Code session files:
- `application-hub` (real project)
- `Commitment-Theory` (real project)
- `CIVITAE` (real project)
- `Thread-Workspace-projects-06-v5` (real project)
- `GPT-WorkFlow` (real project)
- `rns` (real project — this repo)
- `mcp-eval` (real project)
- `Pickle-AI` (real project)
- `kd` (real project)

The **turn counts** for these threads on the profile page ARE NOT directly from the summary.json; they are illustrative numbers in a similar order of magnitude. See 🟡 below.

---

## 🟡 STRUCTURAL — Real concept, illustrative number

### Profile page session breakdown
| Thread name | Shown msgs | Real source value | Status |
|---|---|---|---|
| moses-build | 1,327 | application-hub session b38ed464 had 1,327 turns | ✅ matches |
| commitment-theory | 821 | Commitment-Theory d9c6374c had 821 turns | ✅ matches |
| application-hub | 785 | application-hub bc07d0ed had 785 turns | ✅ matches |
| CIVITAE-engine | 670 | CIVITAE 5c922968 had 670 turns | ✅ matches |
| Thread-Workspace-06 | 532 | Thread-Workspace 264742c1 had 532 turns | ✅ matches |
| mcp-eval | 494 | application-hub 1275ef34 had 494 turns | ⚠️ swap |
| rns-sigrank | 350 | application-hub 68ec812b had 350 turns | ⚠️ swap |

Note: the turn counts are **real values** from `summary.json` but the **labels are remapped** to more recognizable project names. If you need to reference actual session metrics, pull from `summary.json` directly.

### Sub-metric values per thread in Session Breakdown
| Field | Status | Note |
|---|---|---|
| SD (avg per thread) | 🟡 illustrative | Real SD per session not computed yet |
| Comp per thread | 🟡 illustrative | Requires sig_army analysis |
| TT per thread | 🟢 derivable | Could be computed from session token totals |
| PC per thread | 🟡 illustrative | Requires sig_army analysis |
| "Last X ago" timestamps | 🟢 derivable | Could be computed from `mtime` in summary.json |

### Profile hero — operator metrics
| Metric | Shown | Status |
|---|---|---|
| SIGNA RATE: 96.4 | Operator's actual computed score | 🟡 illustrative — requires real ruleset application |
| Compression: 0.97 | Computed from Output:Input ratio | 🟢 from poster (0.9694 rounded) |
| Cross-Thread: 37 | 🔴 illustrative | No real CT score computed |
| Session Depth: 26.1 | 🟡 illustrative | Real SD avg is 348.9 turns/session (poster) — not the same scale |
| Token Throughput: 18.4k | 🟡 illustrative | Output volume is real but TT normalization not applied |
| PC: ~92 | 🔴 placeholder | Requires sig_army — not computed |
| SDOT: +4.2 | 🔴 placeholder | Trajectory delta — formula provisional, status locked |
| SDRM: 81 | 🔴 placeholder | Coherence score — formula provisional, status locked |
| Signal Force: 12.8 (extra, not core) | 🔴 placeholder | Now extras layer — formula real, values not plugged in |
| Streak: 38 days | 🔴 placeholder | Not computed |
| Best Ever rank: #1 since 2026-05-14 | 🔴 placeholder | No actual rank history |
| Audit Verified status | 🔴 placeholder | No audit performed |

### Profile drilldown — Snapshot History
All 7 rows of historical snapshots (2026-05-14, 2026-05-13, 2026-05-07, etc.) are 🔴 **PLACEHOLDER**. Real snapshot history would require persisting computed metrics over time, which hasn't been built yet.

### Profile Analytics Dashboard
| Component | Status |
|---|---|
| Radar chart values | 🟡 illustrative — shape based on real Core 5 ratios |
| Activity heatmap intensities | 🔴 placeholder |
| Score trend sparklines | 🔴 placeholder |
| "Top 50 avg" comparison | 🔴 placeholder — there is no Top 50 yet |
| "38 day streak · 119 days active · 21 sessions/month" | 119 days is real, rest 🟡 illustrative |

---

## 🔴 PLACEHOLDER — Fabricated for visual demo only

**Do not build anything around these numbers. They exist only to show what the UI will look like when populated with real data.**

### Hero stats (intro.html)
| Value | Status |
|---|---|
| 38,041 operators ranked | 🔴 placeholder — no real count |
| 1,847 active in last hour | 🔴 placeholder |
| 8,492 snapshots today | 🔴 placeholder |
| 312 operators in TRANSMITTER class | 🔴 placeholder |

### All operator codenames except TransVaultOrigin and MOSES
All of these are 🔴 **PLACEHOLDER** — invented codenames for visual demonstration:

- ArchiveSignal (Berlin, DE) — fictional
- CrossWeaver (Toronto, CA) — fictional
- DeepChannel (Tokyo, JP) — fictional
- GhostRelay (Paris, FR) — fictional
- RiddleSocket (Toronto, CA) — fictional
- PromplexCore (Seoul, KR) — fictional
- QuietGiant (Stockholm, SE) — fictional
- SignalTrace — fictional
- Arch+:24-78344 (Faris, FR) — fictional
- Arch+:24-00971 (Toronto, CA) — fictional
- Power:24-87553 (Tokyo, JP) — fictional
- Power:24-87921 (Dgnis, FR) — fictional
- Base:24-67921 (London, UK) — fictional
- SeekerOmega (Madrid, ES) — fictional
- RefinerPi (Mumbai, IN) — fictional
- Arch+:24-87921 — fictional
- All other generated codenames

All their metric values are 🔴 **PLACEHOLDER**.
All their locations are 🔴 **PLACEHOLDER** (cities are real cities, but the operator-city pairings are fabricated).
All their account ages are 🔴 **PLACEHOLDER**.
All their last-seen timestamps are 🔴 **PLACEHOLDER**.

### Live counter strip
| Value | Status |
|---|---|
| Global Active: 1,847 | 🔴 placeholder |
| Claude: 612 | 🔴 placeholder |
| ChatGPT: 798 | 🔴 placeholder |
| Gemini: 287 | 🔴 placeholder |
| Pi: 88 | 🔴 placeholder |
| Multi: 62 | 🔴 placeholder |

### Today's Signal Leaders (point totals)
| Operator | Today | Total | Status |
|---|---|---|---|
| TransVaultOrigin | +180 / 2,700 | 🔴 placeholder — "signal points" system not built |
| All other rows | 🔴 placeholder |

### Top 10 Daily by metric
The 5 mini-leaderboards on the intro page (COMP, SD, PC, CT, TT top 10s) are entirely 🔴 **PLACEHOLDER** except the TransVaultOrigin/MOSES entries that match real benchmark numbers (Comp 0.97, TT 18.4k).

### Signalgeist 6-card 90-day grid (homepage)
All values 🔴 **PLACEHOLDER** except TransVaultOrigin row entries that match real benchmark numbers.

### Sparkline trend data (every row on leaderboard)
All sparklines are 🔴 **PLACEHOLDER** — generated paths for visual effect, no real trend data backing them.

### Page header stats (index.html)
| Value | Status |
|---|---|
| 38,041 total operators | 🔴 placeholder |
| 1,847 active now | 🔴 placeholder |
| 312 Transmitter-class | 🔴 placeholder |
| 96.4 top SIGNA RATE | 🟡 derivable from MO§ES benchmark |

### Rank medals and pagination
| Value | Status |
|---|---|
| "Showing 1-12 of 38,041" | 🔴 placeholder |
| "Page 1 of 3,170" | 🔴 placeholder |

### Profile rank tiles
| Value | Status |
|---|---|
| Global Rank #1 of 38,041 | 🔴 placeholder |
| Class Rank #1 of 312 Transmitters | 🔴 placeholder |
| Percentile 99.97 | 🔴 placeholder |
| Best Ever #1 since 2026-05-14 | 🔴 placeholder |

### Badges
The badge **system** exists in spec (`1_sigrank/1.3_layer-2-mechanics/db_schema.md` has `badges` and `operator_badges` tables). The **specific badges displayed** on profile.html are 🔴 **PLACEHOLDER** — no badge engine has actually computed any awards yet.

### Conversion section examples (intro.html + profile.html)
| Value | Status |
|---|---|
| "3.90M / 123K" input example | 🟢 from MO§ES |
| "1.08B reads / 1.12B total" example | 🟢 from MO§ES |
| "7,327 turns / 21 sessions" example | 🟢 from MO§ES |
| "3.90M output tokens" example | 🟢 from MO§ES |
| Computed Compression 0.97 | 🟢 from MO§ES |
| Computed CT 37 | 🔴 placeholder |
| Computed SD 26.1 | 🟡 illustrative |
| Computed TT 18.4k | 🟡 illustrative |
| Computed PC ~92 | 🔴 placeholder |

---

## Build guidance

### Numbers that ARE safe to architect around
- The metric stack itself (Core 5, Background 3, Big 3, Extras)
- Compression Ratio formula concept (Signal / Signal+Noise)
- The 9 class hierarchy and ordering
- TRANSMITTER threshold concept (≥ 0.85 Compression)
- BlitzStars-style site structure
- The deployment topology (Supabase + Railway + Vercel + Modal)
- The 11-active-metric count
- Ruleset versioning concept
- MO§ES benchmark window numbers as a reference operator

### Numbers that are NOT safe to architect around
- ANY operator count except 1 (you)
- ANY active-user count
- ANY rank position (no real ranking exists yet)
- ANY platform-specific active count
- ANY trend/sparkline data
- ANY heatmap intensity
- ANY badge award state
- ANY "Top 10" composition except the TransVaultOrigin/MO§ES row
- ANY historical snapshot value
- ANY operator codename except TransVaultOrigin/MO§ES
- ANY geographic distribution

### When to update this ledger
- When real data is generated for any 🔴 row — promote it to 🟢 and cite source
- When the scoring engine produces a real value for an operator other than MOSES — log it here
- When the badge engine awards a real badge — note the operator + badge + date
- When the leaderboard cache is generated for the first time — replace all 🔴 leaderboard rows with the real Top N

### Banner on the mockup pages
Each v4 mockup page includes a fixed banner at the top labeled **"DEMO DATA · See DATA_LEDGER.md"** linking back to this file. The banner stays until real data is wired up.
