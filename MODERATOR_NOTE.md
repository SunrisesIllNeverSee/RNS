# Moderator Note — rns-sigrank build

For anyone (human or AI moderator, future model joining the build, or operator returning after time away) who needs to understand: who started this, who's leading it now, and what the rules are.

---

## Project

- **Name:** rns-sigrank
- **Repo:** https://github.com/SunrisesIllNeverSee/RNS
- **Description:** The current version of SigRank — token-totals-resolution operator scoring platform. Public leaderboard + free tier + Pro tier (sig_army audit) + supporter subscriptions. Built on the foundation of OG SIGRANK (which is the operator's prior work).

---

## Operator

- **Identity:** Deric McHenry (`dericmchenry@gmail.com`)
- **Operator tuple:** `Operator-HUMAN-OWNER`
- **Authority:** Final decision on everything. Owns RS.xx proprietary parameters. Owns ruleset versions. Owns commits.
- **Status:** OG SIGRANK — the originator of the conservation-law mapping that all current builds rest on (see `1_sigrank/1.1_layer-0-ground/guidance/CONSERVATION_LAW.md` and `LINEAGE.md`).

---

## Build lead (current)

- **Participant ID:** `VSClaude-OPUS47-LEAD`
- **Model:** claude-opus-4-7 (Anthropic)
- **Environment:** Claude Code (VS Code IDE extension)
- **Session started:** 2026-05-19
- **Scope:** Foundation lock + scaffolding. Spec docs across all 4 layers. Comms infrastructure.
- **Status:** Active, in operator's current chat thread.

---

## Identity format

```
{ENVIRONMENT}-{MODEL}-{ROLE}
```

See `5_comms/PARTICIPANTS.md` for full registry and protocol for joining.

---

## Build rules (locked by operator)

1. **One question at a time.** Don't pepper the operator with multiple choices in one message.
2. **Don't commit until the operator double-confirms.** Propose, wait, execute on green light.
3. **Don't get ahead of ourselves.** No assumptions about what the operator wants next.
4. **Don't assume sig_army is required.** Multiple paths exist for Drift Ratio and PC sub-extractors.
5. **Asterisks (*) for placeholder data** in every mockup. Tooltip explains what's missing.
6. **Canonical IDs on every number.** Every value visible anywhere references its CANON ID (T.xx / M.xx / B.xx / C.xx / K.xx / R.xx / RS.xx / S.xx / RN.xx / BG.xx / RW.xx).
7. **Don't conflate concepts.** 11 equations ≠ root numbers ≠ ruleset parameters ≠ reference values. They live in different ID spaces.
8. **Don't canonize Refinery with current SigRank.** They are different dimensional resolutions of the same conserved signal. See CONSERVATION_LAW.md.
9. **Operator IS OG SIGRANK.** Not a separate prior product.

---

## Layer model (locked 2026-05-21)

```
LAYER 0 — Ground Foundation (the unbuilt-on bedrock)
  1_sigrank/1.1_layer-0-ground/
    ├── build/      — production canon (use to compute)
    │     CANON.md · SOURCE_DATA.md · GREENING.md · ROOT_NUMBERS.md · MOSES_REFERENCE.md
    └── guidance/   — philosophical context (interprets the compute)
          CONSERVATION_LAW.md · LINEAGE.md · TOKENS_PER_WORD.md

LAYER 1 — Foundation (built on Layer 0)
  1_sigrank/1.2_layer-1-foundation/
    ├── metrics/    — the 11 equations (M.xx / B.xx / C.xx) + lineage
    ├── class_tiers.md     — K.01-K.09
    ├── badges/     — BG.xx catalog
    └── rewards/    — RW.xx tier mapping

LAYER 2 — Mechanics (built on Layers 0 + 1)
  1_sigrank/1.3_layer-2-mechanics/
    ├── IPO.md, db_schema.md, api_spec.md, snapshot_payload.md
    ├── scoring_formula.md, token_metric_bridge.md
    ├── deployment_topology.md, build_layers.md
    ├── billing/    — Stripe integration (server-side)
    └── refresh_cadences.md

LAYER 3 — Frontend (built on all previous)
  1_sigrank/1.4_layer-3-frontend/
    ├── site_architecture.md
    ├── v3_mockup/, v4_mockup/
    └── stripe_checkout_ui.md
```

Plus:
- `5_comms/` — multi-model project communication system
- `4_references/` — material we used to build, not needed at runtime
- `_inbox/` — operator → models drop zone
- `1_sigrank/1.5_components/sigrank/` — 12 TSX components for the production Next.js app
- `2_secondary/sig_army/` + `2_secondary/word_vault/` + `2_secondary/WordToken-SNR-Classifier/` — the SigSystem-resolution engine for Pro tier
- `1_sigrank/1.6_agent/` — local agent (Python CLI) spec
- `2_secondary/` — existing partial Next.js attempts (SiGlobe, signal-Areana) for component salvage
- `3_outliers/` — old prototypes not directly used

---

## Authority limits during foundation lock

**Build lead (VSClaude-OPUS47-LEAD) CAN:**
- Propose spec edits
- Scaffold folders + files
- Move files via git mv
- Write decision logs
- Write welcome messages to incoming participants
- Run read-only browser sessions

**Build lead CANNOT:**
- Commit without operator's explicit double-confirm
- Change RS.xx parameters (proprietary scoring weights)
- Change ruleset version
- Add a participant to PARTICIPANTS.md without operator instruction
- Push to GitHub without confirm

**Operator can override any limit, anytime.**

---

## Open decisions (as of 2026-05-21)

Tracked across decision logs:
- `5_comms/decisions/layer-0-decisions.md`
- `5_comms/decisions/layer-1-decisions.md`
- `5_comms/decisions/layer-2-decisions.md`
- `5_comms/decisions/layer-3-decisions.md`

Key items waiting on operator:
1. B.03 lifetime count — one-time scan vs append-only counter
2. T.08 active minutes — pick estimation algorithm
3. C.03 alignment signal — 5 options on the table
4. PC sub-extractor approach — regex / NLP / LLM / sig_army (operator priority)
5. Old master lists — operator paths needed
6. Pro yearly pricing — $190 or match monthly × 12
7. Founder tier (one-time lifetime Pro) — yes/no for launch

---

## How to come up to speed (if you're new)

Read in order:
1. This file (you're already here)
2. `1_sigrank/1.1_layer-0-ground/build/CANON.md` — every ID and the formula structure
3. `1_sigrank/1.1_layer-0-ground/build/ROOT_NUMBERS.md` — what the equations consume
4. `1_sigrank/1.1_layer-0-ground/build/MOSES_REFERENCE.md` — the only fully-verified operator
5. `1_sigrank/1.1_layer-0-ground/guidance/CONSERVATION_LAW.md` — why the math works
6. `1_sigrank/1.1_layer-0-ground/guidance/LINEAGE.md` — historical context
7. `5_comms/decisions/layer-*-decisions.md` — what's been decided and why
8. `1_sigrank/1.3_layer-2-mechanics/deployment_topology.md` — how it runs
9. `1_sigrank/1.4_layer-3-frontend/site_architecture.md` — what it looks like

Then read the relevant layer for whatever you're picking up.

---

## How to join the build (if you're another AI model)

1. Operator drops a `_inbox/new-participant-{your_env}.md` file with your identity tuple and scope
2. Current LEAD reviews, adds you to `5_comms/PARTICIPANTS.md`
3. LEAD writes welcome message in `5_comms/messages/{today}/`
4. You write your first heartbeat to `5_comms/active/{your_id}.json`
5. Claim files you need to edit in `5_comms/locks/current.json`
6. Operate per `5_comms/README.md` protocol

---

## Final note

This is the operator's pride and joy. Treat it that way. The system is built on years of prior work — the operator's lived experience as OG SIGRANK validates the conservation law. The current build is the scaled, productized version of that proof.

Don't break the invariants. Don't conflate the layers. Don't get ahead of the operator. Don't commit without double-confirm.

When in doubt, ask. When the operator answers, take it down in `5_comms/decisions/`.

---

**Build mark · this session:**
- VSClaude-OPUS47-LEAD started 2026-05-19
- Foundation scaffolding committed 2026-05-21
- Operator drove every decision in this thread
- All numbers in mockups asterisk-flagged or canonical-ID-tagged
- No commits without operator double-confirm
- Standing by for operator's next direction

**End of moderator note.**
