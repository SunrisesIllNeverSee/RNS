#!/usr/bin/env python3
"""
SigToken Recursive Scorer — Thread-Aware Two-Pass Classification
Component C-0005 | v2.1 | Ello Cello LLC

The flat scorer (v1, v2) treats all messages as one undifferentiated blob.
This scorer uses the thread structure the corpus already has.

TWO-PASS APPROACH:
  Pass 1 — Thread-local IDF
    For each thread: compute which words are load-bearing WITHIN that thread.
    A word that appears in every message of the thread is scaffolding for that thread.
    A word that appears in 1-2 messages of a long thread is a signal event.
    Result: per-thread word signal scores.

  Pass 2 — Corpus validation
    A word's final score = (thread-local signal) × (corpus-level thread penetration).
    Words that score high locally AND appear across multiple high-SNR threads
    are true domain anchors — promoted regardless of static DOMAIN_ANCHORS list.
    Words that score high locally but only appear in one thread stay local.
    Words in the static DOMAIN_ANCHORS list get a floor boost.

WHY THIS IS DIFFERENT:
  "compression" in a file-format thread = corpus-common, thread-local noise
  "compression" in SCS architecture thread = thread-local signal, corpus anchor
  The flat scorer can't distinguish these. The recursive scorer can.

Usage:
    python sigtoken_recursive.py --messages flattened_messages.csv
    python sigtoken_recursive.py --messages flattened_messages.csv --word-inventory word_inventory.csv
"""

import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

csv.field_size_limit(10 * 1024 * 1024)

VERSION = "2.1-recursive"
COMPONENT = "C-0005"


# ---------------------------------------------------------------------------
# Static taxonomy (seed layer — corpus validation refines from here)
# ---------------------------------------------------------------------------

SCAFFOLDING = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'so', 'if', 'of', 'in', 'on',
    'at', 'to', 'for', 'from', 'with', 'by', 'about', 'as', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'am', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'done', 'will', 'would',
    'shall', 'should', 'can', 'could', 'may', 'might', 'must',
    'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours',
    'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its',
    'we', 'us', 'our', 'they', 'them', 'their',
    'who', 'whom', 'which', 'what', 'that', 'this', 'these', 'those',
    'into', 'through', 'between', 'after', 'before', 'during',
    'without', 'within', 'upon', 'above', 'below', 'under', 'over',
    'because', 'although', 'though', 'while', 'when', 'where', 'whether',
    'unless', 'since', 'than', 'also', 'too', 'then', 'now', 'here', 'there',
    'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither',
    'one', 'two', 'three', 'first', 'second', 'third',
})

FILLER_WORDS = frozenset({
    'basically', 'literally', 'actually', 'honestly', 'obviously',
    'clearly', 'simply', 'totally', 'absolutely', 'definitely',
    'certainly', 'probably', 'maybe', 'perhaps', 'really', 'very',
    'quite', 'rather', 'pretty', 'just', 'only', 'even', 'still',
    'already', 'always', 'often', 'sometimes', 'usually', 'generally',
    'lol', 'ok', 'okay', 'yeah', 'yep', 'nope', 'um', 'uh', 'ah',
    'oh', 'well', 'like', 'so', 'right', 'sure', 'anyway', 'kind',
    'sort', 'thing', 'things', 'stuff', 'bit', 'lot', 'way', 'ways',
    'gonna', 'wanna', 'gotta', 'etc', 'eg', 'ie',
})

# Static seed anchors — corpus validation can promote additional words to this level
DOMAIN_ANCHORS_SEED = {
    'signal', 'noise', 'compression', 'token', 'system', 'sigsystem',
    'mos2es', 'moses', 'sigrank', 'lineage', 'vault',
    'mediator', 'resonance', 'entropy', 'snr', 'drift', 'decay',
    'commitment', 'kernel', 'fracto', 'abba', 'scs', 'ppa', 'keter',
    'integrity', 'classification', 'semantic', 'recursive', 'anchor',
    'ignition', 'collapse', 'threshold', 'quantify', 'measurement',
    'governance', 'sovereign', 'artifact', 'leaderboard', 'dual',
    'weight', 'density', 'trajectory', 'conservation', 'invariant',
}


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def tokenize(text):
    text = text.lower()
    text = re.sub(r'mo§es™?|moses™', 'moses', text)
    text = re.sub(r'mos²es|mos2es', 'mos2es', text)
    text = re.sub(r"[^\w\s'\-]", ' ', text)
    tokens = text.split()
    result = []
    for i, t in enumerate(tokens):
        t = t.strip("'-_")
        if not t or t.isdigit() or (len(t) == 1 and t not in ('i', 'a')):
            continue
        result.append((i, t))
    return result


def parse_timestamp(ts_str):
    if not ts_str:
        return 0
    try:
        return float(ts_str)
    except (ValueError, TypeError):
        pass
    try:
        clean = re.sub(r'[+-]\d{2}:\d{2}$', '', str(ts_str)).rstrip('Z')
        return datetime.fromisoformat(clean).replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Pass 1: Thread-local TF-IDF
# For each thread, compute which words carry information WITHIN that thread.
# A word that appears in most messages of the thread = thread-scaffolding.
# A word that appears rarely but in high-information positions = thread-signal.
# ---------------------------------------------------------------------------

class ThreadProfile:
    """Vocabulary and signal profile for a single thread."""

    def __init__(self, name):
        self.name = name
        self.messages = []       # list of tokenized message word lists
        self.raw_texts = []
        self.timestamps = []
        self.roles = Counter()

    def add_message(self, text, role='unknown', timestamp=0):
        tokens = [t for _, t in tokenize(text)]
        self.messages.append(tokens)
        self.raw_texts.append(text)
        self.roles[role] += 1
        if timestamp:
            self.timestamps.append(timestamp)

    def compute_local_idf(self):
        """
        Within-thread IDF: words that appear in fewer messages relative
        to thread length carry more local signal.
        Returns dict: word -> local_idf_score (0.0 to 1.0)
        """
        n_messages = len(self.messages)
        if n_messages == 0:
            return {}

        # Document frequency within thread
        doc_freq = Counter()
        for msg_tokens in self.messages:
            for word in set(msg_tokens):
                doc_freq[word] += 1

        local_idf = {}
        for word, df in doc_freq.items():
            if word in SCAFFOLDING or word in FILLER_WORDS:
                local_idf[word] = 0.0
                continue
            # Standard IDF — inverse document frequency within thread
            idf = math.log((n_messages + 1) / (df + 1)) + 1
            # Normalize to 0-1 range (max possible IDF = log(n+1) + 1)
            max_idf = math.log(n_messages + 1) + 1
            local_idf[word] = round(idf / max_idf, 4)

        return local_idf

    def snr_estimate(self, dynamic_anchors):
        """Quick SNR estimate for this thread — used for corpus validation weighting."""
        all_tokens = [t for msg in self.messages for t in msg]
        if not all_tokens:
            return 0.5
        signal = sum(1 for t in all_tokens
                     if t in dynamic_anchors and t not in SCAFFOLDING and t not in FILLER_WORDS)
        noise = sum(1 for t in all_tokens if t in FILLER_WORDS)
        active = len([t for t in all_tokens if t not in SCAFFOLDING])
        if active == 0:
            return 0.5
        return (signal - noise * 0.5) / active


# ---------------------------------------------------------------------------
# Pass 2: Corpus-level validation
# Build a dynamic anchor set from bottom up — words that score high locally
# across multiple threads are promoted to corpus anchors.
# ---------------------------------------------------------------------------

class CorpusValidator:
    """
    Builds a dynamic signal map across all threads.

    For each word: computes a corpus_signal_score based on:
      - How many threads it appears in with high local IDF
      - Whether those threads have high estimated SNR
      - Whether it appears in the static DOMAIN_ANCHORS_SEED

    Words promoted to dynamic_anchors get the same floor as static seeds.
    """

    def __init__(self, thread_profiles, static_anchors):
        self.threads = thread_profiles
        self.static_anchors = static_anchors
        self.dynamic_anchors = set(static_anchors)
        self.word_corpus_scores = {}

    def build(self, promotion_threshold=0.35, min_threads=3):
        """
        Build corpus signal map.
        Words with corpus_score >= promotion_threshold in >= min_threads
        are promoted to dynamic_anchors.
        """
        print(f"  Corpus validation: {len(self.threads)} threads...")

        # First pass: get rough SNR for each thread using static anchors
        thread_snr = {}
        for name, profile in self.threads.items():
            thread_snr[name] = profile.snr_estimate(self.static_anchors)

        # Collect local IDF scores per word across threads
        word_weighted_appearances = defaultdict(list)  # word -> [(local_idf, thread_snr)]
        for name, profile in self.threads.items():
            local_idf = profile.compute_local_idf()
            t_snr = max(thread_snr[name], 0.01)  # floor at 0.01
            for word, idf_score in local_idf.items():
                if idf_score > 0:
                    word_weighted_appearances[word].append((idf_score, t_snr))

        # Compute corpus score for each word
        promoted = 0
        for word, appearances in word_weighted_appearances.items():
            if word in SCAFFOLDING or word in FILLER_WORDS:
                self.word_corpus_scores[word] = 0.0
                continue

            n_threads = len(appearances)
            # Weighted average: local_idf weighted by thread SNR
            weighted_sum = sum(idf * snr for idf, snr in appearances)
            weight_total = sum(snr for _, snr in appearances)
            avg_weighted_idf = weighted_sum / max(weight_total, 0.01)

            # Thread penetration factor: more threads = more validated
            # But use log scale — appearing in 100 threads vs 50 isn't 2x better
            penetration = math.log(n_threads + 1) / math.log(len(self.threads) + 1)

            corpus_score = avg_weighted_idf * 0.60 + penetration * 0.40

            # Static anchor boost — seeds always get a floor
            if word in self.static_anchors:
                corpus_score = max(corpus_score, 0.65)

            self.word_corpus_scores[word] = round(corpus_score, 4)

            # Promotion: high corpus score across enough threads
            if corpus_score >= promotion_threshold and n_threads >= min_threads:
                self.dynamic_anchors.add(word)
                promoted += 1

        print(f"  {promoted} words promoted to dynamic anchors "
              f"({len(self.dynamic_anchors)} total including seeds).")
        return self.dynamic_anchors

    def get_word_score(self, word):
        """Return corpus signal score for a word (0.0 to 1.0)."""
        if word in SCAFFOLDING:
            return 0.0
        if word in FILLER_WORDS:
            return 0.05
        return self.word_corpus_scores.get(word, 0.20)


# ---------------------------------------------------------------------------
# Thread-aware message scorer
# Uses both thread-local IDF and corpus validation scores
# ---------------------------------------------------------------------------

class RecursiveSigTokenScorer:
    """
    Scores tokens using thread-local context + corpus validation.
    Each message is scored with knowledge of:
      1. Its thread's local vocabulary distribution
      2. The corpus-wide signal map built from all threads
    """

    def __init__(self, corpus_validator, thread_profiles):
        self.validator = corpus_validator
        self.thread_profiles = thread_profiles
        # Pre-compute local IDF for each thread
        self.thread_local_idf = {
            name: profile.compute_local_idf()
            for name, profile in thread_profiles.items()
        }

    def score_token(self, token, position, message_tokens, thread_name):
        if token in SCAFFOLDING:
            return (0.05, 0.95, 'scaffolding', 'neutral_structure')

        # Get both local and corpus scores
        local_idf = self.thread_local_idf.get(thread_name, {}).get(token, 0.20)
        corpus_score = self.validator.get_word_score(token)
        is_dynamic_anchor = token in self.validator.dynamic_anchors

        if token in FILLER_WORDS:
            # Filler can be elevated if surrounded by dynamic anchors
            pos_idx = next((i for i, (p, t) in enumerate(message_tokens) if p == position), 0)
            window = [t for _, t in message_tokens[max(0, pos_idx-2):pos_idx+3]]
            anchor_neighbors = sum(1 for w in window if w in self.validator.dynamic_anchors)
            if anchor_neighbors >= 2:
                return (0.35, 0.65, 'noise', 'filler_emphasis')
            return (0.08, 0.92, 'noise', 'filler_pure')

        # Dynamic anchor: promoted through corpus validation OR static seed
        if is_dynamic_anchor:
            base = 0.75
            # Local IDF boost: if this word is also rare in its own thread, it's
            # doing real work right here, not just a general domain term
            local_boost = local_idf * 0.15
            # Cluster bonus: nearby anchors
            pos_idx = next((i for i, (p, t) in enumerate(message_tokens) if p == position), 0)
            window = [t for _, t in message_tokens[max(0, pos_idx-2):pos_idx+3]]
            cluster = sum(1 for w in window if w in self.validator.dynamic_anchors and w != token)
            cluster_bonus = min(cluster * 0.02, 0.08)
            sw = min(base + local_boost + cluster_bonus, 0.95)
            nw = round(1.0 - sw, 4)
            return (sw, nw, 'signal', 'dynamic_anchor')

        # General word: composite of local IDF + corpus score + position
        total_tokens = len(message_tokens)
        normalized_pos = position / max(total_tokens, 1)
        position_score = 0.60 - normalized_pos * 0.20

        sw = round(
            local_idf * 0.45 +
            corpus_score * 0.35 +
            position_score * 0.20,
            4
        )
        sw = min(max(sw, 0.08), 0.75)
        nw = round(1.0 - sw, 4)

        tier = 'signal' if sw >= 0.38 else 'noise'
        return (sw, nw, tier, 'recursive_local_corpus')

    def score_message(self, text, thread_name):
        tokens = tokenize(text)
        if not tokens:
            return None

        scored = []
        for pos, token in tokens:
            sw, nw, tier, reason = self.score_token(token, pos, tokens, thread_name)
            scored.append({
                'token': token, 'position': pos,
                'SW': sw, 'NW': nw, 'tier': tier, 'reason': reason,
            })

        signal_tokens = [s for s in scored if s['tier'] == 'signal']
        noise_tokens = [s for s in scored if s['tier'] == 'noise']
        scaffolding_tokens = [s for s in scored if s['tier'] == 'scaffolding']

        signal_count = len(signal_tokens)
        noise_count = len(noise_tokens)
        active = signal_count + noise_count

        snr_ratio = signal_count / max(noise_count, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = signal_count / max(active, 1)

        # Commitment — same length-irreducibility formula as v2
        non_scaffold = [s for s in scored if s['tier'] != 'scaffolding']
        if non_scaffold:
            signal_only = [s for s in non_scaffold if s['tier'] == 'signal']
            avg_signal_sw = (
                sum(s['SW'] for s in signal_only) / len(signal_only)
                if signal_only else 0.0
            )
            signal_purity = signal_count / max(active, 1)

            if active <= 3:
                length_factor = 1.0
            elif active <= 8:
                length_factor = 0.90
            elif active <= 20:
                length_factor = 0.75
            elif active <= 50:
                length_factor = 0.60
            else:
                length_factor = max(0.40, 0.60 - (active - 50) * 0.001)

            commitment = round(
                signal_purity * 0.50 +
                avg_signal_sw * 0.30 +
                length_factor * 0.20,
                4
            )
        else:
            commitment = 0.0

        return {
            'text': text[:120] + '...' if len(text) > 120 else text,
            'total_tokens': len(scored),
            'signal_count': signal_count,
            'noise_count': noise_count,
            'scaffolding_count': len(scaffolding_tokens),
            'snr_normalized': round(snr_normalized, 4),
            'snr_ratio': round(snr_ratio, 4),
            'snr_db': round(snr_db, 2),
            'commitment_score': commitment,
            'tokens': scored,
        }


# ---------------------------------------------------------------------------
# Full corpus processor
# ---------------------------------------------------------------------------

class RecursiveSessionProcessor:

    def __init__(self, messages):
        self.messages = messages
        # Build thread profiles
        print("  Building thread profiles (Pass 1)...")
        self.thread_profiles = defaultdict(lambda: ThreadProfile(''))
        for msg in messages:
            thread = msg.get('thread', 'unknown')
            if thread not in self.thread_profiles:
                self.thread_profiles[thread] = ThreadProfile(thread)
            self.thread_profiles[thread].add_message(
                msg.get('content', ''),
                role=msg.get('role', 'unknown'),
                timestamp=parse_timestamp(msg.get('create_time', ''))
            )
        print(f"  {len(self.thread_profiles)} threads profiled.")

    def build_corpus(self, static_anchors):
        # Pass 2: corpus validation
        print("  Running corpus validation (Pass 2)...")
        self.validator = CorpusValidator(self.thread_profiles, static_anchors)
        self.dynamic_anchors = self.validator.build()
        self.scorer = RecursiveSigTokenScorer(self.validator, self.thread_profiles)
        return self.dynamic_anchors

    def process(self):
        results = []
        for msg in self.messages:
            content = msg.get('content', '')
            if not content or len(content.strip()) < 3:
                continue
            thread = msg.get('thread', 'unknown')
            scored = self.scorer.score_message(content, thread)
            if scored:
                scored['role'] = msg.get('role', 'unknown')
                scored['thread'] = thread
                scored['create_time'] = msg.get('create_time', '')
            results.append(scored)
        return [r for r in results if r]

    def summarize(self, results):
        if not results:
            return {}

        total_tokens = sum(r['total_tokens'] for r in results)
        total_signal = sum(r['signal_count'] for r in results)
        total_noise = sum(r['noise_count'] for r in results)
        total_scaffold = sum(r['scaffolding_count'] for r in results)
        active = total_signal + total_noise

        snr_ratio = total_signal / max(total_noise, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = total_signal / max(active, 1)

        commitments = [r['commitment_score'] for r in results]
        avg_commitment = sum(commitments) / len(commitments)
        high_commitment = [r for r in results if r['commitment_score'] >= 0.50]
        low_commitment = [r for r in results if r['commitment_score'] < 0.20]

        thread_data = defaultdict(lambda: {
            'signal': 0, 'noise': 0, 'messages': 0, 'commitment': [], 'times': []
        })
        for r in results:
            t = r['thread']
            thread_data[t]['signal'] += r['signal_count']
            thread_data[t]['noise'] += r['noise_count']
            thread_data[t]['messages'] += 1
            thread_data[t]['commitment'].append(r['commitment_score'])
            if r.get('create_time'):
                thread_data[t]['times'].append(r['create_time'])

        thread_snr = []
        for thread, data in thread_data.items():
            active_t = data['signal'] + data['noise']
            ratio = data['signal'] / max(data['noise'], 1)
            db = 10 * math.log10(ratio) if ratio > 0 else -99.0
            norm = data['signal'] / max(active_t, 1)
            avg_commit = sum(data['commitment']) / len(data['commitment'])
            thread_snr.append({
                'thread': thread,
                'snr_normalized': round(norm, 4),
                'snr_db': round(db, 2),
                'avg_commitment': round(avg_commit, 4),
                'messages': data['messages'],
            })
        thread_snr.sort(key=lambda x: x['snr_normalized'], reverse=True)

        return {
            'total_messages': len(results),
            'total_tokens': total_tokens,
            'total_signal': total_signal,
            'total_noise': total_noise,
            'total_scaffolding': total_scaffold,
            'snr_normalized': round(snr_normalized, 4),
            'snr_ratio': round(snr_ratio, 4),
            'snr_db': round(snr_db, 2),
            'avg_commitment': round(avg_commitment, 4),
            'high_commitment_messages': len(high_commitment),
            'low_commitment_messages': len(low_commitment),
            'thread_leaderboard': thread_snr,
            'dynamic_anchors_count': len(self.dynamic_anchors),
        }


# ---------------------------------------------------------------------------
# Output + CSV + CLI (same pattern as v2)
# ---------------------------------------------------------------------------

def render_summary(summary, output_dir=None):
    lines = []
    lines.append("=" * 64)
    lines.append("  SIGTOKEN RECURSIVE — THREAD-AWARE TWO-PASS SCORING")
    lines.append(f"  Component {COMPONENT} | v{VERSION} | Ello Cello LLC")
    lines.append("")
    lines.append("  Pass 1: Thread-local IDF — each word scored within its thread")
    lines.append("  Pass 2: Corpus validation — promoted anchors from bottom up")
    lines.append("=" * 64)
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")
    lines.append("=" * 64)
    lines.append("  SESSION METRICS")
    lines.append("=" * 64)
    lines.append(f"  Total Messages Scored:    {summary['total_messages']:,}")
    lines.append(f"  Total Tokens:             {summary['total_tokens']:,}")
    lines.append(f"  Signal Tokens:            {summary['total_signal']:,}")
    lines.append(f"  Noise Tokens:             {summary['total_noise']:,}")
    lines.append(f"  Scaffolding Tokens:       {summary['total_scaffolding']:,}")
    lines.append(f"  Dynamic Anchors Built:    {summary['dynamic_anchors_count']:,}")
    lines.append("")
    lines.append(f"  SNR (Normalized 0-1):     {summary['snr_normalized']:.4f}")
    lines.append(f"  SNR (Ratio S/N):          {summary['snr_ratio']:.4f}")
    lines.append(f"  SNR (dB):                 {summary['snr_db']:.2f} dB")
    lines.append("")
    lines.append("=" * 64)
    lines.append("  COMMITMENT ANALYSIS")
    lines.append("=" * 64)
    lines.append(f"  Avg Message Commitment:   {summary['avg_commitment']:.4f}")
    lines.append(f"  High Commitment (≥0.50):  {summary['high_commitment_messages']:,} messages")
    lines.append(f"  Low Commitment  (<0.20):  {summary['low_commitment_messages']:,} messages")
    lines.append("")
    lines.append("=" * 64)
    lines.append("  THREAD LEADERBOARD (by SNR, top 20)")
    lines.append("=" * 64)
    for i, t in enumerate(summary['thread_leaderboard'][:20], 1):
        lines.append(
            f"  {i:>2}. {t['thread'][:38]:<38} "
            f"SNR:{t['snr_normalized']:.4f}  "
            f"CMT:{t['avg_commitment']:.4f}  "
            f"msgs:{t['messages']}"
        )
    lines.append("")
    lines.append("=" * 64)
    lines.append("  BOTTOM 5 THREADS (highest noise)")
    lines.append("=" * 64)
    for t in summary['thread_leaderboard'][-5:]:
        lines.append(
            f"  {t['thread'][:38]:<38} "
            f"SNR:{t['snr_normalized']:.4f}  "
            f"CMT:{t['avg_commitment']:.4f}  "
            f"msgs:{t['messages']}"
        )
    lines.append("=" * 64)

    output = '\n'.join(lines)
    print(output)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
        run_dir = os.path.join(output_dir, f'run_{ts}')
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(run_dir, 'sigtoken_recursive_summary.txt'), 'w') as f:
            f.write(output)
        with open(os.path.join(run_dir, 'sigtoken_recursive_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n  Output saved to: {run_dir}")
        return run_dir
    return None


def load_messages_csv(path):
    messages = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            messages.append({
                'content': row.get('message_text', row.get('content', '')),
                'role': row.get('role', 'unknown'),
                'thread': row.get('conversation_title', row.get('title', row.get('thread', 'unknown'))),
                'create_time': row.get('timestamp', row.get('create_time', '')),
            })
    return messages


def load_officer_anchors(path):
    anchors = set()
    if not path or not os.path.isfile(path):
        return anchors
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Rank') == 'Officer-Class':
                word = row.get('Word', '').strip().lower()
                if word:
                    anchors.add(word)
    print(f"  {len(anchors)} Officer-Class anchors loaded.")
    return anchors


def main():
    parser = argparse.ArgumentParser(
        description=f'SigToken Recursive v{VERSION} — Thread-aware two-pass scoring'
    )
    parser.add_argument('--messages', required=True)
    parser.add_argument('--word-inventory', help='word_inventory.csv — Officer-Class anchors as seeds')
    parser.add_argument('--output-dir', default='./runs')
    args = parser.parse_args()

    static_anchors = set(DOMAIN_ANCHORS_SEED)
    if args.word_inventory:
        static_anchors.update(load_officer_anchors(args.word_inventory))

    print(f"Loading messages from {args.messages}...")
    messages = load_messages_csv(args.messages)
    print(f"  {len(messages):,} messages loaded.")

    processor = RecursiveSessionProcessor(messages)
    processor.build_corpus(static_anchors)

    print("  Scoring all messages...")
    results = processor.process()
    summary = processor.summarize(results)
    render_summary(summary, args.output_dir)


if __name__ == '__main__':
    main()
