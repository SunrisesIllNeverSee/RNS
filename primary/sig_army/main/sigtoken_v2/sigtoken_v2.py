#!/usr/bin/env python3
"""
SigToken System v2.0 — Revised Commitment Scoring
Component C-0005 | Ello Cello LLC

Changes from v1.0:
  - Removed domain_density bleed from frequency scorer (was inflating all tokens
    in domain-rich messages, deflating all tokens in casual messages)
  - Commitment now penalizes length: short irreducible messages score higher
    than long messages with equivalent signal density
  - SNR ceiling fixed: scaffolding excluded from both numerator AND denominator
    so the ratio reflects actual signal vs noise, not signal vs everything
  - Frequency scoring simplified: position + corpus rarity only, no domain bleed

Usage:
    python sigtoken_v2.py --messages flattened_messages.csv
    python sigtoken_v2.py --text "your message here"
    python sigtoken_v2.py --messages flattened_messages.csv --word-inventory word_inventory.csv
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

VERSION = "2.0"
COMPONENT = "C-0005"

# ---------------------------------------------------------------------------
# Three-tier taxonomy (unchanged from v1 — the taxonomy is correct)
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

DOMAIN_ANCHORS = {
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
# Tokenizer (unchanged)
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


# ---------------------------------------------------------------------------
# Core: Revised Dual-Weight Scorer v2
# Key changes:
#   - No domain_density bleed into unrelated tokens
#   - Filler emphasis check uses proximity only (not global domain density)
#   - Frequency scorer: position + corpus rarity, clean separation
# ---------------------------------------------------------------------------

class SigTokenScorer:
    """
    v2: Classifies tokens by contextual function without domain bleed.

    Token scoring is LOCAL — each token scored by its own properties
    and immediate neighbors only. Global message statistics do not
    inflate or deflate unrelated tokens.
    """

    def __init__(self, corpus_frequencies=None, corpus_size=1):
        self.corpus_freq = corpus_frequencies or {}
        self.corpus_size = max(corpus_size, 1)
        # IDF-style rarity: rare tokens get signal boost
        # common tokens (appear in >10% of messages) treated as scaffolding-like
        self.rarity_threshold = self.corpus_size * 0.10

    def score_token(self, token, position, message_tokens):
        """
        Score a single token in local context. Returns (SW, NW, tier, reason).

        v2 change: no global domain_density in the formula.
        Each token stands on its own + immediate neighbors.
        """
        if token in SCAFFOLDING:
            return (0.05, 0.95, 'scaffolding', 'neutral_structure')

        if token in DOMAIN_ANCHORS:
            base_sw = 0.80
            # Only look at immediate neighbors (window of 4) for cluster bonus
            pos_idx = next((i for i, (p, t) in enumerate(message_tokens) if p == position), 0)
            window_tokens = [t for _, t in message_tokens[max(0, pos_idx-2):pos_idx+3]]
            anchor_neighbors = sum(1 for w in window_tokens if w in DOMAIN_ANCHORS and w != token)
            cluster_bonus = min(anchor_neighbors * 0.03, 0.15)
            sw = min(base_sw + cluster_bonus, 0.95)
            nw = round(1.0 - sw, 4)
            return (sw, nw, 'signal', 'domain_anchor')

        if token in FILLER_WORDS:
            # Check immediate neighbors for signal context
            pos_idx = next((i for i, (p, t) in enumerate(message_tokens) if p == position), 0)
            window_tokens = [t for _, t in message_tokens[max(0, pos_idx-2):pos_idx+3]]
            signal_neighbors = sum(1 for w in window_tokens if w in DOMAIN_ANCHORS)
            if signal_neighbors >= 2:
                return (0.35, 0.65, 'noise', 'filler_emphasis')
            else:
                return (0.08, 0.92, 'noise', 'filler_pure')

        # Frequency-based scoring — clean version, no domain bleed
        # Two factors only: corpus rarity + positional weight
        freq = self.corpus_freq.get(token, 0)

        # Rarity: words that appear rarely in corpus carry more information
        # Common words (>10% of docs) treated like scaffolding
        if freq > self.rarity_threshold:
            rarity_score = 0.20  # very common — low signal
        elif freq > self.rarity_threshold * 0.1:
            rarity_score = 0.45  # moderately common
        else:
            rarity_score = 0.70  # rare — higher signal potential

        # Position: earlier in message = more likely load-bearing
        total_tokens = len(message_tokens)
        normalized_pos = position / max(total_tokens, 1)
        position_score = 0.60 - (normalized_pos * 0.20)  # 0.60 at start, 0.40 at end

        sw = round((rarity_score * 0.65 + position_score * 0.35), 4)
        sw = min(max(sw, 0.10), 0.75)
        nw = round(1.0 - sw, 4)

        tier = 'signal' if sw >= 0.40 else 'noise'
        return (sw, nw, tier, 'frequency_rarity')

    def score_message(self, text):
        tokens = tokenize(text)
        if not tokens:
            return None

        scored = []
        for pos, token in tokens:
            sw, nw, tier, reason = self.score_token(token, pos, tokens)
            scored.append({
                'token': token,
                'position': pos,
                'SW': sw,
                'NW': nw,
                'tier': tier,
                'reason': reason,
            })

        signal_tokens = [s for s in scored if s['tier'] == 'signal']
        noise_tokens = [s for s in scored if s['tier'] == 'noise']
        scaffolding_tokens = [s for s in scored if s['tier'] == 'scaffolding']

        total = len(scored)
        signal_count = len(signal_tokens)
        noise_count = len(noise_tokens)

        # v2 SNR fix: scaffolding excluded from BOTH numerator and denominator
        # SNR now measures signal vs noise only — scaffolding is neutral, not counted
        active_tokens = signal_count + noise_count  # scaffolding excluded
        snr_ratio = signal_count / max(noise_count, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = signal_count / max(active_tokens, 1)  # KEY CHANGE

        # v2 Commitment fix: irreducibility score
        # Short messages that are fully signal score higher than long messages
        # with equal signal density. Length IS information when you can't compress further.
        #
        # Formula:
        #   base = avg SW of signal tokens (content quality)
        #   length_factor = diminishing returns on longer messages
        #     - a 5-token fully signal message scores higher than a 50-token one
        #     - models the irreducibility claim: can you remove any of this?
        #   noise_drag = penalty for noise fraction

        non_scaffold = [s for s in scored if s['tier'] != 'scaffolding']
        if non_scaffold:
            signal_only = [s for s in non_scaffold if s['tier'] == 'signal']
            avg_signal_sw = (
                sum(s['SW'] for s in signal_only) / len(signal_only)
                if signal_only else 0.0
            )

            # Signal purity: what fraction of active tokens are signal
            signal_purity = signal_count / max(active_tokens, 1)

            # Length irreducibility factor:
            # Peaks around 3-8 tokens (maximally irreducible short messages)
            # Decreases slowly for longer messages (more room for fat)
            # "yes please" with 2 tokens gets a HIGH irreducibility score
            if active_tokens <= 3:
                length_factor = 1.0  # maximally irreducible
            elif active_tokens <= 8:
                length_factor = 0.90
            elif active_tokens <= 20:
                length_factor = 0.75
            elif active_tokens <= 50:
                length_factor = 0.60
            else:
                # Long messages: factor drops slowly — they CAN be irreducible
                # but it takes more to prove it
                length_factor = max(0.40, 0.60 - (active_tokens - 50) * 0.001)

            commitment = round(
                signal_purity * 0.50 +
                avg_signal_sw * 0.30 +
                length_factor * 0.20,
                4
            )
        else:
            # Pure scaffolding message — no commitment measurable
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
# Session processor (extended: captures create_time for timeline)
# ---------------------------------------------------------------------------

class SessionProcessor:

    def __init__(self, messages):
        all_text = ' '.join(m.get('content', '') for m in messages)
        raw_tokens = tokenize(all_text)
        freq = Counter(t for _, t in raw_tokens)
        # corpus_size = number of messages for IDF-style rarity
        self.scorer = SigTokenScorer(corpus_frequencies=freq, corpus_size=len(messages))
        self.messages = messages

    def process(self):
        results = []
        for msg in self.messages:
            content = msg.get('content', '')
            if not content or len(content.strip()) < 3:
                continue
            scored = self.scorer.score_message(content)
            if scored:
                scored['role'] = msg.get('role', 'unknown')
                scored['thread'] = msg.get('title', msg.get('thread', 'unknown'))
                scored['create_time'] = msg.get('create_time', '')
                results.append(scored)
        return results

    def summarize(self, results):
        if not results:
            return {}

        total_tokens = sum(r['total_tokens'] for r in results)
        total_signal = sum(r['signal_count'] for r in results)
        total_noise = sum(r['noise_count'] for r in results)
        total_scaffold = sum(r['scaffolding_count'] for r in results)

        # v2 SNR: exclude scaffolding from both sides
        active = total_signal + total_noise
        snr_ratio = total_signal / max(total_noise, 1)
        snr_db = 10 * math.log10(snr_ratio) if snr_ratio > 0 else -99.0
        snr_normalized = total_signal / max(active, 1)

        commitments = [r['commitment_score'] for r in results]
        avg_commitment = sum(commitments) / len(commitments)
        high_commitment = [r for r in results if r['commitment_score'] >= 0.50]
        low_commitment = [r for r in results if r['commitment_score'] < 0.20]

        # Thread leaderboard
        thread_data = defaultdict(lambda: {
            'signal': 0, 'noise': 0, 'messages': 0, 'commitment': [],
            'times': []
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
            earliest = min(data['times']) if data['times'] else ''
            thread_snr.append({
                'thread': thread,
                'snr_normalized': round(norm, 4),
                'snr_db': round(db, 2),
                'avg_commitment': round(avg_commit, 4),
                'messages': data['messages'],
                'earliest': earliest,
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
    lines.append("  SIGTOKEN SYSTEM v2 — REVISED COMMITMENT SCORING")
    lines.append(f"  Component {COMPONENT} | v{VERSION} | Ello Cello LLC")
    lines.append("")
    lines.append("  'Commitment is irreducibility, not vocabulary density.'")
    lines.append("  SNR now excludes scaffolding from both S and N counts.")
    lines.append("  Short irreducible messages score higher than long padded ones.")
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
    lines.append(f"  Active (S+N only):        {summary['total_signal'] + summary['total_noise']:,}")
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
    lines.append("  Commitment = signal purity × quality × length irreducibility")
    lines.append("  Short messages that cannot be compressed score highest.")
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

        with open(os.path.join(run_dir, 'sigtoken_v2_summary.txt'), 'w') as f:
            f.write(output)
        with open(os.path.join(run_dir, 'sigtoken_v2_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n  Output saved to: {run_dir}")
        return run_dir

    return None


# ---------------------------------------------------------------------------
# CSV loader + anchor loader (same as v1)
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
                'create_time': row.get('create_time', ''),
            }
            messages.append(msg)
    return messages


def load_officer_anchors(word_inventory_path):
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=f'SigToken System v{VERSION} — Component {COMPONENT}'
    )
    parser.add_argument('--messages', help='Path to flattened_messages.csv from Signal Army')
    parser.add_argument('--text', help='Score a single message directly')
    parser.add_argument('--word-inventory', help='Path to word_inventory.csv — loads Officer-Class anchors')
    parser.add_argument('--output-dir', default='./runs', help='Output directory')
    args = parser.parse_args()

    if args.word_inventory:
        officer_anchors = load_officer_anchors(args.word_inventory)
        DOMAIN_ANCHORS.update(officer_anchors)

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
