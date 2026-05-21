# Signal Army Ecosystem — Workflows, Formulas, and Equations
## Technical Reference Document

**Version:** 2026-03-19
**Author:** Luthen / Ello Cello LLC
**Status:** Living document — updated as tools evolve

---

## Table of Contents

1. Core Theory
2. Signal Army — Word Ranking
3. SIGSYSTEM — 5-Stage Pipeline
4. SigToken — Contextual Classification
5. SigToken Recursive — Two-Pass Architecture
6. Thread Map — Topology Analysis
7. End-to-End Workflow
8. Equation Index

---

## 1. Core Theory

### The Dual-Weight Principle
Every token in a message carries two simultaneous weights:

```
SW (Signal Weight)  — contribution to irreducible meaning
NW (Noise Weight)   — contribution to bloat / replaceability

SW + NW = 1.0  (always)
```

These weights are NOT a property of the word. They are a property of the word
in this position in this message in this thread. Classification resolves at
message level when context collapses the dual state.

Source: `classification_logic.md`, Oct 1 2025 (Component C-0005 origin spec)

---

### The Commitment Kernel
The irreducible meaning kernel of a message is the minimum set of tokens
such that removing any one of them collapses the message's meaning.

**Conservation Law for Commitment (McHenry, 2025):**
> Commitment kernels are invariant under loss-inducing transformations.

That is: summarization, translation, and paraphrase cannot destroy the kernel.
They may compress or re-express it but the kernel's semantic load is conserved.

This is the foundational claim the entire measurement infrastructure is built to test.

---

### Three-Tier Token Taxonomy

| Tier | Definition | Example |
|------|-----------|---------|
| Signal | Intent-bearing, load-carrying, irreplaceable in context | "compression", "kernel", "collapse" |
| Scaffolding | Neutral structure — not signal, not noise | "the", "in", "is", "they" |
| Noise | Filler, replaceable, low semantic contribution | "basically", "just", "lol", "kind of" |

Key: Scaffolding is excluded from BOTH signal and noise counts.
SNR is always computed over Signal and Noise only.

---

## 2. Signal Army — Word Ranking

### Purpose
Build a ranked word inventory from a conversation corpus.
Identifies which words are load-bearing at the corpus level.

### 8-Tier Rank System

| Rank | Percentile Threshold | Role |
|------|---------------------|------|
| Officer-Class | Top 0.5% by frequency | Core domain vocabulary — seed layer for SigToken |
| Doctrine Builder | Top 1% | High-frequency domain terms |
| Division | Top 2% | |
| Platoon | Top 5% | |
| Squad | Top 10% | |
| Fireteam | Top 20% | |
| Scout | Top 35% | |
| Infantry | All remaining | |

### Ranking Formula
```
For each word w with frequency f(w) in corpus of N unique words:

percentile_rank(w) = (rank_by_frequency(w) / N) × 100

Rank assignment:
  percentile_rank ≤ 0.5  → Officer-Class
  percentile_rank ≤ 1.0  → Doctrine Builder
  percentile_rank ≤ 2.0  → Division
  ... etc.
```

### Key Outputs
- `word_inventory.csv` — all words with rank, frequency, token mass
- `flattened_messages.csv` — one row per message with metadata
- `division_inventory.csv` — Division-rank and above only
- `phrase_inventory.csv` — multi-word phrases (bigrams/trigrams)

### Token Mass
```
token_mass(w) = frequency(w) × length(w)

Rationale: longer words that appear frequently carry more "mass" in the corpus.
Used in SIGSYSTEM for weight calculations.
```

---

## 3. SIGSYSTEM — 5-Stage Pipeline

### Purpose
Full signal/noise classification pipeline with dual weights, SNR metrics,
and decay tracking. Operates at the message and session level.

### 5 Stages

```
Stage 1: INGESTION
  Raw text → tokenized message stream
  Applies normalization (MO§ES™ → moses, etc.)

Stage 2: DUAL-WEIGHT ASSIGNMENT
  Each token → (SW, NW) pair
  SW + NW = 1.0
  Uses corpus frequency + static taxonomy

Stage 3: MESSAGE-LEVEL RESOLUTION
  Per-message aggregation of dual weights
  Computes: signal_count, noise_count, scaffolding_count
  SNR_message = signal_count / noise_count

Stage 4: DECAY TRACKING
  Tracks how signal quality changes across messages in a thread
  decay_rate = Δ(SNR) / Δ(message_index)
  Identifies drift events where decay accelerates

Stage 5: SESSION AGGREGATION
  Corpus-level SNR, commitment distribution, leaderboard
  Outputs: summary.txt, summary.json
```

### SNR Formulas (SIGSYSTEM)
```
SNR_ratio      = signal_tokens / noise_tokens
SNR_normalized = signal_tokens / total_tokens  (includes scaffolding in denominator)
SNR_dB         = 10 × log10(SNR_ratio)
```

Note: SIGSYSTEM uses total_tokens in denominator (includes scaffolding).
SigToken v2+ excludes scaffolding from both sides — see Section 5.

---

## 4. SigToken v1 — Contextual Classification (C-0005)

### Origin
Spec files created October 1, 2025. Component ID: C-0005.
Parent lineage: SCS Engine.

### Core Scoring (v1 — has known issues, see v2)

```python
# Domain anchor: high signal
if token in DOMAIN_ANCHORS:
    SW = 0.80 + cluster_bonus (max 0.95)
    NW = 1.0 - SW

# Filler word: context-dependent
if token in FILLER_WORDS:
    if signal_neighbors >= 2:
        SW, NW = 0.35, 0.65  # emphasis context
    else:
        SW, NW = 0.08, 0.92  # pure filler

# General word: frequency + position + domain_density
SW = 0.40 × freq_normalized + 0.25 × position_score + 0.35 × domain_density
```

### Known Issue: Domain Density Bleed
The `domain_density` term bleeds into all tokens in a message.
Messages with many anchor words inflate ALL token scores globally.
User casual messages with zero anchors deflate everything globally.
→ Fixed in v2.

### Commitment Score (v1)
```
commitment = avg_SW_of_non_scaffolding × (1.0 - noise_penalty × 0.5)
where noise_penalty = noise_count / total_tokens
```

Issue: Does not account for message length — long and short messages
with equal signal density score identically. → Fixed in v2.

---

## 5. SigToken v2 / Recursive — Canonical Architecture

### v2 Fixes Over v1
1. Removed domain_density bleed from general word scorer
2. SNR excludes scaffolding from BOTH numerator and denominator
3. Commitment penalizes length — short irreducible messages score higher

### Revised SNR Formula (v2)
```
active_tokens  = signal_tokens + noise_tokens  (scaffolding excluded)
SNR_normalized = signal_tokens / active_tokens
SNR_ratio      = signal_tokens / noise_tokens
SNR_dB         = 10 × log10(SNR_ratio)
```

### Revised Commitment Formula (v2)
```
signal_purity  = signal_tokens / active_tokens

length_factor:
  active_tokens ≤ 3   → 1.00  (maximally irreducible)
  active_tokens ≤ 8   → 0.90
  active_tokens ≤ 20  → 0.75
  active_tokens ≤ 50  → 0.60
  active_tokens > 50  → max(0.40, 0.60 - (n - 50) × 0.001)

avg_signal_SW  = mean(SW) of signal-tier tokens only

commitment = signal_purity × 0.50
           + avg_signal_SW × 0.30
           + length_factor × 0.20
```

### Two-Pass Recursive Architecture (v2.1)

**Pass 1: Thread-Local IDF**

For each thread T containing messages M₁...Mₙ:

```
doc_freq(w, T)   = number of messages in T containing word w
local_IDF(w, T)  = log((n + 1) / (doc_freq(w, T) + 1)) + 1
                   normalized to [0, 1] by dividing by max possible IDF

max_IDF = log(n + 1) + 1
local_IDF_normalized(w, T) = local_IDF(w, T) / max_IDF
```

Words appearing in every message of their thread → low local IDF (thread-scaffolding)
Words appearing rarely within their thread → high local IDF (thread-signal)

**Pass 2: Corpus Validation**

For each word w across all threads T₁...Tₖ:

```
# SNR estimate for each thread (used as reliability weight)
thread_SNR(T) = (signal_tokens - noise_tokens × 0.5) / active_tokens

# Weighted IDF across threads
weighted_sum(w)   = Σ local_IDF(w, Tᵢ) × thread_SNR(Tᵢ)
weight_total(w)   = Σ thread_SNR(Tᵢ)  [for threads containing w]
avg_weighted_IDF  = weighted_sum / weight_total

# Thread penetration (log-scaled)
penetration(w) = log(thread_count(w) + 1) / log(total_threads + 1)

# Final corpus score
corpus_score(w) = avg_weighted_IDF × 0.60 + penetration × 0.40

# Static anchor floor
if w in static_anchors:
    corpus_score(w) = max(corpus_score(w), 0.65)
```

**Promotion to Dynamic Anchors:**
```
if corpus_score(w) ≥ 0.35 AND thread_count(w) ≥ 3:
    promote w to DYNAMIC_ANCHORS
```

**Final Token Scoring (recursive):**
```
SW = local_IDF(w, T) × 0.45
   + corpus_score(w) × 0.35
   + position_score × 0.20

where position_score = 0.60 - (token_position / total_tokens) × 0.20
```

---

## 6. Thread Map — Topology Analysis

### Thread Similarity (Jaccard)
```
vocab(T, N) = top-N most frequent words in thread T (after stopword removal)

Jaccard(Tₐ, T_b) = |vocab(Tₐ) ∩ vocab(T_b)| / |vocab(Tₐ) ∪ vocab(T_b)|

Edge created if Jaccard ≥ min_similarity (default: 0.05)
```

### Concept Stitching
A concept stitch is detected when a word appears in two threads separated by ≥7 days:

```
For word w appearing in threads Tₐ (at time t₁) and T_b (at time t₂):
  gap_days = (t₂ - t₁) / 86400
  if gap_days ≥ min_gap (default 7):
    stitch detected: (w, Tₐ, T_b, gap_days)

Filter requirements:
  len(w) ≥ 4 characters
  w not in STOPWORDS
  freq(w, T) ≥ 2 within its thread
```

### Drift Detection
Drift signature = system losing the kernel of a conversation:

```
For user messages in thread T, ordered by time:
  window = 5 messages

  lookback_avg = mean(token_length) of previous 5 messages
  lookahead_avg = mean(token_length) of next 5 messages

  if lookback_avg ≥ 30 AND lookahead_avg ≤ 8:
    drift event detected
    compression_ratio = lookback_avg / lookahead_avg
```

Interpretation:
- High compression_ratio = severe drift (system was far off-kernel)
- trigger_message = first short message after the long window
- The burst of short messages = user recompressing back to the kernel

---

## 7. End-to-End Workflow

### Standard Pipeline (new corpus)

```
Step 1: SIGNAL ARMY
  Input:  conversations.json (GPT export format)
  Output: word_inventory.csv, flattened_messages.csv

  python signal_army.py --json conversations.json --output-dir ./runs/

Step 2: SIGTOKEN RECURSIVE
  Input:  flattened_messages.csv, word_inventory.csv
  Output: sigtoken_recursive_summary.txt, sigtoken_recursive_summary.json

  python sigtoken_recursive.py \
    --messages flattened_messages.csv \
    --word-inventory word_inventory.csv \
    --output-dir ./runs/

Step 3: THREAD MAP
  Input:  flattened_messages.csv
  Output: thread_nodes.csv, thread_edges.csv, concept_stitches.csv,
          drift_events.csv, timeline.csv

  python thread_map.py \
    --messages flattened_messages.csv \
    --output-dir ./runs/

Step 4: OBSIDIAN VAULT (optional)
  Input:  thread_map CSVs + sigtoken JSON
  Output: .md files per thread with links, SNR, drift markers

  (run build_vault.py or build_three_vaults.py)
```

### Running Both Roles
```bash
# User messages
python signal_army.py --json combined_all.json --role user --output-dir ./runs/user/

# Assistant messages
python signal_army.py --json combined_all.json --role assistant --output-dir ./runs/asst/

# Then run sigtoken_recursive on each output separately
# Compare avg_commitment and SNR_normalized between the two
```

---

## 8. Equation Index

| Equation | Location | Formula |
|----------|----------|---------|
| Dual weight constraint | Core theory | SW + NW = 1.0 |
| Token mass | Signal Army | freq(w) × len(w) |
| Percentile rank | Signal Army | (rank / N) × 100 |
| SNR ratio | All versions | signal / noise |
| SNR normalized (v1) | SIGSYSTEM, SigToken v1 | signal / total |
| SNR normalized (v2) | SigToken v2+ | signal / (signal + noise) |
| SNR dB | All versions | 10 × log₁₀(SNR_ratio) |
| Commitment (v1) | SigToken v1 | avg_SW × (1 - noise_penalty × 0.5) |
| Commitment (v2) | SigToken v2+ | purity×0.5 + avg_SW×0.3 + length_factor×0.2 |
| Length factor | SigToken v2+ | Piecewise: 1.0→0.90→0.75→0.60→≥0.40 |
| Local IDF | Recursive | log((n+1)/(df+1))+1 normalized |
| Corpus score | Recursive | avg_weighted_IDF×0.6 + penetration×0.4 |
| Thread penetration | Recursive | log(thread_count+1) / log(total_threads+1) |
| Jaccard similarity | Thread Map | |A∩B| / |A∪B| |
| Drift compression ratio | Thread Map | lookback_avg / lookahead_avg |

---

*Document generated: 2026-03-19*
*Ecosystem: Signal Army v1.5 | SigToken C-0005 v2.1-recursive | ThreadMap v0.1*
*Owner: Luthen / Ello Cello LLC*
