# MO§ES™ — 5 Benchmark Categories
_Source: Token Dashboard API + ccusage · Generated: 2026-05-14_

---

## 1. Cache Hit Rate
_Cache Read ÷ (Cache Read + Cache Create + Fresh Input) — higher is better_

| Window | Cache Read | Cache Create | Fresh Input | **Cache Hit Rate** |
|--------|----------:|-------------:|------------:|-------------------:|
| **7 Days** | 1,084,399,183 | 34,826,779 | 123,246 | **96.88%** |
| **30 Days** | 1,680,621,842 | 76,555,069 | 145,324 | **95.64%** |
| **90 Days** | 2,438,550,337 | 115,923,631 | 357,743 | **95.45%** |
| **All Time** | 2,437,929,023 | 115,922,067 | 357,738 | **95.45%** |

---

## 2. Output : Fresh Input
_Output tokens per fresh (non-cached) input token — higher is better_

| Window | Output | Fresh Input | **Ratio** |
|--------|-------:|------------:|----------:|
| **7 Days** | 3,902,803 | 123,246 | **31.7×** |
| **30 Days** | 6,183,115 | 145,324 | **42.5×** |
| **90 Days** | 7,896,800 | 357,743 | **22.1×** |
| **All Time** | 7,896,058 | 357,738 | **22.1×** |

---

## 3. Cost per LOC
_API-equivalent cost per line of code shipped — lower is better_
_Scope: App Hub build · 7-day window only · wc -l verified_

| Scope | LOC | Cost Basis | **Cost / LOC** | **LOC / $** |
|-------|----:|------------|---------------:|------------:|
| 35,242 | 35,242 | API equiv ($1,564.47) | **$0.0444** | **22.5** |
| 35,242 | 35,242 | ccusage ($643.80) | **$0.0183** | **54.7** |
| 35,242 | 35,242 | Plan ($100/mo × 7d) | **$0.0007** | **1,510** |

**LOC breakdown (wc -l, honest count — generation is generation):**

| Source | Path | LOC |
|--------|------|----:|
| App TS/TSX | app/**/*.ts + app/**/*.tsx (excl. node_modules, .next) | 23,692 |
| Migrations SQL | migrations/*.sql (38 files, top-level) | 6,876 |
| MCP Server TS | application-hub-mcp-server/src/**/*.ts | 4,060 |
| Scripts | scripts/ (previously missed) | 614 |
| **Total** | | **35,242** |

> Rule: all output traces to the operator who caused it. Generated types, machine-produced DDL, and scripts are all counted. Supabase/migrations/ (41 files, 7,042 LOC) excluded — mirrors canonical migrations/, not additive output.

---

## 4. Cost per Session
_API-equivalent cost per session (est. cost ÷ sessions) — lower is better_

| Window | Est. Cost | Sessions | **Cost / Session** |
|--------|----------:|---------:|-------------------:|
| **7 Days** | $1,564.47 | 21 | **$74.50** |
| **30 Days** | $3,201.32 | 46 | **$69.59** |
| **90 Days** | $4,261.49 | 79 | **$53.94** |
| **All Time** | $4,265.21 | 81 | **$52.65** |

---

## 4. Tokens per Session
_Total tokens consumed per session — lower is better_

| Window | Total Tokens | Sessions | **Tokens / Session** |
|--------|-------------:|---------:|---------------------:|
| **7 Days** | 1,123,252,011 | 21 | **53.49M** |
| **30 Days** | 1,763,505,350 | 46 | **38.34M** |
| **90 Days** | 2,562,728,511 | 79 | **32.44M** |
| **All Time** | 2,562,105,826 | 81 | **31.63M** |

---

## 5. Turns per Session
_Average turns per session (wall-time proxy) — context on session depth_

| Window | Turns | Sessions | **Turns / Session** |
|--------|------:|---------:|--------------------:|
| **7 Days** | 7,327 | 21 | **348.9** |
| **30 Days** | 11,280 | 46 | **245.2** |
| **90 Days** | 17,347 | 79 | **219.6** |
| **All Time** | 17,456 | 81 | **215.5** |

---

## Opus 4.6 vs Opus 4.7 — Split by Days Active

### Active Days

| Model | First Active | Last Active | Total Active Days |
|-------|-------------|-------------|:-----------------:|
| **Opus 4.6** | 2026-02-25 | 2026-04-16 | 16 days |
| **Opus 4.7** | 2026-04-17 | 2026-05-14 | 28 days (ongoing) |

---

### Benchmark 1 — Cache Hit Rate

| Model | Cache Read | Cache Create | Fresh Input | **Cache Hit Rate** |
|-------|----------:|-------------:|------------:|-------------------:|
| **Opus 4.6** | 318,442,467 | 17,446,468 | 105,635 | **94.78%** |
| **Opus 4.7** | 750,770,376 | 37,926,080 | 52,871 | **95.18%** |

---

### Benchmark 2 — Output : Fresh Input

| Model | Output | Fresh Input | **Ratio** |
|-------|-------:|------------:|----------:|
| **Opus 4.6** | 674,360 | 105,635 | **6.4×** |
| **Opus 4.7** | 2,901,405 | 52,871 | **54.9×** |

---

### Benchmark 3 — Cost per Turn

| Model | Total Cost | Turns | **Cost / Turn** |
|-------|----------:|------:|----------------:|
| **Opus 4.6** | $1,046.30 | 1,509 | **$0.694** |
| **Opus 4.7** | $2,464.53 | 3,152 | **$0.782** |

---

### Benchmark 4 — Tokens per Turn

| Model | Cache Read | Output | Total Tokens | Turns | **Tokens / Turn** |
|-------|----------:|-------:|-------------:|------:|------------------:|
| **Opus 4.6** | 318,442,467 | 674,360 | ~336,768,930 | 1,509 | **223.2K** |
| **Opus 4.7** | 750,770,376 | 2,901,405 | ~791,650,732 | 3,152 | **251.2K** |

---

### Benchmark 5 — Output per Turn

| Model | Output | Turns | **Output Tokens / Turn** |
|-------|-------:|------:|-------------------------:|
| **Opus 4.6** | 674,360 | 1,509 | **447** |
| **Opus 4.7** | 2,901,405 | 3,152 | **921** |

Opus 4.7 produces **2.1× more output per turn** than Opus 4.6.

---

## Opus 4.6 vs Opus 4.7 — Daily Cost During Active Periods

### Opus 4.6 Active Days (Feb 25 – Apr 16)
| Date | Cost |
|------|-----:|
| 2026-02-25 | $0.49 |
| 2026-02-26 | $3.67 |
| 2026-02-27 | $0.29 |
| 2026-02-28 | $2.42 |
| 2026-03-02 | $10.25 |
| 2026-03-03 | $6.56 |
| 2026-03-04 | $12.85 |
| 2026-03-05 | $0.21 |
| 2026-03-06 | $2.33 |
| 2026-04-08 | $36.59 |
| 2026-04-09 | $11.09 |
| 2026-04-10 | $48.11 |
| 2026-04-12 | $74.49 |
| 2026-04-14 | $3.12 |
| 2026-04-15 | $53.22 |
| 2026-04-16 | $14.14 |
| **Total (16 days)** | **$279.83** |
| **Avg / active day** | **$17.49** |

### Opus 4.7 Active Days (Apr 17 – May 14)
| Date | Cost |
|------|-----:|
| 2026-04-17 | $13.07 |
| 2026-04-25 | $80.26 |
| 2026-04-30 | $57.32 |
| 2026-05-01 | $100.86 |
| 2026-05-02 | $2.98 |
| 2026-05-03 | $18.11 |
| 2026-05-04 | $34.70 |
| 2026-05-05 | $3.44 |
| 2026-05-08 | $16.70 |
| 2026-05-09 | $13.43 |
| 2026-05-10 | $116.82 |
| 2026-05-11 | $108.43 |
| 2026-05-12 | $78.03 |
| 2026-05-13 | $4.91 |
| 2026-05-14 | $19.54 |
| **Total (15 active days in 28-day span)** | **$668.61** |
| **Avg / active day** | **$44.57** |

> Opus 4.7 average daily cost is **2.5× higher** than Opus 4.6 — reflecting both heavier usage volume and higher output density per turn.
