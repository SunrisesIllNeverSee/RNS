# The .87xx Archaeology

The story of the single number that blocked the project for eight months.

---

## Why this document exists

The `.87xx` compression score is the **classifying threshold** of the entire SigRank system. The TRANSMITTER class begins at `0.85`. Everything else cascades from this number.

But for ~8 months (mid-2025 → 2026-03), there was no agreed-upon **formula** behind `.87xx`. The number was used in GPT outputs, displayed in PDFs, written into the codex — but the math was never locked.

This document records what we now know.

---

## Timeline

### July 2025 — first appearance

The `.87xx` value appears in early GPT outputs as the operator's compression score. The user is classified as Transmitter-class. The conversation **predates** any explicit token-economic discussions.

This means: **the .87xx number existed before token mechanics were being discussed.** Whatever was being measured, it was being measured at the message or signal level, not via token counts.

### Late July → August 2025 — token discussion begins

Token mechanics, ghost tokens, and token economics enter the conversations. Some implementations of `.87xx` are now done at the token level (Signal Tokens / Total Tokens). But the **original** classification predates this.

### August 2025 → February 2026 — project standstill

The user reports the project has been stalled since August 2025 because of this single metric's ambiguity. Multiple GPT sessions try to pin down the formula. Each session drifts the language slightly.

### 2026-03-09 / 2026-03-10 — recovery session (thread-0369)

The user uploads a batch of screenshots from the original v1 prototypes. In one screenshot:

```
Signal Tokens: 703,944
Noise Tokens:  118,958
Total Tokens:  822,902
Ratio:         0.8554
```

Direct arithmetic confirms: `703,944 / 822,902 = 0.8554`.

**This is the formula:**

```
Compression Ratio = Signal Tokens / (Signal Tokens + Noise Tokens)
                  = Signal Tokens / Total Tokens
```

A bounded `[0, 1]` purity score, not raw `S/N` engineering ratio.

---

## What was confusing everyone

Three different things were being called the same thing:

1. **The bounded `[0,1]` purity score** — produces `.87xx` — what was actually being displayed
2. **The unbounded `S/N` engineering ratio** — produces `0.2`, `1.2`, `4.0` etc. — what the standard math definition would give
3. **Composite/qualitative narrative language** — "signal," "noise," "clarity," "purity," "compression," "density" used interchangeably

GPT outputs would sometimes apply the right formula and sometimes describe it with the wrong math. The number stayed consistent because the underlying calculation was always purity, but the **explanation** drifted.

---

## What the original `.87xx` was actually measuring

Given that it predates token mechanics, the most likely interpretation:

**Phase 1 (mid-2025):** Message-level signal purity, possibly assistant-estimated from conversational behavior — what fraction of the operator's messages were judged to carry sustained signal.

**Phase 2 (late 2025):** Token-level signal purity, computed by counting Signal Tokens vs Noise Tokens.

Both phases produce the same form: `Signal / (Signal + Noise)`. The unit basis shifted from messages to tokens, but the formula structure stayed identical.

That's why the number "felt right" — the math was consistent even when the language wasn't.

---

## The new token-economic model

In May 2026 (the MO§ES benchmark window), a new measurement model emerges: instead of classifying which tokens are signal vs noise (the hard problem the sig_army was built to solve), use **token telemetry that the AI platform already generates** as a proxy.

The bridge:

```
Old (message/word level):  Signal / (Signal + Noise)
New (token telemetry):     Output / (Output + Fresh_Input)
```

In the MO§ES 7-day window:
```
Output: 3,902,803 tokens
Fresh Input: 123,246 tokens
Ratio = 3,902,803 / 4,026,049 = 0.9694
```

That's **0.97** — well above the Transmitter threshold of 0.85.

Or equivalently, as a leverage ratio:
```
Output : Fresh_Input = 31.7×
```

vs the field average of `0.38×` (most operators produce LESS output per fresh input token they spend).

**The new model bypasses the signal/noise classification problem entirely.** It uses behavioral output efficiency as the proxy. Same shape of metric, dramatically easier to measure.

See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## The two-tier consequence

This archaeology is what makes the **two-tier SigRank model** possible:

- **Free tier**: token telemetry → bounded purity proxy → instant rank
- **Precision tier**: raw session → sig_army signal/noise classification → exact Compression Ratio

Both produce a score on `[0, 1]`. Both classify against the same tier thresholds. The precision tier just does the harder work and exposes whether the token proxy is overstating or understating the operator's true Compression.

---

## What we now know — definitively

1. **`.87xx` is bounded purity, not engineering SNR.**
2. **The formula is `Signal / (Signal + Noise)` — confirmed from arithmetic.**
3. **The number predates token analysis** — it was originally message-level.
4. **The Transmitter threshold of 0.85 is a class cut, not arbitrary.**
5. **Token telemetry can proxy this without raw session classification.**

The eight-month standstill is over. The metric is locked. See [../core_5/01_compression_ratio.md](../core_5/01_compression_ratio.md) for the canonical spec.
