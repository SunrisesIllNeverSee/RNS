# SIGSYSTEM v1.0 — First Test Run Notes

**Date:** 2026-03-02
**Input:** Signal Army run `run_2026-03-02_06-03-50` (24 threads, 7,807 unique words, 65 divisions)
**Engine:** sigsystem.py v1.0

---

## Results Summary

| Metric | Value |
|--------|-------|
| Words Classified | 7,807 |
| SIGNAL words | 567 (7.3%) |
| NOISE words | 7,240 (92.7%) |
| Session SNR (normalized) | 0.2969 |
| Session SNR (dB) | -3.74 dB |
| Signal Density | 0.4649 |
| Compression Potential | 36.2% removable |

## Trajectory Breakdown

| Trajectory | Count |
|------------|-------|
| RISING | 1,007 |
| STABLE | 1,185 |
| DECLINING | 1,401 |
| SPARSE | 4,214 |

## Key Observations

### 1. Top Signal Words Are Correct
The top 20 signal words (commitment, conservation, recursive, moses, backend, protocol, build, signal, sovereign, semantic, model, drift, system) ARE the core MOS²ES vocabulary. SIGSYSTEM correctly identifies the system's structural pillars.

### 2. Thread SNR Leaderboard Makes Sense
- **Highest SNR:** "ONE-PAGE PITCH" (0.33) — compressed pitch document, mostly signal
- **Lowest SNR:** "Luthen_France.md" (0.096) — movie transcript, not MOS²ES content
- **Mid-range:** Grok sessions cluster around 0.22-0.28 — normal conversational density

### 3. 7.3% Signal Words
Only 567 out of 7,807 unique words carry enough weight to be SIGNAL. This validates the compression thesis — the vast majority of vocabulary is scaffolding. The 567 signal words ARE the compressible payload.

### 4. Compression Potential: 36.2%
43,308 words out of 119,569 total are estimated removable (stop words + infantry). After compression, signal density would rise from 0.4649 to 0.4655 — meaning the signal words already dominate the non-noise portion.

### 5. Dual-Weight Scoring Works
Words like "commitment" show SW:0.686 / NW:0.314 — high signal, low noise. Infantry words like "not" show SW:0.187 / NW:0.813 — both values are meaningful, not just binary. The dual-weight density concept from the user's spec is operational.

### 6. Decay Tracking Reveals Trends
- "compression" is DECLINING (-0.25) — appears more in early threads
- "security" is RISING (0.17) — gaining presence in later threads
- "frontend" is RISING (0.25) — emerging as a focus
- "aaron" is DECLINING (-1.0) — concentrated in early specific threads

## What's Working

- 5-stage pipeline runs end-to-end
- Consumes Signal Army CSV output cleanly
- Per-word classification with 4 sub-scores (rank, context, necessity, decay)
- Per-thread SNR produces a meaningful leaderboard
- Session-level aggregate metrics
- All three SNR forms: normalized (0-1), ratio (S/N), dB

## Known Limitations (v1.0)

1. **Messages are per-file, not per-exchange** — each thread is one large message because Signal Army's markdown parser treats unstructured files as single messages. Per-message SNR would be more granular with structured conversation data.

2. **SPARSE trajectory dominance** — 4,214 out of 7,807 words are SPARSE (too few data points). This is because most words appear in only 1-2 threads. Processing the 84MB chatfiles would significantly reduce the SPARSE count.

3. **Contextual scoring is conservative** — avg contextual score is 0.062, which means most words score low on context. This is partially because division membership is limited to ~15 words per division (Signal Army's cap), so most words aren't in divisions.

4. **No sentence-level granularity** — SIGSYSTEM tokenizes at the word level but doesn't evaluate sentence-level semantic contribution. Future: add sentence-level SNR.

5. **Classification threshold (0.45) was set without calibration** — may need adjustment after more test runs across different corpora.
