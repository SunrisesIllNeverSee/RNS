# Session 001 — Signal Army Build (v1.0 → v1.4)

**Date:** 2026-03-02
**Time:** ~02:00 – 06:30 (approx)
**Tool:** Claude Code (Opus)
**Starting state:** Empty project, doctrine source only
**Ending state:** Signal Army v1.4 running with division clustering

---

## What Was Built

### v1.0 — Foundation
- Created `signal_army.py` from scratch
- 4 classes: MarkdownParser, ConversationFlattener, SignalArmyAnalyzer, ReportGenerator
- Markdown + JSON parsing (ChatGPT export format)
- Word tokenization and counting
- 8-tier rank system: Scout → Fireteam → Squad → Platoon → Division → Doctrine Builder → Officer-Class
- Phrase inventory (bigrams/trigrams)
- CSV + TXT dashboard output
- CLI with --md, --md-dir, --json, --output-dir flags

### v1.1 — MO§ES Compound Word Fix
- Added COMPOUND_WORDS normalization (`mo§es` → `moses`, special character variants)
- Separated rank tier reporting in summary

### v1.2 — Infantry & Timestamped Runs
- Added Infantry rank (105 common words rank-capped regardless of frequency)
- Infantry field connections (what high-signal words march with each infantry word)
- Timestamped run output directories (`runs/run_YYYY-MM-DD_HH-MM-SS/`)

### v1.3 — Lightweight Stemmer
- Added suffix stripping for plurals (-s), possessives (-'s), -ing, -ed, -ly
- NO_STEM protection list for domain words (moses, fracto, abba, aaron, analysis, coherence, etc.)
- Prevents over-counting of inflected forms

### v1.4 — Thematic Division Clustering
- Paragraph-level co-occurrence affinity (not message-level — messages are entire transcripts up to 35k words)
- Affinity metric: `co_occurrence / min(para_count_w1, para_count_w2)`, threshold 0.15
- Greedy seed clustering: Officers seed first, pull unassigned neighbors by affinity
- Division naming: top 2 words + rotating military suffix
- Tested at cap sizes 10, 15, 20 — chose cap 10 (tightest thematic clusters)

---

## Key Decisions Made

| Decision | Reasoning |
| --- | --- |
| Paragraph-level windowing (not message-level) | Messages are entire transcripts (up to 35k words). Message-level co-occurrence makes everything co-occur with everything. Paragraphs (`\n\n` split) produce meaningful thematic windows. |
| Cap 10 members per division (not 15 or 20) | Cap 15: every division hit max, diluted clusters. Cap 20: even worse. Cap 10: sub-themes split naturally (e.g., Lineage and Cryptographic separated into distinct divisions). |
| Infantry words are soldiers, not excluded | Doctrine: "Noise isn't failure — it's the infantry." Common words carry signal when they march with Officers. Rank-capped, not removed. |
| Lightweight stemmer over full NLP | Zero external dependencies. Simple suffix stripping handles 90%+ of cases. Protected word list prevents domain terms from being damaged. |

---

## Run Stats (Final v1.4 Run, Cap 10)

- **Total words deployed:** 76,313
- **Unique words:** 7,807
- **Officers:** 85
- **Doctrine Builders:** 166
- **Division-rank:** 505
- **Thematic divisions formed:** 90
- **Words clustered into divisions:** 722
- **Input files:** 24 markdown transcripts
- **Top officers:** system (678), moses (615), build (472), ai (436), compression (423), signal (409)

---

## Files Created / Modified

| File | Action |
| --- | --- |
| `main /tool/signal_army.py` | Created (v1.0), iterated through v1.4. Final: 1,252 lines. |
| `main /runs/run_2026-03-02_04-42-00/` | v1.2 run output |
| `main /runs/run_2026-03-02_04-46-51/` | v1.3 run output |
| `main /runs/run_2026-03-02_04-48-54/` | v1.3 re-run |
| `main /runs/run_2026-03-02_06-03-50/` | v1.4 run (cap 15) |
| `main /runs/cap_test_10/run_2026-03-02_06-26-06/` | v1.4 cap 10 test |
| `main /runs/cap_test_20/run_2026-03-02_06-26-14/` | v1.4 cap 20 test |

---

## Next Steps Identified (at session end)

1. Deep dive the outside reference documents
2. Compare SIGSYSTEM architecture to Signal Army
3. Process the chatfiles (944a.json, 944b.json) — deferred per user instruction
