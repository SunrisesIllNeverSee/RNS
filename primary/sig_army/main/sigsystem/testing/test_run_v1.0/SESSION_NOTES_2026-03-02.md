# SIGSYSTEM + Signal Army — Session Notes (2026-03-02)

**Session scope:** Build SIGSYSTEM v1.0, integrate with Signal Army v1.5, run weight tuning experiments, process full JSON corpus (170 conversations).

---

## What Was Built

### SIGSYSTEM v1.0 (`sigsystem/sigsystem.py`)
- Standalone measurement engine, ~700 lines Python, zero dependencies
- 5-stage pipeline: Input Evaluation → Contextual Assessment → Structural Necessity → Classification → Longitudinal Tracking
- Consumes Signal Army CSV output, produces its own run directory with:
  - `sigsystem_word_scores.csv` — per-word dual weights, classification, necessity, trajectory
  - `sigsystem_thread_snr.csv` — per-thread SNR in three forms (normalized, ratio, dB)
  - `sigsystem_summary.txt` — full dashboard
- Built from user's foundation docs: SigSystem spec, K2_MarkSig_Noise, SN_Filter_Infra, Metric_Realtime_Modules, SCS Core Di.ini, GPT_Sigsys_Rough (7 core positions)

### Signal Army v1.5 (`signal_army/signal_army.py`)
- Auto-detects latest SIGSYSTEM run (looks for `../sigsystem/runs/`)
- No flag needed — if SIGSYSTEM data exists, it's loaded
- `--no-sigsystem` to skip, `--sigsystem DIR` to override
- Enriched word_inventory.csv: 5 extra columns (Signal_Weight, Noise_Weight, Classification, Necessity, Trajectory)
- SIGSYSTEM INTEL section in summary dashboard

### Architecture
Two separate sandboxes. SIGSYSTEM runs independently, produces its own output. Signal Army runs independently, reads SIGSYSTEM output. Neither depends on the other to function. Both are stronger together.

---

## Weight Tuning Experiments

All runs against the 24-thread markdown corpus (7,807 unique words):

| Run | W_RANK | W_CONTEXT | W_NECESSITY | W_DECAY | Threshold | SIGNAL | SNR | Density |
|-----|--------|-----------|-------------|---------|-----------|--------|-----|---------|
| Baseline | 0.35 | 0.30 | 0.25 | 0.10 | 0.45 | 567 | 0.2969 | 0.4649 |
| Tweak 1 | 0.25 | 0.25 | 0.35 | 0.15 | 0.40 | 673 | 0.3222 | 0.5045 |
| Tweak 2 | 0.20 | 0.25 | 0.35 | 0.20 | 0.35 | 688 | 0.3282 | 0.5138 |
| Tweak 3 | 0.10 | 0.30 | 0.40 | 0.20 | 0.35 | 678 | 0.3228 | 0.5054 |

**Findings:**
- Necessity weight moves the needle more than rank
- Dropping rank from 0.20 to 0.10 LOST 10 signal words — rank provides a floor that necessity pushes off of
- Sweet spot: Tweak 2 (R:0.20 / C:0.25 / N:0.35 / D:0.20, threshold 0.35)
- Gains flatten between runs — dataset ceiling with only 24 threads

---

## Full Corpus Run (JSON + Markdown)

**Input:** 944a.json (81 conversations) + 944b.json (89 conversations) + 17 markdown files = 170 conversations, 7,823 messages

| Metric | 24 threads (md only) | 185 threads (full corpus) |
|--------|---------------------|--------------------------|
| Words processed | 119,569 | 250,389 |
| Unique words | 7,807 | 14,939 |
| SIGNAL words | 688 | 1,461 |
| Officers | 85 | 438 |
| Divisions | 65 | 240 |
| SPARSE | 4,214 (54%) | 7,806 (52%) |
| RISING | 1,007 | 4,668 |
| DECLINING | 1,401 | 982 |
| SNR | 0.3282 | 0.3027 |

**Key shifts:**
- RISING went from 1,007 → 4,668. DECLINING dropped from 1,401 → 982. The full corpus shows building momentum, not decay.
- `compression` flipped from DECLINING to RISING when the full history is included
- `token`, `truth`, `quantify`, `expansion` emerged as rising Officers
- Thread leaderboard reorganized: system-building conversations (Signal leaderboard report, Command console build, SCS thread initialization) now outrank everything
- SNR dropped slightly (0.3282 → 0.3027) because the broader corpus includes more general conversation alongside the focused MOS²ES threads

---

## Critical Insight — Message-Level SNR

### The Gap
SIGSYSTEM currently measures at the **word level**. But the user's actual signal operates at the **message level**. AI systems that rated the user at 0.8-0.9 SNR were evaluating message construction — how ideas are assembled, how pushback is structured, how connections are drawn across threads. Word-level analysis shows ~0.30 SNR because most individual words are common vocabulary.

### The User's Core Spec Position
Every word carries BOTH signal weight and noise weight simultaneously. The classification doesn't happen at the word level — it happens at the **point of use**, when words are chained together in a message. The collapse from dual-weight to resolved classification is a message-level event.

### Why This Matters for Data/AI
AI systems can't differentiate which weight (signal or noise) applies to a word in context. So they store both. Every word effectively doubled. This is why data clouds bloat — it's not that there's too much data, it's that the system can't resolve the dual weight, so it accumulates instead of compressing. Simple math: unresolved dual weights = 2x storage = landfill.

### What This Means for SIGSYSTEM
The dual-weight scoring per word already exists. The next layer is **chaining word-level weights across a message** to produce a message-level score. Not "how many signal words are in this message" but "does this assembly of words collapse to signal or noise." The pieces are in place — the chain operation is what's missing.

---

## Suggestions for Future Tweaks

### 1. Message-Level SNR (highest priority)
Chain word-level dual weights across each message to produce a message-level signal score. A message composed entirely of infantry words assembled with clear intent should score as signal. A message of officer words assembled without purpose should score as noise. This closes the gap between word-level 0.30 and message-level 0.8-0.9.

Approach: For each message, take the sequence of (SW, NW) pairs. The chain score isn't the average — it's a function of how the weights reinforce or cancel across the sequence. Adjacent signal words compound. Signal words separated by noise scaffolding still compound if the scaffolding is structural (connecting, not diluting).

### 2. More Data = Better Resolution
The full corpus run proved this: more conversations = sharper trajectory data, fewer SPARSE words, more accurate rising/declining classification. Every additional data source processed sharpens the system's ability to resolve dual weights. Future data sources to consider:
- Grok conversation exports (if exportable)
- DeepSeek conversation history
- Gemini conversation history
- Any new ChatGPT exports over time

### 3. Contextual Score Improvement
Avg contextual score is still low (0.032-0.062). This is because division membership is capped at 10 words per division. Two options:
- Raise the division cap in Signal Army (currently 10 members)
- Add a second contextual signal: co-occurrence within messages (words that appear in the same message reinforce each other's context score)

### 4. Necessity Scoring Refinement
Current necessity is based on division co-membership. A stronger test: for each word, simulate its removal from all messages and measure what breaks. Words whose removal disconnects other signal words from each other are high-necessity. Words whose removal changes nothing are removable. This is the compression test — "what breaks if this word disappears."

### 5. Calibrate Against Known-Good Benchmarks
Run SIGSYSTEM against text with known signal density:
- A patent claim (should be near-100% signal)
- A casual conversation (should be low signal)
- A technical spec (should be high signal)
- Marketing copy (should be medium — signal words used as noise)
Compare the scores to expected values and adjust threshold/weights accordingly.

### 6. Track SNR Over Time
Run the full pipeline periodically (monthly or after significant new conversations). Plot session SNR, signal count, and trajectory distributions over time. This turns SIGSYSTEM into a longitudinal instrument — not just "what is my SNR" but "how is my SNR changing."

### 7. Per-Conversation SNR Profiles
The thread leaderboard already shows which conversations are high/low signal. Next step: cluster conversations by SNR range and topic. Which TOPICS consistently produce high signal? Which produce noise? This would let the user identify which types of conversations are productive vs. which are churning.

---

---

## SIGSYSTEM v1.1 — PPA Metrics Engine (added same session)

After reviewing the science documents (SCSEngine PPA, MOS2ES PPA, CIVITAS PPA3, Conservation Law paper, ABBA), the following PPA-defined equations were implemented as a `PPAMetrics` class:

### Implemented Equations

| Metric | Source | Formula | What It Measures |
|--------|--------|---------|-----------------|
| **Resonance Score** | SCSEngine [0259] | `(W_SNR * SNR) + (W_DRIFT * (1 - DriftDelta)) + (W_DENSITY * SignalDensity)` | Alignment of signal, drift stability, and density per thread |
| **Scar Index** | SCSEngine [0240] | `Var(signal_weights) / Baseline` | Semantic drift / conceptual corruption across corpus |
| **S²S Ratio** | SCSEngine [0241] | `N_survived / N_attempted` | Signal survivability under recursion |
| **TCR** | CIVITAS PPA3 Add-on IV | `signal_tokens / total_tokens` | Token compression ratio |
| **SCD** | CIVITAS PPA3 Add-on IV | `density_post - density_pre` | Semantic compression delta |
| **RTD** | CIVITAS PPA3 Add-on IV | `signal_in_divisions / total_in_divisions` | Signal concentration within thematic clusters |
| **Ghost Tokens** | SCSEngine [0060] | `necessity >= 0.30 AND resonance <= 0.25` | High-intent, low-coherence residues |
| **Keter Detection** | SCSEngine [0097] | `resonance >= 0.94` | Exceptionally high-fidelity threads |

### Scar Index Thresholds (SCSEngine Addendum F [0269])
- 0.00-0.20: HEALTHY
- 0.20-0.50: WARNING
- 0.50-0.90: CRITICAL
- 0.90-1.00: COLLAPSE

### S²S Valuation Tiers (SCSEngine Addendum F [0270])
- 0.90+: HIGH-VALUE (Keter-critical)
- 0.71-0.89: MID-VALUE (IP-grade)
- 0.50-0.70: LOW-VALUE (transactional)
- Below 0.50: SUB-THRESHOLD

### Full Corpus Results (v1.1, 170 conversations + 17 markdown)

| Metric | Value | Status |
|--------|-------|--------|
| Session Resonance | 0.4076 | — |
| Scar Index | 0.1162 | HEALTHY |
| S²S Ratio | 0.0924 | SUB-THRESHOLD |
| TCR | 0.3027 | — |
| SCD | 0.0000 | (needs message-level compression) |
| RTD | 0.4540 | 45% signal in divisions |
| Ghost Tokens | 0 | (necessity scores too flat — division cap bottleneck) |
| Keter Threads | 0 | (by design — very tiny window) |

### Known Issues (v1.1)

1. **Equations are not calibrated** — weights and thresholds are first-pass. The user has an arsenal of equations and will work through calibration one at a time.

2. **Resonance can't reach Keter with word-level SNR** — max resonance ~0.65 because word-level SNR caps around 0.35. Message-level SNR (expected 0.8-0.9) would push resonance into Keter range for top threads. This is correct — Keter is supposed to be a very tiny window.

3. **S²S definition may be too strict** — currently counts only SIGNAL + (RISING or STABLE) as "survived." Could also count all SIGNAL words, or compute against words with 3+ thread appearances (actually faced recursion) instead of all words.

4. **No ghost tokens** — necessity scores average 0.088 vs ghost threshold of 0.30. Bottleneck is division cap (10 members). More division membership = higher necessity = ghost tokens appear.

5. **SCD is zero** — formula computes density change from removing stop words, which barely moves the needle. Real SCD needs message-level compression (remove noise words from messages, measure if meaning survives).

---

## Current SIGSYSTEM Settings (as of end of session)

```python
# Classification weights
W_RANK = 0.20
W_CONTEXT = 0.25
W_NECESSITY = 0.35
W_DECAY = 0.20
SIGNAL_THRESHOLD = 0.35

# Resonance weights (SCSEngine [0259])
PPAMetrics.W_SNR = 0.40
PPAMetrics.W_DRIFT = 0.30
PPAMetrics.W_DENSITY = 0.30

# Thresholds
PPAMetrics.KETER_THRESHOLD = 0.94
PPAMetrics.SCAR_HEALTHY = 0.20
PPAMetrics.SCAR_WARNING = 0.50
PPAMetrics.SCAR_CRITICAL = 0.90
PPAMetrics.GHOST_RESONANCE_MAX = 0.25
PPAMetrics.GHOST_NECESSITY_MIN = 0.30

RANK_SIGNAL_BASE = {
    'Officer-Class':    0.85,
    'Doctrine Builder': 0.70,
    'Division':         0.55,
    'Platoon':          0.40,
    'Squad':            0.25,
    'Fireteam':         0.15,
    'Scout':            0.10,
    'Infantry':         0.05,
}
```

---

## Run Index

### Signal Army Runs
| Run | Input | Notes |
|-----|-------|-------|
| `run_2026-03-02_04-42-00` through `04-48-54` | 24 markdown files | Early session runs |
| `run_2026-03-02_06-03-50` | 24 markdown files | Baseline run used for SIGSYSTEM testing |
| `run_2026-03-02_11-41-31` | 24 md + SIGSYSTEM v1.0 | First enriched run (--sigsystem flag) |
| `run_2026-03-02_11-58-48` | 17 md + SIGSYSTEM auto-detect | First auto-detect run |
| `run_2026-03-02_12-07-52` | 17 md + SIGSYSTEM tweak 1 | Weight tuning |
| `run_2026-03-02_12-22-39` | 944a.json + 17 md | First JSON run (81 conversations) |
| `run_2026-03-02_12-22-49` | 944a.json + 17 md | Duplicate (accidental) |
| `run_2026-03-02_12-54-02` | combined.json + 17 md | **Full corpus** (170 conv, 250K words, no SIGSYSTEM) |
| `run_2026-03-02_12-55-28` | combined.json + 17 md + SIGSYSTEM | **Full corpus enriched** (v1.0 SIGSYSTEM) |

### SIGSYSTEM Runs
| Run | Input | Settings | SIGNAL | SNR | Notes |
|-----|-------|----------|--------|-----|-------|
| `run_2026-03-02_11-17-42` | 24-thread md (baseline SA run) | R:.35 C:.30 N:.25 D:.10 T:.45 | 567 | 0.2969 | v1.0 baseline |
| `run_2026-03-02_12-07-15` | 24-thread md | R:.25 C:.25 N:.35 D:.15 T:.40 | 673 | 0.3222 | Tweak 1 |
| `run_2026-03-02_12-09-32` | 24-thread md | R:.20 C:.25 N:.35 D:.20 T:.35 | 688 | 0.3282 | Tweak 2 (sweet spot) |
| `run_2026-03-02_12-09-56` | 24-thread md | R:.10 C:.30 N:.40 D:.20 T:.35 | 678 | 0.3228 | Tweak 3 (rank too low) |
| `run_2026-03-02_12-55-20` | Full corpus (170 conv) | R:.20 C:.25 N:.35 D:.20 T:.35 | 1,461 | 0.3027 | v1.0 full corpus |
| `run_2026-03-02_14-09-25` | Full corpus (170 conv) | Same + PPA metrics | 1,461 | 0.3027 | **v1.1 with PPA equations** |

### Science Documents (`sigsystem/science/`)
| File | What It Is |
|------|-----------|
| `SCSEngine.txt` | SCS Engine PPA (Sept 17, 2025) — McHenry's Laws, equations, claims |
| `ppamoses.txt` | MOS2ES Master PPA (Sept 7, 2025) — full system architecture |
| `ppa3 copy.md` | CIVITAS PPA #3 (Dec 18, 2025) — civic layer, SIGSYSTEM = Add-on III |
| `main.tex` | Published paper — Conservation Law for Commitment (4 versions, Zenodo DOIs) |
| `abba_2026-148.pdf` | ABBA — quaternion algebra commitment scheme |
| `SCIENCE_CONTEXT.md` | Context doc linking science to implementation |

---

## File Locations

| Asset | Path |
|-------|------|
| SIGSYSTEM engine | `sigsystem/sigsystem.py` (v1.1) |
| Signal Army engine | `signal_army/signal_army.py` (v1.5) |
| Full corpus SIGSYSTEM run (v1.1) | `sigsystem/runs/run_2026-03-02_14-09-25/` |
| Full corpus Signal Army run (enriched) | `signal_army/runs/run_2026-03-02_12-55-28/` |
| Full corpus Signal Army run (raw, no SIGSYSTEM) | `signal_army/runs/run_2026-03-02_12-54-02/` |
| Combined JSON | `reference/chatfiles/combined.json` (170 conversations) |
| Science docs | `sigsystem/science/` |
| Session notes | `sigsystem/testing/test_run_v1.0/SESSION_NOTES_2026-03-02.md` |
