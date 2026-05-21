# Stripe Integration — backend processing

The server-side integration that handles subscription state, webhooks, customer records, and invoice events. The frontend checkout UI lives in Layer 3 (`stripe_checkout_ui.md`).

---

## Customer model

Each operator → one Stripe Customer record. Link via `operators.stripe_customer_id`.

```sql
ALTER TABLE operators
  ADD COLUMN stripe_customer_id TEXT UNIQUE,
  ADD COLUMN current_supporter_tier TEXT DEFAULT 'free';
  -- supporter_tier: free | patron | pro | circle_sponsor

CREATE TABLE subscriptions (
  subscription_id TEXT PRIMARY KEY,           -- Stripe sub ID
  operator_id UUID NOT NULL REFERENCES operators(operator_id),
  status TEXT NOT NULL,                       -- active, past_due, canceled, etc.
  tier TEXT NOT NULL,                         -- patron | pro | circle_sponsor
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_subscriptions_operator ON subscriptions(operator_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

---

## Stripe products + price IDs

Configured in Stripe dashboard, referenced by env vars:

| Tier | Product | Price | Stripe env var |
|---|---|---|---|
| Patron | "SigRank Patron" | $5/mo | `STRIPE_PRICE_PATRON_MONTHLY` |
| Pro | "Signalgeist Pro" | $19/mo | `STRIPE_PRICE_PRO_MONTHLY` |
| Pro (yearly) | "Signalgeist Pro yearly" | $190/yr | `STRIPE_PRICE_PRO_YEARLY` |
| Circle Sponsor | "Circle Sponsor" | $99/mo | `STRIPE_PRICE_CIRCLE_SPONSOR` |

---

## Webhook endpoint

Hosted as Supabase Edge Function at `/api/v1/billing/stripe-webhook`.

Verifies signature using `STRIPE_WEBHOOK_SECRET`.

Handles these events:

| Stripe event | Action |
|---|---|
| `checkout.session.completed` | Create subscription row, set tier on operator |
| `customer.subscription.created` | INSERT subscriptions row, set tier |
| `customer.subscription.updated` | UPDATE status, period dates, cancel_at_period_end |
| `customer.subscription.deleted` | UPDATE status = canceled, downgrade operator to free |
| `invoice.payment_succeeded` | Extend `current_period_end` |
| `invoice.payment_failed` | Set status = past_due, start grace period |
| `customer.subscription.trial_will_end` | (optional) Send reminder via notification service |

---

## Tier resolution logic

Operator's effective supporter tier is computed live from `subscriptions` table:

```python
def get_supporter_tier(operator_id):
    sub = query("""
        SELECT tier, status FROM subscriptions
        WHERE operator_id = ? AND status IN ('active', 'past_due', 'trialing')
        ORDER BY tier_priority(tier) DESC
        LIMIT 1
    """, operator_id)
    if not sub:
        return 'free'
    if sub.status == 'past_due':
        # within grace period (see subscription_states.md)
        return sub.tier  # still active
    return sub.tier
```

Tier priority (so multi-subscription operators get highest):
1. `circle_sponsor`
2. `pro`
3. `patron`
4. `free`

---

## Reward grant / revoke flow

When `current_supporter_tier` changes:

1. UPDATE `operators.current_supporter_tier`
2. Grant rewards per `layer-1-foundation/rewards/REWARD_TIERS.md` (RW.16–RW.27)
3. Trigger Layer 3 cache invalidation
4. Send notification (if notification service is enabled)

When subscription is canceled:
- If `cancel_at_period_end` — keep tier until `current_period_end`, then revoke
- If hard-canceled mid-period — revoke immediately, log to audit_trail

---

## Audit trail

Every Stripe webhook event → row in `audit_log`:

```sql
INSERT INTO audit_log (event_type, event_source, payload, operator_id, occurred_at)
VALUES ('stripe.subscription.updated', 'stripe', $payload_json, $operator_id, now());
```

This enables:
- Disputing of billing decisions
- Re-syncing if webhooks are missed
- Compliance (PCI-adjacent reasoning)

---

## Env vars required

```
STRIPE_SECRET_KEY=sk_live_...           # server-side calls
STRIPE_PUBLISHABLE_KEY=pk_live_...      # frontend Checkout Sessions
STRIPE_WEBHOOK_SECRET=whsec_...         # signature verification
STRIPE_PRICE_PATRON_MONTHLY=price_...
STRIPE_PRICE_PRO_MONTHLY=price_...
STRIPE_PRICE_PRO_YEARLY=price_...
STRIPE_PRICE_CIRCLE_SPONSOR=price_...
```

---

## Test mode protocol

- Local dev uses `sk_test_...` keys exclusively
- Test webhooks via `stripe listen --forward-to localhost:3000/api/v1/billing/stripe-webhook`
- Test customer IDs are sandboxed from production `operators` table via separate `stripe_customer_id_test` column (alternative: separate DB)

---

## See also

- [`webhook_handling.md`](webhook_handling.md) — detailed webhook event handling
- [`subscription_states.md`](subscription_states.md) — state machine for subscriptions
- [`../../../layer-3-frontend/stripe_checkout_ui.md`](../../layer-3-frontend/stripe_checkout_ui.md) — frontend checkout UI spec
