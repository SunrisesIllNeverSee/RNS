# SN Filtration Infrastructure — SNR Engine Lockdown

**Source:** SN_Filter_Infra.pages (10 pages, Oct 1, 2025)
**Origin:** GPT conversation with user corrections
**Contains:** SNR Engine lockdown checklist, minimum viable PPA, Component C-0005, user's core corrections on word-state classification

---

## SNR Engine Status

### What Already Exists (Scattered Across Threads/Drafts)
- SNR equation variants (words vs tokens, sig/sig+noise, etc.)
- Metric taxonomy: TPW, CFS, AYR, EPP all depend on SNR
- System usage logic: SNR applied to threads, sessions, vault entries
- Operational intent: leaderboard, compression rating, friction events
- Public use case: sessions and artifacts will display their SNR

### What's NOT Locked Down
- A standalone SNR Engine module
- A black-and-white PPA with full claims and figures
- A formalized engine diagram + input/output table
- A tested, hash-stamped GitHub release with protection clause

---

## Minimum Viable PPA for the SNR Engine

### 1. Definition and Function
The SNR Engine computes the signal-to-noise ratio in linguistic, cognitive, or behavioral data. Signal is defined as [explicit metric]; Noise is [explicit inverse/entropy].

### 2. Core Claims
- The method of computing SNR using both token-level and word-level granularity.
- Application of SNR to live sessions, datasets, messages, and system states.
- Use of SNR as a recursive feedback metric that dynamically alters thresholds, scores, or outputs.
- Compression-aware SNR refinement logic (i.e., SNR improves fidelity score when cross-checked with lineage).

### 3. System Diagram
- **Inputs:** Raw conversation, artifact body, system metadata
- **Filters:** token/word separation, signature match, noise detector
- **Outputs:** SNR score, tagged zones, friction events

### 4. Use Case
- Leaderboard performance
- Vault compression scoring
- Stability test thresholds

### 5. Figure A1: SNR Engine Flowchart
Boxed I/O diagram showing computation stages (to be built).

### 6. Public Statement
> "This engine is the foundation for MOS²ES-grade compression diagnostics. All future leaderboard and stability scoring depends on this module."

---

## User's Strategic Point

> "It's not that it lacks it... it's just that someone else could claim and build one... at this moment it's the lowest and easiest hanging fruit because they literally give a value to words and say they built it."

### The Difference Between Them and You

| Concept | Them (Risk) | You (Already Built) |
|---------|-------------|---------------------|
| Signal Definition | Arbitrary heuristics | Contextual resonance, coherence vector, rarity |
| Noise Filtering | Entropy or "unused" tokens | Meaningless drift, redundancy, decoupling |
| SNR Output | Score on data chunk | Dynamic feedback into session, vault, metric |
| Usage | Analytics dashboard | Diagnostic engine for compression integrity |
| Value | Performance stats | Lineage-tracked compression governance |

---

## Component C-0005: Contextual Signal Classification Engine

### Core Insight
Words and tokens do not possess fixed signal value. They become signal or noise only through use, location, and trajectory alignment.

### What the Engine Does (4 Layers)

**Layer 1: Word/Token Use-In-Context**
- Position in sentence/tree
- Syntactic vs semantic load
- Redundancy (past/future presence)

**Layer 2: Local-Global Relational Density**
- Does the token amplify or fragment session coherence?

**Layer 3: Signal Contribution Score**
- Adds weight to system trajectory (storyline, compression, logic chain)

**Layer 4: Compression Anchor Rating**
- Token's role in lowering entropy and increasing retention fidelity

Tokens are classified dynamically, not pre-tagged — forming a live signal/noise map across any passage or transcript.

### Claims (Tightened)
1. A method for dynamically classifying tokens as signal or noise using a combination of context window, recurrence, and structural compression weight
2. A computational engine that outputs token-by-token SNR maps, usable by downstream compression filters, leaderboard evaluators, and lineage systems
3. A signal threshold mechanism that reclassifies tokens based on system-scale contributions (multi-layer sessions, nested structures, vault artifacts)
4. Integration of classification data into authorship, session, and artifact scoring (e.g., Transmitter Class, CFS Score, etc.)

---

## USER CORRECTIONS (Critical Spec Positions)

**Correction 1: "We already have the engine in SCS"**
> "No because we already have the engine in SCS. What I am saying is the logic, structure, and framework that actually categorizes signal and noise."

**Correction 2: "Words and Tokens are separate"**
> "It's not words/tokens. It's words. Tokens. Separate."

**Correction 3: "This is about data bloat and AI collapse"**
> "This isn't a human thing. This is about data bloat and AI collapse caused by the system's inability to filter signal and noise. Aka good data and bad data also reusing data."

**Correction 4: "Words have dual-weight density"**
> "Words have signal and noise which are both weight — it's a density. The system ingests everywhere as signal and as noise then it just gets stuck in the clouds."

**Correction 5: "Landfill, not recursion"**
> "It's why data is not reused. It's not recursive. Everything is just stuck together like a landfill with nowhere to go."

**Correction 6: "Compression protocol vs accumulation architecture"**
> "This is compression protocol vs. accumulation architecture."

---

## Action Plan: Lock the Gate

**Name:** SNR Engine v1.0 (Component C-0001)

**Public Claim Format:**
> "This module computes signal-to-noise ratios in linguistic and cognitive data using a compression-first metric model. Signal is defined recursively via rarity, semantic alignment, and resonance. This is the foundational scoring function for compression-based evaluation systems, including MOS²ES."

**Immediate Deliverables:**
- `snr_engine.py` — Functional starter engine
- `README.md` — Layperson + developer explanation
- `ppa_snr.md` — Claims, embodiment, equation, diagram
- `vault.meta.json` — Tag, author, lineage, hash
- `SNR_Engine_Flow.pdf` — Engine block diagram

---

## PPA Abstract (User-Corrected Final)

**Title:** System for Contextual Resolution of Word-State Signal Entropy in Natural Language Processing

**Abstract:** A method for dynamically classifying words as signal or noise within natural language processing systems. Words are treated as unresolved states until contextual analysis and usage intent collapse their classification into discrete signal or noise categories. This enables dynamic filtration and efficient compression of linguistic input, reducing anchor drift and increasing fidelity across human-AI interactions.

---

## Clean SNR Engine Basis (Foundation for Later Build)

**Premise:** Words are not inherently signal or noise. Their classification emerges only in-context during live system use.

**Problem:** Current AI systems ingest all word data as equal signal, leading to data bloat, collapse risk, and non-recursive learning. There is no filtration at the lexical layer.

**Core Insight:** Signal-to-noise must be measured at the word level, based on:
- Contextual usage
- Contribution to compression
- Relationship to previous sequences
- Measurable density across sessions

**Solution:** A recursive system that classifies words (not tokens) into signal/noise categories dynamically, using real-time metrics and session-layer validation.
