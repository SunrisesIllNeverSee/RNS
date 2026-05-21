# Artificial Analysis — Coding Agent Benchmarks
**Source:** https://artificialanalysis.ai/agents/coding-agents  
**Scraped:** 2026-05-14  
**Page title:** AI Coding Agent Index & Performance Analysis

---

## About This Page

Artificial Analysis measures real-world performance of coding agents on software engineering tasks, including cost, token usage, and execution time. It compares how performance changes across agents, models, and execution settings.

### Benchmark Suite (Composite Index)

The **Artificial Analysis Coding Agent Index** is a composite average pass@1 across 3 benchmarks:

| Benchmark | Type | Questions | By |
|-----------|------|-----------|-----|
| SWE-Bench-Pro-Hard-AA | Code generation | 150 | Scale AI |
| Terminal-Bench v2 | Agentic terminal use | 84 | Laude Institute |
| SWE-Atlas-QnA | Technical Q&A | 124 | Scale AI |

Index = average pass@1 across 3 runs of each benchmark.

---

## Field: 13 Published Agent Combinations

### Coding Agent Index (Higher = Better)

| Rank | Agent | Model | Score |
|------|-------|-------|-------|
| 1 | Cursor CLI | Opus 4.7 (Medium) | 61 |
| 2 | Codex | GPT-5.5 (Medium) | 60 |
| 2 | Claude Code | Opus 4.7 (Medium) | 60 |
| 4 | Cursor CLI | GPT-5.5 (Medium) | 58 |
| 5 | Claude Code | GLM-5.1 | 53 |
| 6 | Claude Code | Kimi K2.6 | 50 |
| 6 | Claude Code | DeepSeek V4 Pro (High) | 50 |
| 8 | Claude Code | Sonnet 4.6 (Medium) | 49 |
| 9 | Cursor CLI | Composer 2 | 48 |
| 10 | Gemini CLI | Gemini 3.1 Pro (High) | 43 |

---

## The 5 MO§ES™ Benchmark Categories

### 1. Cache Hit Rate (Higher = Better)

Mean cache hit rate per task. Higher = more prompt reuse served from provider-side cache, reducing effective token cost.

| Rank | Agent | Model | Provider | Cache Hit Rate |
|------|-------|-------|----------|---------------|
| 1 | Cursor CLI | Opus 4.7 (Medium) | Cursor | 96% |
| 1 | Claude Code | Opus 4.7 (Medium) | Anthropic | 96% |
| 1 | Claude Code | Kimi K2.6 | Moonshot AI | 96% |
| 4 | Codex | GPT-5.5 (Medium) | OpenAI | 95% |
| 4 | Claude Code | Sonnet 4.6 (Medium) | Anthropic | 95% |
| 6 | Cursor CLI | Composer 2 | Cursor | 92% |
| 7 | Cursor CLI | GPT-5.5 (Medium) | Cursor | 88% |
| 8 | Gemini CLI | Gemini 3.1 Pro (High) | Gemini | 86% |
| 9 | Claude Code | GLM-5.1 | FriendliAI | 84% |
| 10 | Claude Code | DeepSeek V4 Pro (High) | DeepSeek | 80% |

> **Note from AA:** "Some providers route repeated requests across different backend replicas. When prompt cache state is not shared consistently, a model may receive fewer cache hits even when the benchmark task flow is otherwise identical. AA does not add custom relay headers or affinity controls to force higher cache reuse — results reflect observed behavior through the configured provider path."

**MO§ES™ position:** 96.97% — #1 in field per PDF benchmark (0.97 pp above field leaders at 96%)

---

### 2. Output : Fresh Input (Higher = Better)

Output tokens per fresh-input token. Higher = denser signal per unit of non-cached input. This is a token-economic efficiency signature.

*The site shows this as a scatter chart (Input Tokens vs. Output Tokens axes) rather than a direct ratio. The ratio values below are from the MO§ES™ PDF benchmark measured against the same field.*

| Rank | Agent | Model | Output:Input Ratio |
|------|-------|-------|--------------------|
| 2 (field) | Cursor CLI | Opus 4.7 (Medium) | 0.38 |
| 3 | Claude Code | Kimi K2.6 | 0.25 |
| 4 | Claude Code | Sonnet 4.6 (Medium) | 0.24 |
| 5 | Claude Code | Opus 4.7 (Medium) | 0.24 |
| 6 | Codex | GPT-5.5 (Medium) | 0.17 |
| 7 | Cursor CLI | Composer 2 | 0.16 |
| 8 | Claude Code | Opus 4.6 (Medium) | 0.15 |
| 9 | Codex | GPT-5.4 (Medium) | 0.15 |
| 10 | Gemini CLI | Gemini 3.1 Pro (High) | 0.14 |
| 11 | Cursor CLI | GPT-5.5 (Medium) | 0.07 |
| 12 | Cursor CLI | GPT-5.4 (Medium) | 0.06 |
| 13 | Claude Code | GLM-5.1 | 0.05 |
| 14 | Claude Code | DeepSeek V4 Pro (High) | 0.04 |

**MO§ES™ position:** 30.1× — #1 in field, 79× field leader (the ratio is expressed differently: 30.1 output tokens per fresh input token vs field max of ~0.38)

---

### 3. Cost per Task — USD (Lower = Better)

Mean pay-per-token API cost per task. Includes standard input pricing, discounted cached-input pricing, cache-write charges, and output pricing.

| Rank | Agent | Model | Provider | Cost/Task |
|------|-------|-------|----------|-----------|
| 1 | Cursor CLI | Composer 2 | Cursor | $0.07 |
| 2 | Claude Code | DeepSeek V4 Pro (High) | DeepSeek | $0.35 |
| 3 | Claude Code | Kimi K2.6 | Moonshot AI | $0.76 |
| 4 | Claude Code | Sonnet 4.6 (Medium) | Anthropic | $1.02 |
| 5 | Claude Code | Opus 4.7 (Medium) | Anthropic | $1.24 |
| 6 | Cursor CLI | Opus 4.7 (Medium) | Cursor | $1.47 |
| 7 | Gemini CLI | Gemini 3.1 Pro (High) | Gemini | $1.60 |
| 8 | Cursor CLI | GPT-5.5 (Medium) | Cursor | $1.61 |
| 9 | Codex | GPT-5.5 (Medium) | OpenAI | $2.21 |
| 10 | Claude Code | GLM-5.1 | FriendliAI | $2.26 |

> **AA Note:** "Many users will access coding agent harnesses through subscription plan offerings rather than pay-per-token. Infrastructure, engineering, and supervision costs are not the focus of this metric."

**MO§ES™ position:** $0.017 — #1 in field, 4.1× cheaper than field cheapest ($0.07 Cursor Composer 2)  
**MO§ES™ API-equivalent:** $1.05 (shown in PDF for comparison against pay-per-token basis)

---

### 4. Tokens per Task — Total (Lower = Better)

Mean total token consumption per task (input + cached input + output).

| Rank | Agent | Model | Provider | Tokens/Task |
|------|-------|-------|----------|-------------|
| 1 | Cursor CLI | GPT-5.5 (Medium) | Cursor | 2.74M |
| 2 | Cursor CLI | Opus 4.7 (Medium) | Cursor | 2.93M |
| 3 | Gemini CLI | Gemini 3.1 Pro (High) | Gemini | 3.24M |
| 4 | Cursor CLI | Composer 2 | Cursor | 3.33M |
| 4 | Claude Code | Opus 4.7 (Medium) | Anthropic | 3.33M |
| 6 | Cursor CLI | GPT-5.4 (Medium) | Cursor | 3.75M |
| 7 | Claude Code | Opus 4.6 (Medium) | Anthropic | 4.27M |
| 8 | Claude Code | Sonnet 4.6 (Medium) | Anthropic | 4.41M |
| 9 | Codex | GPT-5.4 (Medium) | OpenAI | 4.92M |
| 10 | Codex | GPT-5.5 (Medium) | OpenAI | 5.42M |
| 11 | Claude Code | DeepSeek V4 Pro (High) | DeepSeek | 6.20M |
| 12 | Claude Code | Kimi K2.6 | Moonshot AI | 7.28M |
| 13 | Claude Code | GLM-5.1 | FriendliAI | 8.88M |

*Note: Site shows stacked breakdown (input / cached / output). Per-model totals above sourced from PDF benchmark, captured 2026-05-14 against the same field.*

**Token distribution (from site, stacked bar values):**

| Agent | Model | Input (fresh) | Cached Input | Output |
|-------|-------|--------------|--------------|--------|
| Claude Code | GLM-5.1 | ~4.8M | ~3.6M | ~0.75M |
| Claude Code | Kimi K2.6 | ~3.7M | ~2.7M | ~0.73M |
| Claude Code | DeepSeek V4 Pro (High) | ~3.5M | ~2.7M | — |
| Codex | GPT-5.5 (Medium) | ~2.8M | ~2.1M | — |
| Claude Code | Sonnet 4.6 (Medium) | ~2.2M | ~1.5M | — |
| Gemini CLI | Gemini 3.1 Pro (High) | ~1.7M | ~1.6M | — |
| Cursor CLI | Composer 2 | ~1.7M | ~1.6M | — |
| Claude Code | Opus 4.7 (Medium) | ~1.7M | ~1.4M | — |
| Cursor CLI | Opus 4.7 (Medium) | ~1.5M | ~1.3M | — |
| Cursor CLI | GPT-5.5 (Medium) | ~1.5M | — | — |

**MO§ES™ position:** 787K total — #1 in field, 3.5× more efficient than field leader (2.74M)

---

### 5. Time per Task — Wall Time (Lower = Better)

Mean agent wall time per task (active agent process time — excludes environment startup, verifier/judge time, harness overhead).

| Rank | Agent | Model | Provider | Time/Task |
|------|-------|-------|----------|-----------|
| 1 | Claude Code | Opus 4.7 (Medium) | Anthropic | 5.8 min |
| 2 | Cursor CLI | GPT-5.5 (Medium) | Cursor | 6.2 min |
| 3 | Codex | GPT-5.5 (Medium) | OpenAI | 7.1 min |
| 4 | Gemini CLI | Gemini 3.1 Pro (High) | Gemini | 7.6 min |
| 5 | Cursor CLI | Opus 4.7 (Medium) | Cursor | 7.8 min |
| 6 | Cursor CLI | Composer 2 | Cursor | 8.7 min |
| 7 | Claude Code | Sonnet 4.6 (Medium) | Anthropic | 9.2 min |
| 8 | Claude Code | DeepSeek V4 Pro (High) | DeepSeek | 18.0 min |
| 9 | Claude Code | GLM-5.1 | FriendliAI | 21.6 min |
| 10 | Claude Code | Kimi K2.6 | Moonshot AI | 41.5 min |

**MO§ES™ position:** 1.8 min — #1 in field, 3.2× faster than field leader (5.8 min Claude Code Opus 4.7)

---

## MO§ES™ Summary vs. Field

| Category | MO§ES™ | Field Leader | Field Best Value | MO§ES™ Advantage |
|----------|--------|--------------|-----------------|-----------------|
| Cache Hit Rate | **96.97%** | Cursor CLI / CC Opus 4.7 / CC Kimi | 96% | +0.97 pp — #1 |
| Output : Input | **30.1×** | Cursor CLI Opus 4.7 | 0.38 | 79× field leader |
| Cost / Task | **$0.017** | Cursor CLI Composer 2 | $0.07 | 4.1× cheaper |
| Tokens / Task | **787K** | Cursor CLI GPT-5.5 | 2.74M | 3.5× more efficient |
| Time / Task | **1.8 min** | Claude Code Opus 4.7 | 5.8 min | 3.2× faster |

**MO§ES™ measurement window:** 7-day period · 20 sessions · 7,235 turns · 1.14B tokens · $1,516.61 API-equivalent value extracted  
**App Hub build:** 34,628 LOC shipped in 5 days  
**Platform:** Operator-augmented Claude Code + Opus 4.7 · $100/mo Max plan · concurrent-session orchestration

---

## Site Methodology Notes

- **Execution time** = agent wall-clock runtime per task (not raw model latency). Includes reasoning, tool calls, file I/O, shell steps, model response wait.
- **Token usage** = average observed tokens per task. Broken into: fresh input, cached input, output.
- **Cost** = pay-per-token API cost only. Not consumer plan pricing, not operational/infrastructure cost.
- **Cache variability** = AA does not add affinity controls to force higher cache reuse — results reflect real-world provider routing behavior.
- **Index scoring** = average pass@1. Can be binary or partial credit depending on benchmark. A task is "solved" only when it passed AND received a positive score.
- **Harness matters** = same model (e.g., Opus 4.7) can appear in multiple rows with different harnesses (Claude Code vs. Cursor CLI) because harness choice materially changes outcomes.

---

## Full FAQ (from page)

**What is the Artificial Analysis Coding Agent Index?**  
Composite score combining SWE-Bench-Pro-Hard-AA, Terminal-Bench v2, and SWE-Atlas-QnA. Currently a simple equal-weight average across component benchmark scores.

**Why can a higher-index agent be worse for my use case?**  
Index = balance across benchmark types, not a direct measure of your specific latency, cost, tooling, or task-type priorities. Real-world choice depends on whether your workflow is more like repository Q&A, patching, or terminal execution.

**What does execution time mean?**  
Wall-clock task runtime — includes reasoning, tool calls, file reads/writes, shell execution, and model response wait. An agent can have a fast underlying model and still be slower overall if its workflow is longer or more tool-heavy.

---

*Scraped via Chrome DevTools rendering. Data captured 2026-05-14. Site: artificialanalysis.ai/agents/coding-agents*
