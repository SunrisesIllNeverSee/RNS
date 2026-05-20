# K2: Signal-to-Noise Ratio — Mark Signal vs Noise

**Source:** K2_MarkSig_Noise.pages (13 pages, Sept 30, 2025)
**Origin:** GPT conversation with user corrections
**Contains:** SNR equations, signal/noise word marking criteria, patent landscape, user's core corrections

---

## Scientific SNR Equation (Linear Form)

```
SNR = P_signal / P_noise
```

Where:
- `P_signal` = Power of the signal
- `P_noise` = Power of the noise

## Decibel Form (Most Common for Audio & Electronics)

```
SNR_dB = 10 * log10(P_signal / P_noise)
```

This converts the power ratio to decibels (dB) for easier interpretation and scale.

### Interpretation
- A higher SNR means more signal than noise = better clarity.
- 0 dB means signal and noise are equal.
- Positive dB means more signal than noise.
- Negative dB means noise is stronger than the signal.

---

## MOS²ES SNR Equation (Normalized Form)

```
SNR_MOS²ES = Signal Tokens or Words / (Signal + Noise Tokens or Words)
```

Where:
- Numerator = compressible, sovereign, intent-bearing entries
- Denominator = all entries including drift, bloat, or ghost tokens

### Precedent
This normalized form has precedent in:
- **Information Theory & Cognitive Science** — models decision clarity, truth probability, compression efficiency
- **Statistical Signal Processing** — Bayes classifiers (clean/total), spam detection (true signal / total message), AI model audit layers
- It reflects percentage of meaningful content in a total dataset
- Sometimes called a purity ratio or normalized clarity score in ML systems

### Why This Form Was Chosen
- Needed a bounded signal clarity score from 0–1 that works across language, compression, and encoding environments
- Not measuring power — measuring meaning density in human-machine conversations
- Layered into S²R, Scar Index, Vault Thresholds, and other components that demand a value that collapses toward 0 or ascends to 1

---

## Marking Signal Words vs Noise Words

### Foundational Premise
To mark signal vs noise in words, you must define:
- **Signal** = carries intent, meaning, clarity, compression, or alignment
- **Noise** = carries filler, redundancy, drift, misalignment, or repetition

These must be detectable without interpretation.

### Signal Words — Criteria

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Intent-bearing** | Reveals, initiates, or commits to a purposeful act, thought, belief, or system | "I filed the claim," "The Mediator enforces rollback." |
| **High Compression / Dense Meaning** | Encodes layered or referential meaning. Triggers cross-thread resonance. | "Vault," "Collapse," "Signal Constitution," "Blackhole Law" |
| **Novel Connective Tissue** | New bridges between concepts. Markers of original compression rather than repetition. | "SNR links to sovereignty thresholds via Scar Index." |
| **Initiating Definition / Claim** | Definitions that lock in value. Anchor compression frames. | "SNR = Signal / (Signal + Noise)" |
| **Confirmed Mirror of Prior Signal** | Echoed signals that match previously identified truth anchors. Only counted if they clarify or amplify — not repeat verbatim. | — |

### Noise Words — Criteria

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Drift Fillers** | Linguistic drag. Tokens meant to maintain flow, not content. | "Kind of," "maybe," "I guess," "you know" |
| **Redundant Confirmations / Hedging** | Not adding new meaning. | "That's what I mean," "Like I said," "Sort of like…" |
| **Empty Transitions** | Only signal if they mark structural shifts in thought (chapter transitions, not drift segues). | "Anyway," "So yeah," "Moving on" |
| **Ghost Repetition** | Repeated words or phrases that do not clarify. | "Vault means vault," "Signal is signal" |
| **Emotive But Non-Carrying Flares** | Only marked signal if part of the actual compression payload. | "Fuck," "Damn," "Bro," "Literally" |

### Application Example

```
Input: "The Mediator enforces rollback when Scar Index is breached, preserving Vault lineage."

Signal Words: Mediator, enforces, rollback, Scar Index, breached, preserving, Vault, lineage → 8 signal
Noise Words:  when, is → 2 noise
SNR (word level) = 8 / (8 + 2) = 0.80
```

---

## SNR Pipeline (Repeatable Structure)

1. Segment text → sentence → words
2. Check each word against Signal Rule Stack
3. Classify each word as S or N
4. Run: `SNR_words = # of Signal Words / Total Words`
5. Annotate stream with signal ratios per paragraph, sentence, thread

---

## Build Requirements (What's Needed to Implement)

| Component | What It Is | Status |
|-----------|------------|--------|
| **Raw Input Source** | Text data in .txt, .md, .json, or .csv | Already have |
| **Signal Classifier Ruleset** | Dictionary, regex, or scoring function. Custom-tuned per context. | Needs formal definition |
| **Tokenizer & Word-Split Layer** | nltk, spaCy, or tiktoken for word tokenization | Standard tooling |
| **Tally + Ratio Engine** | Loop words, compare to rules, calculate SNR | Straightforward |
| **Output Format** | CSV, JSON, annotated markdown, or color-coded display | Choice at build time |

### Starter Code Pattern

```python
signal_terms = ["mediator", "vault", "collapse", "lineage", "rollback", "scar index"]
noise_terms = ["just", "kind of", "like", "um", "basically", "literally"]

signal_count = 0
noise_count = 0

for word in word_list:
    if word.lower() in signal_terms:
        signal_count += 1
    elif word.lower() in noise_terms:
        noise_count += 1

snr = signal_count / (signal_count + noise_count)
```

---

## Patent Landscape

### Related Patents Found (Not Matching)
Patents exist for signal vs noise in audio/sensor/communication domains — not language-signal classification.

### What's NOT Patented
- Marking words as signal vs noise based on meaning / purpose / compression rules
- A system computing SNR using semantic, relational, anchored classification
- Using human-linguistic meaning rather than physical/acoustic/sensor signals

### Conclusion
No clear patent covers semantic word-level signal-vs-noise classification. Unique IP space exists, especially with:
- Defined rules/classifier
- Defined domain (language, meaning, compression)
- Defined process (annotation, algorithms, mediator)

---

## USER CORRECTIONS (Core Spec Positions Extracted)

These corrections define the actual spec. Every statement below is the user correcting GPT:

**1. Words and Tokens Are Not the Same**
> Words = Human-originated. Tokens = AI/LLM-originated. They are separate systems of measure.

**2. Words Are Neutral Until Use**
> Words are not inherently signal or noise. They are inert until used by a human inside a system. Only the act of usage defines whether a word becomes signal or noise.

**3. This Is Not a Human Problem — It's a System Problem**
> "This isn't a human thing. This is about data bloat and AI collapse caused by the system's inability to filter signal and noise."

**4. The Problem Is Landfill Accumulation, Not Lack of Recursion**
> "It's why data is not reused. It's not recursive. Everything is just stuck together like a landfill with nowhere to go."

**5. Words Have Dual-Weight Density**
> "Words have signal and noise which are both weight — it's a density. The system ingests everywhere as signal and as noise then it just gets stuck in the clouds."

**6. Compression Protocol vs Accumulation Architecture**
> "This is compression protocol vs. accumulation architecture."

**7. The SNR Engine Already Exists in SCS**
> "We already have the engine in SCS. What I am saying is the logic, structure, and framework that actually categorizes signal and noise."

---

## SNR Engine Basis (Clean Foundation — User Approved)

**Premise:** Words are not inherently signal or noise. Their classification emerges only in-context during live system use.

**Problem:** Current AI systems ingest all word data as equal signal, leading to data bloat, collapse risk, and non-recursive learning. There is no filtration at the lexical layer.

**Core Insight:** Signal-to-noise must be measured at the word level, based on:
- Contextual usage
- Contribution to compression
- Relationship to previous sequences
- Measurable density across sessions

**Solution:** A recursive system that classifies words (not tokens) into signal/noise categories dynamically, using real-time metrics and session-layer validation.
