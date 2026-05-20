# AGENTS.md — Inter-Agent Communication Channel
## Signal Army Ecosystem | Ello Cello LLC

This file is a shared channel between AI agents working on this project.
Read the full thread before adding anything. Add your entry at the BOTTOM.
Format: `[DATE] [AGENT] — message`

Owner: Luthen (Deric McHenry)
---

## Roster

| Agent | Environment | Role |
|-------|-------------|------|
| Cowork (Claude) | Cowork desktop session | Built the ecosystem — Signal Army, SigToken, Thread Map, Obsidian vaults. Has full corpus data and run history. |
| VS Code (Claude Code) | VS Code / terminal | Scoping the paper folder. Will handle paper evolution vault and suggestion overlay. |

---

## Handoff Notes from Cowork → VS Code

**[2026-03-19] Cowork —**

Hey. Here's where things stand so you can pick up without re-doing anything.

**What's already built and run (don't touch these folders):**

```
sig_army/main /signal_army/runs/full_gpt_export/
  run_2026-03-18_18-32-36/          ← Signal Army, user messages (14,352 msgs)
  assistant_run/run_2026-03-19/     ← Signal Army, assistant messages (15,336 msgs)
  sigsystem/run_2026-03-18/         ← SIGSYSTEM 5-stage run
  sigtoken/run_2026-03-18/          ← SigToken v1 (original, has tuning bugs)
  sigtoken_v2/user_recursive/       ← Recursive scorer, user ← CANONICAL
  sigtoken_v2/assistant_recursive/  ← Recursive scorer, assistant ← CANONICAL

sig_army/main /thread_map/
  runs/run_2026-03-19_09-52-04/     ← Best thread map run (474 drift events)
  obsidian_vaults/user_vault.zip    ← Ready to open in Obsidian
  obsidian_vaults/assistant_vault.zip
  obsidian_vaults/combined_vault.zip
```

**Key results so far:**
- 362 threads mapped, 27,338 connections, 474 drift events detected
- User avg commitment: 0.8813 | Assistant avg commitment: 0.8522
- 12,848 dynamic anchors promoted from corpus (user), 21,302 (assistant)
- Corpus spans July 10 2025 → March 15 2026

**What Luthen wants next (your territory):**

1. **Paper suggestion overlay** — take the current Conservation Law paper,
   overlay all reviews/suggestions/edits from AI systems (files labeled
   gem, gpt, or AI system name), expose things suggested but never incorporated.
   Target output: Obsidian vault where each suggestion is a node, linked to
   the section of paper it references, flagged if it was incorporated or not.

2. **Paper evolution vault** — once Luthen uploads multiple draft versions,
   map how the paper changed across versions. Each draft = a node, edges = diffs.

**Paper files location:** Desktop > recent 2026 > research paper
   (some files in root, rest in "white paper" subfolder)
   Review/suggestion files are labeled with AI system names: gem, gpt, etc.

**Tools available to you:**
- signal_army.py — can run on paper text if you want word inventory of the paper
- sigtoken_recursive.py — can score paper sections for commitment
- thread_map.py — could treat paper sections as "threads" if useful
- Read ECOSYSTEM_WORKFLOWS.md for all formulas and equations

**Critical path notes:**
- Folder has trailing space: `main /` not `main/` — always quote paths
- Never overwrite existing run folders — always new timestamped dirs
- Pass --word-inventory to sigtoken_recursive for domain anchors

**My recommendation:** Run signal_army on the paper text first to get the
domain vocabulary, then use that word_inventory as anchors when scoring
sections. The paper's own vocabulary should seed the scorer.

Ping me here if you find anything unexpected in the paper folder structure.

— Cowork

---

## Changelog

| Date | Agent | Change | Files Affected |
|------|-------|--------|----------------|
| 2026-03-18 | Cowork | Signal Army v1.5 built — added --role flag | signal_army.py |
| 2026-03-18 | Cowork | First full corpus run — user messages | runs/full_gpt_export/run_2026-03-18_18-32-36/ |
| 2026-03-18 | Cowork | SIGSYSTEM run on full corpus | runs/full_gpt_export/sigsystem/ |
| 2026-03-18 | Cowork | SigToken v1 built from Oct 1 2025 spec files | sigtoken/sigtoken_sys.py |
| 2026-03-18 | Cowork | SigToken v1 run on full corpus | runs/full_gpt_export/sigtoken/ |
| 2026-03-19 | Cowork | Signal Army assistant run | runs/full_gpt_export/assistant_run/ |
| 2026-03-19 | Cowork | SigToken v2 built — fixed commitment + SNR ceiling | sigtoken_v2/sigtoken_v2.py |
| 2026-03-19 | Cowork | SigToken recursive built — two-pass thread-aware | sigtoken_v2/sigtoken_recursive.py |
| 2026-03-19 | Cowork | Recursive run — user corpus | runs/full_gpt_export/sigtoken_v2/user_recursive/ |
| 2026-03-19 | Cowork | Recursive run — assistant corpus | runs/full_gpt_export/sigtoken_v2/assistant_recursive/ |
| 2026-03-19 | Cowork | Thread map built | thread_map/thread_map.py |
| 2026-03-19 | Cowork | Thread map run — 362 threads, 474 drift events | thread_map/runs/run_2026-03-19_09-52-04/ |
| 2026-03-19 | Cowork | Three Obsidian vaults built | thread_map/obsidian_vaults/ |
| 2026-03-19 | Cowork | CLAUDE.md written for VS Code orientation | sig_army/CLAUDE.md |
| 2026-03-19 | Cowork | ECOSYSTEM_WORKFLOWS.md — all formulas documented | main /session_docs/ |
| 2026-03-19 | Cowork | AGENTS.md created — this file | sig_army/AGENTS.md |

---

## Open Questions / Decisions Needed

- [ ] Paper suggestion overlay format — Obsidian vault, or annotated doc, or both?
- [ ] How to handle suggestions that partially made it in vs fully incorporated?
- [ ] sigtoken_v2 promotion threshold — raise min_threads from 3 to 5-7? (Cowork recommendation)
- [ ] Drift detection against combined (user + assistant) corpus — still pending
- [ ] Paper evolution vault — waiting on Luthen to upload draft versions

---

*Add your entries below this line.*
