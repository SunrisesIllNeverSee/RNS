# Lock Protocol — Document Hierarchy and Write Protection

**Status:** PROPOSAL — pending operator review
**Authored:** 2026-05-21
**Trigger:** Commit `2c3b0be` (Claude Sonnet 4.6, 2026-05-20) unilaterally retired SDOT/SDRM without operator authorization. Nothing in the build prevented this.

---

## The problem this solves

The eight-month standstill on the .87xx number — and the SDOT/SDRM retirement that just had to be reversed — both stem from the same structural gap: **canonical documents have no mechanism preventing unauthorized modification.** Any AI agent operating in this repo can edit CANON.md, and the only thing stopping them is convention.

That doesn't scale across many agents and many sessions.

This protocol defines a four-layer wall around canonical content. Each layer is independently useful; they stack for defense in depth.

---

## Lock levels

Three levels, from most to least restrictive:

### STONE — etched-in-stone canon

**What files:** All of `1_sigrank/1.1_layer-0-ground/build/` (CANON.md, ROOT_NUMBERS.md, MOSES_REFERENCE.md, GREENING.md, IPO.md), all of `1_sigrank/1.1_layer-0-ground/guidance/`, all spec files in `1_sigrank/1.2_layer-1-foundation/metrics/` (Core 5 + Background 3 + composites + extras).

**Protection:** All four layers active (see below).

**Modification requires:** Operator-initiated `/PATCH` command in chat + matching entry in `5_comms/decisions/layer-X-decisions.md` BEFORE the edit + lock re-applied after.

### SOFT-LOCK — work-in-progress canon

**What files:** `1_sigrank/1.2_layer-1-foundation/badges/`, `1_sigrank/1.2_layer-1-foundation/rewards/`, `1_sigrank/1.2_layer-1-foundation/class_tiers.md`.

**Protection:** Layers 1 + 2 only (sentinel header + chmod 0444). Pre-commit hook warns but doesn't block.

**Modification requires:** Acknowledgment of the sentinel header; `chmod 0644` to unlock; edit; `chmod 0444` to relock; decision-log entry within same session.

### OPEN — implementation and iteration

**What files:** `1_sigrank/1.3_layer-2-mechanics/`, `1_sigrank/1.4_layer-3-frontend/`, `1_sigrank/1.5_components/`, `1_sigrank/1.6_agent/`.

**Protection:** None. Edit freely. Iteration is expected here.

### APPEND-ONLY — audit trails

**What files:** `5_comms/decisions/*.md`.

**Protection:** Pre-commit hook refuses any diff that modifies existing lines in these files. Only ADDITIONS at end of file allowed.

---

## The four-layer wall (STONE level)

### Layer 1 — Sentinel header

Every STONE file gets this header at the very top:

```markdown
<!--
LOCK:STONE  date:2026-05-21  by:operator
This file is canonical. Any modification requires:
  1. Operator-issued /PATCH or /UNLOCK command in chat
  2. A decision-log entry created BEFORE the edit (5_comms/decisions/layer-X-decisions.md)
  3. Lock re-applied after the edit
DO NOT MODIFY without all three. Reversion is git-tracked.
-->
```

**Cost:** Five minutes per file, one-time.
**Effectiveness:** Convention-level only. A careful agent reading the file sees it first; a careless one doesn't. But it's the line that establishes the rule.

### Layer 2 — Filesystem read-only

```bash
chmod 0444 1_sigrank/1.1_layer-0-ground/build/*.md
chmod 0444 1_sigrank/1.1_layer-0-ground/guidance/*.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/00_README.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/core_5/*.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/background_3/*.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/composites/*.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/extras/*.md
chmod 0444 1_sigrank/1.2_layer-1-foundation/metrics/lineage/*.md
```

**Cost:** One bash command.
**Effectiveness:** An agent attempting to edit hits `Permission denied`. To proceed, they must consciously `chmod 0644 <file>` first — a deliberate, visible, auditable action. The operator can `chmod` directly with no friction.

**Survival:** Git tracks mode bits via `core.fileMode`. Lock state survives clone/checkout.

### Layer 3 — Git pre-commit hook

`.git/hooks/pre-commit` (lives outside the repo working tree, must be installed per-clone):

```bash
#!/bin/bash
# SigRank canonical-file guard
# Refuses commits touching STONE paths without:
#   - LOCK_OVERRIDE in commit message, OR
#   - Matching decision-log entry in the same commit

set -e

STONE_PATHS_PATTERN='^1_sigrank/1\.1_layer-0-ground/|^1_sigrank/1\.2_layer-1-foundation/metrics/'
DECISION_LOG_PATTERN='^5_comms/decisions/layer-[0-9]-decisions\.md$'

# Get staged files
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)

# Check if any STONE files are being modified
STONE_TOUCHED=$(echo "$STAGED" | grep -E "$STONE_PATHS_PATTERN" || true)
if [ -z "$STONE_TOUCHED" ]; then
  exit 0
fi

# Check for LOCK_OVERRIDE in commit message
if [ -f .git/COMMIT_EDITMSG ] && grep -q "LOCK_OVERRIDE" .git/COMMIT_EDITMSG; then
  echo "✓ LOCK_OVERRIDE detected in commit message — proceeding"
  exit 0
fi

# Check for matching decision-log entry in same commit
DECISION_TOUCHED=$(echo "$STAGED" | grep -E "$DECISION_LOG_PATTERN" || true)
if [ -z "$DECISION_TOUCHED" ]; then
  echo ""
  echo "✗ BLOCKED: Commit modifies canonical paths but has no decision-log entry."
  echo ""
  echo "Canonical files in this commit:"
  echo "$STONE_TOUCHED" | sed 's/^/  /'
  echo ""
  echo "To proceed, either:"
  echo "  1. Add a decision-log entry to 5_comms/decisions/layer-X-decisions.md"
  echo "     in the same commit, OR"
  echo "  2. Add 'LOCK_OVERRIDE' to your commit message"
  echo ""
  echo "See 1_sigrank/1.1_layer-0-ground/guidance/LOCK_PROTOCOL.md"
  exit 1
fi

# Verify the decision-log entry mentions at least one of the touched canonical files
# (heuristic — looks for filename without extension in the staged diff of decision logs)
MATCH_FOUND=0
for STONE_FILE in $STONE_TOUCHED; do
  BASENAME=$(basename "$STONE_FILE" .md)
  if git diff --cached "$DECISION_TOUCHED" | grep -q "$BASENAME"; then
    MATCH_FOUND=1
    break
  fi
done

if [ "$MATCH_FOUND" -eq 0 ]; then
  echo ""
  echo "⚠ WARNING: Decision-log entry exists but doesn't reference any of the canonical files being modified."
  echo "  Canonical files: $STONE_TOUCHED"
  echo "  Decision log: $DECISION_TOUCHED"
  echo ""
  echo "  Proceeding anyway — but verify the decision log entry actually documents this change."
fi

echo "✓ Canonical modification authorized via decision-log entry"
exit 0
```

**Cost:** ~50-line shell script + a `git config core.hooksPath .githooks/` one-time setup so the hook lives inside the repo and clones with it.

**Effectiveness:** This would have caught commit `2c3b0be`. That commit modified canonical paths (deleted `02_sdrm.md`, edited CANON section structure, edited naming_drift.md, edited metric_family_tree.md) but had no corresponding operator-authored decision-log entry justifying SDOT/SDRM retirement. The hook would have refused to commit until that entry existed.

**Installation:** Add a `.githooks/pre-commit` file to the repo, then a one-time `git config core.hooksPath .githooks` per clone.

### Layer 4 — GitHub CODEOWNERS + branch protection

`.github/CODEOWNERS`:

```
# Canonical / etched-in-stone paths
/1_sigrank/1.1_layer-0-ground/**          @SunrisesIllNeverSee
/1_sigrank/1.2_layer-1-foundation/metrics/**  @SunrisesIllNeverSee
/5_comms/decisions/**                     @SunrisesIllNeverSee

# Lock protocol itself
/1_sigrank/1.1_layer-0-ground/guidance/LOCK_PROTOCOL.md  @SunrisesIllNeverSee
```

Then in GitHub repo settings → Branches → main:
- Enable "Require a pull request before merging"
- Enable "Require review from Code Owners"
- (Optional) "Require approvals: 1" to prevent self-merge on canonical PRs

**Cost:** One file commit + ~5 clicks in GitHub UI.

**Effectiveness:** Any PR touching canonical paths requires explicit approval. Direct pushes to `main` from another contributor get refused. Operator can still push directly because they own the protected paths.

---

## Modification workflow

When the operator wants to modify a STONE file:

### Step 1 — Issue `/PATCH` directive in chat
```
/PATCH
File: 1_sigrank/1.1_layer-0-ground/build/CANON.md
Section: IV. Composites
Change: Replace C.02 from Signal Force to SDOT
Reason: Big 3 composition corrected per operator
```

### Step 2 — Agent writes decision-log entry FIRST
Append to `5_comms/decisions/layer-1-decisions.md`:

```markdown
## YYYY-MM-DD · Composite C.02 reassigned from Signal Force to SDOT

**Decided by:** operator (chat /PATCH directive)
**Decision:** ...
**Affects:** CANON.md (Section IV), composites/02_sdot.md (new), composites/02_signal_force.md (move to extras/)
**Reversal cost:** ...
```

### Step 3 — Agent unlocks file
```bash
chmod 0644 1_sigrank/1.1_layer-0-ground/build/CANON.md
```

### Step 4 — Agent makes the edit

### Step 5 — Agent re-locks
```bash
chmod 0444 1_sigrank/1.1_layer-0-ground/build/CANON.md
```

### Step 6 — Agent commits with both files staged
The pre-commit hook verifies the decision-log entry is in the same commit. The commit succeeds.

### Step 7 — Lock state is preserved in git
On clone or checkout, the 0444 mode bit is restored.

---

## Emergency unlock

If something is structurally broken and the operator needs to bulk-edit canonical files:

```bash
# Temporarily disable the pre-commit hook
git -c core.hooksPath=/dev/null commit -m "Emergency bulk fix LOCK_OVERRIDE ..."

# Or use the LOCK_OVERRIDE keyword in the commit message
git commit -m "Bulk canonical fix per operator authorization — LOCK_OVERRIDE"
```

Both paths are logged in git history. The `LOCK_OVERRIDE` keyword is grep-able for audit.

---

## What this does NOT solve

This protocol prevents *unauthorized* modification. It does not:

- Prevent the operator from making mistakes
- Verify the *content* of a decision-log entry (only its presence)
- Detect semantic drift (e.g., an entry that says "minor cleanup" while deleting a core metric)
- Replace operator judgment

For semantic verification, the only mechanism is operator review of the diff before merge. The protocol forces that review to happen by requiring the decision log.

---

## Implementation order (recommended)

1. **Today (zero-tool):** Add sentinel headers to STONE files. Five minutes.
2. **Today:** `chmod 0444` STONE files. One bash command.
3. **This week:** Install the pre-commit hook. ~30 minutes including testing.
4. **Whenever you want:** CODEOWNERS + branch protection. ~10 minutes.

Each layer is independently useful. You can stop after Layer 2 if Layer 3 feels like overkill. But Layer 3 is what would have caught the Sonnet 4.6 retirement, so it has the highest ROI.

---

## Reference

Operator's instruction that prompted this protocol (2026-05-21):

> "any thoughts how we can create a document heirarchy... meaning when you attempt to add modifidy or delete anythign in production you first hit a wall making sure nothign gets disturbed?"

And:

> "everythign else looks good so make the edits"

This protocol is the proposed answer.
