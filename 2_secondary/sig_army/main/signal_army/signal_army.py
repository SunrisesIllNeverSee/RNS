#!/usr/bin/env python3
"""
Signal Army — Word Inventory & Force Ranking Tool
"Every Word a Soldier"

Parses ChatGPT conversation exports (JSON) and/or markdown transcripts,
inventories every word, ranks them by the Signal Army doctrine, and
produces CSV inventories + a HUD-style summary dashboard.

Usage:
    python signal_army.py --md GPT_72325_army.md
    python signal_army.py --md-dir ./transcripts/
    python signal_army.py --json ~/Downloads/conversations.json
    python signal_army.py --json conversations.json --md-dir ./transcripts/
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

# Handle large CSV fields (flattened_messages can contain entire transcripts)
csv.field_size_limit(10 * 1024 * 1024)  # 10 MB

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "1.5"

# Compound words that should not be split by special characters
COMPOUND_WORDS = {
    'mo§es': 'moses',
    'moses™': 'moses',
    'mo§es™': 'moses',
    'sigrank': 'sigrank',
}

# Infantry words — common English words that deploy constantly but carry
# no strategic signal on their own. They stay in the inventory (they ARE
# soldiers), but their rank is capped at Infantry regardless of frequency.
# Their value shows up in PHRASES, not as individual words.
INFANTRY_WORDS = frozenset({
    # Negation / affirmation
    'not', 'no', 'yes', 'never', 'none', 'nothing',
    # Interrogatives
    'how', 'why', 'what', 'where', 'when',
    # Common cognitive verbs
    'think', 'know', 'feel', 'want', 'need', 'believe', 'understand',
    'mean', 'thought', 'knew', 'felt', 'wanted', 'needed',
    # Common adjectives/adverbs that inflate
    'high', 'low', 'new', 'old', 'good', 'bad', 'big', 'small',
    'right', 'wrong', 'different', 'specific', 'real', 'true', 'full',
    'long', 'short', 'hard', 'easy', 'possible', 'important',
    'better', 'best', 'able', 'available', 'clear', 'sure', 'next',
    # Common action verbs that show up everywhere
    'use', 'used', 'using', 'work', 'working', 'works', 'worked',
    'run', 'running', 'runs', 'set', 'start', 'started', 'help',
    'try', 'tried', 'trying', 'show', 'shows', 'call', 'called',
    'move', 'change', 'find', 'found', 'create', 'created',
    'add', 'added', 'allows', 'allow', 'based', 'include', 'includes',
    'provide', 'provides', 'means', 'requires', 'support', 'supports',
    # Common nouns that appear in any topic
    'time', 'point', 'part', 'place', 'case', 'end', 'example',
    'fact', 'lot', 'kind', 'level', 'type', 'number', 'group',
    'form', 'result', 'process', 'information', 'line', 'name',
    'side', 'head', 'area', 'world', 'state', 'power', 'order',
    'problem', 'question', 'idea', 'issue', 'sense', 'step', 'key',
    'everything', 'something', 'anything', 'nothing', 'someone',
    # Discourse/structure words
    'actually', 'basically', 'simply', 'note', 'please', 'thank',
    'great', 'exactly', 'likely', 'essentially', 'especially',
})

# Curated stop words — common English function words that carry no signal.
# Intentionally KEEPS: not, no, never, why, how, want, need, feel, think, know
STOP_WORDS = frozenset({
    'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'yet', 'so', 'for',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'done',
    'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
    'i', 'me', 'my', 'mine', 'myself',
    'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself',
    'it', 'its', 'itself',
    'we', 'us', 'our', 'ours', 'ourselves',
    'they', 'them', 'their', 'theirs', 'themselves',
    'who', 'whom', 'whose', 'which', 'what',
    'that', 'this', 'these', 'those',
    'in', 'on', 'at', 'to', 'for', 'from', 'with', 'by', 'of', 'about',
    'into', 'through', 'between', 'after', 'before', 'during', 'without',
    'within', 'upon', 'above', 'below', 'under', 'over', 'against',
    'along', 'among', 'around', 'behind', 'beside', 'beyond', 'beneath',
    'despite', 'except', 'inside', 'outside', 'toward', 'towards',
    'until', 'unto', 'via', 'up', 'down', 'out', 'off',
    'because', 'although', 'though', 'while', 'if', 'when', 'where',
    'whether', 'unless', 'since', 'as', 'than', 'like',
    'very', 'really', 'just', 'also', 'too', 'quite', 'rather',
    'still', 'already', 'always', 'often', 'sometimes', 'ever',
    'even', 'only', 'then', 'now', 'here', 'there',
    'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither',
    'much', 'many', 'more', 'most', 'few', 'less', 'several',
    'such', 'own', 'other', 'another', 'else', 'same',
    'well', 'back', 'get', 'got', 'going', 'go', 'went', 'goes',
    'come', 'came', 'put', 'take', 'took', 'taken',
    'make', 'made', 'let', 'say', 'said', 'says',
    'tell', 'told', 'ask', 'asked',
    'see', 'saw', 'seen', 'look', 'looked',
    'give', 'gave', 'given',
    'been', 'being', 'become', 'became',
    'keep', 'kept',
    'thing', 'things',
    'way', 'ways',
    'one', 'two', 'three', 'first', 'second',
    'could', 'would', 'should',
    'may', 'might', 'must',
    "i'm", "i've", "i'll", "i'd",
    "it's", "that's", "there's", "here's",
    "don't", "doesn't", "didn't", "won't", "wouldn't", "shouldn't",
    "can't", "couldn't", "isn't", "aren't", "wasn't", "weren't",
    "haven't", "hasn't", "hadn't",
    "let's", "he's", "she's", "we're", "they're", "you're",
    "we've", "they've", "you've", "who's", "what's",
    'okay', 'ok', 'yeah', 'yes', 'oh', 'ah', 'um', 'uh', 'lol',
    'gonna', 'wanna', 'gotta',
    'etc', 'eg', 'ie',
})

# Rank thresholds: checked top-down, first match wins
RANK_THRESHOLDS = [
    (100, 1, 'Officer-Class'),
    (50,  1, 'Doctrine Builder'),
    (20,  2, 'Division'),       # 20+ AND multi-thread required
    (20,  1, 'Platoon'),        # 20+ but single thread
    (10,  1, 'Platoon'),
    (5,   1, 'Squad'),
    (2,   1, 'Fireteam'),
    (1,   1, 'Scout'),
]

# Infantry rank cap — max rank an infantry word can reach
INFANTRY_MAX_RANK = 'Infantry'

# Division clustering parameters
DIVISION_AFFINITY_THRESHOLD = 0.15   # min affinity score to join a division
MAX_DIVISION_SIZE = 10               # cap members per division
MIN_COOCCURRENCE = 3                 # min paragraph co-occurrences to count
PARAGRAPH_SPLIT = re.compile(r'\n\s*\n')  # double-newline paragraph breaks

DIVISION_SUFFIXES = [
    'Division', 'Corps', 'Command', 'Unit', 'Force',
    'Group', 'Brigade', 'Column',
]

# Ranks eligible for division clustering
CLUSTER_RANKS = frozenset({'Officer-Class', 'Doctrine Builder', 'Division'})


# Domain words that must NEVER be stemmed
NO_STEM = frozenset({
    'moses', 'moes', 'sigrank', 'fracto', 'abba', 'aaron', 'kleya',
    'luthen', 'nemik', 'hange', 'levi', 'zoran', 'keter',
    'analysis', 'basis', 'thesis', 'genesis', 'axis',
    'coherence', 'governance', 'compliance', 'insurance', 'convergence',
    'class', 'process', 'address', 'access', 'success', 'stress',
})


def stem_word(word):
    """Lightweight English stemmer — collapses plurals, possessives,
    and common suffixes into root form. No external libraries needed.
    Preserves domain terms by only applying safe, reversible rules."""
    # Protected words — never stem these
    if word in NO_STEM:
        return word
    # Don't stem very short words
    if len(word) <= 3:
        return word

    # Possessives: system's -> system
    if word.endswith("'s"):
        return word[:-2]
    if word.endswith("s'"):
        return word[:-1]

    # -ing: building -> build (but not 'ring', 'king', 'thing')
    if word.endswith('ing') and len(word) > 5:
        base = word[:-3]
        # Handle doubled consonant: running -> run
        if len(base) >= 2 and base[-1] == base[-2]:
            return base[:-1]
        return base

    # -tion / -sion: keep as-is (these are distinct words: compression, conservation)

    # -ly: recursively -> recursive (but not 'fly', 'rely')
    if word.endswith('ly') and len(word) > 4:
        return word[:-2]

    # -ed: worked -> work (but not 'red', 'bed', 'forged')
    if word.endswith('ed') and len(word) > 4:
        base = word[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            return base[:-1]
        # created -> create
        if word.endswith('ated') and len(word) > 5:
            return word[:-1]  # drop the d, keep 'e' -> create
        return base

    # Plural -s: systems -> system (but not 'analysis', 'moses', 'fractos')
    if word.endswith('s') and not word.endswith('ss') and len(word) > 3:
        # -ies -> -y: economies -> economy
        if word.endswith('ies') and len(word) > 4:
            return word[:-3] + 'y'
        # -es: gates -> gate, phases -> phase
        if word.endswith('es') and len(word) > 4:
            # Don't strip 'es' from words where it's part of the root
            # (moses, phases ending in -ses, -xes, -zes, -ches, -shes)
            if word.endswith(('ses', 'xes', 'zes', 'ches', 'shes')):
                return word[:-2]
            return word[:-1]  # gates -> gate
        # Simple -s: tokens -> token, signals -> signal
        if not word.endswith(('us', 'is', 'ss')):
            return word[:-1]

    return word

# Role markers for structured markdown detection
ROLE_PATTERN = re.compile(
    r'^\*\*(?:User|You):\*\*',
    re.MULTILINE | re.IGNORECASE
)
GPT_ROLE_PATTERN = re.compile(
    r'^\*\*(?:GPT|Grok|Claude|DeepSeek|Gemini|Assistant)\s*(?:\([^)]*\))?:\*\*',
    re.MULTILINE | re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Markdown Parser
# ---------------------------------------------------------------------------

class MarkdownParser:
    """Parses markdown transcript files to extract user messages."""

    def __init__(self, md_paths, md_mode='detect'):
        self.md_paths = md_paths
        self.md_mode = md_mode
        self.warnings = []

    def parse_all(self):
        """Parse all .md files. Returns list of message dicts."""
        all_messages = []
        msg_number = 0

        for path in self.md_paths:
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except OSError as e:
                self.warnings.append(f"Could not read {path}: {e}")
                continue

            title = os.path.splitext(os.path.basename(path))[0]
            mtime = os.path.getmtime(path)
            timestamp = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

            if self.md_mode == 'detect':
                user_matches = len(ROLE_PATTERN.findall(content))
                if user_matches >= 3:
                    messages = self._parse_structured(content, title, timestamp)
                else:
                    self.warnings.append(
                        f"{title}: No role markers detected, treating entire file as user text"
                    )
                    messages = self._parse_as_whole(content, title, timestamp)
            else:  # user-only
                messages = self._parse_as_whole(content, title, timestamp)

            for msg in messages:
                msg_number += 1
                msg['message_number'] = msg_number
                all_messages.append(msg)

        return all_messages

    def _parse_structured(self, content, title, timestamp):
        """Extract text between **User:** markers and the next role marker."""
        messages = []
        # Find all role markers (user and GPT) with their positions
        all_markers = []
        for m in ROLE_PATTERN.finditer(content):
            all_markers.append(('user', m.start(), m.end()))
        for m in GPT_ROLE_PATTERN.finditer(content):
            all_markers.append(('gpt', m.start(), m.end()))

        # Sort by position
        all_markers.sort(key=lambda x: x[1])

        for i, (role, start, end) in enumerate(all_markers):
            if role != 'user':
                continue
            # Text runs from end of this marker to start of next marker (or EOF)
            if i + 1 < len(all_markers):
                text_end = all_markers[i + 1][1]
            else:
                text_end = len(content)

            text = content[end:text_end].strip()
            # Clean up markdown artifacts
            text = self._clean_md(text)
            if text:
                messages.append({
                    'message_text': text,
                    'conversation_title': title,
                    'timestamp': timestamp,
                })
        return messages

    def _parse_as_whole(self, content, title, timestamp):
        """Treat entire file content as user text."""
        text = self._clean_md(content)
        if not text:
            return []
        return [{
            'message_text': text,
            'conversation_title': title,
            'timestamp': timestamp,
        }]

    def _clean_md(self, text):
        """Remove markdown formatting artifacts."""
        # Remove horizontal rules
        text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
        # Remove code fences (but keep content inside)
        text = re.sub(r'```[a-z]*\n?', '', text)
        # Remove bold/italic markers
        text = re.sub(r'\*{1,3}', '', text)
        # Remove heading markers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove markdown table pipes (keep cell content)
        text = re.sub(r'\|', ' ', text)
        # Remove image/link syntax but keep text
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        # Collapse whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


# ---------------------------------------------------------------------------
# JSON Flattener (ChatGPT conversations.json)
# ---------------------------------------------------------------------------

class ConversationFlattener:
    """Reads conversations.json and walks message trees to extract
    ordered user messages."""

    def __init__(self, json_path, target_role='user'):
        self.json_path = json_path
        self.target_role = target_role
        self.warnings = []

    def flatten_all(self):
        """Process all conversations. Returns list of message dicts."""
        print(f"  Loading {self.json_path}...")
        try:
            with open(self.json_path, 'r', encoding='utf-8', errors='replace') as f:
                conversations = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: JSON parse failed at byte {e.pos}: {e.msg}", file=sys.stderr)
            return []
        except OSError as e:
            print(f"  ERROR: Could not read file: {e}", file=sys.stderr)
            return []

        if not isinstance(conversations, list):
            print("  ERROR: Expected a JSON array at top level", file=sys.stderr)
            return []

        total = len(conversations)
        print(f"  Found {total} conversations")

        all_messages = []
        msg_number = 0
        skipped = 0

        for idx, convo in enumerate(conversations, 1):
            if idx % 50 == 0 or idx == total:
                print(f"  [{idx}/{total}] conversations processed", end='\r')

            title = convo.get('title') or f"Untitled_{idx}"
            create_time = convo.get('create_time')
            mapping = convo.get('mapping')

            if not mapping or not isinstance(mapping, dict):
                skipped += 1
                self.warnings.append(f"Skipping '{title}': no mapping")
                continue

            # Walk the message tree
            ordered = self._walk_tree(mapping)

            for message in ordered:
                author = message.get('author', {})
                role = author.get('role', '')
                if self.target_role and role != self.target_role:
                    continue

                text = self._extract_text(message)
                if not text:
                    continue

                msg_time = message.get('create_time')
                if msg_time:
                    ts = datetime.fromtimestamp(msg_time, tz=timezone.utc).isoformat()
                elif create_time:
                    ts = datetime.fromtimestamp(create_time, tz=timezone.utc).isoformat()
                else:
                    ts = ''

                msg_number += 1
                all_messages.append({
                    'message_number': msg_number,
                    'message_text': text,
                    'conversation_title': title,
                    'timestamp': ts,
                })

        print(f"\n  Extracted {msg_number} user messages ({skipped} conversations skipped)")
        return all_messages

    def _walk_tree(self, mapping):
        """Walk conversation tree in order, following last child at branches."""
        # Find root node (parent is None)
        root_id = None
        for node_id, node in mapping.items():
            if node.get('parent') is None:
                root_id = node_id
                break

        if root_id is None:
            # Fallback: find node whose parent isn't in mapping
            all_ids = set(mapping.keys())
            for node_id, node in mapping.items():
                if node.get('parent') not in all_ids:
                    root_id = node_id
                    break

        if root_id is None:
            return []

        # Iterative walk: follow last child at each step
        ordered = []
        current = root_id
        visited = set()

        while current and current not in visited:
            visited.add(current)
            node = mapping.get(current)
            if node is None:
                break

            message = node.get('message')
            if message is not None:
                ordered.append(message)

            children = node.get('children', [])
            if children:
                current = children[-1]  # Last child = final version
            else:
                current = None

        return ordered

    def _extract_text(self, message):
        """Safely extract text from a message object."""
        if message is None:
            return None
        content = message.get('content')
        if content is None:
            return None
        parts = content.get('parts')
        if not parts:
            return None
        text_parts = [str(p) for p in parts if isinstance(p, str)]
        if not text_parts:
            return None
        text = ' '.join(text_parts).strip()
        return text if text else None


# ---------------------------------------------------------------------------
# Signal Army Analyzer
# ---------------------------------------------------------------------------

class SignalArmyAnalyzer:
    """Tokenizes, counts, and ranks words + phrases by Signal Army doctrine."""

    def __init__(self, messages):
        self.messages = messages  # list of message dicts

    def _tokenize(self, text):
        """Tokenize text: lowercase, strip punctuation, stem, split."""
        text = text.lower()
        # Normalize compound words BEFORE stripping special chars
        for pattern, replacement in COMPOUND_WORDS.items():
            text = text.replace(pattern, replacement)
        # Replace special chars with space, but keep hyphens and apostrophes within words
        text = re.sub(r"[^\w\s'\-]", ' ', text)
        # Split
        tokens = text.split()
        # Clean each token
        cleaned = []
        for t in tokens:
            # Strip leading/trailing punctuation
            t = t.strip("'-_")
            # Skip empty, pure numeric, single char (except meaningful ones)
            if not t:
                continue
            if t.isdigit():
                continue
            if len(t) == 1 and t not in ('i', 'a'):
                continue
            # Stem: collapse plurals, possessives, -ing, -ed into root
            t = stem_word(t)
            if t:  # stem might return empty on edge cases
                cleaned.append(t)
        return cleaned

    def _tokenize_paragraphs(self, text):
        """Split text into paragraphs and tokenize each one.
        Returns list of frozensets of non-stop tokens per paragraph.
        Used for co-occurrence analysis at paragraph granularity
        (messages are entire transcripts — too coarse for clustering)."""
        paragraphs = PARAGRAPH_SPLIT.split(text)
        result = []
        for para in paragraphs:
            para = para.strip()
            if len(para) < 20:
                continue
            tokens = self._tokenize(para)
            token_set = frozenset(t for t in tokens if t not in STOP_WORDS)
            if len(token_set) >= 2:
                result.append(token_set)
        return result

    def build_word_inventory(self):
        """Count every non-stop word across all messages.
        Returns dict with word data, sorted by count descending."""
        word_counts = Counter()
        word_threads = defaultdict(set)
        word_first_seen = {}
        word_first_convo = {}

        for msg in self.messages:
            text = msg.get('message_text', '')
            title = msg.get('conversation_title', 'Unknown')
            ts = msg.get('timestamp', '')
            tokens = self._tokenize(text)

            for token in tokens:
                if token in STOP_WORDS:
                    continue
                word_counts[token] += 1
                word_threads[token].add(title)
                if token not in word_first_seen:
                    word_first_seen[token] = ts
                    word_first_convo[token] = title

        # Build sorted inventory
        inventory = []
        for word, count in word_counts.most_common():
            thread_count = len(word_threads[word])
            is_infantry = word in INFANTRY_WORDS
            rank = INFANTRY_MAX_RANK if is_infantry else self._assign_rank(count, thread_count)
            inventory.append({
                'Word': word,
                'Count': count,
                'Threads_Appeared_In': thread_count,
                'Thread_Names': ';'.join(sorted(word_threads[word])),
                'Token_Weight': round(len(word) / 4.0, 1),
                'Rank': rank,
                'First_Appearance': word_first_seen.get(word, ''),
                'First_Conversation': word_first_convo.get(word, ''),
            })

        return inventory

    def build_infantry_context(self, top_n=20):
        """For the top infantry words, find what they connect to.
        E.g., 'not' -> ['not ready', 'not possible', 'not just'].
        Returns dict: {infantry_word: [(phrase, count), ...]}"""
        # Collect bigrams where one word is infantry
        infantry_phrases = defaultdict(Counter)

        for msg in self.messages:
            text = msg.get('message_text', '')
            tokens = self._tokenize(text)

            for i in range(len(tokens) - 1):
                w1, w2 = tokens[i], tokens[i + 1]
                if w1 in INFANTRY_WORDS and w2 not in STOP_WORDS and w2 not in INFANTRY_WORDS:
                    infantry_phrases[w1][f"{w1} {w2}"] += 1
                if w2 in INFANTRY_WORDS and w1 not in STOP_WORDS and w1 not in INFANTRY_WORDS:
                    infantry_phrases[w2][f"{w1} {w2}"] += 1

        # Return top phrases per infantry word
        result = {}
        for word, phrases in infantry_phrases.items():
            top = phrases.most_common(5)
            if top:
                result[word] = top
        return result

    def build_phrase_inventory(self, min_count=2):
        """Extract 2-gram and 3-gram phrases. Returns sorted list of dicts."""
        bigram_counts = Counter()
        trigram_counts = Counter()
        phrase_threads = defaultdict(set)

        for msg in self.messages:
            text = msg.get('message_text', '')
            title = msg.get('conversation_title', 'Unknown')
            tokens = self._tokenize(text)

            # Build n-grams
            for i in range(len(tokens) - 1):
                bigram = f"{tokens[i]} {tokens[i+1]}"
                # Skip if both words are stop words
                if tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS:
                    bigram_counts[bigram] += 1
                    phrase_threads[bigram].add(title)

            for i in range(len(tokens) - 2):
                trigram = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                non_stop = sum(1 for t in [tokens[i], tokens[i+1], tokens[i+2]]
                               if t not in STOP_WORDS)
                if non_stop >= 2:  # At least 2 non-stop words
                    trigram_counts[trigram] += 1
                    phrase_threads[trigram].add(title)

        # Combine and filter
        all_phrases = {}
        for phrase, count in bigram_counts.items():
            if count >= min_count:
                all_phrases[phrase] = count
        for phrase, count in trigram_counts.items():
            if count >= min_count:
                all_phrases[phrase] = count

        # Sort by count
        inventory = []
        for phrase, count in sorted(all_phrases.items(), key=lambda x: -x[1]):
            thread_count = len(phrase_threads[phrase])
            inventory.append({
                'Phrase': phrase,
                'Count': count,
                'Threads_Appeared_In': thread_count,
                'Thread_Names': ';'.join(sorted(phrase_threads[phrase])),
                'Rank': self._assign_rank(count, thread_count),
            })

        return inventory

    def build_division_clusters(self, word_inventory):
        """Cluster high-signal words into thematic Divisions using
        paragraph-level co-occurrence affinity.

        Algorithm:
        1. Identify candidates (Division rank and above, excluding Infantry)
        2. Split all messages into paragraphs, tokenize each
        3. Count pairwise co-occurrence among candidates within paragraphs
        4. Compute affinity = co_count / min(para_count_w1, para_count_w2)
        5. Greedy seed-based clustering: Officers seed first, pull in neighbors

        Returns list of division dicts sorted by total strength descending.
        """
        # Build lookups from inventory
        word_rank = {}
        word_count = {}
        word_thread_names = {}
        for w in word_inventory:
            word_rank[w['Word']] = w['Rank']
            word_count[w['Word']] = w['Count']
            word_thread_names[w['Word']] = w.get('Thread_Names', '')

        # Candidates: Division+ rank, not infantry
        candidates = frozenset(
            w for w, r in word_rank.items()
            if r in CLUSTER_RANKS and w not in INFANTRY_WORDS
        )

        if not candidates:
            return []

        # Build paragraph token sets from all messages
        all_paragraphs = []
        for msg in self.messages:
            text = msg.get('message_text', '')
            title = msg.get('conversation_title', 'Unknown')
            para_sets = self._tokenize_paragraphs(text)
            for pset in para_sets:
                all_paragraphs.append((title, pset))

        # Count paragraphs containing each candidate
        word_para_count = Counter()
        for _title, pset in all_paragraphs:
            for word in pset:
                if word in candidates:
                    word_para_count[word] += 1

        # Count pairwise co-occurrences within paragraphs
        cooccur = Counter()
        for _title, pset in all_paragraphs:
            present = sorted(pset & candidates)
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    cooccur[(present[i], present[j])] += 1

        # Compute affinity scores (only keep strong pairs)
        affinity = {}
        for (w1, w2), co_count in cooccur.items():
            if co_count < MIN_COOCCURRENCE:
                continue
            min_para = min(word_para_count.get(w1, 0), word_para_count.get(w2, 0))
            if min_para == 0:
                continue
            aff = co_count / min_para
            if aff >= DIVISION_AFFINITY_THRESHOLD:
                affinity[(w1, w2)] = aff

        # Build neighbor lists sorted by affinity
        neighbors = defaultdict(list)
        for (w1, w2), aff in affinity.items():
            neighbors[w1].append((w2, aff))
            neighbors[w2].append((w1, aff))
        for word in neighbors:
            neighbors[word].sort(key=lambda x: -x[1])

        # Seed order: Officers first, then Doctrine Builders, then Division-rank
        rank_priority = {'Officer-Class': 0, 'Doctrine Builder': 1, 'Division': 2}
        seed_order = sorted(
            candidates,
            key=lambda w: (rank_priority.get(word_rank.get(w, ''), 99),
                           -word_count.get(w, 0))
        )

        # Greedy clustering
        assigned = set()
        divisions = []
        suffix_idx = 0

        for seed in seed_order:
            if seed in assigned:
                continue

            members = [seed]
            assigned.add(seed)

            # Pull in unassigned neighbors by affinity
            for neighbor, _aff in neighbors.get(seed, []):
                if neighbor in assigned:
                    continue
                if len(members) >= MAX_DIVISION_SIZE:
                    break
                members.append(neighbor)
                assigned.add(neighbor)

            # Solo words don't form divisions — leave them unattached
            if len(members) < 2:
                assigned.discard(seed)
                continue

            # Name: top 2 words by frequency + rotating suffix
            name_words = sorted(members, key=lambda w: -word_count.get(w, 0))[:2]
            suffix = DIVISION_SUFFIXES[suffix_idx % len(DIVISION_SUFFIXES)]
            suffix_idx += 1
            div_name = '-'.join(w.capitalize() for w in name_words) + ' ' + suffix

            # Stats
            total_strength = sum(word_count.get(w, 0) for w in members)
            threads_spanned = set()
            for w in members:
                tnames = word_thread_names.get(w, '')
                if tnames:
                    threads_spanned.update(tnames.split(';'))

            divisions.append({
                'Division_Name': div_name,
                'Commander': seed,
                'Commander_Rank': word_rank.get(seed, ''),
                'Member_Count': len(members),
                'Members': ';'.join(members),
                'Total_Strength': total_strength,
                'Threads_Spanned': len(threads_spanned),
                'Thread_Names': ';'.join(sorted(threads_spanned)),
            })

        divisions.sort(key=lambda d: -d['Total_Strength'])
        return divisions

    def _assign_rank(self, count, thread_count):
        """Apply Signal Army rank system."""
        for min_count, min_threads, rank in RANK_THRESHOLDS:
            if count >= min_count and thread_count >= min_threads:
                return rank
        return 'Scout'


# ---------------------------------------------------------------------------
# SIGSYSTEM Integration
# ---------------------------------------------------------------------------

def find_latest_sigsystem_run():
    """Auto-detect the latest SIGSYSTEM run directory.
    Looks for ../sigsystem/runs/ relative to this script's location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sigsystem_runs = os.path.join(script_dir, '..', 'sigsystem', 'runs')
    sigsystem_runs = os.path.normpath(sigsystem_runs)

    if not os.path.isdir(sigsystem_runs):
        return None

    # Find the latest run_* directory by name (timestamped, so sort works)
    run_dirs = sorted(
        [d for d in os.listdir(sigsystem_runs)
         if d.startswith('run_') and os.path.isdir(os.path.join(sigsystem_runs, d))],
        reverse=True
    )
    if run_dirs:
        return os.path.join(sigsystem_runs, run_dirs[0])
    return None


def load_sigsystem_data(sigsystem_dir):
    """Load SIGSYSTEM run data to enrich Signal Army output.
    Returns (word_scores dict, thread_snr list) or (None, None)."""
    word_scores_path = os.path.join(sigsystem_dir, 'sigsystem_word_scores.csv')
    thread_snr_path = os.path.join(sigsystem_dir, 'sigsystem_thread_snr.csv')

    word_scores = {}
    thread_snr = []

    if os.path.isfile(word_scores_path):
        with open(word_scores_path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                word_scores[row['Word']] = {
                    'signal_weight': float(row.get('Signal_Weight', 0)),
                    'noise_weight': float(row.get('Noise_Weight', 0)),
                    'classification': row.get('Classification', ''),
                    'necessity': float(row.get('Necessity_Score', 0)),
                    'trajectory': row.get('Trajectory', ''),
                    'decay_score': float(row.get('Decay_Score', 0)),
                }

    if os.path.isfile(thread_snr_path):
        with open(thread_snr_path, 'r', encoding='utf-8') as f:
            thread_snr = list(csv.DictReader(f))

    if word_scores:
        print(f'  SIGSYSTEM: loaded {len(word_scores)} word scores, '
              f'{len(thread_snr)} thread SNR entries')
        return word_scores, thread_snr
    else:
        return None, None


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generates CSV inventories and HUD-style summary dashboard."""

    def __init__(self, word_inventory, phrase_inventory, messages, output_dir,
                 infantry_context=None, division_clusters=None,
                 sigsystem_scores=None, sigsystem_thread_snr=None):
        self.words = word_inventory
        self.phrases = phrase_inventory
        self.messages = messages
        self.output_dir = output_dir
        self.infantry_context = infantry_context or {}
        self.division_clusters = division_clusters or []
        self.sigsystem = sigsystem_scores      # dict: word -> {...}
        self.sigsystem_threads = sigsystem_thread_snr or []

    def save_word_inventory(self):
        """Write word_inventory.csv. If SIGSYSTEM data is loaded,
        adds Signal_Weight, Noise_Weight, Classification, Necessity, Trajectory."""
        path = os.path.join(self.output_dir, 'word_inventory.csv')
        if not self.words:
            print("  No words to write.")
            return path

        fieldnames = ['Word', 'Count', 'Threads_Appeared_In', 'Thread_Names',
                      'Token_Weight', 'Rank', 'First_Appearance', 'First_Conversation']

        if self.sigsystem:
            fieldnames.extend(['Signal_Weight', 'Noise_Weight', 'Classification',
                               'Necessity', 'Trajectory'])
            # Enrich word data with SIGSYSTEM scores
            for w in self.words:
                ss = self.sigsystem.get(w['Word'], {})
                w['Signal_Weight'] = ss.get('signal_weight', '')
                w['Noise_Weight'] = ss.get('noise_weight', '')
                w['Classification'] = ss.get('classification', '')
                w['Necessity'] = ss.get('necessity', '')
                w['Trajectory'] = ss.get('trajectory', '')

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.words)

        label = f"{len(self.words)} entries"
        if self.sigsystem:
            label += " (SIGSYSTEM enriched)"
        print(f"  word_inventory.csv      -- {label}")
        return path

    def save_phrase_inventory(self):
        """Write phrase_inventory.csv."""
        path = os.path.join(self.output_dir, 'phrase_inventory.csv')
        if not self.phrases:
            print("  No phrases to write.")
            return path
        fieldnames = ['Phrase', 'Count', 'Threads_Appeared_In', 'Thread_Names', 'Rank']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.phrases)
        print(f"  phrase_inventory.csv    -- {len(self.phrases)} entries")
        return path

    def save_division_inventory(self):
        """Write division_inventory.csv."""
        path = os.path.join(self.output_dir, 'division_inventory.csv')
        if not self.division_clusters:
            print("  No divisions to write.")
            return path
        fieldnames = [
            'Division_Name', 'Commander', 'Commander_Rank', 'Member_Count',
            'Members', 'Total_Strength', 'Threads_Spanned', 'Thread_Names'
        ]
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.division_clusters)
        print(f"  division_inventory.csv  -- {len(self.division_clusters)} divisions")
        return path

    def save_flattened_messages(self):
        """Write flattened_messages.csv."""
        path = os.path.join(self.output_dir, 'flattened_messages.csv')
        if not self.messages:
            return path
        fieldnames = ['message_number', 'conversation_title', 'timestamp', 'message_text']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for msg in self.messages:
                writer.writerow({k: msg.get(k, '') for k in fieldnames})
        print(f"  flattened_messages.csv  -- {len(self.messages)} messages")
        return path

    def generate_summary(self):
        """Build and write signal_army_summary.txt dashboard."""
        # Calculate stats
        total_words_deployed = sum(w['Count'] for w in self.words)
        total_unique = len(self.words)
        total_messages = len(self.messages)
        convos = set(m.get('conversation_title', '') for m in self.messages)
        total_convos = len(convos)
        total_token_mass = sum(w['Count'] * w['Token_Weight'] for w in self.words)

        # Rank distribution
        rank_dist = Counter()
        for w in self.words:
            rank_dist[w['Rank']] += 1

        rank_order = [
            'Officer-Class', 'Doctrine Builder', 'Division',
            'Platoon', 'Squad', 'Fireteam', 'Scout', 'Infantry'
        ]

        # Top words per rank tier (show the actual roster)
        officers = [w for w in self.words if w['Rank'] == 'Officer-Class'][:20]
        doctrine = [w for w in self.words if w['Rank'] == 'Doctrine Builder'][:15]
        platoons = [w for w in self.words if w['Rank'] == 'Platoon'][:15]
        squads = [w for w in self.words if w['Rank'] == 'Squad'][:15]
        infantry = [w for w in self.words if w['Rank'] == 'Infantry']

        # Top phrases
        top_phrases = self.phrases[:10]

        # Build report
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = []
        lines.append('=' * 64)
        lines.append('  SIGNAL ARMY -- FORCE INVENTORY REPORT')
        lines.append('  Operation: SIGNAL FORCE | Phase Zero Inventory')
        lines.append('=' * 64)
        lines.append(f'  Generated:  {now}')
        lines.append(f'  Parser:     signal_army.py v{VERSION}')
        lines.append('')
        lines.append('=' * 64)
        lines.append('  FORCE OVERVIEW')
        lines.append('=' * 64)
        lines.append(f'  Total Words Deployed:        {total_words_deployed:,}')
        lines.append(f'  Total Unique Words:          {total_unique:,}')
        lines.append(f'  Total Messages Scanned:      {total_messages:,}')
        lines.append(f'  Total Conversations:         {total_convos:,}')
        lines.append(f'  Estimated Total Token Mass:  {total_token_mass:,.1f}')
        lines.append('')
        lines.append('=' * 64)
        lines.append('  RANK DISTRIBUTION')
        lines.append('=' * 64)
        for rank in rank_order:
            count = rank_dist.get(rank, 0)
            pct = (count / total_unique * 100) if total_unique else 0
            lines.append(f'  {rank:<20s}  {count:>6,} words   ({pct:>5.1f}%)')
        lines.append('')

        if officers:
            lines.append('=' * 64)
            lines.append('  OFFICER-CLASS (100+ deployments)')
            lines.append('=' * 64)
            for i, w in enumerate(officers, 1):
                lines.append(
                    f'  {i:>2}. {w["Word"]:<20s} -- {w["Count"]:>5,} deployments '
                    f'across {w["Threads_Appeared_In"]} thread(s)'
                )
            lines.append('')

        if doctrine:
            lines.append('=' * 64)
            lines.append('  DOCTRINE BUILDERS (50-99 deployments)')
            lines.append('=' * 64)
            for i, w in enumerate(doctrine, 1):
                lines.append(
                    f'  {i:>2}. {w["Word"]:<20s} -- {w["Count"]:>5,} deployments '
                    f'across {w["Threads_Appeared_In"]} thread(s)'
                )
            lines.append('')

        if platoons:
            lines.append('=' * 64)
            lines.append('  PLATOON LEADERS (10-49 deployments)')
            lines.append('=' * 64)
            for i, w in enumerate(platoons, 1):
                lines.append(
                    f'  {i:>2}. {w["Word"]:<20s} -- {w["Count"]:>5,} deployments '
                    f'across {w["Threads_Appeared_In"]} thread(s)'
                )
            lines.append('')

        if squads:
            lines.append('=' * 64)
            lines.append('  SQUAD LEADERS (5-9 deployments)')
            lines.append('=' * 64)
            for i, w in enumerate(squads, 1):
                lines.append(
                    f'  {i:>2}. {w["Word"]:<20s} -- {w["Count"]:>5,} deployments '
                    f'across {w["Threads_Appeared_In"]} thread(s)'
                )
            lines.append('')

        if infantry:
            lines.append('=' * 64)
            lines.append(f'  INFANTRY ({len(infantry)} privates — rank-capped, '
                         f'never promoted)')
            lines.append('  "Noise isn\'t failure — it\'s the infantry."')
            lines.append('=' * 64)
            top_infantry = sorted(infantry, key=lambda w: -w['Count'])[:20]
            for i, w in enumerate(top_infantry, 1):
                lines.append(
                    f'  {i:>2}. {w["Word"]:<20s} -- {w["Count"]:>5,} deployments '
                    f'across {w["Threads_Appeared_In"]} thread(s)'
                )
            # Show what infantry words connect to
            if self.infantry_context:
                lines.append('')
                lines.append('  INFANTRY FIELD CONNECTIONS (what they march with):')
                lines.append('  ' + '-' * 50)
                shown = 0
                for word in sorted(self.infantry_context.keys()):
                    phrases = self.infantry_context[word]
                    if not phrases:
                        continue
                    phrase_str = ', '.join(
                        f'"{p}" ({c})' for p, c in phrases[:4]
                    )
                    lines.append(f'  {word:<12s} -> {phrase_str}')
                    shown += 1
                    if shown >= 15:
                        break
            lines.append('')

        if self.division_clusters:
            lines.append('=' * 64)
            lines.append(f'  THEMATIC DIVISIONS ({len(self.division_clusters)} formed)')
            lines.append('  "Themes are divisions -- strategic units with')
            lines.append('   command power."')
            lines.append('=' * 64)
            for i, div in enumerate(self.division_clusters[:20], 1):
                members_list = div['Members'].split(';')
                commander = div['Commander']
                others = [m for m in members_list if m != commander]
                member_display = ', '.join(others[:8])
                if len(others) > 8:
                    member_display += f', +{len(others) - 8} more'
                lines.append(
                    f'  {i:>2}. {div["Division_Name"]}'
                )
                lines.append(
                    f'      Commander: {commander}  |  '
                    f'Strength: {div["Total_Strength"]:,}  |  '
                    f'{div["Member_Count"]} members  |  '
                    f'{div["Threads_Spanned"]} threads'
                )
                lines.append(
                    f'      Troops: {member_display}'
                )
                lines.append('')

        if top_phrases:
            lines.append('=' * 64)
            lines.append('  TOP 10 TACTICAL PHRASES (recurring n-grams)')
            lines.append('=' * 64)
            for i, p in enumerate(top_phrases, 1):
                lines.append(
                    f'  {i:>2}. "{p["Phrase"]:<30s}" -- {p["Count"]:>4} uses '
                    f'across {p["Threads_Appeared_In"]} thread(s)'
                )
            lines.append('')

        # SIGSYSTEM integration section
        if self.sigsystem:
            lines.append('=' * 64)
            lines.append('  SIGSYSTEM INTEL (Signal Classification Layer)')
            lines.append('=' * 64)

            # Signal/Noise breakdown
            sig_words = [w for w in self.words if w.get('Classification') == 'SIGNAL']
            noi_words = [w for w in self.words if w.get('Classification') == 'NOISE']
            lines.append(f'  Words classified as SIGNAL:  {len(sig_words):,}')
            lines.append(f'  Words classified as NOISE:   {len(noi_words):,}')
            lines.append('')

            # Trajectory breakdown
            traj_counts = Counter(w.get('Trajectory', '') for w in self.words
                                  if w.get('Trajectory'))
            lines.append('  Signal Trajectories:')
            for traj in ['RISING', 'STABLE', 'DECLINING', 'SPARSE']:
                lines.append(f'    {traj:<12s}  {traj_counts.get(traj, 0):>5,} words')
            lines.append('')

            # Officer-class intel: show trajectory + necessity for top officers
            sig_officers = [w for w in self.words
                            if w.get('Rank') == 'Officer-Class'
                            and w.get('Classification') == 'SIGNAL']
            if sig_officers:
                lines.append('  OFFICER INTEL (signal weight + necessity + trajectory):')
                lines.append('  ' + '-' * 56)
                for w in sig_officers[:15]:
                    sw = w.get('Signal_Weight', '')
                    nec = w.get('Necessity', '')
                    traj = w.get('Trajectory', '')
                    sw_str = f'{float(sw):.3f}' if sw else '  --'
                    nec_str = f'{float(nec):.3f}' if nec else '  --'
                    lines.append(
                        f'  {w["Word"]:<20s}  SW:{sw_str}  NEC:{nec_str}  '
                        f'{traj}'
                    )
                lines.append('')

            # Rising words — emerging signal
            rising = [w for w in self.words if w.get('Trajectory') == 'RISING'
                      and w.get('Classification') == 'SIGNAL']
            rising.sort(key=lambda w: -float(w.get('Signal_Weight', 0)))
            if rising:
                lines.append('  RISING SIGNAL (emerging words gaining ground):')
                lines.append('  ' + '-' * 56)
                for w in rising[:10]:
                    lines.append(
                        f'  {w["Word"]:<20s}  '
                        f'Count:{w["Count"]:>5}  '
                        f'SW:{float(w.get("Signal_Weight", 0)):.3f}  '
                        f'Rank:{w["Rank"]}'
                    )
                lines.append('')

            # Declining words — fading signal
            declining = [w for w in self.words if w.get('Trajectory') == 'DECLINING'
                         and w.get('Classification') == 'SIGNAL']
            declining.sort(key=lambda w: -float(w.get('Signal_Weight', 0)))
            if declining:
                lines.append('  DECLINING SIGNAL (fading words losing ground):')
                lines.append('  ' + '-' * 56)
                for w in declining[:10]:
                    lines.append(
                        f'  {w["Word"]:<20s}  '
                        f'Count:{w["Count"]:>5}  '
                        f'SW:{float(w.get("Signal_Weight", 0)):.3f}  '
                        f'Rank:{w["Rank"]}'
                    )
                lines.append('')

            # Thread SNR leaderboard
            if self.sigsystem_threads:
                lines.append('  THREAD SNR LEADERBOARD:')
                lines.append('  ' + '-' * 56)
                for t in self.sigsystem_threads[:10]:
                    thread_name = t.get('Thread', '')
                    snr = float(t.get('SNR_Normalized', 0))
                    snr_db = float(t.get('SNR_dB', 0))
                    words = int(t.get('Total_Words', 0))
                    lines.append(
                        f'  {thread_name:<35s}  '
                        f'SNR:{snr:.4f}  '
                        f'dB:{snr_db:>6.2f}  '
                        f'Words:{words:>5,}'
                    )
                lines.append('')

        lines.append('=' * 64)
        lines.append('  "Every word I write is a soldier.')
        lines.append('   Every thread I spin is a campaign.')
        lines.append('   Every theme that survives becomes a commander."')
        lines.append('                              -- Operation SIGNAL FORCE')
        lines.append('=' * 64)

        report = '\n'.join(lines)

        path = os.path.join(self.output_dir, 'signal_army_summary.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"  signal_army_summary.txt -- dashboard generated")

        return report

    def save_all(self):
        """Generate all output files. Returns list of paths."""
        paths = []
        paths.append(self.save_flattened_messages())
        paths.append(self.save_word_inventory())
        paths.append(self.save_phrase_inventory())
        paths.append(self.save_division_inventory())
        self.generate_summary()
        return paths


# ---------------------------------------------------------------------------
# CLI & Main
# ---------------------------------------------------------------------------

def collect_md_paths(args):
    """Gather all .md file paths from --md and --md-dir arguments."""
    paths = []
    if args.md:
        for p in args.md:
            if os.path.isfile(p):
                paths.append(os.path.abspath(p))
            else:
                print(f"  WARNING: File not found: {p}", file=sys.stderr)
    if args.md_dir:
        d = args.md_dir
        if os.path.isdir(d):
            for fname in sorted(os.listdir(d)):
                if fname.lower().endswith('.md'):
                    paths.append(os.path.abspath(os.path.join(d, fname)))
        else:
            print(f"  WARNING: Directory not found: {d}", file=sys.stderr)
    return paths


def main():
    parser = argparse.ArgumentParser(
        description='Signal Army -- Word Inventory & Force Ranking Tool\n'
                    '"Every Word a Soldier"',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  python signal_army.py --md GPT_72325_army.md\n'
               '  python signal_army.py --md-dir ./transcripts/\n'
               '  python signal_army.py --json ~/Downloads/conversations.json\n'
               '  python signal_army.py --json data.json --md-dir ./transcripts/\n'
    )
    parser.add_argument('--json', metavar='PATH',
                        help='Path to ChatGPT conversations.json export')
    parser.add_argument('--md', metavar='PATH', nargs='+',
                        help='One or more .md transcript files')
    parser.add_argument('--md-dir', metavar='DIR',
                        help='Directory of .md files (processes all *.md)')
    parser.add_argument('--md-mode', choices=['detect', 'user-only'],
                        default='detect',
                        help='How to parse .md files (default: detect)')
    parser.add_argument('--output-dir', metavar='DIR',
                        help='Output directory (default: same as first input)')
    parser.add_argument('--no-phrases', action='store_true',
                        help='Skip phrase (n-gram) analysis')
    parser.add_argument('--min-phrase-count', type=int, default=2, metavar='N',
                        help='Minimum occurrences for phrases (default: 2)')
    parser.add_argument('--sigsystem', metavar='DIR',
                        help='Path to SIGSYSTEM run directory (overrides auto-detect)')
    parser.add_argument('--no-sigsystem', action='store_true',
                        help='Skip SIGSYSTEM integration even if data exists')
    parser.add_argument('--role', choices=['user', 'assistant', 'all'],
                        default='user',
                        help='Which messages to analyze: user (default), assistant (AI responses), or all')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed progress and warnings')

    args = parser.parse_args()

    # Validate inputs
    md_paths = collect_md_paths(args)
    has_json = args.json and os.path.isfile(args.json)

    if not md_paths and not has_json:
        parser.error('At least one input source required (--json, --md, or --md-dir)')

    # Determine output directory — each run gets a timestamped subfolder
    run_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    if args.output_dir:
        base_dir = args.output_dir
    elif md_paths:
        base_dir = os.path.dirname(md_paths[0])
    elif has_json:
        base_dir = os.path.dirname(os.path.abspath(args.json))
    else:
        base_dir = '.'
    output_dir = os.path.join(base_dir, f'run_{run_stamp}')
    os.makedirs(output_dir, exist_ok=True)

    # Header
    print(f'\nSignal Army -- Word Inventory Tool v{VERSION}')
    print('=' * 48)
    print()

    # Phase 1: Gather messages
    all_messages = []

    if md_paths:
        print(f'[1/3] Parsing {len(md_paths)} markdown file(s)...')
        md_parser = MarkdownParser(md_paths, md_mode=args.md_mode)
        md_messages = md_parser.parse_all()
        all_messages.extend(md_messages)
        print(f'      Extracted {len(md_messages)} user messages from markdown')
        if args.verbose and md_parser.warnings:
            for w in md_parser.warnings:
                print(f'      WARNING: {w}')
        print()

    if has_json:
        print(f'[1/3] Loading conversations.json...')
        target_role = None if args.role == 'all' else args.role
        flattener = ConversationFlattener(args.json, target_role=target_role)
        json_messages = flattener.flatten_all()
        all_messages.extend(json_messages)
        if args.verbose and flattener.warnings:
            for w in flattener.warnings:
                print(f'      WARNING: {w}')
        print()

    if not all_messages:
        print('No messages extracted. Nothing to analyze.')
        sys.exit(1)

    print(f'      Total messages to analyze: {len(all_messages)}')
    print()

    # Phase 2: Analyze
    print('[2/3] Building word inventory...')
    analyzer = SignalArmyAnalyzer(all_messages)

    word_inventory = analyzer.build_word_inventory()
    total_deployed = sum(w['Count'] for w in word_inventory)
    print(f'      {total_deployed:,} total words deployed')
    print(f'      {len(word_inventory):,} unique words (after stop word removal)')

    if not args.no_phrases:
        print('      Building phrase inventory (2-grams, 3-grams)...')
        phrase_inventory = analyzer.build_phrase_inventory(
            min_count=args.min_phrase_count
        )
        print(f'      {len(phrase_inventory):,} recurring phrases found')
    else:
        phrase_inventory = []

    print('      Building infantry field connections...')
    infantry_context = analyzer.build_infantry_context()
    print(f'      {len(infantry_context)} infantry words mapped to connections')

    print('      Building thematic division clusters...')
    division_clusters = analyzer.build_division_clusters(word_inventory)
    print(f'      {len(division_clusters)} thematic divisions formed')
    total_clustered = sum(d['Member_Count'] for d in division_clusters)
    print(f'      {total_clustered} words assigned to divisions')
    print()

    # Load SIGSYSTEM data — auto-detect unless disabled
    sigsystem_scores = None
    sigsystem_thread_snr = None
    if not args.no_sigsystem:
        sigsystem_dir = args.sigsystem or find_latest_sigsystem_run()
        if sigsystem_dir and os.path.isdir(sigsystem_dir):
            sigsystem_scores, sigsystem_thread_snr = load_sigsystem_data(sigsystem_dir)
            if sigsystem_scores:
                print(f'      SIGSYSTEM run: {os.path.basename(sigsystem_dir)}')
        elif args.sigsystem:
            print(f'  WARNING: SIGSYSTEM directory not found: {args.sigsystem}',
                  file=sys.stderr)

    # Phase 3: Generate reports
    print('[3/3] Generating reports...')
    reporter = ReportGenerator(word_inventory, phrase_inventory,
                               all_messages, output_dir,
                               infantry_context=infantry_context,
                               division_clusters=division_clusters,
                               sigsystem_scores=sigsystem_scores,
                               sigsystem_thread_snr=sigsystem_thread_snr)
    reporter.save_all()
    print()

    # Quick stats footer
    rank_counts = Counter(w['Rank'] for w in word_inventory)
    print('=' * 48)
    print('QUICK STATS:')
    print(f'  Officer-Class words:  {rank_counts.get("Officer-Class", 0)}')
    print(f'  Doctrine Builders:    {rank_counts.get("Doctrine Builder", 0)}')
    print(f'  Division-rank words:  {rank_counts.get("Division", 0)}')
    print(f'  Thematic Divisions:   {len(division_clusters)}')
    print(f'  Words in Divisions:   {total_clustered}')
    print(f'  Total Token Mass:     {sum(w["Count"] * w["Token_Weight"] for w in word_inventory):,.1f}')
    print('=' * 48)
    print(f'\nAll files written to: {output_dir}/')
    print()


if __name__ == '__main__':
    main()
