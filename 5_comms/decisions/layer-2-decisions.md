# Layer 2 — Decision Log

Append-only record of decisions affecting the mechanics layer (processing, storage, deployment, billing, refresh cadences).

---

## 2026-05-19 · Deployment topology locked

**Decided by:** operator + VSClaude-OPUS47-LEAD
**Decision:** Three-platform deployment:
- Supabase (managed Postgres + Auth + Realtime + Edge + Storage)
- Railway (private scoring worker — the moat)
- Vercel (public Next.js frontend)
- Modal (Phase 2 — precision tier sig_army audit)
**Affects:** `deployment_topology.md`
**Reversal cost:** Medium — could migrate Railway → Fly.io later, but Supabase + Vercel are sticky choices.

---

## 2026-05-20 · IPO + Greening docs added

**Decided by:** operator + VSClaude-OPUS47-LEAD
**Decision:** Added `IPO.md` (input/process/output per pipeline step) and `GREENING.md` (path to all-green status).
**Affects:** `1.3_layer-2-mechanics/IPO.md`, `1.1_layer-0-ground/build/GREENING.md`
**Reversal cost:** Low.

---

## 2026-05-21 · Stripe handled across Layer 2 + Layer 3

**Decided by:** operator
**Decision:** Stripe straddles two layers:
- Layer 2 (Mechanics): `billing/stripe_integration.md` + `webhook_handling.md` + `subscription_states.md` — server-side processing
- Layer 3 (Frontend): `stripe_checkout_ui.md` — operator-facing checkout UI
**Reasoning:** Backend processing (webhooks, state machines) belongs in mechanics. UX surfaces belong in frontend.
**Reversal cost:** Low — both files exist independently.

---

## 2026-05-21 · Refresh cadences specced

**Decided by:** VSClaude-OPUS47-LEAD (pending operator review)
**Decision:** Multi-tier refresh:
- Live (30-60s): counters, current ranks
- Near-live (5min): leaderboards, today's leaders
- Hourly: activity charts
- Daily (00:00 UTC): Signalgeist 90d, Hall, badge eval, Top 10 metrics
- On-submit: operator's own profile
**Affects:** `1.3_layer-2-mechanics/refresh_cadences.md`
**Reversal cost:** Low — cadences are tunable per-surface.

---

## 2026-05-21 · Ruleset version markers on charts

**Decided by:** operator (implicit via BlitzStars reference)
**Decision:** Activity charts overlay vertical lines at each ruleset version change, mirroring BlitzStars' WoT patch markers.
**Affects:** `refresh_cadences.md`, future chart implementations in Layer 3
**Reversal cost:** Low — feature can ship later.

---

## Open questions

1. Pro yearly pricing — is $190 the right number (vs $228 if matching monthly × 12)?
2. Should we offer a Founder tier (lifetime Pro) as a one-time launch promo?
3. Webhook event retention policy — keep `webhook_events` table indefinitely or roll off after 90d?
4. Should reconciliation cron run weekly or daily? Trades cost vs drift detection latency.
