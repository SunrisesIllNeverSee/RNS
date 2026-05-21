# Conservation Law — dimensional layers of the same signal

**Read this when you need to understand WHY the math works at all — not HOW to compute it.**

This is a **guidance-within reference**, not a build-with reference. The equations don't change based on this document. But the interpretation of the equations does.

---

## The fundamental observation

**Commitment Theory, SigSystem, SigRank, Refinery, and Switchboard are not stacked products. They are dimensions of the same underlying signal, measured at different resolutions.**

The same signal is observable at every layer. Each layer is a projection — like the same 3D object measured at different magnifications and from different angles.

The error is treating these as discrete products that "enable" or "depend on" each other in a build sense. They are dimensional projections of the same conservation law.

---

## The dimensions, from finest to coarsest resolution

```
Resolution                 Dimension              What it measures
─────────────────────────────────────────────────────────────────────────
philosophical              COMMITMENT THEORY      Why signal is preserved at all
                                                  Isolates the invariant so it can be quantified

word-level                 SIGSYSTEM              Signal vs noise per word, in context
                                                  Token-per-word resolution
                                                  Lives in: Sigrank/sig_army/ + Sigrank/word_vault/

behavioral                 OG SIGRANK             SNR of language → behavioral coherence → tokens
                                                  THE OPERATOR IS OG SIGRANK
                                                  Established the mapping between behavior and tokens
                                                  Not a separate product — the originating intuition

token-total resolution     rns-sigrank            What we're building now
                                                  Ranks via token totals (the leverageable signal)
                                                  Only viable because OG SIGRANK proved the mapping
                                                  Free tier + Pro tier

token-per-word resolution  REFINERY               Future build
                                                  SigSystem-grade signal/noise per token
                                                  Powers routing decisions
                                                  Lives in: Sigrank/sig_army/ at this scale

routing layer              SWITCHBOARD            Existing build, depends on Refinery
                                                  ~/Desktop/hermes/moses/switchboard/
                                                  ~/Desktop/claude-switchboard-plugin/
```

---

## Critical clarifications

### The operator IS OG SigRank

OG SIGRANK is not a prior product that someone else built. The operator (you) is OG SIGRANK. The original mapping from language SNR → behavioral coherence → tokens lives in the operator's prior work, observations, and judgment. The proof of the mapping is the operator's lived demonstration of it.

This matters because:
- **The proof of validity is not a paper or a benchmark — it's the operator's prior body of work.**
- Future versions (Refinery, etc.) can be validated by checking they produce results consistent with what OG SIGRANK already produced.
- The mapping doesn't need to be re-validated for the current build (rns-sigrank). It's already proven.

### Layers don't enable/disable each other

The wrong mental model:
> "SigRank depends on SigSystem depends on Commitment, so we need to build them in order"

The right mental model:
> "The signal is conserved across all dimensions. We can measure it at any resolution. We choose the resolution that fits the use case."

This means:
- The current SigRank build (token-total resolution) does NOT require SigSystem to be running. The token totals carry the signal — that's the OG SIGRANK insight.
- The Refinery (token-per-word resolution) will use SigSystem under the hood, but the signal it measures is the same signal SigRank measures, just sampled finer.
- Switchboard routes signals scored at any resolution.

### What "conservation" means here

The signal that SigSystem measures word-by-word, when aggregated to token totals, produces the same ordering of operators that SigRank measures directly from token totals.

That is, if Operator A has higher word-level signal density than Operator B (measured by SigSystem), then Operator A will also have a higher token-total compression ratio (measured by SigRank), as long as token sampling is large enough.

This is conservation across resolution. The aggregate preserves the signal of the fine-grained measurement.

---

## Why this matters for the current build

The current build (rns-sigrank, token-totals resolution) is shippable as MVP because:

1. **OG SIGRANK already proved the conservation** — token totals carry the behavioral signal
2. **The free tier doesn't need finer resolution** — token telemetry is enough to rank operators meaningfully
3. **The Pro tier (sig_army) is the resolution upgrade** — same signal, finer measurement, audit-grade

This is why we say in the spec:
- Free tier uses **proxies** (Output:Fresh-Input ratio, Cache Hit Rate, turns/session)
- Pro tier uses **exact** (signal_tokens / total_tokens, parent-message reply chains)

Both measure the same conserved signal. The Pro tier just samples finer.

---

## Reference invariants

The system holds these conservation invariants — when one is broken, something is wrong:

| Invariant | Statement |
|---|---|
| **I.1** | If Operator A has higher SIGNA RATE than Operator B at the free tier, Pro-tier scoring should not invert the ordering (within tolerance). |
| **I.2** | If Compression Ratio (free-tier proxy) is high, sig_army-measured Compression Ratio (Pro) will be high with high probability. |
| **I.3** | Aggregating word-level SNR over a session produces the same Compression Ratio (within rounding) as token-total Compression Ratio computed directly. |
| **I.4** | Ruleset version changes that re-weight Core 5 should not invert ordering for operators with sufficient sample size. |
| **I.5** | Class assignments are sticky across resolution — TRANSMITTER-class at free tier remains TRANSMITTER-class at Pro tier (within audit-revision tolerance). |

If we observe an invariant violation in production, it's a signal that one of:
- The ruleset is mis-calibrated
- A bug exists in the proxy → exact bridge
- The operator's behavior is genuinely anomalous (gaming, drift, etc.)

---

## How to use this document

When in doubt about whether two things are different products or the same thing at different resolution — **default to "same thing, different resolution."** That's the conservation law.

When proposing a new metric or layer:
- Ask: which resolution does this operate at?
- Ask: does it preserve the conservation invariants?
- Ask: where does it live in the dimensional stack above?

When debugging unexpected ranking changes:
- Check the invariants in this document
- Check whether the resolution changed
- Check whether the ruleset version changed

---

## What this is NOT

- This is **not** a build dependency tree. The layers don't enable each other in a software-engineering sense.
- This is **not** a formal proof. The conservation is empirical, established by OG SIGRANK's prior work.
- This is **not** something to canonize in the current ruleset. The conservation law informs interpretation, not computation.

---

## See also

- [`LINEAGE.md`](LINEAGE.md) — historical evolution of the layers and their naming
- [`TOKENS_PER_WORD.md`](TOKENS_PER_WORD.md) — the finer-resolution primitive that Refinery would use
- [`../build/CANON.md`](../build/CANON.md) — the canonical IDs and equations that this conservation law underlies
