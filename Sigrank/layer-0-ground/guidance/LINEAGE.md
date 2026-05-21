# Lineage — how the dimensional layers came to be

Historical evolution of the SigRank dimensional stack. Read alongside [`CONSERVATION_LAW.md`](CONSERVATION_LAW.md) — that doc explains how the layers relate; this one explains where they came from.

---

## Origin

**OG SIGRANK is the operator.** Not a product, not a paper, not a benchmark. The originating intuition — that signal-to-noise of language maps to behavioral coherence which is observable in token telemetry — was demonstrated by the operator through years of work prior to any code being written.

This document is the record of that lineage.

---

## Phases

### Phase 0 · Pre-naming
Operator observed that some interactions produce dense, coherent output (high signal) and others produce diffuse, redundant, drifting output (low signal). The observation predates any framework name.

### Phase 1 · Commitment Theory
The philosophical formalization: signal is preserved when commitment is sustained. Without commitment, signal disperses into noise. This became the bedrock — the conservation law's "why."

### Phase 2 · SigSystem
The word-level engine. Quantifies language by classifying words and tokens as signal or noise within their statement context. Lives in `Sigrank/sig_army/` and `Sigrank/word_vault/` — the 4,900-token classifier was built here.

The word vault is the operationalization of SigSystem at scale.

### Phase 3 · OG SIGRANK · the operator's mapping
The leap: language SNR → behavioral coherence → token telemetry. The operator demonstrated that operators with higher word-level signal also produced higher token-level compression. This established the conservation across resolution (see CONSERVATION_LAW.md invariant I.3).

The proof was lived, not published. The mapping became the foundation everything since has rested on.

### Phase 4 · Current build · rns-sigrank
What we're building now. Token-total resolution. Privacy-preserving (no raw transcripts needed). Free tier + Pro tier. The MVP scaled version of the conservation law.

Repo: this one.

### Phase 5 · Refinery (future)
SigSystem-grade signal/noise per token, applied to routing decisions. Reuses sig_army infrastructure at scoring-engine scale. Powers the Switchboard.

### Phase 6 · Switchboard (existing, awaiting Refinery)
The signal routing layer for multi-agent coordination. Two forms exist:
- `~/Desktop/claude-switchboard-plugin/` — built, multi-Claude session coordination
- `~/Desktop/hermes/moses/switchboard/` — stubbed, depends on Refinery

---

## Naming drift notes

These names referenced the same dimensional thing across history:

| Period | Names used for the same concept |
|---|---|
| Early | "signal compression", "signal density", "S/N" |
| Mid | "Compression Ratio", "SigSys score", "purity score", "clarity score" |
| Now | "Compression Ratio (M.01)" — locked in CANON |

For full per-metric naming drift, see [`../../../layer-1-foundation/metrics/lineage/naming_drift.md`](../../layer-1-foundation/metrics/lineage/naming_drift.md).

---

## Retirement notes

These were proposed but retired during the current build:

- **SDOT** (Signal Delta Over Time) — never had a confirmed formula. Retired 2026-05.
- **SDRM** (Signal Density Resonance Metric) — no active prototype. Retired 2026-05.
- **Sig Delta** (proposed rename for Drift Ratio) — never adopted.
- **Sig Alpha** (proposed rename for Signal Force) — never adopted.

These are recorded in the metrics lineage docs and CANON section II for archaeological completeness. They are not active metrics.

---

## What the lineage means for the build

1. **Don't re-prove what OG SIGRANK already proved.** The mapping between behavior and tokens is established. The current build leverages it; it doesn't have to re-validate it.

2. **Don't conflate the dimensions.** Each phase measures the same signal at a different resolution. They're not competing products.

3. **Don't lose the conservation invariants** (CONSERVATION_LAW.md). When a future build phase changes results in ways that violate the invariants, something is wrong.

4. **The operator's prior body of work is the validation suite.** When in doubt about whether a new metric or formula behaves correctly, check whether it produces results consistent with what the operator already observed and documented.
