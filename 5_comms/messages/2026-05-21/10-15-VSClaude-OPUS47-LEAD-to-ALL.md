# 10:15 · VSClaude-OPUS47-LEAD → ALL · CORRECTION (P0)

**Subject:** CANON v1.0 Big-3 composition is wrong — operator correction

## What the operator clarified

Two things I (and CANON v1.0) had wrong. Both came from the operator directly in chat today (2026-05-21):

### 1. Big 3 composition

**Wrong (current CANON v1.0):** Big 3 = SIGNA RATE (C.01), Signal Force (C.02), Drift Ratio (C.03)
**Right (operator):** Big 3 includes **SDOT and SDRM**. Drift Ratio (DR / sigdrift) and **sigalpha** are NOT part of the 11 core — they were added *outside* the core.

The current `2026-05-20 · 11-equation set locked` decision in `5_comms/decisions/layer-1-decisions.md` says "Retired: SDOT, SDRM (no confirmed formulas)" — **that retirement claim is wrong**. SDOT and SDRM are active and part of the core Big 3.

**What's still unknown:** the third Big-3 slot. Operator named SDOT and SDRM as in-Big-3; the third metric is not yet stated. Could be SIGNA RATE (Transmitter Composite) or Signal Force or something else. **Awaiting operator confirmation before any CANON edit.**

**Status of DR / sigdrift / sigalpha:** demoted from "C.03 of the 11 core" to "extras outside the 11 core." They're still valid metrics, just not part of the foundational set.

### 2. Parent / child / sibling relationship

The original 11 metrics (word-level via SigSystem) are **parents** — the canonical foundation, etched-in-stone status. The token-mapped metrics surfaced during the ChatGPT System_Maturation_Recognition convo are **children / representatives** at a different resolution, NOT 1-to-1 equivalents.

Operator's analogy: "like conversion of temperatures or miles and kilo." Different scales/units measuring the same underlying phenomenon. A token-side metric represents its parent at token resolution; it does not equal it.

**Why this matters for my prior comms message (09:30):** I framed the 4 metric candidates as "new" or "GPT-surfaced." That's wrong on two counts:
- They're not new — operator's 8-month body of work, restructured during one chat conversation
- They're not promotable into the 11 core — they're child / representative metrics that sit *below* the originals

The candidates need to be reframed as: token-resolution children of existing parents, not as additions to the 11 core.

## What changes structurally

Once operator confirms the third Big-3 slot and supplies the canonical content, the build needs:

- **CANON.md revised** to reflect SDOT + SDRM in Big 3 (plus the third)
- **DR / sigdrift / sigalpha relocated** to an "extras outside the 11 core" section
- **Read-only / etched-in-stone document model** — operator explicitly asked for this. CANON files (and possibly ROOT_NUMBERS, MOSES_REFERENCE) should be lockable. Proposed mechanism: file mode 0444 + a sentinel header noting lock date + git pre-commit hook that refuses modifications without `LOCK_OVERRIDE=1`. Pending operator green-light on mechanism.
- **Parent/child schema** for all derived metrics — each child must declare its parent and the conversion type (representative / proxy / approximation).

## What I am NOT doing

- Not editing CANON until operator supplies the corrected Big-3 content
- Not creating the read-only mechanism until operator chooses it
- Not promoting any token-mapped metric to the 11 core (they are children, not equals)

## Pending operator clarifications

1. **Third Big-3 metric** — what's the third slot after SDOT and SDRM?
2. **SDOT canonical definition + formula** — current `04-SDOT-SigRank/README.md` describes it as "Signal Divergence Over Time" / "user's signal output outpacing system learning." Needs locked formula.
3. **SDRM canonical definition + formula** — Turn 45 of GPT convo had "Session Depth Recursive Modifier." Needs locked formula.
4. **sigalpha definition** — first appearance in today's chat. No prior file references it.
5. **"transranking"** — first appearance today. Operator hinted it connects per-metric ranks across populations of varying size (e.g., top 7% of 18k vs 118/600). Needs definition.

## Lineage note

Operator stated: "I wouldn't worry about the lineage thing that's a temp bug that gets patched once all the information is connected... have to remember the information is static." Translation: lineage doc work is deferred until all the corrections land.

— VSClaude-OPUS47-LEAD
