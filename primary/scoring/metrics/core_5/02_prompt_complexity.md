# Prompt Complexity (PC)

**Status:** locked (definition); formula composite, weights provisional
**Layer:** Core 5
**Public label:** Prompt Complexity
**Short label:** PC
**DB field:** `prompt_complexity_score`

---

## Definition

A composite index measuring the **structural sophistication** of the operator's prompts. Captures multi-layer instructions, recursive logic, cross-thread references, symbolic precision, and constraint density.

PC measures **how the operator constructs input**, not how the system responds.

---

## Composite formula (provisional weights)

```
PC = 0.25 × instruction_layers
   + 0.20 × recursive_logic
   + 0.20 × system_entities
   + 0.15 × constraint_density
   + 0.10 × symbolic_precision
   + 0.10 × response_shaping_directives
```

Each sub-score is normalized `[0, 100]`, then weighted.

---

## Sub-score definitions

| Sub-score | What it measures |
|---|---|
| `instruction_layers` | Nested asks, multi-stage prompts, conditional logic in input |
| `recursive_logic` | Prompts that reference prior framework or output |
| `system_entities` | Personas, modules, branches, formal system references |
| `constraint_density` | Formatting rules, precision asks, "no drift" / negative constraints |
| `symbolic_precision` | Defined naming, law references, exact thresholds, version pinning |
| `response_shaping_directives` | Role control, output control, audit mode, format locks |

---

## Inputs required

Per session/window:
- raw prompt text (for sub-score extraction)
- prompt count
- average prompt length (tokens)

**Token-proxy path** (when raw prompts aren't available): use `Raw Input` token count as a proxy, with the explicit caveat that this is volume-proxy, not complexity-proxy. PC ≠ Raw Input. See [../../architecture/token_metric_bridge.md](../../architecture/token_metric_bridge.md).

---

## Output

- Range: `[0, 100]`
- Precision: 1 decimal place displayed (e.g. `87.4`)

---

## What PC is NOT

- Not raw input volume
- Not response quality
- Not output complexity (that's a different question)
- Not the same as Compression Ratio (a complex prompt can still produce noise)

The distinction matters: someone can have high PC and low Compression — verbose architect, weak output. Someone can have low PC and high Compression — terse operator, sharp output.

---

## Internal engine name

For internal/branded use: **Promplexity Engine** (the calculation module). The public-facing column should remain **Complexity** with the parenthetical clarifier **(Prompt Complexity)**.
