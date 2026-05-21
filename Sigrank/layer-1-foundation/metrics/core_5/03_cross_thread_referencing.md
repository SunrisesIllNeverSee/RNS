# Cross-Thread Referencing (CT)

**Status:** locked
**Layer:** Core 5
**Public label:** Cross-Thread Referencing
**Short label:** CT (or X-Ref on compact displays)
**DB field:** `cross_thread_score`

---

## Definition

Measures the operator's ability to maintain **long-range continuity** — referencing prior threads, calling back to earlier system state, and weaving knowledge across separate sessions without re-establishing context.

CT is the **continuity persistence** metric. It captures memory weaving, knowledge integration, and the kind of sustained reasoning that crosses session boundaries.

---

## Formula

```
CT_SCORE = min(100, 8 × unique_thread_refs + 4 × memory_linked_callbacks)
```

Where:
- `unique_thread_refs` = count of distinct prior thread/session IDs referenced
- `memory_linked_callbacks` = count of references to operator's persistent memory (named modules, persona invocations, prior named system state)

**Example calibration:**
- 5 thread refs + 5 callbacks → 8(5) + 4(5) = 60
- 8 thread refs + 9 callbacks → 8(8) + 4(9) = 100 (cap)

---

## Inputs required

- list of thread/session IDs referenced
- list of memory/module/persona names invoked
- window boundaries (24h / 7d / 30d / 90d / all-time)

**Token-proxy path** (token submission model): use `Cache Hit Rate` as the primary CT proxy. High cache hit rate = high context reuse = high continuity. See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## Output

- Range: `[0, 100]`
- Precision: integer displayed
- Stored as both raw counts (`thread_refs`, `callbacks`) and computed score

---

## Why CT matters

CT is the metric that's hardest to fake. Volume can be inflated. Compression can be manipulated through curated short answers. But long-range thread continuity requires actual sustained engagement with the system over time.

A high CT score is one of the strongest signals of a real Architect-class or Transmitter-class operator.

---

## Display name decisions

| Context | Label |
|---|---|
| Full leaderboard column | Cross-Thread Referencing |
| Compact display | Cross-Thread |
| Mobile / icon view | X-Ref |
| Profile detail | Threads Recalled (humanized) |
