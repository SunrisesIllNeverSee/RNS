# Token Metric Bridge

How the new token-economic submission model maps to the established SigRank Core 5. This is the bridge between the two tiers — free (token telemetry) and precision (sig_army audit).

---

## The two paths

```
                            OPERATOR SUBMISSION
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                                   │
            FREE TIER                          PRECISION TIER
       (token telemetry)                       (sig_army audit)
                  │                                   │
       Platform-generated                  Raw session analysis
       Cache stats, token                  Word/token signal vs
       counts, turns, etc.                 noise classification
                  │                                   │
                  ↓                                   ↓
       Behavioral proxies                   Direct measurement
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    │
                              CORE 5 SCORES
                                    │
                              SIGNA RATE
                                    │
                              CLASS TIER
                                    │
                              LEADERBOARD
```

Both paths produce a Core 5 score. The precision tier exposes whether the free-tier proxies overstated or understated the operator's true scores.

---

## The mapping

### Compression Ratio ← Output : Fresh Input ratio

**Confirmed clean mapping.**

```
Free tier:
  compression_proxy = output_tokens / (output_tokens + fresh_input_tokens)

Precision tier:
  compression_exact = signal_tokens / (signal_tokens + noise_tokens)
```

**Worked example (MO§ES 7d window):**
- output_tokens: 3,902,803
- fresh_input_tokens: 123,246
- proxy = 3,902,803 / (3,902,803 + 123,246) = **0.9694**

Or equivalently as a leverage ratio:
```
output_to_input_ratio = 3,902,803 / 123,246 = 31.7×
```

Field average for coding agents: 0.38×. MO§ES is 83× the field leader on this axis.

**Why this works:** high output per fresh input token = high context reuse = the operator is leveraging existing structure rather than reconstructing it. That's the operational definition of signal density.

**Where the proxy can mislead:** an operator who uses very few prompts but each produces enormous output (single-prompt code dumps) can game this. The precision tier catches this via Drift Ratio and PC sub-scores.

---

### Cross-Thread Referencing ← Cache Hit Rate

**Confirmed clean mapping.**

```
Free tier:
  ct_proxy_pct = cache_read / (cache_read + cache_creation + fresh_input)

Precision tier:
  ct_exact = thread_refs_count + memory_callbacks (with formula)
```

**Worked example (MO§ES 7d window):**
- cache_read: 1,084,399,183
- cache_creation: 34,826,779
- fresh_input: 123,246
- proxy = 1,084,399,183 / (1,084,399,183 + 34,826,779 + 123,246) = **96.88%**

Field average for top coding agents: 91-96%. MO§ES leads.

**Why this works:** the cache contains conversational context. A high hit rate means the operator is consistently referencing the same persistent context structures — the operational equivalent of thread continuity.

**Scoring:** convert percentage to `[0, 100]` for CT_SCORE directly. `96.88%` → `CT_SCORE = 96.88`.

---

### Session Depth ← Turns per Session

**Strong mapping.**

```
Free tier:
  sd_proxy = turns_total / sessions_count

Precision tier:
  sd_exact = avg(max_reply_chain_length) across sessions
```

**Worked example (MO§ES 7d window):**
- turns: 7,327
- sessions: 21
- proxy = 7,327 / 21 = **348.9 turns/session**

Apply normalization (the bucket scoring from scoring_formula.md). A 348-turn average session is far above the 30+ threshold → `DEPTH_SCORE = 100`.

**Difference from exact:** turns ≠ reply chain length. A session with 100 turns of single-back-and-forth has the same turn count as a session with 5 chains of 20 each. The proxy can't see chain structure.

For free tier ranking, the proxy is good enough. Precision tier exposes the chain structure.

---

### Token Throughput ← Output tokens per Active minute

**Direct mapping.**

```
TT_proxy = output_tokens / active_minutes
```

**Worked example (MO§ES 7d window):**
- output_tokens: 3,902,803
- active_minutes: ~2,700 (45 hours)
- TT_proxy = 3,902,803 / 2,700 = **~1,445 tokens/min**

Apply log normalization → high TT_SCORE.

Or, more usefully for the leaderboard, **time per task** rather than tokens per minute:

```
time_per_task = active_minutes / task_count
```

For MO§ES: 2,700 / 1,465 = **1.84 min/task**. Field average: 11.54 min/task. MO§ES is 3.2× faster.

---

### Prompt Complexity ← (no clean proxy)

**Weak mapping. This is the precision-tier upsell driver.**

The free tier can attempt to proxy PC via:
- raw input token count (volume, not complexity)
- input variance / standard deviation across prompts (structural diversity)
- count of distinct semantic clusters in inputs (requires NLP)

None of these are clean. **Raw Input alone is a volume proxy, not a complexity proxy.**

**Decision for MVP:** free tier reports `prompt_complexity_estimate` with a confidence flag. Precision tier reports `prompt_complexity_exact`.

**Free tier PC estimate (best-effort):**
```
pc_estimate = min(100, log10(unique_prompt_count + 1) × 20)
              × (avg_prompt_length / 100)   // length factor
```

This is a placeholder. Don't trust it for top-class rankings.

**Why PC needs sig_army:** Real prompt complexity requires analyzing instruction structure, recursion, system entity references, constraint density. None of that is in token telemetry. This is what the sig_army Python engine was built to extract.

---

### Background metrics — direct ingestion

These don't need proxying — they're already counts:

| Background metric | Source |
|---|---|
| `message_volume` | Platform message count in window |
| `account_age_days` | First-seen timestamp |
| `total_messages_lifetime` | All-time platform message count |

---

## Free vs Precision tier feature matrix

| Feature | Free | Precision |
|---|:---:|:---:|
| Submit token telemetry | ✓ | ✓ |
| Get Core 5 scores | ✓ (proxies) | ✓ (exact) |
| Compression Ratio | proxy (Output:Input) | exact (Signal:Noise) |
| Cross-Thread | proxy (Cache Hit Rate) | exact (refs + callbacks) |
| Session Depth | proxy (turns/session) | exact (chain length) |
| Token Throughput | direct | direct |
| Prompt Complexity | weak estimate | exact (full sub-score breakdown) |
| Drift Ratio | not computed | computed |
| Class assignment | yes | yes (with confidence) |
| Leaderboard rank | yes | yes (with audit verified badge) |
| Profile sub-score breakdown | top-level only | full drilldown |
| Trend chart depth | 90d max | unlimited history |

---

## The commercial argument

The precision tier is the upsell. The free tier is the funnel. The token bridge makes this possible.

**Free tier value:** instant rank with zero friction (submit telemetry the platform already generates). Class assignment is reasonable. Most operators stay free and that's fine — they're the volume.

**Precision tier value:** exact scores, full sub-score visibility, audit-verified badge, drift detection, deeper trend history. The operators who really care about their class will pay for precision.

**Key insight:** the precision tier doesn't replace the free tier. It **verifies** it. A free-tier TRANSMITTER who runs the precision audit gets either confirmation (audit verified badge) or revision (their actual Compression is lower than the proxy suggested).

---

## Implementation order

1. **First**: build the free tier completely. Token telemetry submission → proxy computation → Core 5 scores → SIGNA RATE → class → leaderboard.
2. **Second**: ship the leaderboard publicly with free tier scores.
3. **Third**: build the precision tier as an upsell that operators opt into. Connect sig_army for exact PC and Compression.
4. **Fourth**: add precision-only metrics (Drift Ratio).

The free tier alone is shippable. Don't gate launch on precision.
