# MO§ES™ — Raw Stats
_Sources: Token Dashboard API (localhost:8080) + ccusage_report.md · Generated: 2026-05-14_
_Pricing: Opus $15/$75/$1.5/$18.75/$30 per M · Sonnet $3/$15/$0.30/$3.75/$6 per M_

---

## All-Time Overview

| Metric | Value |
|--------|-------|
| **Sessions** | 81 |
| **Turns** | 17,456 |
| **Input (fresh)** | 357,738 |
| **Output** | 7,896,058 |
| **Cache Read** | 2,437,929,023 (2.44B) |
| **Cache Create (5m)** | 24,181,130 |
| **Cache Create (1h)** | 91,740,937 |
| **Cache Create (total)** | 115,922,067 |
| **Total Tokens** | ~2,562,105,826 |
| **Total Cost (API rates)** | **$4,265.21** |
| **Actual Plan Cost** | $100/mo Max |
| **API Value : Plan Cost** | ~42.6× |

---

## Time Window Comparison

| Metric | 7 Days (May 8–14) | 30 Days (Apr 14–May 14) | 90 Days (Feb 13–May 14) | All Time |
|--------|-------------------|------------------------|------------------------|----------|
| **Input (fresh)** | 123,246 | 145,324 | 357,743 | 357,738 |
| **Output** | 3,902,803 | 6,183,115 | 7,896,800 | 7,896,058 |
| **Cache Read** | 1,084,399,183 | 1,680,621,842 | 2,438,550,337 | 2,437,929,023 |
| **Cache Create** | 34,826,779 | 76,555,069 | 115,923,631 | 115,922,067 |
| **Total Tokens** | 1,123,252,011 | 1,763,505,350 | 2,562,728,511 | 2,562,105,826 |
| **Cache Hit Rate** | **99.9886%** | **99.9914%** | **99.9853%** | **99.9985%** |
| **Output : Fresh Input** | **31.7×** | **42.5×** | **22.1×** | **22.1×** |
| **Sessions (dashboard)** | 21 | 46 | 79 | 81 |
| **Turns (dashboard)** | 7,327 | 11,280 | 17,347 | 17,456 |
| **Est. Cost (dashboard)** | $1,564.47 | $3,201.32 | $4,261.49 | $4,265.21 |

---

## Model Split — All Time

| Model | Turns | Input | Output | Cache Read | Cache Create | **Cost (API)** |
|-------|-------|-------|--------|------------|--------------|----------------|
| **claude-opus-4-7** | 3,152 | 52,871 | 2,901,405 | 750,770,376 | 37,926,080 | **$2,464.53** |
| claude-sonnet-4-6 | 8,109 | 130,999 | 3,930,521 | 1,321,305,242 | 53,412,918 | **$736.81** |
| **claude-opus-4-6** | 1,509 | 105,635 | 674,360 | 318,442,467 | 17,446,468 | **$1,046.30** |
| claude-haiku-4-5 | 966 | 68,218 | 389,677 | 48,018,956 | 7,130,780 | **$17.73** |
| **Total** | **13,846** | **357,723** | **7,895,963** | **2,438,537,041** | **115,916,246** | **$4,265.37** |

### Opus 4.6 vs Opus 4.7 — Head to Head

| Metric | Opus 4.6 | Opus 4.7 | Δ |
|--------|----------|----------|---|
| Turns | 1,509 | 3,152 | Opus 4.7 2.1× more turns |
| Output tokens | 674,360 | 2,901,405 | Opus 4.7 4.3× more output |
| Cache Read | 318.4M | 750.8M | Opus 4.7 2.4× more cache leverage |
| **Cost** | **$1,046.30** | **$2,464.53** | Opus 4.7 2.4× higher cost |
| Cost/turn | $0.694 | $0.782 | Opus 4.7 12.7% more per turn |
| Output/turn | 447 tokens | 920 tokens | Opus 4.7 2.1× more output/turn |
| Period active | Feb–Apr 2026 | Apr–May 2026 | Fully transitioned by May |

---

## 7-Day Window — Benchmark Period (May 8–14)

_This is the window closest to the MO§ES™ PDF benchmark (PDF window: 7 days, 20 sessions, 7,235 turns)_

| Metric | Value | PDF Benchmark |
|--------|-------|---------------|
| Total Tokens | 1,123,252,011 | 1.14B |
| Cache Hit Rate | 99.9886% | 96.97% (AA methodology) |
| Output : Fresh Input | **31.7×** | 30.1× |
| Sessions | 21 | 20 |
| Turns | 7,327 | 7,235 |
| Est. Cost (API-equiv) | $1,564.47 | $1,516.61 |

> **Note on cache hit rate discrepancy:** ccusage/dashboard measures only sessions where caching is active and counts at token level. The PDF's 96.97% uses Artificial Analysis's methodology (measured across benchmark task runs which include cold-start overhead tokens). Both are valid; they measure different things.

---

## Monthly Breakdown (from ccusage, API rates)

| Month | Total Tokens | Cost | Opus 4.6 | Opus 4.7 | Sonnet 4.6 | Haiku |
|-------|-------------|------|----------|----------|------------|-------|
| Feb 2026 | 13,855,647 | $10.09 | $6.87 | — | $0.42 | $2.80 |
| Mar 2026 | 111,738,443 | $67.89 | $32.21 | — | $31.77 | $3.91 |
| Apr 2026 | 890,933,507 | $608.38 | $240.76 | $150.65 | $211.50 | $5.47 |
| May 2026 (to date) | 1,525,109,644 | $920.07 | — | $517.95 | $398.99 | $3.14 |
| **TOTAL** | **2,541,637,241** | **$1,606.43** | **$279.84** | **$668.60** | **$642.68** | **$15.32** |

---

## Top Sessions (from ccusage)

| # | Session | Cost | Last Active | Models |
|---|---------|------|-------------|--------|
| 1 | CIVITAE | $341.14 | 2026-05-11 | Sonnet 4.6, Opus 4.6, Opus 4.7 |
| 2 | application hub | $244.09 | 2026-05-14 | Sonnet 4.6, Opus 4.7 |
| 3 | application hub→wt/nostalgic goldstine | $201.60 | 2026-05-14 | Sonnet 4.6, Opus 4.7 |
| 4 | Commitment Theory | $152.55 | 2026-05-09 | Sonnet 4.6, Opus 4.7 |
| 5 | ~/openclaw | $117.22 | 2026-04-17 | Opus 4.6, Sonnet 4.6, Haiku, Opus 4.7 |
| 6 | Thread Workspace | $117.13 | 2026-05-02 | Opus 4.7, Sonnet 4.6 |
| 7 | mcp eval | $76.66 | 2026-05-14 | Sonnet 4.6, Opus 4.7 |
| 8 | GPT WorkFlow | $50.53 | 2026-05-04 | Sonnet 4.6, Opus 4.6, Opus 4.7 |
| 9 | Thread Workspace projects 06 v5 | $49.41 | 2026-05-04 | Opus 4.7, Sonnet 4.6 |
| 10 | application hub [sub] | $38.24 | 2026-05-12 | Sonnet 4.6, Opus 4.7, Haiku |
| | **68 sessions total** | **$1,606.43** | | |

---

## The 5 Benchmark Categories — MO§ES™ Numbers

| Category | 7-Day Value | 30-Day Value | All-Time | PDF Benchmark | Field Best |
|----------|------------|-------------|---------|---------------|------------|
| **Cache Hit Rate** | 99.99% | 99.99% | 99.99% | 96.97% | 96% (AA method) |
| **Output : Input** | 31.7× | 42.5× | 22.1× | 30.1× | 0.38× |
| **Est. Cost / session** | $74.50 | $69.59 | $52.65 | $0.017/task* | $0.07/task* |
| **Total Tokens / session** | 53.5M | 38.3M | 31.6M | 787K/task* | 2.74M/task* |
| **Time / session** | — | — | — | 1.8 min/task* | 5.8 min/task* |

> *Task vs Session: AA field uses benchmark "tasks" (~1 exchange per task). MO§ES™ sessions are full multi-turn working sessions. The PDF benchmark cost-per-task ($0.017) is calculated differently — see PDF methodology note.

---

_Token Dashboard API: http://127.0.0.1:8080 · Data window: 2026-02-21 through 2026-05-14_
_Pricing source: token-dashboard/pricing.json (Opus $15/$75 per M, Sonnet $3/$15 per M)_
