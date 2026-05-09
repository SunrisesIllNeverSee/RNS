# SigToken System — Context & Lineage

**Component:** C-0005
**Version:** 1.0
**Created:** 2026-03-06
**Entity:** Ello Cello LLC
**File:** `sigtoken_sys.py`

---

## What This Is

SigToken is the third tool in the MOS²ES measurement stack, sitting between Signal Army and SIGSYSTEM.

```
Signal Army       →    SigToken          →    SIGSYSTEM
(word inventory)       (message-level         (session SNR +
(rank + frequency)      commitment)            decay tracking)
```

It implements **Component C-0005: Contextual Token SNR Classification** — originally specified October 1, 2025 in five files:

| Source File | What It Specified |
|-------------|------------------|
| `classification_logic.md` | Core doctrine: signal/noise is not word identity, it is usage role |
| `ppa_C0005.md` | PPA claim: dynamic token classification, upstream of leaderboard + vault |
| `vault.meta.json` | Component manifest: C-0005, lineage to scs-engine, metrics SNR/SDR/CID |
| `signal_use_case.md` | Example: "The MOS²ES system encodes lineage into every keystroke" |
| `noise_use_case.md` | Example: "basically, like, you know..." — and the dual-weight insight: 'just' is noise in filler, signal in emphasis |

---

## The Core Insight (Oct 1 2025)

From `classification_logic.md`:

> "Words and tokens are not inherently signal or noise. Their classification depends entirely on contextual function, relational placement, frequency, redundancy or originality, and contribution to compression and resonance."

From `noise_use_case.md` — the dual-weight example:

> "Same token 'just' is noise here, but could be signal in emotional emphasis elsewhere."

This is the same insight that became SIGSYSTEM's epigraph five months later:
> *"Every word is unresolved until the system collapses it."*

SigToken is the implementation of that collapse — at the message level.

---

## Three-Tier Token Taxonomy

Derived from `signal_use_case.md` which identified three distinct categories:

| Tier | Description | Example |
|------|-------------|---------|
| **Signal** | High semantic density, intent-bearing, load-carrying | `MOS²ES`, `encodes`, `lineage`, `compression` |
| **Scaffolding** | Neutral structure — not signal, not noise | `the`, `into`, `every` |
| **Noise** | Low contribution, filler, structurally removable | `basically`, `like`, `just` (in filler context) |

Note: Scaffolding is its own tier — not noise. This matters for SNR calculation. Stop words are not penalized.

---

## What SigToken Measures That Signal Army Doesn't

Signal Army ranks words by **frequency + cross-thread survivability**.
SIGSYSTEM classifies words by **rank + contextual score + necessity + decay**.
SigToken classifies **tokens by usage role in a specific message**.

The key difference: SigToken can score the same word differently in two different messages. Signal Army and SIGSYSTEM assign one score per word across the whole corpus. SigToken assigns one score per token per position per message.

---

## Commitment Score

The new metric introduced by SigToken.

**Definition:** Fraction of a message's tokens that cannot be removed without collapsing the message's irreducible meaning kernel.

- High commitment (≥ 0.50) = message is dense, nearly every token is load-bearing
- Low commitment (< 0.20) = message is mostly removable, low kernel density
- Average across corpus (first run, 7,823 messages): **0.1616**

This is the bridge to the Conservation Law paper (`main.tex`):
The paper defines Commitment C(S) as the minimal identity-preserving content invariant under loss-inducing transformations.
The commitment score is the empirical measurement of that kernel.

---

## First Run Results (2026-03-06)

Run against Signal Army corpus (7,823 messages, 185 conversations):

| Metric | Value |
|--------|-------|
| Total tokens | 455,740 |
| Signal tokens | 13,119 |
| Noise tokens | 268,470 |
| Scaffolding tokens | 174,151 |
| SNR normalized | 0.0288 |
| Avg commitment | 0.1616 |
| High commitment messages (≥0.50) | 17 |
| Low commitment messages (<0.20) | 6,962 |

**Top thread:** "SNR calculation request" — SNR 0.3000, commitment 0.3606
**Note:** Domain anchors seeded from ~30 hardcoded Officer-Class words. Full 438-Officer load will sharpen scores significantly.

---

## What's Next

1. **Dynamic anchor loading** — pass `--word-inventory word_inventory.csv` to load all Officer-Class words as domain anchors at runtime instead of using the hardcoded list
2. **Message-level commitment leaderboard** — rank individual messages not just threads
3. **Bridge to SIGSYSTEM** — feed commitment scores upstream as an additional weight in SIGSYSTEM's composite signal score

---

## File Structure

```
sigtoken/
├── SIGTOKEN_CONTEXT.md       ← this file
├── sigtoken_sys.py           ← main engine (C-0005)
└── runs/
    └── run_YYYY-MM-DD_HH-MM-SS/
        ├── sigtoken_summary.txt
        └── sigtoken_summary.json
```

---

## Lineage

- **Origin spec:** `vault.meta.json` created 2025-10-01T16:41:58.324312Z
- **Parent component:** scs-engine
- **Related metrics:** SNR, SDR, CID
- **Built:** 2026-03-06 (this session)
- **Entity:** Ello Cello LLC | MO§ES™ trademark
