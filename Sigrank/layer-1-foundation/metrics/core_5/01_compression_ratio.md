# Compression Ratio (S/Nr)

**Status:** locked — formula confirmed from screenshot arithmetic
**Layer:** Core 5
**Public label:** Compression Ratio
**Short label:** S/Nr (legacy) or Comp (preferred new)
**DB field:** `compression_ratio`

---

## Definition

The bounded ratio of identified signal tokens to total tokens in a measurement window. Represents how much of the operator's output is structured, coherent signal vs. noise/redundancy/drift.

This is **NOT** raw engineering signal-to-noise ratio (`S/N`). It is a bounded purity score on `[0, 1]`.

---

## Confirmed formula

```
compression_ratio = signal_tokens / (signal_tokens + noise_tokens)
                  = signal_tokens / total_tokens
```

**Confirmed from screenshot arithmetic (GPT thread-0369, 2026-03-10):**

```
signal_tokens = 703,944
noise_tokens  = 118,958
total_tokens  = 822,902

ratio = 703,944 / 822,902 = 0.8554
```

That value lands cleanly in the Transmitter class. The math is direct.

---

## Inputs required

For raw computation (sig_army / SigSystem path):
- classified signal tokens (count)
- classified noise tokens (count)

For token-proxy path (new submission model):
- output tokens
- fresh input tokens
- See [../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md)

---

## Output

- Range: `[0.0, 1.0]`
- Precision: 4 decimal places stored, 2 displayed (e.g. `0.87`)

---

## Class thresholds

| Class | Compression range |
|---|---|
| TRANSMITTER | ≥ 0.85 |
| ARCHITECT+ | 0.75 – 0.84 |
| ARCHITECT | 0.65 – 0.74 |
| POWER | 0.50 – 0.64 |
| BASE | 0.40 – 0.49 |
| SEEKER | 0.30 – 0.39 |
| REFINER | 0.20 – 0.29 |
| BEARER | 0.15 – 0.24 |
| IGNITER | < 0.15 |

See [../../architecture/class_tiers.md](../../architecture/class_tiers.md) for full class definitions.

---

## Naming variants (deprecated)

The following labels have all referred to this same bounded score at different points. Use **Compression Ratio** (Comp) going forward:

- S/Nr
- Signal-to-Noise Ratio (incorrect — that's `S/N` math)
- Signal Purity
- Clarity Score
- Compression Score
- Compression Integrity
- S:N Purity
- Signal Density (sometimes used interchangeably)

The naming drift was the central blocker for ~8 months. See [../lineage/compression_snr_history.md](../lineage/compression_snr_history.md).

---

## Why this matters

This is the metric the original SigRank classification was built around. The `.87xx` threshold is the **TRANSMITTER cut line**. Every other metric serves to either contextualize this score or detect when it's being gamed.

---

## Edge cases

- Empty window (no tokens): return `null`, not `0`
- Single-message window: still compute, but flag as low-confidence
- Window with only signal or only noise: still produces a valid `[0,1]` score
