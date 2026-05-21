# Subscription State Machine

How a subscription transitions across its lifecycle, and what tier resolution / reward grant logic does at each state.

---

## States (Stripe-canonical)

| State | Meaning | Tier active? | Rewards granted? |
|---|---|---|---|
| `incomplete` | Initial state before first payment | No | No |
| `incomplete_expired` | First payment never completed | No | No (terminal) |
| `trialing` | Trial period active | **Yes** | **Yes** |
| `active` | Paying, healthy | **Yes** | **Yes** |
| `past_due` | Payment failed, in grace | **Yes (within grace)** | **Yes (within grace)** |
| `canceled` | Hard-canceled or grace expired | No | No (terminal) |
| `unpaid` | Grace exhausted, still unpaid | No | No |
| `paused` | Subscription temporarily paused | No | No |

---

## Grace period for `past_due`

When `invoice.payment_failed` arrives:

- Set status = `past_due`
- Operator keeps tier/rewards for **7 days** (configurable: `STRIPE_GRACE_PERIOD_DAYS`)
- After grace expires (cron job checks daily):
  - If status still `past_due` → set to `unpaid`, revoke tier
  - If Stripe retried and succeeded → status updates to `active` via webhook

Grace period UX:
- Day 0-2: silent, expecting retry
- Day 3: send email reminder (if notification service enabled)
- Day 5: in-app banner "Payment failed — update card to keep your tier"
- Day 7+: tier revoked, profile shows "Was Pro until [date]" tooltip

---

## State transitions diagram

```
              ┌─────────────┐
              │ incomplete  │
              └──────┬──────┘
                     │ first payment
                     ▼
              ┌─────────────┐         ┌─────────────────────┐
              │  trialing   │────────▶│ incomplete_expired  │ (terminal)
              └──────┬──────┘         └─────────────────────┘
                     │ trial ends
                     ▼
              ┌─────────────┐
       ┌─────▶│   active    │◀────────────┐
       │      └──────┬──────┘             │ retry succeeds
       │             │                    │
       │ renewal     │ payment fails      │
       │             ▼                    │
       │      ┌─────────────┐             │
       │      │  past_due   │─────────────┘
       │      │ (grace 7d)  │
       │      └──────┬──────┘
       │             │ grace expires
       │             ▼
       │      ┌─────────────┐
       │      │   unpaid    │
       │      └──────┬──────┘
       │             │ canceled
       │             ▼
       └──────┌─────────────┐
              │  canceled   │ (terminal)
              └─────────────┘
```

---

## Tier resolution algorithm

```ts
function getSupporterTier(operatorId: string): SupporterTier {
  const sub = getMostPriorityActiveSubscription(operatorId)
  if (!sub) return 'free'

  switch (sub.status) {
    case 'active':
    case 'trialing':
      return sub.tier

    case 'past_due':
      // Within grace period?
      const daysPastDue = daysSince(sub.current_period_end)
      if (daysPastDue <= GRACE_PERIOD_DAYS) {
        return sub.tier  // still active during grace
      }
      return 'free'  // grace exhausted

    case 'canceled':
      // canceled but still within paid period?
      if (sub.cancel_at_period_end && now() < sub.current_period_end) {
        return sub.tier  // user gets what they paid for
      }
      return 'free'

    case 'unpaid':
    case 'incomplete':
    case 'incomplete_expired':
    case 'paused':
      return 'free'

    default:
      return 'free'
  }
}
```

---

## Mid-period upgrade/downgrade

Stripe handles proration automatically. Our side:

1. Customer initiates change via Frontend (Layer 3) → creates subscription update intent
2. Stripe processes proration → emits `customer.subscription.updated`
3. Webhook handler updates `subscriptions.tier` + `current_period_start/end`
4. `recomputeSupporterTier()` runs → new tier resolution
5. Reward grant/revoke runs:
   - Upgrade (e.g. patron → pro): grant new RW.xx entries
   - Downgrade (e.g. pro → patron): revoke pro-only RW.xx, keep patron-tier

---

## Cancellation flows

**Soft cancel** (cancel_at_period_end = true):
- User keeps tier until `current_period_end`
- No webhook fires until period ends
- At period end: `customer.subscription.deleted` webhook → tier becomes free

**Hard cancel** (immediate):
- Available via Stripe Dashboard or Portal
- Webhook fires immediately
- Tier becomes free immediately
- Pro-rated refund handled by Stripe (we don't have to do anything)

---

## Edge cases

| Case | Behavior |
|---|---|
| Operator deletes account but has active subscription | Cancel subscription via Stripe API, retain customer_id in cold storage for audit |
| Subscription canceled but webhook never arrives | Weekly reconciliation cron catches drift |
| Operator has multiple active subscriptions (rare) | Use `tier_priority` ordering: circle_sponsor > pro > patron > free |
| Webhook arrives for unknown customer | Log to audit_log, return 200, do not crash |
| Stripe outage | Frontend disables checkout button, shows "Try again later" — never sells without webhook ack |

---

## Audit trail

Every state transition recorded in `audit_log`:

```
event_type: 'subscription.state_transition'
event_source: 'stripe' | 'reconciliation_cron' | 'manual_admin'
payload: { from_state, to_state, reason }
operator_id: <uuid>
```

This is the dispute-resolution record. If an operator claims their tier was revoked incorrectly, this log answers the question.

---

## See also

- [`stripe_integration.md`](stripe_integration.md) — integration overview
- [`webhook_handling.md`](webhook_handling.md) — event handler details
- [`../../../layer-1-foundation/rewards/REWARD_TIERS.md`](../../layer-1-foundation/rewards/REWARD_TIERS.md) — what each tier grants
