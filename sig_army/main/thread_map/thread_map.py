#!/usr/bin/env python3
"""
Thread Map — Conversation Topology Analyzer
Signal Army Ecosystem | Ello Cello LLC

Maps threads as nodes in a network — not a list.
Identifies:
  - Convergence: threads that share vocabulary / concept clusters
  - Divergence: threads that never reconnect (true dead-ends)
  - Stitching: a concept from thread A resurfaces in thread C (weeks later)
  - Drift events: commitment drops + recovery signature (short bursts after long decay)
  - Timeline arc: how the corpus moves through time as a connected graph

Input: flattened_messages.csv (from Signal Army)
       sigtoken_v2_summary.json (optional — enriches with commitment scores)

Output:
  - thread_nodes.csv     — one row per thread with metrics
  - thread_edges.csv     — pairwise similarity between threads (overlap score)
  - timeline.csv         — per-thread timeline sorted by first message
  - drift_events.csv     — identified drift+recovery signatures
  - thread_map_summary.txt

Usage:
    python thread_map.py --messages flattened_messages.csv
    python thread_map.py --messages flattened_messages.csv --sigtoken sigtoken_v2_summary.json
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

VERSION = "0.1-demo"


# ---------------------------------------------------------------------------
# Tokenizer (minimal — word-level only)
# ---------------------------------------------------------------------------

STOPWORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'so', 'if', 'of', 'in', 'on',
    'at', 'to', 'for', 'from', 'with', 'by', 'about', 'as', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'am', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can',
    'could', 'may', 'might', 'must', 'i', 'me', 'my', 'you', 'your',
    'he', 'him', 'his', 'she', 'her', 'it', 'its', 'we', 'us', 'our',
    'they', 'them', 'their', 'who', 'which', 'what', 'that', 'this',
    'these', 'those', 'into', 'through', 'after', 'before', 'during',
    'because', 'although', 'though', 'while', 'when', 'where', 'than',
    'also', 'too', 'then', 'now', 'here', 'there', 'some', 'any', 'all',
    'each', 'every', 'both', 'one', 'two', 'three', 'first', 'second',
    'just', 'like', 'okay', 'ok', 'yeah', 'lol', 'well', 'really',
    'basically', 'actually', 'so', 'right', 'sure', 'thing', 'things',
    'way', 'ways', 'lot', 'bit', 'kind', 'sort', 'stuff',
})

def tokenize(text):
    text = text.lower()
    text = re.sub(r'mo§es™?|moses™', 'moses', text)
    text = re.sub(r'mos²es|mos2es', 'mos2es', text)
    text = re.sub(r"[^\w\s]", ' ', text)
    tokens = [t for t in text.split() if len(t) > 2 and t not in STOPWORDS and not t.isdigit()]
    return tokens


# ---------------------------------------------------------------------------
# Load messages
# ---------------------------------------------------------------------------

def parse_timestamp(ts_str):
    """Parse ISO string or unix float to unix timestamp float. Returns 0 on failure."""
    if not ts_str:
        return 0
    try:
        return float(ts_str)
    except (ValueError, TypeError):
        pass
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f+00:00', '%Y-%m-%dT%H:%M:%S+00:00',
                '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d'):
        try:
            return datetime.strptime(ts_str[:len(fmt)+5], fmt).replace(
                tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    # Last resort: strip timezone and try
    try:
        clean = re.sub(r'[+-]\d{2}:\d{2}$', '', ts_str).rstrip('Z')
        return datetime.fromisoformat(clean).replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return 0


def load_messages(path):
    messages = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            content = row.get('message_text', row.get('content', ''))
            thread = row.get('conversation_title', row.get('title', row.get('thread', 'unknown')))
            role = row.get('role', 'unknown')
            # Support both 'timestamp' (Signal Army) and 'create_time' (raw JSON)
            raw_ts = row.get('timestamp', row.get('create_time', ''))
            ts = parse_timestamp(raw_ts)
            if content and content.strip():
                messages.append({
                    'content': content,
                    'thread': thread,
                    'role': role,
                    'create_time': ts,
                })
    return messages


# ---------------------------------------------------------------------------
# Build thread profiles
# ---------------------------------------------------------------------------

def build_thread_profiles(messages):
    """
    For each thread: collect all words, track message count,
    earliest/latest timestamp, and role breakdown.
    """
    threads = defaultdict(lambda: {
        'words': Counter(),
        'messages': [],
        'times': [],
        'roles': Counter(),
        'message_lengths': [],
    })

    for msg in messages:
        t = msg['thread']
        tokens = tokenize(msg['content'])
        threads[t]['words'].update(tokens)
        threads[t]['messages'].append(msg['content'])
        threads[t]['roles'][msg['role']] += 1
        threads[t]['message_lengths'].append(len(tokens))
        if msg['create_time']:
            threads[t]['times'].append(msg['create_time'])

    return threads


# ---------------------------------------------------------------------------
# Compute pairwise thread similarity (Jaccard on top-N vocabulary)
# ---------------------------------------------------------------------------

def compute_thread_similarity(thread_profiles, top_n=50, min_similarity=0.05):
    """
    For each pair of threads, compute vocabulary overlap.
    Uses top-N most frequent words per thread.
    Returns list of (thread_a, thread_b, similarity_score).
    """
    thread_names = list(thread_profiles.keys())
    thread_vocab = {}
    for name, data in thread_profiles.items():
        top_words = set(w for w, _ in data['words'].most_common(top_n))
        thread_vocab[name] = top_words

    edges = []
    n = len(thread_names)
    for i in range(n):
        for j in range(i + 1, n):
            a = thread_names[i]
            b = thread_names[j]
            va = thread_vocab[a]
            vb = thread_vocab[b]
            intersection = len(va & vb)
            union = len(va | vb)
            if union == 0:
                continue
            jaccard = intersection / union
            if jaccard >= min_similarity:
                edges.append({
                    'thread_a': a,
                    'thread_b': b,
                    'similarity': round(jaccard, 4),
                    'shared_words': intersection,
                    'shared_vocab': ', '.join(sorted(va & vb)[:10]),
                })

    edges.sort(key=lambda x: x['similarity'], reverse=True)
    return edges


# ---------------------------------------------------------------------------
# Identify concept stitching — same term appearing in threads far apart in time
# ---------------------------------------------------------------------------

def find_concept_stitching(thread_profiles, min_gap_days=7, top_concepts=20):
    """
    Find terms that appear across multiple threads separated by time.
    These are the stitching points — ideas that resurface.

    Only tracks words that are:
      - >= 4 characters (filters out short common words)
      - Not in STOPWORDS
      - Appear with meaningful frequency in their thread (count >= 2)
    """
    # Build: word -> list of (thread_name, earliest_time)
    word_threads = defaultdict(list)
    for name, data in thread_profiles.items():
        if not data['times']:
            continue
        earliest = min(data['times'])
        for word, count in data['words'].most_common(top_concepts):
            # Filter: domain-meaningful words only
            if len(word) < 4:
                continue
            if word in STOPWORDS:
                continue
            if count < 2:
                continue
            word_threads[word].append((name, earliest, count))

    stitches = []
    for word, appearances in word_threads.items():
        if len(appearances) < 2:
            continue
        appearances.sort(key=lambda x: x[1])
        # Check if any pair has a gap > min_gap_days
        for i in range(len(appearances)):
            for j in range(i + 1, len(appearances)):
                t1 = appearances[i][1]
                t2 = appearances[j][1]
                gap_days = (t2 - t1) / 86400
                if gap_days >= min_gap_days:
                    stitches.append({
                        'concept': word,
                        'thread_origin': appearances[i][0],
                        'thread_return': appearances[j][0],
                        'gap_days': round(gap_days, 1),
                        'origin_time': datetime.fromtimestamp(t1, tz=timezone.utc).strftime('%Y-%m-%d') if t1 else '',
                        'return_time': datetime.fromtimestamp(t2, tz=timezone.utc).strftime('%Y-%m-%d') if t2 else '',
                    })

    stitches.sort(key=lambda x: x['gap_days'], reverse=True)
    return stitches


# ---------------------------------------------------------------------------
# Drift detection
# Signature: several long messages → sudden drop in message length + freq increase
# Represents: system loses kernel, user sends short corrective bursts
# ---------------------------------------------------------------------------

def detect_drift_events(messages, window=5, short_threshold=8, long_threshold=30):
    """
    Drift signature:
      - A window of long user messages (avg tokens > long_threshold)
      - Followed by a burst of short user messages (avg tokens < short_threshold)
      - The burst = user recompressing/correcting

    Returns list of (thread, drift_start_index, recovery_start_index, context)
    """
    # Group by thread, keep order
    # Note: Signal Army user-only CSV has no role column — role reads as 'unknown'
    # Treat 'unknown' as user since this CSV only contains user messages
    thread_msgs = defaultdict(list)
    for i, msg in enumerate(messages):
        if msg['role'] in ('user', 'unknown'):
            tokens = tokenize(msg['content'])
            thread_msgs[msg['thread']].append({
                'idx': i,
                'length': len(tokens),
                'text': msg['content'][:80],
                'time': msg['create_time'],
            })

    drift_events = []
    for thread, msgs in thread_msgs.items():
        if len(msgs) < window * 2:
            continue

        for i in range(window, len(msgs) - window):
            # Look back window: avg length
            lookback = [m['length'] for m in msgs[max(0, i-window):i]]
            lookahead = [m['length'] for m in msgs[i:i+window]]

            avg_back = sum(lookback) / len(lookback)
            avg_ahead = sum(lookahead) / len(lookahead)

            # Drift: was long, became short AND frequency increases
            if avg_back >= long_threshold and avg_ahead <= short_threshold:
                drift_events.append({
                    'thread': thread,
                    'drift_position': i,
                    'avg_length_before': round(avg_back, 1),
                    'avg_length_after': round(avg_ahead, 1),
                    'compression_ratio': round(avg_back / max(avg_ahead, 1), 2),
                    'trigger_message': msgs[i]['text'],
                    'time': msgs[i].get('time', ''),
                })

    drift_events.sort(key=lambda x: x['compression_ratio'], reverse=True)
    return drift_events


# ---------------------------------------------------------------------------
# Timeline — per-thread sorted by earliest message
# ---------------------------------------------------------------------------

def build_timeline(thread_profiles):
    timeline = []
    for name, data in thread_profiles.items():
        if data['times']:
            earliest = min(data['times'])
            latest = max(data['times'])
            span_days = (latest - earliest) / 86400
        else:
            earliest = 0
            latest = 0
            span_days = 0

        msg_count = len(data['messages'])
        avg_len = sum(data['message_lengths']) / max(len(data['message_lengths']), 1)
        dominant_role = data['roles'].most_common(1)[0][0] if data['roles'] else 'unknown'

        timeline.append({
            'thread': name,
            'earliest': datetime.fromtimestamp(earliest, tz=timezone.utc).strftime('%Y-%m-%d') if earliest else '',
            'latest': datetime.fromtimestamp(latest, tz=timezone.utc).strftime('%Y-%m-%d') if latest else '',
            'span_days': round(span_days, 1),
            'message_count': msg_count,
            'avg_message_length': round(avg_len, 1),
            'dominant_role': dominant_role,
            'earliest_ts': earliest,
        })

    timeline.sort(key=lambda x: x['earliest_ts'])
    return timeline


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_outputs(thread_profiles, edges, stitches, drift_events, timeline, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
    run_dir = os.path.join(output_dir, f'run_{ts}')
    os.makedirs(run_dir, exist_ok=True)

    # Thread nodes
    nodes_path = os.path.join(run_dir, 'thread_nodes.csv')
    with open(nodes_path, 'w', newline='', encoding='utf-8') as f:
        fields = ['thread', 'earliest', 'latest', 'span_days', 'message_count',
                  'avg_message_length', 'dominant_role']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(timeline)

    # Thread edges (similarity)
    edges_path = os.path.join(run_dir, 'thread_edges.csv')
    with open(edges_path, 'w', newline='', encoding='utf-8') as f:
        if edges:
            writer = csv.DictWriter(f, fieldnames=list(edges[0].keys()))
            writer.writeheader()
            writer.writerows(edges[:500])  # top 500 strongest connections

    # Concept stitches
    stitches_path = os.path.join(run_dir, 'concept_stitches.csv')
    with open(stitches_path, 'w', newline='', encoding='utf-8') as f:
        if stitches:
            writer = csv.DictWriter(f, fieldnames=list(stitches[0].keys()))
            writer.writeheader()
            writer.writerows(stitches[:200])

    # Drift events
    drift_path = os.path.join(run_dir, 'drift_events.csv')
    with open(drift_path, 'w', newline='', encoding='utf-8') as f:
        if drift_events:
            writer = csv.DictWriter(f, fieldnames=list(drift_events[0].keys()))
            writer.writeheader()
            writer.writerows(drift_events[:100])

    # Timeline
    timeline_path = os.path.join(run_dir, 'timeline.csv')
    with open(timeline_path, 'w', newline='', encoding='utf-8') as f:
        if timeline:
            writer = csv.DictWriter(f, fieldnames=list(timeline[0].keys()))
            writer.writeheader()
            writer.writerows(timeline)

    # Summary text
    summary_lines = []
    summary_lines.append("=" * 64)
    summary_lines.append("  THREAD MAP — CONVERSATION TOPOLOGY ANALYZER")
    summary_lines.append(f"  v{VERSION} | Ello Cello LLC")
    summary_lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    summary_lines.append("=" * 64)
    summary_lines.append("")
    summary_lines.append(f"  Total Threads:         {len(thread_profiles):,}")
    summary_lines.append(f"  Thread Connections:    {len(edges):,}  (similarity ≥ 0.05)")
    summary_lines.append(f"  Concept Stitches:      {len(stitches):,}  (gap ≥ 7 days)")
    summary_lines.append(f"  Drift Events:          {len(drift_events):,}")
    summary_lines.append("")

    if timeline:
        first = timeline[0]
        last = timeline[-1]
        summary_lines.append(f"  Corpus start:          {first['earliest']}")
        summary_lines.append(f"  Corpus end:            {last['latest']}")
        summary_lines.append("")

    summary_lines.append("=" * 64)
    summary_lines.append("  TOP 20 STRONGEST THREAD CONNECTIONS")
    summary_lines.append("=" * 64)
    for e in edges[:20]:
        summary_lines.append(
            f"  [{e['similarity']:.3f}] {e['thread_a'][:30]:<30} ↔  {e['thread_b'][:30]}"
        )
        summary_lines.append(f"         shared: {e['shared_vocab'][:60]}")

    summary_lines.append("")
    summary_lines.append("=" * 64)
    summary_lines.append("  TOP 20 CONCEPT STITCHES (ideas that resurface)")
    summary_lines.append("=" * 64)
    for s in stitches[:20]:
        summary_lines.append(
            f"  [{s['gap_days']:>6.1f} days]  '{s['concept']}'  "
            f"{s['origin_time']} → {s['return_time']}"
        )
        summary_lines.append(
            f"    {s['thread_origin'][:35]:<35} → {s['thread_return'][:35]}"
        )

    summary_lines.append("")
    summary_lines.append("=" * 64)
    summary_lines.append("  TOP 15 DRIFT EVENTS (system loses kernel)")
    summary_lines.append("=" * 64)
    summary_lines.append("  Signature: long messages → sudden burst of short corrective messages")
    summary_lines.append("")
    for d in drift_events[:15]:
        summary_lines.append(
            f"  [{d['compression_ratio']:.1f}x compression drop]  {d['thread'][:40]}"
        )
        summary_lines.append(
            f"    avg before: {d['avg_length_before']} tokens  →  after: {d['avg_length_after']} tokens"
        )
        summary_lines.append(f"    trigger: \"{d['trigger_message'][:60]}\"")

    summary_lines.append("")
    summary_lines.append("=" * 64)
    summary_lines.append("  FILES SAVED")
    summary_lines.append("=" * 64)
    summary_lines.append(f"  thread_nodes.csv     — {len(timeline)} threads with timeline data")
    summary_lines.append(f"  thread_edges.csv     — {min(len(edges), 500)} strongest connections")
    summary_lines.append(f"  concept_stitches.csv — {min(len(stitches), 200)} concept stitches")
    summary_lines.append(f"  drift_events.csv     — {min(len(drift_events), 100)} drift events")
    summary_lines.append(f"  timeline.csv         — full chronological thread order")
    summary_lines.append("=" * 64)

    summary_text = '\n'.join(summary_lines)
    print(summary_text)

    with open(os.path.join(run_dir, 'thread_map_summary.txt'), 'w') as f:
        f.write(summary_text)

    print(f"\n  Output saved to: {run_dir}")
    return run_dir


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=f'Thread Map v{VERSION} — Conversation Topology Analyzer'
    )
    parser.add_argument('--messages', required=True, help='flattened_messages.csv from Signal Army')
    parser.add_argument('--output-dir', default='./runs', help='Output directory')
    parser.add_argument('--min-similarity', type=float, default=0.05,
                        help='Minimum Jaccard similarity for thread edges (default 0.05)')
    parser.add_argument('--min-gap-days', type=float, default=7,
                        help='Minimum days between thread appearances for stitch detection (default 7)')
    args = parser.parse_args()

    print(f"Loading messages from {args.messages}...")
    messages = load_messages(args.messages)
    print(f"  {len(messages):,} messages loaded.")

    print("Building thread profiles...")
    thread_profiles = build_thread_profiles(messages)
    print(f"  {len(thread_profiles):,} unique threads found.")

    print("Computing thread similarity network...")
    edges = compute_thread_similarity(
        thread_profiles,
        min_similarity=args.min_similarity
    )
    print(f"  {len(edges):,} connections found.")

    print("Finding concept stitches...")
    stitches = find_concept_stitching(
        thread_profiles,
        min_gap_days=args.min_gap_days
    )
    print(f"  {len(stitches):,} stitches found.")

    print("Detecting drift events...")
    drift_events = detect_drift_events(messages)
    print(f"  {len(drift_events):,} drift events found.")

    print("Building timeline...")
    timeline = build_timeline(thread_profiles)

    print("\nGenerating output...\n")
    save_outputs(thread_profiles, edges, stitches, drift_events, timeline, args.output_dir)


if __name__ == '__main__':
    main()
