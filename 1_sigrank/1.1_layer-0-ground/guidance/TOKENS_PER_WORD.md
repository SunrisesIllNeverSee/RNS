# Tokens per Word — the finer-resolution primitive

A guidance-within reference. Helps interpret what's happening at the Refinery resolution (below the current SigRank build).

The current build uses **token totals** as inputs (RN.01–RN.04). The Refinery resolution would use **tokens per word** — a finer sampling of the same conserved signal.

---

## Why tokens-per-word matters

A token is not a word. Modern tokenizers split words into subword units (BPE, SentencePiece, etc.). The mapping between words and tokens carries information:

| Word | Token count (typical) | Why |
|---|---|---|
| "the" | 1 | Common short word |
| "running" | 1 | Common gerund |
| "antidisestablishmentarianism" | 6–8 | Rare long compound |
| "k8s" | 2–3 | Domain-specific abbreviation |
| "プロンプト" | 4–6 | Non-Latin script |
| Code identifier `getUserAccount` | 3–4 | CamelCase split |
| Symbol `→` | 1 | Reserved single token |

A high token-per-word ratio in a prompt signals:
- Technical or rare vocabulary
- Code, identifiers, or symbols
- Non-English content
- Compound or specialized concepts

A low token-per-word ratio signals:
- Common conversational language
- Short, frequent words
- Padding or filler text

---

## Where this fits in the dimensional stack

```
COMMITMENT THEORY    — preservation invariant
SIGSYSTEM            — word-level signal/noise classification
  ↓ aggregates to
TOKENS PER WORD      — resolution layer between SigSystem and SigRank
  ↓ aggregates to
TOKEN TOTALS         — what current SigRank uses (RN.01-RN.04)
```

**Conservation across this resolution boundary:**

If an operator's word-level SNR is high (SigSystem) AND their vocabulary skews specialized/rare (high tokens-per-word), then their token-total compression (current SigRank) will be high.

If their word-level SNR is high but vocabulary is common (low tokens-per-word), the token-total compression will be lower than the word-level signal would suggest.

This is why the **proxy** in the free tier (Output:Fresh-Input ratio) approximates Compression Ratio but doesn't equal it. The proxy misses the tokens-per-word information.

---

## Why we don't use this in the current build

The current build is **token-total resolution**. We chose this resolution because:

1. **Token totals are universally available** — every modern AI platform reports them as part of usage telemetry
2. **Token totals don't require sentence-by-sentence analysis** — fast, cheap, privacy-preserving
3. **OG SIGRANK proved that token totals carry the conserved signal** with sufficient fidelity for ranking
4. **The Pro-tier upsell uses sig_army at SigSystem resolution** — bypasses tokens-per-word as an intermediate layer

So tokens-per-word exists as a reference primitive — useful for understanding the conservation — but not currently sampled directly in production.

---

## When tokens-per-word would matter

Future builds where tokens-per-word becomes relevant:

| Use case | Why |
|---|---|
| **Refinery scoring engine** | Routes signals between agents at finer granularity than token totals |
| **Multi-language operator parity** | Account for token inflation in non-Latin scripts |
| **Code vs prose scoring** | Code produces higher tokens-per-word; needs distinct scoring track |
| **Cross-tokenizer comparability** | When comparing GPT (cl100k) vs Claude (different tokenizer) vs Gemini |
| **Drift detection finer than session-level** | Word-by-word drift via SigSystem |

For now, these are deferred. The token-total resolution is sufficient for the MVP.

---

## Operational note

If we ever need to compute tokens-per-word for an operator's session:

```
tokens_per_word = total_tokens_in_message / word_count(message_text)
```

Where:
- `total_tokens_in_message` = RN.01 + RN.02 for that message (output + fresh input)
- `word_count` = simple whitespace split, or NLP word tokenization

Word count requires RN.11 (prompt_text), which is precision-tier only. So this primitive is only computable when the precision tier is engaged.

---

## See also

- [`CONSERVATION_LAW.md`](CONSERVATION_LAW.md) — why this resolution preserves the signal
- [`LINEAGE.md`](LINEAGE.md) — where Refinery sits historically
- [`../build/ROOT_NUMBERS.md`](../build/ROOT_NUMBERS.md) — the current build's resolution (token-total)
