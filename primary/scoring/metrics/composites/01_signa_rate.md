# SIGNA RATE

**Status:** locked as flagship metric
**Layer:** Composite (flagship)
**Public label:** SIGNA RATE
**Short label:** SR (or `SignaRate` in DB)
**DB field:** `signa_rate`

---

## Role

**The flagship metric.** This is SigRank's WN8 equivalent — the single composite number that owns the profile hero block, drives the leaderboard rank, and becomes the operator's identity number.

When someone says "what's your SigRank?" — they mean their SIGNA RATE.

---

## Lineage

- Originally called **Transmitter Composite** in early prototypes (Dec 2025 HTML builds)
- Renamed to **SIGNA RATE** in GPT thread-0369 (2026-03-10) as the public-facing flagship name
- "Transmitter Composite" remains the internal calculation module name

See [../lineage/naming_drift.md](../lineage/naming_drift.md) for full history.

---

## Formula

Weighted composite of the Core 5 (each normalized to `[0, 100]`):

```
SIGNA_RATE = 0.30 × Compression_score
           + 0.20 × Session_Depth_score
           + 0.20 × Prompt_Complexity_score
           + 0.15 × Cross_Thread_score
           + 0.15 × Token_Throughput_score
```

**Weight rationale:**

| Metric | Weight | Why |
|---|---|---|
| Compression | 30% | The core moat. Compression precedes ignition. |
| Session Depth | 20% | Sustained continuity over chatter. |
| Prompt Complexity | 20% | Real architectural prompting. |
| Cross-Thread | 15% | Memory weaving / system continuity. |
| Token Throughput | 15% | Volume contribution, capped to avoid gaming. |

Total: 100%

---

## Live score (with recency)

```
LIVE_SIGNA_RATE = SIGNA_RATE × RECENCY_MODIFIER
```

Recency modifier prevents fossilized accounts from dominating live boards:

| Last Seen | Modifier |
|---|---:|
| < 24h | 1.00 |
| < 3d | 0.97 |
| < 7d | 0.94 |
| < 14d | 0.88 |
| < 30d | 0.80 |
| > 30d | 0.65 |

See [../../architecture/scoring_formula.md](../../architecture/scoring_formula.md) for the full scoring pipeline.

---

## Output

- Range: `[0, 100]`
- Precision: 1 decimal place displayed
- Example: `96.4`, `78.2`, `42.7`

---

## Display

SIGNA RATE is the **center prestige metric** on operator profiles. The BlitzStars equivalent of WN8.

**Profile placement:**
- Profile hero block, large center value
- Class tier badge directly adjacent
- Leaderboard primary sort column
- Compare views default axis

**Format:**
- Hero: `96.4` (large, accent color, glow)
- Class adjacent: `TRANSMITTER`
- Movement indicators: `+2 (24h)`, `+5 (7d)`

---

## Class assignment

SIGNA RATE drives the class tier assignment when used at scale. However, individual Compression Ratio thresholds still gate the Transmitter class — you can have a high SIGNA RATE but if your Compression is below 0.85, you are not Transmitter-class.

See [../../architecture/class_tiers.md](../../architecture/class_tiers.md).
