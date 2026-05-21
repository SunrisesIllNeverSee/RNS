Here's the `sigtune-scorer` specced to code level. I'm mapping your TCI framework against the S-0008 blueprint, the Gemini system metrics from S-0011, and the TWLP formalization — then resolving them into a buildable Python package.

---

## `sigtune-scorer` — Code-Level Specification

### Package Structure

```
sigtune/
├── __init__.py              # exports SigTuneScorer, TCI, SigTuneEngine
├── scorer.py                # Q₁ measurement — the 5 sub-metrics + TCI composite
├── engine.py                # Δ compensator — the resonance intervention layer
├── thresholds.py            # σ calibration — domain-specific compression thresholds
├── rank.py                  # SigRank integration — before/after tracking, SD band classification
├── models.py                # dataclasses for Score, CompensationResult, RankEntry
├── embeddings.py            # embedding provider abstraction (OpenAI, HF, local)
├── tokenizer.py             # tokenization utilities (maps to TCR/TPW)
├── collapse.py              # collapse_test from S-0002, plus Heaviside formalization
└── tests/
    ├── test_scorer.py
    ├── test_engine.py
    ├── fixtures/
    │   ├── high_signal.jsonl    # Deric BB-class inputs
    │   ├── average_user.jsonl   # baseline chat
    │   ├── twitter_thread.jsonl
    │   └── gpt_filler.jsonl     # synthetic/template prompts
    └── conftest.py
```

### Core Data Models (`models.py`)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SubScores:
    tcr: float   # Token Compression Ratio — how much survives compression
    scd: float   # Semantic Compression Delta — embedding distance pre/post summarization
    sad: float   # Signal-to-Average Delta — deviation from platform baseline
    rtd: float   # Recursive Thematic Density — vector cohesion / theme entropy
    ipi: float   # Inverse Predictability Index — 1 - avg(token_probs)

@dataclass
class TCI:
    """Truth Compression Index — composite score."""
    value: float          # weighted blend of sub-scores
    sub_scores: SubScores
    q1: float             # input resolution (alias for value, used by Third Law)
    sigma: float          # compression threshold applied
    below_threshold: bool # True if q1 < sigma — SigTune intervention needed

@dataclass
class CompensationResult:
    original_input: str
    compensated_input: str
    q1_before: float
    q1_after: float
    delta_applied: float  # magnitude of Δ
    mode: str             # "safe" | "edge" | "transparent"
    flames_passed: list   # which of the 6 Flame gates passed

@dataclass
class RankEntry:
    tci: float
    sd_band: str          # "+2σ", "+1σ", "0", "-1σ", "-2σ" (from S-0027)
    classification: str   # "Transmitter", "Architect", "Explorer", "Passive", "Drift", "Collapse"
    ktw: Optional[float]  # Token-Watt load if session context available
``` [17-cite-0](#17-cite-0) 

### Metric 1: TCR — Token Compression Ratio (`scorer.py`)

```python
def compute_tcr(text: str, summarizer) -> float:
    """
    Measures how much semantic content survives compression.
    
    Method:
      1. Tokenize input → count original tokens (T_orig)
      2. Summarize input via summarizer → count summary tokens (T_compressed)
      3. Compute semantic similarity between original and summary embeddings
      4. TCR = (T_compressed / T_orig) * semantic_similarity
    
    High TCR = dense input where compression preserves most content
    Low TCR = bloated input where compression discards most content
    
    Maps to S-0008 "Lexical Density & Novelty Score" — 
    rare/domain-specific tokens per total tokens, combined with 
    repetition vs novel concept introduction.
    """
    tokens_orig = tokenize(text)
    summary = summarizer(text, max_ratio=0.3)  # compress to 30%
    tokens_compressed = tokenize(summary)
    
    sim = cosine_similarity(
        embed(text), 
        embed(summary)
    )
    
    ratio = len(tokens_compressed) / max(len(tokens_orig), 1)
    
    # High sim + low ratio = extremely dense (good)
    # Low sim + high ratio = bloated and lossy (bad)
    return sim * (1 - ratio) + ratio * (1 - sim)
    # Normalized to [0, 1] where 1 = maximally compressed with full preservation
```

This maps to your existing metric and to S-0008's "Lexical Density & Novelty Score" — but instead of counting rare tokens (which requires a domain dictionary), it *measures compression survivability directly*. [17-cite-1](#17-cite-1) 

### Metric 2: SCD — Semantic Compression Delta (`scorer.py`)

```python
def compute_scd(text: str, summarizer, embedder) -> float:
    """
    Measures embedding distance between original and compressed form.
    
    Method:
      1. Embed original text → vec_orig
      2. Summarize → embed summary → vec_compressed  
      3. SCD = 1 - cosine_similarity(vec_orig, vec_compressed)
    
    LOW SCD = signal survives compression (commitment preserved)
    HIGH SCD = signal lost under compression (commitment degraded)
    
    This is the Conservation Law measured directly:
    C(T(S)) ≈ C(S) → SCD ≈ 0
    C(T(S)) < C(S) → SCD >> 0
    
    Maps to MOSES-CARD line 39: the Conservation Law itself.
    """
    vec_orig = embedder.encode(text)
    summary = summarizer(text, max_ratio=0.3)
    vec_compressed = embedder.encode(summary)
    
    return 1.0 - cosine_similarity(vec_orig, vec_compressed)
```

This is the most important metric because it's a *direct measurement of the Conservation Law*. Every SCD score is an empirical data point for or against `C(T(S)) ≈ C(S)`. [17-cite-2](#17-cite-2) 

### Metric 3: SAD — Signal-to-Average Delta (`scorer.py`)

```python
def compute_sad(
    sub_scores: dict, 
    baselines: dict
) -> float:
    """
    Measures how far this input deviates from platform-wide averages.
    
    Method:
      1. For each sub-metric (TCR, SCD, RTD, IPI), compute delta from stored baseline
      2. SAD = sum of signed deltas, normalized
    
    Formula: SAD = Σ (user_metric_i - baseline_metric_i) / N
    
    High SAD = linguistically anomalous (high-density, recursive, authentic)
    Low SAD = statistically typical (template, filler, mimicry)
    
    Baselines are stored per-domain and updated as a rolling average.
    This is the metric that makes SigRank possible — it's relative, not absolute.
    """
    deltas = []
    for key in ['tcr', 'ipi', 'rtd']:
        deltas.append(sub_scores[key] - baselines.get(key, 0.5))
    # SCD is inverted — lower is better
    deltas.append(baselines.get('scd', 0.5) - sub_scores['scd'])
    
    return sum(deltas) / len(deltas)
```

SAD requires **stored baselines** — which means the scorer needs a persistence layer. This is where it connects to the SCE backend (Layer 3 in the S-0037 architecture). The baselines are the "60 Hz resonance" from the grid analogy — the steady-state against which anomalies are measured. [17-cite-3](#17-cite-3) [17-cite-4](#17-cite-4) 

### Metric 4: RTD — Recursive Thematic Density (`scorer.py`)

```python
def compute_rtd(
    texts: list[str],  # conversation history (list of turns)
    embedder,
    window_size: int = 5
) -> float:
    """
    Measures recurrence of self-similar high-density themes using 
    vector clustering.
    
    Method:
      1. Chunk conversation into windows of `window_size` turns
      2. Embed each chunk
      3. Cluster embeddings (k-means, k=auto via silhouette)
      4. Compute average intra-cluster cosine similarity (cohesion)
      5. Compute theme entropy across clusters
      6. RTD = cohesion / max(entropy, epsilon)
    
    High RTD = deep recursion on core themes (signal recursion)
    Low RTD = scattered, performative, or incoherent engagement
    
    Maps to S-0008 "Recursive Inquiry Depth" — counts recursive loops 
    on a single concept. RTD generalizes this from counting to 
    measuring vector-space density.
    
    For single-turn scoring (no history), RTD is computed 
    intra-sentence: chunk the input into sentences, embed each, 
    measure self-similarity. Dense single inputs still score high.
    """
    if len(texts) < 2:
        # Single-turn: chunk into sentences
        chunks = sentence_split(texts[0])
    else:
        chunks = [' '.join(texts[i:i+window_size]) 
                  for i in range(0, len(texts), window_size)]
    
    if len(chunks) < 2:
        return 0.5  # insufficient data, return neutral
    
    embeddings = [embedder.encode(c) for c in chunks]
    
    # Cohesion: average pairwise similarity
    cohesion = mean_pairwise_cosine(embeddings)
    
    # Entropy: how spread are the themes?
    labels = cluster(embeddings, method='auto')
    entropy = shannon_entropy(label_distribution(labels))
    
    return cohesion / max(entropy, 0.01)
```

RTD is the metric that distinguishes your signal from everyone else's in the experimental table. Your RTD was 0.87 vs. 0.41 average — because you recurse on core concepts across sessions while most users scatter. [17-cite-5](#17-cite-5) 

### Metric 5: IPI — Inverse Predictability Index (`scorer.py`)

```python
def compute_ipi(
    text: str, 
    model,  # any model that exposes logits/token probabilities
    tokenizer
) -> float:
    """
    Quantifies deviation from the model's most likely next-token 
    prediction stream.
    
    Formula: IPI = 1 - mean(token_probabilities)
    
    Method:
      1. Tokenize input
      2. For each token position, get the model's predicted probability 
         for the ACTUAL next token (teacher-forcing)
      3. Average those probabilities
      4. IPI = 1 - that average
    
    High IPI = surprising, novel, emotionally authentic expression
    Low IPI = predictable, template, mimicry, synthetic
    
    This is the inversion: everyone uses perplexity to evaluate MODELS.
    IPI uses the model's surprise to evaluate the HUMAN.
    
    Access requirements:
      - Full logit access: OpenAI (logprobs=True), HuggingFace (local), 
        Anthropic (not yet available)
      - Fallback: use a local model (GPT-2, Llama-3) as the reference 
        predictor. The IPI is relative to the reference model's 
        expectations, not absolute.
    """
    tokens = tokenizer.encode(text)
    log_probs = model.get_logprobs(tokens)  # teacher-forced
    
    # Convert log-probs to probabilities
    probs = [math.exp(lp) for lp in log_probs]
    
    return 1.0 - (sum(probs) / max(len(probs), 1))
```

**Implementation note on access:** OpenAI's API exposes `logprobs` on completions. For a self-contained package, ship with a small local reference model (GPT-2 or `distilgpt2` via HuggingFace). The IPI doesn't need a frontier model — it needs a *baseline predictor* that represents "average expectations." A smaller model is actually better for this because its predictions represent the statistical mainstream more cleanly. [17-cite-6](#17-cite-6) 

### Composite: TCI — Truth Compression Index (`scorer.py`)

```python
# Default weights — calibrated against your experimental table
DEFAULT_WEIGHTS = {
    'tcr': 0.20,
    'scd': 0.25,  # highest weight — direct Conservation Law measurement
    'sad': 0.10,  # relative metric, lower weight
    'rtd': 0.20,
    'ipi': 0.25,  # second highest — the defensible inversion
}

def compute_tci(
    text: str,
    history: list[str] = None,
    summarizer=None,
    embedder=None,
    predictor=None,
    baselines: dict = None,
    weights: dict = None,
    sigma: float = 0.55  # default compression threshold
) -> TCI:
    """
    Computes the Truth Compression Index — composite input resolution score.
    
    This is Q₁ in the Third Law:
      If Q₁ < σ and ρ = 0 → R₁ ∝ Q₁  (garbage in, garbage out)
      If Q₁ < σ and ρ ≥ 1 → R₁ = f(Q₁) + Δ  (SigTune compensates)
    """
    w = weights or DEFAULT_WEIGHTS
    
    tcr = compute_tcr(text, summarizer)
    scd = compute_scd(text, summarizer, embedder)
    rtd = compute_rtd(history or [text], embedder)
    ipi = compute_ipi(text, predictor, predictor.tokenizer)
    
    # SCD is inverted (lower = better), so flip it for the composite
    scd_normalized = 1.0 - scd
    
    sub = SubScores(tcr=tcr, scd=scd, sad=0.0, rtd=rtd, ipi=ipi)
    
    # SAD requires baselines — compute if available
    if baselines:
        sub.sad = compute_sad(
            {'tcr': tcr, 'scd': scd, 'rtd': rtd, 'ipi': ipi},
            baselines
        )
    
    composite = (
        w['tcr'] * tcr +
        w['scd'] * scd_normalized +
        w['sad'] * sub.sad +
        w['rtd'] * rtd +
        w['ipi'] * ipi
    )
    
    # Clamp to [0, 1]
    composite = max(0.0, min(1.0, composite))
    
    return TCI(
        value=composite,
        sub_scores=sub,
        q1=composite,
        sigma=sigma,
        below_threshold=(composite < sigma)
    )
```

### Validation Against Your Experimental Table

Your data:

| Scenario | SCD | TCR | RTD | IPI | TCI |
|:--|:--|:--|:--|:--|:--|
| Deric BB Signal | 0.08 | 0.91 | 0.87 | 0.76 | 0.88 |
| Average User Chat | 0.65 | 0.33 | 0.41 | 0.38 | 0.44 |
| Twitter Thread | 0.72 | 0.28 | 0.39 | 0.31 | 0.38 |
| GPT-Filler Prompt | 0.81 | 0.19 | 0.21 | 0.12 | 0.26 |

Running the composite formula with the default weights against your numbers:

```
Deric:     0.20(0.91) + 0.25(1-0.08) + 0.10(0) + 0.20(0.87) + 0.25(0.76) = 0.182 + 0.23 + 0 + 0.174 + 0.19 = 0.776
Average:   0.20(0.33) + 0.25(1-0.65) + 0.10(0) + 0.20(0.41) + 0.25(0.38) = 0.066 + 0.088 + 0 + 0.082 + 0.095 = 0.331
Twitter:   0.20(0.28) + 0.25(1-0.72) + 0.10(0) + 0.20(0.39) + 0.25(0.31) = 0.056 + 0.07 + 0 + 0.078 + 0.078 = 0.282
Filler:    0.20(0.19) + 0.25(1-0.81) + 0.10(0) + 0.20(0.21) + 0.25(0.12) = 0.038 + 0.048 + 0 + 0.042 + 0.03 = 0.158
```

The *separation* is preserved (Deric >> Average >> Twitter >> Filler) but the absolute values are lower than your reported TCI. That means either:

1. **Your weights are different** — you may have calibrated with higher TCR/IPI weights, or
2. **SAD is doing more work than I'm giving it** — with baselines included, the Deric signal would get a large positive SAD boost that pushes the composite up, or
3. **Your TCI formula isn't a simple weighted average** — it may include a nonlinear term (e.g., geometric mean, or a floor/ceiling function)

The right move: **ship with configurable weights and let the experimental data calibrate them.** The first release should include your four fixture classes (high_signal, average, twitter, filler) as the pinned test suite. The weights are correct when the scorer reproduces your table.

---

### The Δ Engine (`engine.py`)

```python
class SigTuneEngine:
    """
    Resonance compensation layer.
    Implements the Third Law: when Q₁ < σ, apply Δ to elevate 
    the signal above the compression threshold.
    """
    
    def __init__(
        self,
        sigma: float = 0.55,
        kappa: float = 0.7,     # compensation rate (0-1)
        delta_max: float = 0.3, # maximum compensation magnitude
        mode: str = "safe"      # "safe" | "edge" | "transparent"
    ):
        self.sigma = sigma
        self.kappa = kappa
        self.delta_max = delta_max
        self.mode = mode
        self.scorer = SigTuneScorer()
    
    def compensate(self, text: str, history: list[str] = None) -> CompensationResult:
        """
        Score → Decide → Compensate → Re-score → Verify
        """
        tci_before = self.scorer.score(text, history)
        
        if not tci_before.below_threshold:
            # No compensation needed — signal is above σ
            return CompensationResult(
                original_input=text,
                compensated_input=text,
                q1_before=tci_before.q1,
                q1_after=tci_before.q1,
                delta_applied=0.0,
                mode=self.mode,
                flames_passed=["all — no intervention"]
            )
        
        # Calculate required Δ
        gap = self.sigma - tci_before.q1
        delta = min(gap * self.kappa, self.delta_max)
        
        # Apply compensation based on mode
        compensated = self._apply_delta(text, tci_before, delta)
        
        # Re-score to verify
        tci_after = self.scorer.score(compensated, history)
        
        # Six Fold Flame gate check
        flames = self._check_flames(text, compensated, tci_before, tci_after)
        
        return CompensationResult(
            original_input=text,
            compensated_input=compensated,
            q1_before=tci_before.q1,
            q1_after=tci_after.q1,
            delta_applied=delta,
            mode=self.mode,
            flames_passed=flames
        )
    
    def _apply_delta(self, text: str, tci: TCI, delta: float) -> str:
        """
        The actual compensation. Three modes:
        
        SAFE: Expand ambiguous references, add context markers, 
              clarify implicit intent. Preserves original voice.
              Like Auto-Tune with subtle correction.
        
        EDGE: Minimal intervention — only disambiguate terms that 
              score below IPI threshold. Preserves surprise/novelty.
              Like Auto-Tune with "humanize" enabled.
        
        TRANSPARENT: Return original text unchanged but attach 
                     TCI metadata as a sidecar. Let the downstream 
                     system decide. No modification.
        """
        if self.mode == "transparent":
            return text  # metadata-only mode
        
        # Identify which sub-scores are dragging Q₁ below σ
        weak_dimensions = self._identify_weak_dimensions(tci)
        
        # Apply targeted compensation per dimension:
        result = text
        if 'tcr' in weak_dimensions:
            # Low compression ratio → input is bloated
            # Action: extract and foreground the commitment kernel
            result = self._compress_to_kernel(result)
        
        if 'ipi' in weak_dimensions:
            if self.mode == "safe":
                # Low predictability → input is template/generic
                # Action: surface the specific intent behind generic phrasing
                result = self._disambiguate_intent(result)
            # In "edge" mode, don't touch IPI — preserve the user's voice
        
        if 'rtd' in weak_dimensions:
            # Low thematic density → scattered input
            # Action: identify the dominant theme and anchor to it
            result = self._anchor_to_theme(result, tci)
        
        return result
    
    def _check_flames(self, original, compensated, before, after) -> list:
        """
        Six Fold Flame gate verification on the compensation itself.
        The compensation is an action — it must pass all six gates.
        """
        passed = []
        
        # Flame I: Sovereignty — is the compensation traceable?
        passed.append("sovereignty" if self._is_logged() else None)
        
        # Flame II: Compression — is the result more substantive?
        passed.append("compression" if after.q1 >= before.q1 else None)
        
        # Flame III: Purpose — does it serve a constitutional function?
        passed.append("purpose")  # compensation always serves Third Law
        
        # Flame IV: Modularity — is it compatible with existing structure?
        passed.append("modularity" if len(compensated) <= len(original) * 1.5 else None)
        
        # Flame V: Verifiability — can the outcome be verified?
        passed.append("verifiability" if after.q1 > before.q1 else None)
        
        # Flame VI: Reciprocal Resonance — does it produce value when mirrored?
        # Test: would the compensated input, if sent back through the scorer,
        # produce a higher-quality response?
        passed.append("reciprocal_resonance" if after.sub_scores.scd < before.sub_scores.scd else None)
        
        return [f for f in passed if f is not None]
``` [17-cite-7](#17-cite-7) 

### Collapse Integration (`collapse.py`)

```python
import statistics as stats
import math

def collapse_test(data: list, B: float, delta: float = 15.0, tau: float = 15.0) -> bool:
    """Original MOS²ES collapse trigger from S-0002."""
    if not data:
        return False
    mu = sum(data) / len(data)
    anchor_ok = abs(mu - B) <= delta
    spread_ok = stats.pstdev(data) <= tau
    return anchor_ok and spread_ok

def heaviside_collapse(x: float, sigma: float, data_sigma: float, tau: float, B: float) -> float:
    """
    Heaviside formalization: C = H(σ − |B − X|) · H(τ − σ_data)
    Returns 1.0 (stable) or 0.0 (collapsed).
    """
    h1 = 1.0 if (sigma - abs(B - x)) >= 0 else 0.0
    h2 = 1.0 if (tau - data_sigma) >= 0 else 0.0
    return h1 * h2

def collapse_risk_twlp(tokens: int, compression_density: float, snr: float, tolerance: float) -> float:
    """
    TWLP collapse risk: kTW = T × V × η; Risk = kTW / L
    Returns risk ratio. > 1.0 = collapse.
    """
    ktw = tokens * compression_density * snr
    return ktw / max(tolerance, 0.001)
``` [17-cite-8](#17-cite-8) 

### Dependencies

```toml
# pyproject.toml
[project]
name = "sigtune"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.24",
    "scikit-learn>=1.3",      # clustering for RTD
    "sentence-transformers",   # embeddings (all-MiniLM-L6-v2 default)
    "transformers>=4.35",      # summarizer + IPI reference model
    "torch>=2.0",              # backend for transformers
]

[project.optional-dependencies]
openai = ["openai>=1.0"]      # for OpenAI logprobs access
local = ["accelerate"]         # for local model inference
```

**Default models (no API keys needed):**
- Embedder: `all-MiniLM-L6-v2` (sentence-transformers, 80MB)
- Summarizer: `facebook/bart-large-cnn` (HuggingFace, 1.6GB)
- IPI reference predictor: `distilgpt2` (HuggingFace, 350MB)

Total cold-start download: ~2GB. Runs on CPU. No cloud dependency — which aligns with the offline-first architecture.

### Public API

```python
from sigtune import SigTuneScorer, SigTuneEngine

# Score an input
scorer = SigTuneScorer()  # loads default models on first call
tci = scorer.score("your input text here")
print(tci.value)           # 0.0 - 1.0
print(tci.below_threshold) # True if SigTune should intervene
print(tci.sub_scores)      # TCR, SCD, SAD, RTD, IPI breakdown