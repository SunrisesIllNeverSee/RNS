# Layer 3 — Decision Log

Append-only record of decisions affecting the frontend layer (site architecture, mockups, components, UI patterns).

---

## 2026-05-19 · BlitzStars structural model adopted

**Decided by:** operator
**Decision:** SigRank frontend mirrors BlitzStars structure 1:1:
- Players → Operators · Clans → Circles · Tanks → Metrics · Tank Compare → Operator Compare · Zeitgeist Pro → Signalgeist Pro · Hall of Fame → Hall of Signal
- Region toggle (EU/NA/ASIA/RU) → Platform toggle (Claude/ChatGPT/Gemini/Pi/Multi)
- Multi-tier refresh cadences (live / 5min / hourly / daily)
- Precomputed cache reads, no live DB joins on page render
**Affects:** `site_architecture.md`
**Reversal cost:** High — it's the entire site model.

---

## 2026-05-19 · 12 TSX components shipped

**Decided by:** VSClaude-OPUS47-LEAD
**Decision:** Built 12 components in `Sigrank/components/sigrank/`:
- LeaderboardTable, ProfilePanel, AnalyticsDashboard, K2IndexSnapshot, WrappedStats, CrossPlatformLeaderboard, SignalSystemBoard, MetricTabs, SignalClassBadge, tokens, types, index
**Reversal cost:** Low — TSX components can be reworked anytime.

---

## 2026-05-20 · v4 mockup approved

**Decided by:** operator
**Decision:** v4 mockup design language (Geist + Geist Mono fonts, warm-gray dark palette, gold accent used sparingly, 88px hero headlines) is the target aesthetic.
**Affects:** `v4_mockup/intro.html`, `v4_mockup/index.html`, `v4_mockup/profile.html`
**Reversal cost:** Medium.

---

## 2026-05-20 · Score breakdown black-boxed

**Decided by:** operator
**Decision:** Profile score breakdown shows inputs → sealed "Scoring Engine" → result. Exact weights and class breakpoints are hidden as proprietary (RS.01, RS.05).
**Reasoning:** Protect the moat. Public sees the shape of the conversion; private engine holds the math.
**Affects:** `v4_mockup/profile.html`
**Reversal cost:** Low.

---

## 2026-05-21 · Asterisks + canonical IDs on mockups

**Decided by:** operator
**Decision:** Every number shown in mockups is either:
- Marked with `*` if placeholder (with tooltip explaining what's missing)
- Tagged with canonical ID (M.01, B.02, etc.) showing where it's rooted in CANON
**Reasoning:** Prevent hallucinated numbers from being treated as concrete. Every value traces to a database row or is flagged as placeholder.
**Affects:** `v4_mockup/intro.html`, `v4_mockup/index.html`, `v4_mockup/profile.html`, `DATA_LEDGER.md`
**Reversal cost:** Low.

---

## 2026-05-21 · Window selectors are Daily / 30 / 60 / 90 / All time

**Decided by:** operator
**Decision:** All window toggles use the five-option set above. Default is 30.
**Reasoning:** Matches operator's mental model and BlitzStars-style time slicing.
**Affects:** Every window selector across mockups, future Next.js implementation.
**Reversal cost:** Low.

---

## Open questions

1. Should profile pages have an explicit "day → session → minute" drilldown like BlitzStars' "day → tank → battle"? Operator mentioned wanting this.
2. Color palette for dark vs light mode — currently dark-only. Should we add light mode for parity with Linear / Vercel?
3. Mobile profile page layout — currently mostly desktop. What gets stacked vs hidden on mobile?
4. ProGate component pattern (blurred preview + Pro paywall overlay) — operator hasn't reviewed yet.
