#!/usr/bin/env python3
"""
SigToken System — Contextual Token SNR Classification
Component C-0005 | Ello Cello LLC

"Words and tokens are not inherently signal or noise.
 Their classification depends entirely on contextual function,
 relational placement, frequency, and contribution to compression."
                                        — classification_logic.md, Oct 1 2025

Takes a message or corpus and classifies every token dynamically —
not by identity, but by usage role in context.

Output:
  - Per-token dual weights (SW / NW)
  - Message-level commitment score
  - Session SNR
  - Leaderboard-ready resonance scores

Usage:
    python sigtoken_sys.py --messages flattened_messages.csv
    python sigtoken_sys.py --text "your message here"
    python sigtoken_sys.py --messages flattened_messages.csv --output-dir ./runs/
"""

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

csv.field_size_limit(10 * 1024 * 1024)

VERSION = "1.0"
COMPONENT = "C-0005"

# ---------------------------------------------------------------------------
# The three-tier taxonomy (signal_use_case.md, noise_use_case.md Oct 1 2025)
# Signal    — high semantic density, intent-bearing
# Scaffolding — neutral support structure (the, into, every)
# Noise     — low contribution, filler, replaceable
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

# Noise: filler words — low semantic contribution in most contexts
# NOTE: these carry DUAL WEIGHTS. 'just' is noise in filler but
# signal in emotional emphasis. We score by context, not identity.
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

# High-signal domain terms — when these appear they carry heavy SW
# Seeded from Signal Army Officer-Class words in your corpus
# NOTE: mutable set so --word-inventory can extend it at runtime
DOMAIN_ANCHORS = {
    'signal', 'noise', 'compression', 'token', 'system', 'sigsystem',
    'mos2es', 'moses', 'sigrank', 'compression', 'lineage', 'vault',
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
    """Tokenize preserving positional context for dual-weight scoring."""
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
        result.append((i, t))  # (position, token)
    return result


# ---------------------------------------------------------------------------
# Core: Contextual Dual-Weight Scorer
# C-0005 — classification by usage role, not identity
# ---------------------------------------------------------------------------

class SigTokenScorer:
    """
    Classifies tokens by contextual function.

    The key insight (Oct 1 2025, classification_logic.md):
    Signal/noise is not a property of the word.
    It is a property of the word IN THIS POSITION IN THIS MESSAGE.

    Dual weights are held simultaneously — SW + NW = 1.0
    Classification resolves at message level when context collapses them.
    """

    def __init__(self, corpus_frequencies=None):
        # Corpus-level frequency data for relative scoring
        self.corpus_freq = corpus_frequencies or {}
        self.max_freq = max(self.corpus_freq.values()) if self.corpus_freq else 1

    def score_token(self, token, position, message_tokens, message_text=""):
        """
        Score a single token in context. Returns (SW, NW, tier, reason).

        Tier: 'signal' | 'scaffolding' | 'noise'
        """
        # Scaffolding — neutral structure, not signal or noise
        if token in SCAFFOLDING:
            return (0.05, 0.05, 'scaffolding', 'neutral_structure')

        # Domain anchor — high signal in this corpus by definition
        if token in DOMAIN_ANCHORS:
            base_sw = 0.80
            # Boost if it appears in a dense cluster of other anchors
            anchor_neighbors = sum(
                1 for _, t in message_tokens
                if t in DOMAIN_ANCHORS and t != token
            )
            cluster_bonus = min(anchor_neighbors * 0.02, 0.15)
            sw = min(base_sw + cluster_bonus, 0.95)
            nw = round(1.0 - sw, 4)
            return (sw, nw, 'signal', 'domain_anchor')

        # Filler words — dual weight depends on context
        if token in FILLER_WORDS:
            # Check if surrounded by high-signal content
            # If yes: may be emphasis, not pure noise
            # e.g. "just" in "just compression" vs "just kind of the thing"
            window = [t for _, t in message_tokens]
            pos_idx = next((i for i, (p, t) in enumerate(message_tokens) if t == token), 0)
            nearby = window[max(0, pos_idx-2):pos_idx+3]
            signal_neighbors = sum(1 for w in nearby if w in DOMAIN_ANCHORS)

            if signal_neighbors >= 2:
                # Emphasis context — elevated SW
                return (0.35, 0.65, 'noise', 'filler_emphasis')
            else:
                # Pure filler
                return (0.08, 0.92, 'noise', 'filler_pure')

        # Frequency-based scoring for everything else
        # High corpus frequency = well-established in this domain
        # But also check: is it ONLY in this corpus (narrow) or widespread?
        freq = self.corpus_freq.get(token, 0)
        freq_normalized = freq / self.max_freq if self.max_freq > 0 else 0

        # Position signal: early in message = likely load-bearing
        total_tokens = len(message_tokens)
        position_score = 1.0 - (position / max(total_tokens, 1)) * 0.3

        # Uniqueness signal: rare tokens in a domain-dense message = high signal
        message_word_set = set(t for _, t in message_tokens)
        domain_density = len(message_word_set & DOMAIN_ANCHORS) / max(len(message_word_set), 1)

        # Composite SW
        sw = (
            0.40 * freq_normalized +
            0.25 * position_score +
            0.35 * domain_density
        )
        sw = round(min(max(sw, 0.10), 0.75), 4)
        nw = round(1.0 - sw, 4)

        tier = 'signal' if sw >= 0.35 else 'noise'
        return (sw, nw, tier, 'frequency_context')

    def score_message(self, text):
        """
        Score all tokens in a message. Returns message-level commitment data.

        Commitment score = fraction of tokens that cannot be removed
        without collapsing the message's irreducible meaning.
        """
        tokens = tokenize(text)
        if not tokens:
            return None

        scored = []
        for pos, token in tokens:
            sw, nw, tier, reason = self.score_token(token, pos, tokens, text)
            scored.append({
                'token': token,
                'position': pos,
                'SW': sw,
                'NW': nw,
                'tier': tier,
                'reason': reason,
            })

        # Message-level SNR
        signal_tokens = [s for s in scored if s['tier'] == 'signal']
        noise_tokens = [s for s in scored if s['tier'] == 'noise']
        scaffolding_tokens = [s for s in scored if s['tier'] == 'scaffolding']

        total = len(scored)
        signal_count = len(signal_tokens)
        noise_count = len(noise_tokens)

        snr_ratio = signal_count / max(noise_count, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = signal_count / max(total, 1)

        # Commitment score:
        # Average SW of non-scaffolding tokens weighted by necessity
        # High commitment = message collapses cleanly to its kernel
        non_scaffold = [s for s in scored if s['tier'] != 'scaffolding']
        if non_scaffold:
            avg_sw = sum(s['SW'] for s in non_scaffold) / len(non_scaffold)
            # Penalize messages that are mostly noise
            noise_penalty = noise_count / max(total, 1)
            commitment = round(avg_sw * (1.0 - noise_penalty * 0.5), 4)
        else:
            commitment = 0.0

        return {
            'text': text[:120] + '...' if len(text) > 120 else text,
            'total_tokens': total,
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
# Session-level processor
# ---------------------------------------------------------------------------

class SessionProcessor:
    """Processes a full conversation corpus through SigToken."""

    def __init__(self, messages):
        # Build corpus frequency table first
        all_text = ' '.join(m.get('content', '') for m in messages)
        raw_tokens = tokenize(all_text)
        freq = Counter(t for _, t in raw_tokens)
        self.scorer = SigTokenScorer(corpus_frequencies=freq)
        self.messages = messages

    def process(self):
        results = []
        for msg in self.messages:
            content = msg.get('content', '')
            if not content or len(content.strip()) < 5:
                continue
            scored = self.scorer.score_message(content)
            if scored:
                scored['role'] = msg.get('role', 'unknown')
                scored['thread'] = msg.get('title', msg.get('thread', 'unknown'))
                results.append(scored)
        return results

    def summarize(self, results):
        if not results:
            return {}

        total_tokens = sum(r['total_tokens'] for r in results)
        total_signal = sum(r['signal_count'] for r in results)
        total_noise = sum(r['noise_count'] for r in results)
        total_scaffold = sum(r['scaffolding_count'] for r in results)

        snr_ratio = total_signal / max(total_noise, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = total_signal / max(total_tokens, 1)

        # Commitment distribution
        commitments = [r['commitment_score'] for r in results]
        avg_commitment = sum(commitments) / len(commitments)
        high_commitment = [r for r in results if r['commitment_score'] >= 0.50]
        low_commitment = [r for r in results if r['commitment_score'] < 0.20]

        # Thread-level leaderboard
        thread_data = defaultdict(lambda: {'signal': 0, 'noise': 0, 'messages': 0, 'commitment': []})
        for r in results:
            t = r['thread']
            thread_data[t]['signal'] += r['signal_count']
            thread_data[t]['noise'] += r['noise_count']
            thread_data[t]['messages'] += 1
            thread_data[t]['commitment'].append(r['commitment_score'])

        thread_snr = []
        for thread, data in thread_data.items():
            ratio = data['signal'] / max(data['noise'], 1)
            db = 10 * math.log10(ratio) if ratio > 0 else -99.0
            norm = data['signal'] / max(data['signal'] + data['noise'], 1)
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
        }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render_summary(summary, output_dir=None):
    lines = []
    lines.append("=" * 64)
    lines.append("  SIGTOKEN SYSTEM — CONTEXTUAL TOKEN SNR CLASSIFICATION")
    lines.append(f"  Component {COMPONENT} | v{VERSION} | Ello Cello LLC")
    lines.append("")
    lines.append("  'Words are not inherently signal or noise.")
    lines.append("   Their classification depends entirely on")
    lines.append("   contextual function and usage role.'")
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
    lines.append("  Commitment = fraction of a message that cannot be removed")
    lines.append("  without collapsing its irreducible meaning kernel.")
    lines.append("")
    lines.append("=" * 64)
    lines.append("  THREAD LEADERBOARD (by SNR)")
    lines.append("=" * 64)
    for i, t in enumerate(summary['thread_leaderboard'][:20], 1):
        lines.append(
            f"  {i:>2}. {t['thread'][:40]:<40} "
            f"SNR:{t['snr_normalized']:.4f}  "
            f"CMT:{t['avg_commitment']:.4f}  "
            f"dB:{t['snr_db']:>6.2f}  "
            f"msgs:{t['messages']}"
        )
    lines.append("")
    lines.append("=" * 64)
    lines.append("  BOTTOM 5 THREADS (highest noise)")
    lines.append("=" * 64)
    for t in summary['thread_leaderboard'][-5:]:
        lines.append(
            f"  {t['thread'][:40]:<40} "
            f"SNR:{t['snr_normalized']:.4f}  "
            f"CMT:{t['avg_commitment']:.4f}  "
            f"dB:{t['snr_db']:>6.2f}"
        )
    lines.append("=" * 64)

    output = '\n'.join(lines)
    print(output)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
        run_dir = os.path.join(output_dir, f'run_{ts}')
        os.makedirs(run_dir, exist_ok=True)

        with open(os.path.join(run_dir, 'sigtoken_summary.txt'), 'w') as f:
            f.write(output)

        with open(os.path.join(run_dir, 'sigtoken_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n  Output saved to: {run_dir}")
        return run_dir

    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_messages_csv(path):
    messages = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg = {
                'content': row.get('message_text', row.get('content', '')),
                'role': row.get('role', 'unknown'),
                'thread': row.get('conversation_title', row.get('title', row.get('thread', 'unknown'))),
            }
            messages.append(msg)
    return messages


def load_officer_anchors(word_inventory_path):
    """Load Officer-Class words from Signal Army word_inventory.csv.
    These become domain anchors — dynamically seeded, not hardcoded.
    """
    anchors = set()
    if not word_inventory_path or not os.path.isfile(word_inventory_path):
        return anchors
    with open(word_inventory_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Rank') == 'Officer-Class':
                word = row.get('Word', '').strip().lower()
                if word:
                    anchors.add(word)
    print(f"  {len(anchors)} Officer-Class anchors loaded from word inventory.")
    return anchors


def main():
    parser = argparse.ArgumentParser(
        description=f'SigToken System v{VERSION} — Component {COMPONENT}'
    )
    parser.add_argument('--messages', help='Path to flattened_messages.csv from Signal Army')
    parser.add_argument('--text', help='Score a single message directly')
    parser.add_argument('--word-inventory', help='Path to word_inventory.csv — loads Officer-Class words as domain anchors')
    parser.add_argument('--output-dir', default='./runs', help='Output directory')
    args = parser.parse_args()

    # Load dynamic anchors if provided — extends (not replaces) hardcoded DOMAIN_ANCHORS
    if args.word_inventory:
        officer_anchors = load_officer_anchors(args.word_inventory)
        DOMAIN_ANCHORS.update(officer_anchors)  # type: ignore

    if args.text:
        scorer = SigTokenScorer()
        result = scorer.score_message(args.text)
        print(f"\nMessage: {args.text}")
        print(f"Commitment Score: {result['commitment_score']}")
        print(f"SNR (normalized): {result['snr_normalized']}")
        print(f"SNR (dB): {result['snr_db']}")
        print(f"\nToken breakdown:")
        for t in result['tokens']:
            print(f"  {t['token']:<20} SW:{t['SW']:.3f}  NW:{t['NW']:.3f}  [{t['tier']}]  ({t['reason']})")
        return

    if args.messages:
        print(f"Loading messages from {args.messages}...")
        messages = load_messages_csv(args.messages)
        print(f"  {len(messages):,} messages loaded.")
        processor = SessionProcessor(messages)
        results = processor.process()
        summary = processor.summarize(results)
        render_summary(summary, args.output_dir)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
