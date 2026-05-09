# CLAUDE.md — Signal Army Ecosystem
## Orientation for Claude Code / VS Code Agent

This file is your entry point. Read it fully before touching anything.

---

## What This Is

This is the **Signal Army Ecosystem** — a signal/noise measurement and classification
system for natural language, built by Luthen (Deric McHenry), Ello Cello LLC.

The ecosystem measures **information density, commitment, and signal-to-noise ratio**
in conversation corpora. It has been run against a full GPT export (~371 conversations,
8 months, July 2025 – March 2026).

There is an associated research paper on **Conservation Law for Commitment** — the
mathematical claim that irreducible meaning kernels are invariant under
loss-inducing transformations. Zenodo DOIs exist. This is real published work.

---

## Folder Structure

```
sig_army/
├── CLAUDE.md                  ← you are here
└── main /                     ← NOTE: folder name has trailing space, always quote paths
    ├── signal_army/
    │   ├── signal_army.py     ← Core tool v1.5 — word inventory & force ranking
    │   └── runs/              ← All run outputs (never delete)
    │       └── full_gpt_export/
    │           ├── run_2026-03-18_18-32-36/      ← Signal Army, user messages
    │           ├── sigsystem/run_.../             ← SIGSYSTEM run
    │           ├── assistant_run/run_.../         ← Signal Army, assistant messages
    │           ├── sigtoken/run_.../              ← SigToken v1 (original)
    │           └── sigtoken_v2/
    │               ├── user_run/                  ← SigToken v2, user
    │               ├── assistant_run/             ← SigToken v2, assistant
    │               ├── user_recursive/            ← Recursive scorer, user ← BEST
    │               └── assistant_recursive/       ← Recursive scorer, assistant ← BEST
    ├── sigsystem/             ← SIGSYSTEM 5-stage pipeline (separate tool)
    ├── sigtoken/              ← SigToken v1.0 (original, has known tuning issues)
    ├── sigtoken_v2/
    │   ├── sigtoken_v2.py     ← Flat scorer v2 (fixed commitment + SNR ceiling)
    │   └── sigtoken_recursive.py ← TWO-PASS recursive scorer ← CANONICAL VERSION
    ├── thread_map/
    │   ├── thread_map.py      ← Thread topology analyzer
    │   ├── runs/              ← Thread map outputs (CSV + txt)
    │   ├── obsidian_vault/    ← Single vault (user messages)
    │   └── obsidian_vaults/   ← Three vaults: user/, assistant/, combined/
    └── reference/             ← Spec files, diagrams, lineage docs
```

---

## The Tools — What Each Does

### 1. signal_army.py
**Purpose:** Word inventory and force ranking across a conversation corpus.

Extracts all words from GPT export JSON, ranks them by frequency into an 8-tier
military rank system:

| Rank | Threshold | Meaning |
|------|-----------|---------|
| Officer-Class | Top 0.5% | Core domain vocabulary |
| Doctrine Builder | Top 1% | High-frequency domain terms |
| Division | Top 2% | ... |
| Platoon | Top 5% | ... |
| Squad | Top 10% | ... |
| Fireteam | Top 20% | ... |
| Scout | Top 35% | ... |
| Infantry | Everything else | |

**Key outputs:** `word_inventory.csv`, `flattened_messages.csv`, `signal_army_summary.txt`

**CLI:**
```bash
python signal_army.py --json conversations.json --output-dir ./runs/
python signal_army.py --json conversations.json --role assistant --output-dir ./runs/
python signal_army.py --json conversations.json --role all --output-dir ./runs/
```

**--role flag:** `user` (default) | `assistant` | `all`

---

### 2. sigtoken_recursive.py  ← USE THIS ONE
**Purpose:** Contextual token SNR classification using thread-aware two-pass scoring.

Component C-0005 | Origin: Oct 1 2025 spec files

**The core insight (classification_logic.md, Oct 1 2025):**
> "Words and tokens are not inherently signal or noise. Their classification
> depends entirely on contextual function, relational placement, frequency,
> and contribution to compression."

**Two-pass architecture:**
- Pass 1: Thread-local IDF — each word scored within its own thread context
- Pass 2: Corpus validation — words promoted to dynamic anchors bottom-up

**Three-tier taxonomy:**
- Signal — intent-bearing, load-carrying
- Scaffolding — neutral structure (articles, prepositions, pronouns)
- Noise — filler, replaceable, low contribution

**Commitment Score formula:**
```
commitment = signal_purity × 0.50 + avg_signal_SW × 0.30 + length_factor × 0.20

where:
  signal_purity   = signal_tokens / (signal_tokens + noise_tokens)
  avg_signal_SW   = mean SW of signal-tier tokens
  length_factor   = 1.0 if ≤3 active tokens (maximally irreducible)
                    0.90 if ≤8 tokens
                    0.75 if ≤20 tokens
                    0.60 if ≤50 tokens
                    max(0.40, 0.60 - (n-50)×0.001) for longer messages
```

Short irreducible messages score higher than long padded ones.
"yes please" scores ~0.89. A 200-word padded response scores ~0.75.

**SNR formula (v2 — scaffolding excluded from both sides):**
```
SNR_normalized = signal_count / (signal_count + noise_count)
SNR_ratio      = signal_count / noise_count
SNR_dB         = 10 × log10(SNR_ratio)
```

**CLI:**
```bash
python sigtoken_recursive.py \
  --messages flattened_messages.csv \
  --word-inventory word_inventory.csv \
  --output-dir ./runs/
```

---

### 3. thread_map.py
**Purpose:** Thread topology analyzer — maps 362 threads as a network.

**Outputs:**
- `thread_nodes.csv` — one row per thread with timeline + metadata
- `thread_edges.csv` — pairwise Jaccard similarity between threads
- `concept_stitches.csv` — concepts that resurfaced across threads (gap ≥ 7 days)
- `drift_events.csv` — drift signature detection (474 events found)
- `timeline.csv` — chronological thread order

**Drift detection signature:**
Long user messages (avg >30 tokens) → sudden burst of short messages (avg <8 tokens).
This is the system losing the kernel and the user recompressing it back in.
474 events detected. Strongest: 441x compression drop in "MO§ES and OpenAI Grove".

**Obsidian vaults** (ready to open):
```
thread_map/obsidian_vaults/user_vault.zip
thread_map/obsidian_vaults/assistant_vault.zip
thread_map/obsidian_vaults/combined_vault.zip
```
Open folder as vault in Obsidian → Ctrl+G for graph view.

**CLI:**
```bash
python thread_map.py --messages flattened_messages.csv --output-dir ./runs/
```

---

## Key Results (Full GPT Export — 371 conversations)

### Signal Army
| Metric | User | Assistant |
|--------|------|-----------|
| Messages | 14,352 | 15,336 |
| Total words | 710,760 | 2,331,850 |
| Unique words | 26,501 | 49,311 |
| Officer-Class words | 1,325 | 2,986 |

### SigToken Recursive (canonical)
| Metric | User | Assistant |
|--------|------|-----------|
| Avg Commitment | 0.8813 | 0.8522 |
| SNR (normalized) | 0.9673 | 0.9713 |
| Dynamic anchors built | 12,848 | 21,302 |

### Thread Map
- 362 unique threads
- 27,338 thread connections (similarity ≥ 0.05)
- 474 drift events
- Corpus: July 10 2025 → March 15 2026

---

## Critical Path Notes

**DO NOT mix run outputs.** Each run folder is timestamped and immutable.
New runs always create new timestamped subdirectories.

**Folder name has a trailing space:** `main /` not `main/`
Always quote paths: `"/path/to/main /signal_army/"`

**The canonical scorer is sigtoken_recursive.py.**
sigtoken_sys.py (v1) and sigtoken_v2.py exist for comparison only.
v1 had a domain_density bleed bug. v2 fixed SNR ceiling but is flat.
The recursive version is the correct architecture.

**Officer-Class words are the seed layer for sigtoken_recursive.**
Always pass `--word-inventory` when running against a new corpus.
The system promotes additional words dynamically — do not hardcode anchors.

---

## Pending Work / Known Issues

1. **Concept stitch filter** — still passing some generic 4-char words.
   Needs min_threads tightening (currently 3, should be 5-7).
   promotion_threshold should raise from 0.35 to 0.50.

2. **Drift detection needs combined corpus** — currently only runs on user messages.
   Running against combined CSV would show both sides of the drift/recovery cycle.

3. **Paper evolution vault** — not yet built. Paper files need to be uploaded.
   Target: Obsidian vault mapping each draft version + suggestion overlay showing
   things proposed but never incorporated.

4. **SNR ceiling** — too many threads scoring 1.0 at the top of the leaderboard.
   Thread leaderboard needs more variance. Consider penalizing thread length in
   the thread-level SNR aggregation.

---

## Research Paper Context

**Title:** Conservation Law for Commitment
**Claim:** Commitment kernels are invariant under loss-inducing transformations.
**Published:** Zenodo (DOIs exist)
**Component:** C-0005 (SigToken) is the measurement tool for the paper's claims.

The paper's core assertion: when you compress a message to its irreducible meaning
kernel, that kernel is conserved across transformations — summarization, translation,
paraphrase. The commitment score measures proximity to that kernel.

All scoring infrastructure here was built to operationalize and test that claim
on real data.

---

## If You Are Running Tools

1. Always check which run folder you're using — newest is usually best
2. Pass `--word-inventory` to sigtoken_recursive.py for domain anchors
3. New outputs go in new timestamped dirs — never overwrite existing runs
4. The combined_all.json lives at:
   `main /signal_army/runs/full_gpt_export/combined_all.json`
   This is all 4 GPT export files merged (371 conversations total)

---

*Last updated: 2026-03-19 by Cowork session*
*Ecosystem: Signal Army v1.5 | SigToken C-0005 v2.1 | ThreadMap v0.1*
*Owner: Luthen / Ello Cello LLC*
