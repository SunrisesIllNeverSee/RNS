#!/usr/bin/env python3
"""
SIGSYSTEM — Signal Classification & Measurement Subsystem
"Every word is unresolved until the system collapses it."

Consumes Signal Army CSV output and applies the SIGSYSTEM 5-stage
pipeline to classify words as Signal or Noise, compute SNR at every
level (word, message, thread, session), measure compression necessity,
and track signal decay across threads.

Architecture (from PPA-safe foundation doc):
    Stage 1: Input Evaluation
    Stage 2: Contextual Assessment
    Stage 3: Structural Necessity Evaluation
    Stage 4: Classification (dual-weight: signal + noise)
    Stage 5: Recursive Validation & Longitudinal Tracking

Usage:
    python sigsystem.py --run-dir ../signal_army/runs/run_2026-03-02_06-03-50/
    python sigsystem.py --run-dir ../signal_army/runs/run_2026-03-02_06-03-50/ --output-dir ./runs/
"""

import argparse
import csv
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

# Handle large CSV fields (flattened_messages can contain entire transcripts)
csv.field_size_limit(10 * 1024 * 1024)  # 10 MB

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "1.1"

# Base signal scores by Signal Army rank
# These represent the structural assessment from Signal Army —
# SIGSYSTEM refines them with contextual, necessity, and decay analysis
RANK_SIGNAL_BASE = {
    'Officer-Class':    0.85,
    'Doctrine Builder': 0.70,
    'Division':         0.55,
    'Platoon':          0.40,
    'Squad':            0.25,
    'Fireteam':         0.15,
    'Scout':            0.10,
    'Infantry':         0.05,
}

# Weights for the composite signal score
W_RANK = 0.20        # structural rank from Signal Army
W_CONTEXT = 0.25     # contextual assessment (thread spread, division membership)
W_NECESSITY = 0.35   # compression necessity (structural dependency)
W_DECAY = 0.20       # longitudinal trajectory bonus/penalty

# Classification threshold — above = Signal, below = Noise
SIGNAL_THRESHOLD = 0.35

# Stop words — must match Signal Army's list for consistent tokenization
STOP_WORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'so', 'if', 'of', 'in', 'on',
    'at', 'to', 'for', 'from', 'with', 'by', 'about', 'as', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'am', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'done', 'will', 'would',
    'shall', 'should', 'can', 'could', 'may', 'might', 'must',
    'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself',
    'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
    'herself', 'it', 'its', 'itself', 'we', 'us', 'our', 'ours',
    'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
    'who', 'whom', 'whose', 'which', 'what', 'that', 'this', 'these',
    'those', 'into', 'through', 'between', 'after', 'before', 'during',
    'without', 'within', 'upon', 'above', 'below', 'under', 'over',
    'against', 'along', 'among', 'around', 'behind', 'beside', 'beyond',
    'beneath', 'despite', 'except', 'inside', 'outside', 'toward',
    'towards', 'until', 'unto', 'via', 'up', 'down', 'out', 'off',
    'because', 'although', 'though', 'while', 'when', 'where', 'whether',
    'unless', 'since', 'than', 'like', 'very', 'really', 'just', 'also',
    'too', 'quite', 'rather', 'still', 'already', 'always', 'often',
    'sometimes', 'ever', 'even', 'only', 'then', 'now', 'here', 'there',
    'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither',
    'much', 'many', 'more', 'most', 'few', 'less', 'several', 'such',
    'own', 'other', 'another', 'else', 'same', 'well', 'back', 'get',
    'got', 'going', 'go', 'went', 'goes', 'come', 'came', 'put', 'take',
    'took', 'taken', 'make', 'made', 'let', 'say', 'said', 'says',
    'tell', 'told', 'ask', 'asked', 'see', 'saw', 'seen', 'look',
    'looked', 'give', 'gave', 'given', 'been', 'being', 'become', 'became',
    'keep', 'kept', 'thing', 'things', 'way', 'ways', 'one', 'two',
    'three', 'first', 'second', 'could', 'would', 'should', 'may',
    'might', 'must', "i'm", "i've", "i'll", "i'd", "it's", "that's",
    "there's", "here's", "don't", "doesn't", "didn't", "won't",
    "wouldn't", "shouldn't", "can't", "couldn't", "isn't", "aren't",
    "wasn't", "weren't", "haven't", "hasn't", "hadn't", "let's",
    "he's", "she's", "we're", "they're", "you're", "we've", "they've",
    "you've", "who's", "what's", 'okay', 'ok', 'yeah', 'yes', 'oh',
    'ah', 'um', 'uh', 'lol', 'gonna', 'wanna', 'gotta', 'etc', 'eg', 'ie',
})

# Infantry words (from Signal Army — noise carriers, rank-capped)
INFANTRY_WORDS = frozenset({
    'not', 'no', 'yes', 'never', 'none', 'nothing',
    'how', 'why', 'what', 'where', 'when',
    'think', 'know', 'feel', 'want', 'need', 'believe', 'understand',
    'mean', 'thought', 'knew', 'felt', 'wanted', 'needed',
    'high', 'low', 'new', 'old', 'good', 'bad', 'big', 'small',
    'right', 'wrong', 'different', 'specific', 'real', 'true', 'full',
    'long', 'short', 'hard', 'easy', 'possible', 'important',
    'better', 'best', 'able', 'available', 'clear', 'sure', 'next',
    'use', 'used', 'using', 'work', 'working', 'works', 'worked',
    'run', 'running', 'runs', 'set', 'start', 'started', 'help',
    'try', 'tried', 'trying', 'show', 'shows', 'call', 'called',
    'point', 'part', 'level', 'type', 'kind', 'form', 'case',
    'end', 'line', 'world', 'place', 'time', 'people', 'man',
    'great', 'actually', 'basically', 'literally', 'probably',
    'exactly', 'maybe', 'perhaps', 'simply', 'certainly', 'definitely',
    'bit', 'lot', 'enough', 'whole', 'entire',
})

# Compound words (match Signal Army)
COMPOUND_WORDS = {
    'mo§es': 'moses',
    'moses™': 'moses',
    'mo§es™': 'moses',
    'sigrank': 'sigrank',
}

# Protected from stemming
NO_STEM = frozenset({
    'moses', 'moes', 'sigrank', 'fracto', 'abba', 'aaron', 'kleya',
    'luthen', 'nemik', 'hange', 'levi', 'zoran', 'keter',
    'analysis', 'basis', 'thesis', 'genesis', 'axis',
    'coherence', 'governance', 'compliance', 'insurance', 'convergence',
    'class', 'process', 'address', 'access', 'success', 'stress',
})


# ---------------------------------------------------------------------------
# Stemmer (identical to Signal Army for consistency)
# ---------------------------------------------------------------------------

def stem_word(word):
    """Lightweight stemmer matching Signal Army's logic."""
    if word in NO_STEM:
        return word
    if len(word) <= 3:
        return word
    if word.endswith("'s"):
        return word[:-2]
    if word.endswith("s'"):
        return word[:-1]
    if word.endswith('ing') and len(word) > 5:
        base = word[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            return base[:-1]
        return base
    if word.endswith('ly') and len(word) > 4:
        return word[:-2]
    if word.endswith('ed') and len(word) > 4:
        base = word[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            return base[:-1]
        if word.endswith('ated') and len(word) > 5:
            return word[:-1]
        return base
    if word.endswith('s') and not word.endswith('ss') and len(word) > 3:
        if word.endswith('ies') and len(word) > 4:
            return word[:-3] + 'y'
        if word.endswith('es') and len(word) > 4:
            if word.endswith(('ses', 'xes', 'zes', 'ches', 'shes')):
                return word[:-2]
            return word[:-1]
        if not word.endswith(('us', 'is', 'ss')):
            return word[:-1]
    return word


def tokenize(text):
    """Tokenize text matching Signal Army's approach.
    Returns ALL tokens (including stop words and infantry) for SNR computation."""
    text = text.lower()
    for pattern, replacement in COMPOUND_WORDS.items():
        text = text.replace(pattern, replacement)
    text = re.sub(r"[^\w\s'\-]", ' ', text)
    tokens = text.split()
    cleaned = []
    for t in tokens:
        t = t.strip("'-_")
        if not t:
            continue
        if t.isdigit():
            continue
        if len(t) == 1 and t not in ('i', 'a'):
            continue
        t = stem_word(t)
        if t:
            cleaned.append(t)
    return cleaned


# ---------------------------------------------------------------------------
# Stage 1: Input Evaluation — Data Loader
# ---------------------------------------------------------------------------

class DataLoader:
    """Loads Signal Army run data from CSV files."""

    def __init__(self, run_dir):
        self.run_dir = run_dir

    def load_word_inventory(self):
        """Load word_inventory.csv into list of dicts."""
        path = os.path.join(self.run_dir, 'word_inventory.csv')
        return self._load_csv(path)

    def load_phrase_inventory(self):
        """Load phrase_inventory.csv into list of dicts."""
        path = os.path.join(self.run_dir, 'phrase_inventory.csv')
        return self._load_csv(path)

    def load_division_inventory(self):
        """Load division_inventory.csv into list of dicts."""
        path = os.path.join(self.run_dir, 'division_inventory.csv')
        return self._load_csv(path)

    def load_messages(self):
        """Load flattened_messages.csv into list of dicts."""
        path = os.path.join(self.run_dir, 'flattened_messages.csv')
        return self._load_csv(path)

    def _load_csv(self, path):
        """Generic CSV loader."""
        if not os.path.isfile(path):
            print(f"  WARNING: {os.path.basename(path)} not found", file=sys.stderr)
            return []
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            return list(reader)


# ---------------------------------------------------------------------------
# Stage 2: Contextual Assessment
# ---------------------------------------------------------------------------

class ContextualAssessor:
    """Evaluates each word's contextual signal contribution.

    Inputs from Signal Army:
    - Rank (structural position)
    - Thread spread (how many threads the word appears in)
    - Division membership (thematic coherence)

    Outputs:
    - contextual_score (0-1) for each word
    """

    def __init__(self, word_inventory, division_inventory):
        self.word_inventory = word_inventory
        self.division_inventory = division_inventory

        # Build lookups
        self.word_data = {}
        self.max_threads = 0
        self.max_count = 0
        for w in word_inventory:
            word = w['Word']
            threads = int(w.get('Threads_Appeared_In', 0))
            count = int(w.get('Count', 0))
            self.word_data[word] = {
                'rank': w.get('Rank', 'Scout'),
                'threads': threads,
                'count': count,
                'thread_names': w.get('Thread_Names', ''),
            }
            if threads > self.max_threads:
                self.max_threads = threads
            if count > self.max_count:
                self.max_count = count

        # Build division membership: word -> list of division names
        self.word_divisions = defaultdict(list)
        self.division_officers = defaultdict(set)
        for div in division_inventory:
            div_name = div.get('Division_Name', '')
            members = div.get('Members', '').split(';')
            commander = div.get('Commander', '')
            commander_rank = div.get('Commander_Rank', '')
            for member in members:
                member = member.strip()
                if member:
                    self.word_divisions[member].append(div_name)
            if commander_rank == 'Officer-Class':
                for member in members:
                    member = member.strip()
                    if member:
                        self.division_officers[member].add(commander)

    def score(self, word):
        """Compute contextual signal score for a word (0-1)."""
        data = self.word_data.get(word)
        if data is None:
            # Unknown word — not in Signal Army inventory
            if word in STOP_WORDS:
                return 0.0
            if word in INFANTRY_WORDS:
                return 0.05
            return 0.08  # unclassified non-stop word gets minimal score

        # Component 1: Thread spread (0-1)
        # Words that survive across many threads have higher signal potential
        thread_spread = data['threads'] / max(self.max_threads, 1)

        # Component 2: Division membership (0, 0.5, or 1.0)
        # Being in a division = thematic coherence = signal indicator
        divisions = self.word_divisions.get(word, [])
        if divisions:
            div_score = min(len(divisions) / 3.0, 1.0)  # cap at 3 divisions
        else:
            div_score = 0.0

        # Component 3: Officer proximity
        # Words that share a division with Officers have higher signal
        officers_connected = self.division_officers.get(word, set())
        officer_score = min(len(officers_connected) / 5.0, 1.0)

        # Weighted combination
        contextual = (
            0.35 * thread_spread +
            0.35 * div_score +
            0.30 * officer_score
        )

        return round(min(contextual, 1.0), 4)

    def score_all(self):
        """Score all words in the inventory. Returns dict: word -> score."""
        scores = {}
        for w in self.word_inventory:
            word = w['Word']
            scores[word] = self.score(word)
        return scores


# ---------------------------------------------------------------------------
# Stage 3: Structural Necessity Evaluation
# ---------------------------------------------------------------------------

class NecessityEvaluator:
    """Assesses compression necessity: would removal of this word
    degrade semantic coherence?

    Uses division-level dependency: how many other division members
    depend on this word's presence for their thematic cluster to hold.

    From the spec (SN_Filter_Infra.md, Component C-0005):
    - Layer 3: Signal Contribution Score — adds weight to system trajectory
    - Layer 4: Compression Anchor Rating — role in lowering entropy
    """

    def __init__(self, word_inventory, division_inventory):
        # Build word -> divisions mapping
        self.word_divisions = defaultdict(set)
        self.division_members = {}
        self.word_rank = {}
        self.word_count = {}

        for w in word_inventory:
            self.word_rank[w['Word']] = w.get('Rank', 'Scout')
            self.word_count[w['Word']] = int(w.get('Count', 0))

        for div in division_inventory:
            div_name = div.get('Division_Name', '')
            members = [m.strip() for m in div.get('Members', '').split(';') if m.strip()]
            self.division_members[div_name] = members
            for member in members:
                self.word_divisions[member].add(div_name)

        # Build co-membership graph: for each word, count unique division co-members
        self.co_members = defaultdict(set)
        for div_name, members in self.division_members.items():
            for m in members:
                for other in members:
                    if other != m:
                        self.co_members[m].add(other)

        # Count officer co-members specifically
        self.officer_connections = defaultdict(set)
        for word, co_words in self.co_members.items():
            for co in co_words:
                if self.word_rank.get(co) == 'Officer-Class':
                    self.officer_connections[word].add(co)

    def score(self, word):
        """Compute compression necessity score (0-1).

        High necessity = removing this word would break connections.
        Low necessity = word is structurally replaceable."""
        # Words not in any division have low structural necessity
        if word not in self.word_divisions:
            # But high-frequency non-division words still carry some weight
            count = self.word_count.get(word, 0)
            if count > 100:
                return 0.2
            return 0.05

        # Factor 1: How many division connections does this word have?
        co_count = len(self.co_members.get(word, set()))
        # Normalize: 15+ connections = max
        connection_score = min(co_count / 15.0, 1.0)

        # Factor 2: How many of those connections are Officers?
        officer_count = len(self.officer_connections.get(word, set()))
        # Normalize: 5+ officer connections = max
        officer_dep_score = min(officer_count / 5.0, 1.0)

        # Factor 3: How many divisions does this word appear in?
        div_count = len(self.word_divisions.get(word, set()))
        # Being in multiple divisions = cross-thematic importance
        cross_div_score = min(div_count / 3.0, 1.0)

        # Weighted combination
        necessity = (
            0.40 * connection_score +
            0.35 * officer_dep_score +
            0.25 * cross_div_score
        )

        return round(min(necessity, 1.0), 4)

    def score_all(self):
        """Score all words. Returns dict: word -> necessity_score."""
        scores = {}
        for w in self.word_rank:
            scores[w] = self.score(w)
        return scores


# ---------------------------------------------------------------------------
# Stage 5: Longitudinal Tracking — Signal Decay Rate
# ---------------------------------------------------------------------------

class DecayTracker:
    """Tracks signal persistence and decay across threads over time.

    For each word, measures whether its presence is:
    - RISING: appearing in more recent threads
    - STABLE: consistent presence across time
    - DECLINING: fading from recent threads
    - SPARSE: too few data points to determine

    Uses thread timestamps to establish temporal ordering.
    """

    def __init__(self, word_inventory, messages):
        # Build temporal ordering of threads
        self.thread_order = self._order_threads(messages)
        self.total_threads = len(self.thread_order)
        self.thread_index = {t: i for i, t in enumerate(self.thread_order)}

        # Build word -> thread presence
        self.word_threads = {}
        for w in word_inventory:
            word = w['Word']
            thread_names = w.get('Thread_Names', '')
            threads = set(t.strip() for t in thread_names.split(';') if t.strip())
            self.word_threads[word] = threads

    def _order_threads(self, messages):
        """Order threads by earliest message timestamp."""
        thread_first_ts = {}
        for msg in messages:
            title = msg.get('conversation_title', '')
            ts = msg.get('timestamp', '')
            if title and ts:
                if title not in thread_first_ts or ts < thread_first_ts[title]:
                    thread_first_ts[title] = ts
        # Sort by timestamp
        return [t for t, _ in sorted(thread_first_ts.items(), key=lambda x: x[1])]

    def compute_decay(self, word):
        """Compute decay rate and trajectory for a word.

        Returns: (decay_score, trajectory)
        - decay_score: -1 (declining) to +1 (rising), 0 = stable
        - trajectory: 'RISING', 'STABLE', 'DECLINING', or 'SPARSE'
        """
        threads = self.word_threads.get(word, set())
        if not threads or self.total_threads < 3:
            return 0.0, 'SPARSE'

        # Get temporal positions of word's threads
        positions = sorted(self.thread_index[t] for t in threads if t in self.thread_index)
        if len(positions) < 2:
            return 0.0, 'SPARSE'

        # Split timeline in half
        midpoint = self.total_threads / 2.0
        early_count = sum(1 for p in positions if p < midpoint)
        late_count = sum(1 for p in positions if p >= midpoint)
        total = len(positions)

        # Compute directional bias
        early_ratio = early_count / total
        late_ratio = late_count / total

        # Decay score: positive = rising, negative = declining
        decay_score = late_ratio - early_ratio

        # Classify trajectory
        if abs(decay_score) < 0.15:
            trajectory = 'STABLE'
        elif decay_score > 0:
            trajectory = 'RISING'
        else:
            trajectory = 'DECLINING'

        # Also check coverage: words present across most threads are stable
        coverage = total / max(self.total_threads, 1)
        if coverage > 0.7 and abs(decay_score) < 0.3:
            trajectory = 'STABLE'
            decay_score *= 0.5  # dampen score for high-coverage words

        return round(decay_score, 4), trajectory

    def compute_all(self):
        """Compute decay for all words.
        Returns dict: word -> (decay_score, trajectory)."""
        results = {}
        for word in self.word_threads:
            results[word] = self.compute_decay(word)
        return results


# ---------------------------------------------------------------------------
# Stage 4: Classification — Signal/Noise Dual-Weight
# ---------------------------------------------------------------------------

class SignalClassifier:
    """Produces dual-weight classification for every word.

    From the user's core spec:
    "Words have signal and noise which are both weight — it's a density."

    Combines:
    - Rank base score (from Signal Army structural analysis)
    - Contextual score (Stage 2)
    - Necessity score (Stage 3)
    - Decay modifier (Stage 5)

    Outputs: signal_weight, noise_weight, classification
    """

    def __init__(self, word_inventory, contextual_scores, necessity_scores, decay_results):
        self.word_inventory = word_inventory
        self.contextual = contextual_scores
        self.necessity = necessity_scores
        self.decay = decay_results

    def classify(self, word, rank=None):
        """Classify a single word. Returns (signal_weight, noise_weight, classification)."""
        # Rank base
        if rank is None:
            rank = 'Scout'
        rank_base = RANK_SIGNAL_BASE.get(rank, 0.10)

        # Contextual score
        ctx = self.contextual.get(word, 0.08)

        # Necessity score
        nec = self.necessity.get(word, 0.05)

        # Decay modifier
        decay_score, trajectory = self.decay.get(word, (0.0, 'SPARSE'))
        # Convert decay to a bonus/penalty: rising words get a boost, declining get a penalty
        decay_modifier = decay_score * 0.5  # scale the effect

        # Composite signal weight
        signal_weight = (
            W_RANK * rank_base +
            W_CONTEXT * ctx +
            W_NECESSITY * nec +
            W_DECAY * max(decay_modifier, 0)  # only positive decay helps signal
        )

        # Noise weight is not simply 1-signal — it's independently computed
        # Words can carry BOTH signal and noise (this is the dual-weight density insight)
        noise_base = 1.0 - rank_base
        noise_context = 1.0 - ctx
        noise_decay_penalty = abs(min(decay_modifier, 0))  # declining words increase noise

        noise_weight = (
            W_RANK * noise_base +
            W_CONTEXT * noise_context +
            W_NECESSITY * (1.0 - nec) +
            W_DECAY * noise_decay_penalty
        )

        # Normalize so signal + noise = 1.0 (density interpretation)
        total = signal_weight + noise_weight
        if total > 0:
            signal_weight = signal_weight / total
            noise_weight = noise_weight / total
        else:
            signal_weight = 0.5
            noise_weight = 0.5

        # Classification
        if signal_weight >= SIGNAL_THRESHOLD:
            classification = 'SIGNAL'
        else:
            classification = 'NOISE'

        return (round(signal_weight, 4), round(noise_weight, 4), classification)

    def classify_all(self):
        """Classify all words in inventory.
        Returns dict: word -> (signal_weight, noise_weight, classification, rank)."""
        results = {}
        for w in self.word_inventory:
            word = w['Word']
            rank = w.get('Rank', 'Scout')
            sw, nw, cls = self.classify(word, rank)
            results[word] = {
                'signal_weight': sw,
                'noise_weight': nw,
                'classification': cls,
                'rank': rank,
                'contextual_score': self.contextual.get(word, 0.0),
                'necessity_score': self.necessity.get(word, 0.0),
                'decay_score': self.decay.get(word, (0.0, 'SPARSE'))[0],
                'trajectory': self.decay.get(word, (0.0, 'SPARSE'))[1],
            }
        return results


# ---------------------------------------------------------------------------
# SNR Engine
# ---------------------------------------------------------------------------

class SNREngine:
    """Computes Signal-to-Noise Ratio at message, thread, and session levels.

    From the SCS Root Equation:
        SCS_r = (Signal_Words / max(Noise_Words, 1)) × Weight(t) – Drift(n)

    From the MOS²ES normalized form:
        SNR = Signal / (Signal + Noise)  — bounded 0-1

    Both forms are computed. The normalized form is primary.
    """

    def __init__(self, classifications, messages):
        self.classifications = classifications  # word -> {...}
        self.messages = messages

    def _classify_token(self, token):
        """Classify a single token for SNR computation."""
        if token in STOP_WORDS:
            return 'NOISE', 0.0, 1.0
        if token in INFANTRY_WORDS:
            sw = 0.05
            nw = 0.95
            return 'NOISE', sw, nw

        data = self.classifications.get(token)
        if data:
            return data['classification'], data['signal_weight'], data['noise_weight']

        # Unknown word — not in Signal Army inventory, not stop/infantry
        return 'NOISE', 0.08, 0.92

    def analyze_message(self, message_text):
        """Compute SNR for a single message.
        Returns dict with SNR metrics."""
        tokens = tokenize(message_text)
        if not tokens:
            return {
                'total_words': 0,
                'signal_count': 0,
                'noise_count': 0,
                'stop_count': 0,
                'snr_normalized': 0.0,
                'snr_ratio': 0.0,
                'snr_db': 0.0,
                'signal_density': 0.0,
            }

        signal_count = 0
        noise_count = 0
        stop_count = 0
        signal_mass = 0.0
        noise_mass = 0.0

        for token in tokens:
            if token in STOP_WORDS:
                stop_count += 1
                noise_mass += 1.0
                noise_count += 1
                continue

            cls, sw, nw = self._classify_token(token)
            signal_mass += sw
            noise_mass += nw
            if cls == 'SIGNAL':
                signal_count += 1
            else:
                noise_count += 1

        total = len(tokens)
        total_non_stop = total - stop_count

        # MOS²ES normalized SNR (0-1)
        snr_normalized = signal_mass / (signal_mass + noise_mass) if (signal_mass + noise_mass) > 0 else 0.0

        # SCS ratio form
        snr_ratio = signal_count / max(noise_count, 1)

        # dB form
        if snr_ratio > 0:
            snr_db = 10 * math.log10(snr_ratio)
        else:
            snr_db = -99.0

        # Signal density: signal words / non-stop words
        signal_density = signal_count / max(total_non_stop, 1)

        return {
            'total_words': total,
            'signal_count': signal_count,
            'noise_count': noise_count,
            'stop_count': stop_count,
            'snr_normalized': round(snr_normalized, 4),
            'snr_ratio': round(snr_ratio, 4),
            'snr_db': round(snr_db, 2),
            'signal_density': round(signal_density, 4),
        }

    def analyze_by_thread(self):
        """Compute SNR per thread. Returns dict: thread_name -> metrics."""
        thread_metrics = defaultdict(lambda: {
            'total_words': 0, 'signal_count': 0, 'noise_count': 0,
            'stop_count': 0, 'signal_mass': 0.0, 'noise_mass': 0.0,
            'message_count': 0,
        })

        for msg in self.messages:
            title = msg.get('conversation_title', 'Unknown')
            text = msg.get('message_text', '')
            tokens = tokenize(text)
            tm = thread_metrics[title]
            tm['message_count'] += 1

            for token in tokens:
                if token in STOP_WORDS:
                    tm['stop_count'] += 1
                    tm['noise_count'] += 1
                    tm['noise_mass'] += 1.0
                    tm['total_words'] += 1
                    continue

                cls, sw, nw = self._classify_token(token)
                tm['signal_mass'] += sw
                tm['noise_mass'] += nw
                tm['total_words'] += 1
                if cls == 'SIGNAL':
                    tm['signal_count'] += 1
                else:
                    tm['noise_count'] += 1

        # Compute final metrics per thread
        results = {}
        for title, tm in thread_metrics.items():
            sm = tm['signal_mass']
            nm = tm['noise_mass']
            snr_norm = sm / (sm + nm) if (sm + nm) > 0 else 0.0
            snr_ratio = tm['signal_count'] / max(tm['noise_count'], 1)
            snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
            total_non_stop = tm['total_words'] - tm['stop_count']

            results[title] = {
                'message_count': tm['message_count'],
                'total_words': tm['total_words'],
                'signal_count': tm['signal_count'],
                'noise_count': tm['noise_count'],
                'stop_count': tm['stop_count'],
                'snr_normalized': round(snr_norm, 4),
                'snr_ratio': round(snr_ratio, 4),
                'snr_db': round(snr_db, 2),
                'signal_density': round(tm['signal_count'] / max(total_non_stop, 1), 4),
            }

        return results

    def analyze_session(self, thread_metrics):
        """Compute session-level aggregate SNR."""
        total_words = sum(t['total_words'] for t in thread_metrics.values())
        total_signal = sum(t['signal_count'] for t in thread_metrics.values())
        total_noise = sum(t['noise_count'] for t in thread_metrics.values())
        total_stop = sum(t['stop_count'] for t in thread_metrics.values())
        total_messages = sum(t['message_count'] for t in thread_metrics.values())

        snr_ratio = total_signal / max(total_noise, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        total_non_stop = total_words - total_stop
        snr_normalized = total_signal / max(total_signal + total_noise, 1)

        return {
            'total_threads': len(thread_metrics),
            'total_messages': total_messages,
            'total_words': total_words,
            'total_signal': total_signal,
            'total_noise': total_noise,
            'total_stop': total_stop,
            'snr_normalized': round(snr_normalized, 4),
            'snr_ratio': round(snr_ratio, 4),
            'snr_db': round(snr_db, 2),
            'signal_density': round(total_signal / max(total_non_stop, 1), 4),
        }


# ---------------------------------------------------------------------------
# PPA Metrics Engine — Equations from SCSEngine PPA + CIVITAS PPA3
# ---------------------------------------------------------------------------

class PPAMetrics:
    """Computes metrics defined in the MOS2ES patent filings.

    From SCSEngine PPA:
        ResonanceScore = (SNR_w * SNR) + (Drift_w * (1 - DriftDelta)) + (Density_w * SignalDensity)
        ScarIndex(t) = Var(signal_weights) / Baseline
        S2S = N_survived / N_attempted
        Ghost Token: high necessity, low resonance (quarantine candidates)
        Keter threshold: resonance >= 0.94

    From CIVITAS PPA3 (Survivability-Based Truth Compression):
        TCR — Token Compression Ratio (signal tokens / total tokens)
        RTD — Recursive Thematic Density (signal density within divisions)
    """

    # Resonance score weights (system-tunable per SCSEngine [0259])
    W_SNR = 0.40
    W_DRIFT = 0.30
    W_DENSITY = 0.30

    # Scar Index thresholds (SCSEngine Addendum F [0269])
    SCAR_HEALTHY = 0.20
    SCAR_WARNING = 0.50
    SCAR_CRITICAL = 0.90

    # Keter threshold (SCSEngine [0097], [0271])
    KETER_THRESHOLD = 0.94

    # Ghost Token threshold (SCSEngine [0060])
    GHOST_RESONANCE_MAX = 0.25
    GHOST_NECESSITY_MIN = 0.30

    def __init__(self, classifications, thread_snr, session_snr, division_data=None):
        self.classifications = classifications
        self.thread_snr = thread_snr
        self.session_snr = session_snr
        self.divisions = division_data or []

    def resonance_score(self, snr, drift_delta, signal_density):
        """Per SCSEngine [0259]:
        ResonanceScore = (SNR_w * SNR) + (Drift_w * (1 - DriftDelta)) + (Density_w * Density)
        Range: 0.0-1.0. Threshold >= 0.94 = Keter event."""
        return (
            self.W_SNR * snr +
            self.W_DRIFT * (1.0 - abs(drift_delta)) +
            self.W_DENSITY * signal_density
        )

    def thread_resonance_scores(self):
        """Compute resonance score for each thread."""
        results = {}
        for thread, metrics in self.thread_snr.items():
            snr = metrics['snr_normalized']
            density = metrics['signal_density']
            # Drift delta: how far this thread's SNR deviates from session average
            session_snr = self.session_snr['snr_normalized']
            drift = (snr - session_snr) / max(session_snr, 0.001)
            res = self.resonance_score(snr, drift, density)
            results[thread] = {
                'resonance': round(res, 4),
                'snr': round(snr, 4),
                'drift_delta': round(drift, 4),
                'density': round(density, 4),
                'keter': res >= self.KETER_THRESHOLD,
            }
        return results

    def scar_index(self):
        """Per SCSEngine [0240], Addendum L:
        ScarIndex = Var(signal_weights) / Baseline
        Measures semantic drift / conceptual corruption across the corpus.
        0.0-0.20 = healthy, 0.20-0.50 = warning, >= 0.50 = critical."""
        signal_weights = [d['signal_weight'] for d in self.classifications.values()]
        if not signal_weights:
            return 0.0
        mean_sw = sum(signal_weights) / len(signal_weights)
        variance = sum((sw - mean_sw) ** 2 for sw in signal_weights) / len(signal_weights)
        baseline = max(mean_sw, 0.001)
        si = variance / baseline
        return round(min(si, 1.0), 4)

    def scar_status(self, si):
        """Classify scar index into operational bands."""
        if si <= self.SCAR_HEALTHY:
            return 'HEALTHY'
        elif si <= self.SCAR_WARNING:
            return 'WARNING'
        elif si < self.SCAR_CRITICAL:
            return 'CRITICAL'
        else:
            return 'COLLAPSE'

    def s2s_ratio(self):
        """Per SCSEngine [0241]:
        S2S = N_survived / N_attempted
        Where N_survived = signal words appearing in 2+ threads (survived recursion).
        N_attempted = total unique words classified."""
        survived = sum(1 for d in self.classifications.values()
                       if d['classification'] == 'SIGNAL'
                       and d['trajectory'] in ('RISING', 'STABLE'))
        attempted = len(self.classifications)
        if attempted == 0:
            return 0.0
        return round(survived / attempted, 4)

    def s2s_tier(self, s2s):
        """S2S valuation tiers (SCSEngine Addendum F [0270])."""
        if s2s >= 0.90:
            return 'HIGH-VALUE (Keter-critical)'
        elif s2s >= 0.71:
            return 'MID-VALUE (IP-grade)'
        elif s2s >= 0.50:
            return 'LOW-VALUE (transactional)'
        else:
            return 'SUB-THRESHOLD'

    def tcr(self):
        """Token Compression Ratio (CIVITAS PPA3, Add-on IV):
        TCR = signal_tokens / total_tokens"""
        ss = self.session_snr
        total = ss.get('total_words', 0)
        signal = ss.get('total_signal', 0)
        if total == 0:
            return 0.0
        return round(signal / total, 4)

    def scd(self):
        """Semantic Compression Delta (CIVITAS PPA3, Add-on IV):
        SCD = signal_density_post_compression - signal_density_pre_compression
        Measures how much density improves after removing stop/infantry."""
        ss = self.session_snr
        pre = ss.get('signal_density', 0)
        removable = ss.get('total_stop', 0)
        total = ss.get('total_words', 0)
        signal = ss.get('total_signal', 0)
        post = signal / max(total - removable, 1)
        return round(post - pre, 4)

    def rtd(self):
        """Recursive Thematic Density (CIVITAS PPA3, Add-on IV):
        RTD = signal words in divisions / total words in divisions
        Measures signal concentration within thematic clusters."""
        if not self.divisions:
            return 0.0
        division_words = set()
        for div in self.divisions:
            members = div.get('Members', '').split(', ')
            division_words.update(m.strip() for m in members if m.strip())
            commander = div.get('Commander', '')
            if commander:
                division_words.add(commander)
        if not division_words:
            return 0.0
        signal_in_div = sum(1 for w in division_words
                           if w in self.classifications
                           and self.classifications[w]['classification'] == 'SIGNAL')
        return round(signal_in_div / len(division_words), 4)

    def ghost_tokens(self):
        """Per SCSEngine [0060], [0095]:
        Ghost Tokens = high necessity, low resonance words.
        'High-intent, low-coherence residues quarantined for reprocessing.'"""
        ghosts = []
        for word, data in self.classifications.items():
            nec = data.get('necessity_score', 0)
            sw = data.get('signal_weight', 0)
            if nec >= self.GHOST_NECESSITY_MIN and sw <= self.GHOST_RESONANCE_MAX:
                ghosts.append((word, data))
        ghosts.sort(key=lambda x: -x[1]['necessity_score'])
        return ghosts

    def compute_all(self):
        """Compute all PPA metrics and return as a dict."""
        si = self.scar_index()
        s2s = self.s2s_ratio()
        thread_res = self.thread_resonance_scores()
        ghosts = self.ghost_tokens()

        # Session-level resonance (average of thread resonances)
        if thread_res:
            session_resonance = sum(r['resonance'] for r in thread_res.values()) / len(thread_res)
        else:
            session_resonance = 0.0

        keter_threads = [(t, r) for t, r in thread_res.items() if r['keter']]

        return {
            'resonance_scores': thread_res,
            'session_resonance': round(session_resonance, 4),
            'scar_index': si,
            'scar_status': self.scar_status(si),
            's2s_ratio': s2s,
            's2s_tier': self.s2s_tier(s2s),
            'tcr': self.tcr(),
            'scd': self.scd(),
            'rtd': self.rtd(),
            'ghost_tokens': ghosts,
            'keter_threads': keter_threads,
        }


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generates SIGSYSTEM output files."""

    def __init__(self, output_dir, classifications, thread_snr,
                 session_snr, word_inventory, decay_results, ppa_metrics=None):
        self.output_dir = output_dir
        self.classifications = classifications
        self.thread_snr = thread_snr
        self.session_snr = session_snr
        self.word_inventory = word_inventory
        self.decay = decay_results
        self.ppa = ppa_metrics or {}

    def save_word_scores(self):
        """Write sigsystem_word_scores.csv — per-word classification + metrics."""
        path = os.path.join(self.output_dir, 'sigsystem_word_scores.csv')
        fieldnames = [
            'Word', 'Count', 'Rank', 'Signal_Weight', 'Noise_Weight',
            'Classification', 'Contextual_Score', 'Necessity_Score',
            'Decay_Score', 'Trajectory'
        ]

        # Merge word inventory data with classification data
        rows = []
        for w in self.word_inventory:
            word = w['Word']
            cls_data = self.classifications.get(word, {})
            rows.append({
                'Word': word,
                'Count': w.get('Count', 0),
                'Rank': w.get('Rank', ''),
                'Signal_Weight': cls_data.get('signal_weight', 0),
                'Noise_Weight': cls_data.get('noise_weight', 0),
                'Classification': cls_data.get('classification', 'NOISE'),
                'Contextual_Score': cls_data.get('contextual_score', 0),
                'Necessity_Score': cls_data.get('necessity_score', 0),
                'Decay_Score': cls_data.get('decay_score', 0),
                'Trajectory': cls_data.get('trajectory', 'SPARSE'),
            })

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  sigsystem_word_scores.csv    -- {len(rows)} words scored")
        return path

    def save_thread_snr(self):
        """Write sigsystem_thread_snr.csv — per-thread SNR breakdown."""
        path = os.path.join(self.output_dir, 'sigsystem_thread_snr.csv')
        fieldnames = [
            'Thread', 'Messages', 'Total_Words', 'Signal_Count', 'Noise_Count',
            'Stop_Count', 'SNR_Normalized', 'SNR_Ratio', 'SNR_dB', 'Signal_Density'
        ]

        rows = []
        for thread, metrics in sorted(self.thread_snr.items(),
                                       key=lambda x: -x[1]['snr_normalized']):
            rows.append({
                'Thread': thread,
                'Messages': metrics['message_count'],
                'Total_Words': metrics['total_words'],
                'Signal_Count': metrics['signal_count'],
                'Noise_Count': metrics['noise_count'],
                'Stop_Count': metrics['stop_count'],
                'SNR_Normalized': metrics['snr_normalized'],
                'SNR_Ratio': metrics['snr_ratio'],
                'SNR_dB': metrics['snr_db'],
                'Signal_Density': metrics['signal_density'],
            })

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  sigsystem_thread_snr.csv     -- {len(rows)} threads analyzed")
        return path

    def save_summary(self):
        """Generate and write sigsystem_summary.txt dashboard."""
        ss = self.session_snr
        cls = self.classifications

        # Separate signal and noise words
        signal_words = [(w, d) for w, d in cls.items() if d['classification'] == 'SIGNAL']
        noise_words = [(w, d) for w, d in cls.items() if d['classification'] == 'NOISE']
        signal_words.sort(key=lambda x: -x[1]['signal_weight'])
        noise_words.sort(key=lambda x: -x[1]['noise_weight'])

        # Trajectory counts
        trajectories = Counter(d['trajectory'] for d in cls.values())

        # Thread rankings
        thread_ranked = sorted(self.thread_snr.items(),
                               key=lambda x: -x[1]['snr_normalized'])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = []
        lines.append('=' * 64)
        lines.append('  SIGSYSTEM -- SIGNAL CLASSIFICATION & MEASUREMENT')
        lines.append('  "Every word is unresolved until the system')
        lines.append('   collapses it."')
        lines.append('=' * 64)
        lines.append(f'  Generated:  {now}')
        lines.append(f'  Engine:     sigsystem.py v{VERSION}')
        lines.append('')

        # Session-level SNR
        lines.append('=' * 64)
        lines.append('  SESSION SNR')
        lines.append('=' * 64)
        lines.append(f'  Total Threads:             {ss["total_threads"]:,}')
        lines.append(f'  Total Messages:            {ss["total_messages"]:,}')
        lines.append(f'  Total Words Processed:     {ss["total_words"]:,}')
        lines.append(f'  Signal Words:              {ss["total_signal"]:,}')
        lines.append(f'  Noise Words:               {ss["total_noise"]:,}')
        lines.append(f'  Stop Words:                {ss["total_stop"]:,}')
        lines.append('')
        lines.append(f'  SNR (Normalized 0-1):      {ss["snr_normalized"]:.4f}')
        lines.append(f'  SNR (Ratio S/N):           {ss["snr_ratio"]:.4f}')
        lines.append(f'  SNR (dB):                  {ss["snr_db"]:.2f} dB')
        lines.append(f'  Signal Density:            {ss["signal_density"]:.4f}')
        lines.append('')

        # Classification summary
        lines.append('=' * 64)
        lines.append('  CLASSIFICATION SUMMARY')
        lines.append('=' * 64)
        total_classified = len(cls)
        lines.append(f'  Total Words Classified:    {total_classified:,}')
        lines.append(f'  Classified as SIGNAL:      {len(signal_words):,}  '
                     f'({len(signal_words)/max(total_classified,1)*100:.1f}%)')
        lines.append(f'  Classified as NOISE:       {len(noise_words):,}  '
                     f'({len(noise_words)/max(total_classified,1)*100:.1f}%)')
        lines.append('')
        lines.append('  Signal Trajectories:')
        for traj in ['RISING', 'STABLE', 'DECLINING', 'SPARSE']:
            count = trajectories.get(traj, 0)
            lines.append(f'    {traj:<12s}  {count:>6,} words')
        lines.append('')

        # Top signal words
        lines.append('=' * 64)
        lines.append('  TOP 20 SIGNAL WORDS (highest signal weight)')
        lines.append('=' * 64)
        for i, (word, data) in enumerate(signal_words[:20], 1):
            lines.append(
                f'  {i:>2}. {word:<22s}  '
                f'SW:{data["signal_weight"]:.3f}  '
                f'NW:{data["noise_weight"]:.3f}  '
                f'CTX:{data["contextual_score"]:.3f}  '
                f'NEC:{data["necessity_score"]:.3f}  '
                f'{data["trajectory"]}'
            )
        lines.append('')

        # Top noise words (non-infantry, non-stop — the interesting ones)
        interesting_noise = [(w, d) for w, d in noise_words
                            if d['rank'] not in ('Infantry',) and w not in STOP_WORDS]
        if interesting_noise:
            lines.append('=' * 64)
            lines.append('  TOP 15 NOISE WORDS (highest noise weight, non-infantry)')
            lines.append('=' * 64)
            for i, (word, data) in enumerate(interesting_noise[:15], 1):
                lines.append(
                    f'  {i:>2}. {word:<22s}  '
                    f'SW:{data["signal_weight"]:.3f}  '
                    f'NW:{data["noise_weight"]:.3f}  '
                    f'Rank:{data["rank"]}'
                )
            lines.append('')

        # Thread SNR leaderboard
        lines.append('=' * 64)
        lines.append('  THREAD SNR LEADERBOARD (by normalized SNR)')
        lines.append('=' * 64)
        for i, (thread, metrics) in enumerate(thread_ranked[:20], 1):
            lines.append(
                f'  {i:>2}. {thread:<35s}  '
                f'SNR:{metrics["snr_normalized"]:.4f}  '
                f'dB:{metrics["snr_db"]:>6.2f}  '
                f'Words:{metrics["total_words"]:>5,}'
            )
        lines.append('')

        # Bottom threads (highest noise)
        if len(thread_ranked) > 5:
            lines.append('=' * 64)
            lines.append('  BOTTOM 5 THREADS (lowest SNR — highest noise)')
            lines.append('=' * 64)
            for i, (thread, metrics) in enumerate(reversed(thread_ranked[-5:]), 1):
                lines.append(
                    f'  {i:>2}. {thread:<35s}  '
                    f'SNR:{metrics["snr_normalized"]:.4f}  '
                    f'dB:{metrics["snr_db"]:>6.2f}  '
                    f'Words:{metrics["total_words"]:>5,}'
                )
            lines.append('')

        # Compression opportunity
        lines.append('=' * 64)
        lines.append('  COMPRESSION ANALYSIS')
        lines.append('=' * 64)
        removable = ss['total_stop'] + sum(1 for _, d in noise_words
                                           if d['rank'] == 'Infantry')
        lines.append(f'  Stop words (pure scaffolding):  {ss["total_stop"]:,}')
        lines.append(f'  Est. removable words:           {removable:,}')
        lines.append(f'  Compression potential:          '
                     f'{removable/max(ss["total_words"],1)*100:.1f}% reducible')
        lines.append(f'  Post-compression signal density: '
                     f'{ss["total_signal"]/max(ss["total_words"]-removable,1):.4f}')
        lines.append('')

        # PPA Metrics (SCSEngine + CIVITAS equations)
        if self.ppa:
            lines.append('=' * 64)
            lines.append('  SCS ENGINE METRICS (from PPA equations)')
            lines.append('=' * 64)

            lines.append(f'  Session Resonance Score:    {self.ppa.get("session_resonance", 0):.4f}')
            lines.append(f'  Scar Index:                 {self.ppa.get("scar_index", 0):.4f}  '
                         f'[{self.ppa.get("scar_status", "?")}]')
            lines.append(f'  S²S Ratio:                  {self.ppa.get("s2s_ratio", 0):.4f}  '
                         f'[{self.ppa.get("s2s_tier", "?")}]')
            lines.append(f'  Token Compression Ratio:    {self.ppa.get("tcr", 0):.4f}')
            lines.append(f'  Semantic Compression Delta: {self.ppa.get("scd", 0):.4f}')
            lines.append(f'  Recursive Thematic Density: {self.ppa.get("rtd", 0):.4f}')
            lines.append('')

            # Scar Index interpretation
            si = self.ppa.get('scar_index', 0)
            lines.append('  Scar Index Ranges:')
            lines.append(f'    0.00-0.20  HEALTHY    {"<-- HERE" if si <= 0.20 else ""}')
            lines.append(f'    0.20-0.50  WARNING    {"<-- HERE" if 0.20 < si <= 0.50 else ""}')
            lines.append(f'    0.50-0.90  CRITICAL   {"<-- HERE" if 0.50 < si < 0.90 else ""}')
            lines.append(f'    0.90-1.00  COLLAPSE   {"<-- HERE" if si >= 0.90 else ""}')
            lines.append('')

            # Keter threads
            keter = self.ppa.get('keter_threads', [])
            if keter:
                lines.append(f'  KETER-LEVEL THREADS (resonance >= 0.94):')
                for thread, res in keter:
                    lines.append(f'    {thread:<35s}  RES:{res["resonance"]:.4f}')
                lines.append('')

            # Top resonance threads
            thread_res = self.ppa.get('resonance_scores', {})
            if thread_res:
                lines.append('  THREAD RESONANCE SCORES (top 10):')
                sorted_res = sorted(thread_res.items(), key=lambda x: -x[1]['resonance'])
                for thread, res in sorted_res[:10]:
                    keter_flag = ' [KETER]' if res['keter'] else ''
                    lines.append(
                        f'    {thread:<35s}  '
                        f'RES:{res["resonance"]:.4f}  '
                        f'DRIFT:{res["drift_delta"]:+.4f}{keter_flag}'
                    )
                lines.append('')

            # Ghost tokens
            ghosts = self.ppa.get('ghost_tokens', [])
            if ghosts:
                lines.append(f'  GHOST TOKENS ({len(ghosts)} detected):')
                lines.append('  "High-intent, low-coherence residues quarantined')
                lines.append('   for reprocessing."  -- SCSEngine [0095]')
                for word, data in ghosts[:15]:
                    lines.append(
                        f'    {word:<22s}  '
                        f'NEC:{data["necessity_score"]:.3f}  '
                        f'SW:{data["signal_weight"]:.3f}  '
                        f'Rank:{data["rank"]}'
                    )
                lines.append('')

        lines.append('=' * 64)
        lines.append('  "Words are not inherently signal or noise.')
        lines.append('   Their classification emerges only in-context')
        lines.append('   during live system use."')
        lines.append('                     -- SIGSYSTEM Foundation Spec')
        lines.append('=' * 64)

        report = '\n'.join(lines)
        path = os.path.join(self.output_dir, 'sigsystem_summary.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"  sigsystem_summary.txt        -- dashboard generated")
        return path

    def save_all(self):
        """Generate all output files."""
        paths = []
        paths.append(self.save_word_scores())
        paths.append(self.save_thread_snr())
        paths.append(self.save_summary())
        return paths


# ---------------------------------------------------------------------------
# CLI & Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='SIGSYSTEM — Signal Classification & Measurement Subsystem\n'
                    '"Every word is unresolved until the system collapses it."',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  python sigsystem.py --run-dir ../signal_army/runs/run_2026-03-02_06-03-50/\n'
               '  python sigsystem.py --run-dir <dir> --output-dir ./runs/\n'
    )
    parser.add_argument('--run-dir', metavar='DIR', required=True,
                        help='Path to Signal Army run directory (must contain CSVs)')
    parser.add_argument('--output-dir', metavar='DIR',
                        help='Output directory (default: ./runs/ with timestamp)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed progress')

    args = parser.parse_args()

    if not os.path.isdir(args.run_dir):
        parser.error(f'Run directory not found: {args.run_dir}')

    # Output directory
    run_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    if args.output_dir:
        base_dir = args.output_dir
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runs')
    output_dir = os.path.join(base_dir, f'run_{run_stamp}')
    os.makedirs(output_dir, exist_ok=True)

    # Header
    print(f'\nSIGSYSTEM — Signal Classification & Measurement v{VERSION}')
    print('=' * 56)
    print()

    # ---- Stage 1: Input Evaluation ----
    print('[1/5] Loading Signal Army data...')
    loader = DataLoader(args.run_dir)
    word_inventory = loader.load_word_inventory()
    phrase_inventory = loader.load_phrase_inventory()
    division_inventory = loader.load_division_inventory()
    messages = loader.load_messages()

    if not word_inventory:
        print('ERROR: No word inventory found. Cannot proceed.', file=sys.stderr)
        sys.exit(1)

    print(f'      {len(word_inventory):,} words loaded')
    print(f'      {len(division_inventory)} divisions loaded')
    print(f'      {len(messages):,} messages loaded')
    print()

    # ---- Stage 2: Contextual Assessment ----
    print('[2/5] Running contextual assessment...')
    assessor = ContextualAssessor(word_inventory, division_inventory)
    contextual_scores = assessor.score_all()
    avg_ctx = sum(contextual_scores.values()) / max(len(contextual_scores), 1)
    print(f'      Avg contextual score: {avg_ctx:.4f}')
    print()

    # ---- Stage 3: Structural Necessity Evaluation ----
    print('[3/5] Evaluating compression necessity...')
    evaluator = NecessityEvaluator(word_inventory, division_inventory)
    necessity_scores = evaluator.score_all()
    avg_nec = sum(necessity_scores.values()) / max(len(necessity_scores), 1)
    print(f'      Avg necessity score: {avg_nec:.4f}')
    print()

    # ---- Stage 5 (before 4): Longitudinal Tracking ----
    print('[4/5] Computing signal decay rates...')
    tracker = DecayTracker(word_inventory, messages)
    decay_results = tracker.compute_all()
    trajectories = Counter(t for _, t in decay_results.values())
    for traj in ['RISING', 'STABLE', 'DECLINING', 'SPARSE']:
        print(f'      {traj:<12s} {trajectories.get(traj, 0):>5,} words')
    print()

    # ---- Stage 4: Classification ----
    print('[5/5] Classifying signal vs noise...')
    classifier = SignalClassifier(word_inventory, contextual_scores,
                                  necessity_scores, decay_results)
    classifications = classifier.classify_all()

    signal_count = sum(1 for d in classifications.values() if d['classification'] == 'SIGNAL')
    noise_count = sum(1 for d in classifications.values() if d['classification'] == 'NOISE')
    print(f'      SIGNAL: {signal_count:,} words')
    print(f'      NOISE:  {noise_count:,} words')
    print()

    # ---- SNR Engine ----
    print('Computing SNR metrics...')
    engine = SNREngine(classifications, messages)
    thread_snr = engine.analyze_by_thread()
    session_snr = engine.analyze_session(thread_snr)

    print(f'      Session SNR (normalized): {session_snr["snr_normalized"]:.4f}')
    print(f'      Session SNR (dB):         {session_snr["snr_db"]:.2f} dB')
    print(f'      Signal density:           {session_snr["signal_density"]:.4f}')
    print()

    # ---- PPA Metrics Engine ----
    print('Computing PPA metrics (SCSEngine + CIVITAS equations)...')
    ppa_engine = PPAMetrics(classifications, thread_snr, session_snr, division_inventory)
    ppa_metrics = ppa_engine.compute_all()

    print(f'      Resonance Score:     {ppa_metrics["session_resonance"]:.4f}')
    print(f'      Scar Index:          {ppa_metrics["scar_index"]:.4f} [{ppa_metrics["scar_status"]}]')
    print(f'      S²S Ratio:           {ppa_metrics["s2s_ratio"]:.4f} [{ppa_metrics["s2s_tier"]}]')
    print(f'      Ghost Tokens:        {len(ppa_metrics["ghost_tokens"])}')
    keter_count = len(ppa_metrics['keter_threads'])
    if keter_count:
        print(f'      Keter Threads:       {keter_count}')
    print()

    # ---- Generate Reports ----
    print('Generating reports...')
    reporter = ReportGenerator(output_dir, classifications, thread_snr,
                               session_snr, word_inventory, decay_results,
                               ppa_metrics=ppa_metrics)
    reporter.save_all()
    print()

    # Quick stats footer
    print('=' * 56)
    print('SIGSYSTEM RESULTS:')
    print(f'  Words classified:    {len(classifications):,}')
    print(f'  Signal words:        {signal_count:,}')
    print(f'  Noise words:         {noise_count:,}')
    print(f'  Session SNR:         {session_snr["snr_normalized"]:.4f} '
          f'({session_snr["snr_db"]:.2f} dB)')
    print(f'  Resonance:           {ppa_metrics["session_resonance"]:.4f}')
    print(f'  Scar Index:          {ppa_metrics["scar_index"]:.4f} [{ppa_metrics["scar_status"]}]')
    print(f'  S²S Ratio:           {ppa_metrics["s2s_ratio"]:.4f}')
    print(f'  Threads analyzed:    {len(thread_snr)}')
    print('=' * 56)
    print(f'\nAll files written to: {output_dir}/')
    print()


if __name__ == '__main__':
    main()
