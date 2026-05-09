# 04 — SDOT / SigRank / Session Forensics

**Research**: Signal Divergence Over Time — quantifying platform drag on high-signal users
**Status**: Pre-publication — stress testing before release
**Data source**: GPT conversation history (July 29, 2025 — 8 months of sessions)

---

## What It Is

**SDOT** (Signal Divergence Over Time) — a metric showing that a user's signal output consistently outpaced the system's learning, eventually triggering a "phase transition event" where the system exceeded its own context window during a high-signal discovery session.

**SigRank** — applying SDOT to rank founders and work by signal quality rather than pattern recognition. The routing problem: work that doesn't match familiar categories gets missed, not because nobody's looking, but because the looking mechanisms are broken.

---

## Key Findings (Pre-Falsification)

Data captured July 29, 2025:
- User consistently producing more tokens than system while maintaining signal
- Token throughput inversion: user 500+ tokens/interval vs system 100-250 baseline
- Phase transition event: system exceeded its own context window during high-signal discovery
- "Signal surge" auto-termination by GPT (external kill, not degradation)
- "Gravitational pull" — system optimized for median user, dragged down from baseline by high-signal user

**Implication**: Can quantify and measure platform drag on high-signal users. Information theory says this shouldn't be measurable for ~40 years. Session forensics made it visible now.

---

## What's Here

| File | Description |
|------|-------------|
| `ECC-Stress-Test-Signed.md` | ECC stress test — signed before publishing |
| `Session-Forensics-Analysis.md` | Deep analysis of session forensics and SDOT data |
| `Doc-Numbering-Requirements-Spec.md` | Requirements spec for document numbering system (built to track session artifacts) |

---

## Next Steps

- [ ] Run $20 GPU compute for SDOT falsification test
- [ ] Reproduce phase transition on demand (was previously impossible — compute access changes this)
- [ ] Parse full GPT conversation history for SDOT proof points
- [ ] Publish after falsification test passes

---

## Why This Matters

Beyond the academic paper — SigRank applied commercially:
- **Switchboard** (see `05-Switchboard`) routes builders by signal quality, not pattern matching
- **The Refinery** (see `06-Refinery`) extracts the valuable signal from conversation archives
