# Stripe Webhook Handling

Detailed event handling per webhook type. The endpoint is implemented as a Supabase Edge Function at `/api/v1/billing/stripe-webhook`.

---

## Verification

```ts
const sig = request.headers.get('stripe-signature')
const payload = await request.text()
let event: Stripe.Event

try {
  event = stripe.webhooks.constructEvent(payload, sig, STRIPE_WEBHOOK_SECRET)
} catch (err) {
  return new Response('Invalid signature', { status: 400 })
}
```

If signature verification fails → 400, log to audit_log, do nothing else.

---

## Idempotency

Stripe may deliver the same webhook multiple times. Use `event.id` (e.g., `evt_xxx`) as idempotency key:

```sql
CREATE TABLE webhook_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  received_at TIMESTAMPTZ DEFAULT now(),
  processed_at TIMESTAMPTZ,
  payload_json JSONB NOT NULL
);
```

On receive:
1. INSERT INTO webhook_events ON CONFLICT (event_id) DO NOTHING
2. If row already existed (no insert) → 200 immediately, no-op
3. Otherwise, process the event, then UPDATE processed_at

---

## Event handlers

### `checkout.session.completed`

Triggered when a checkout flow completes (whether subscription or one-time).

```ts
const session = event.data.object as Stripe.Checkout.Session
const customerId = session.customer
const subscriptionId = session.subscription
const operatorId = session.metadata.operator_id  // we set this in checkout

// Link customer to operator
await db.query(`
  UPDATE operators SET stripe_customer_id = $1 WHERE operator_id = $2
`, [customerId, operatorId])

// The subscription.created event will follow — let that handle subscriptions table
```

### `customer.subscription.created`

```ts
const sub = event.data.object as Stripe.Subscription
const tier = mapPriceToTier(sub.items.data[0].price.id)
const operatorId = await lookupOperatorByCustomer(sub.customer)

await db.query(`
  INSERT INTO subscriptions (subscription_id, operator_id, status, tier, current_period_start, current_period_end, cancel_at_period_end)
  VALUES ($1, $2, $3, $4, to_timestamp($5), to_timestamp($6), $7)
  ON CONFLICT (subscription_id) DO UPDATE SET
    status = EXCLUDED.status,
    tier = EXCLUDED.tier,
    current_period_start = EXCLUDED.current_period_start,
    current_period_end = EXCLUDED.current_period_end,
    cancel_at_period_end = EXCLUDED.cancel_at_period_end,
    updated_at = now()
`, [sub.id, operatorId, sub.status, tier, sub.current_period_start, sub.current_period_end, sub.cancel_at_period_end])

await recomputeSupporterTier(operatorId)
await grantRewards(operatorId, tier)
await invalidateProfileCache(operatorId)
```

### `customer.subscription.updated`

Same as `created` (upsert pattern). Stripe sends this for ANY change — including renewals, plan changes, cancellation scheduling.

### `customer.subscription.deleted`

```ts
const sub = event.data.object as Stripe.Subscription

await db.query(`
  UPDATE subscriptions SET status = 'canceled', updated_at = now()
  WHERE subscription_id = $1
`, [sub.id])

const operatorId = await lookupOperatorBySubscription(sub.id)
await recomputeSupporterTier(operatorId)
await revokeRewards(operatorId)
await invalidateProfileCache(operatorId)
```

### `invoice.payment_succeeded`

```ts
const invoice = event.data.object as Stripe.Invoice
const subId = invoice.subscription

// Refresh subscription state from Stripe (period dates updated)
const sub = await stripe.subscriptions.retrieve(subId)
// Trigger subscription.updated handler logic
```

### `invoice.payment_failed`

```ts
const invoice = event.data.object as Stripe.Invoice

await db.query(`
  UPDATE subscriptions SET status = 'past_due', updated_at = now()
  WHERE subscription_id = $1
`, [invoice.subscription])

// Tier stays until grace period expires (see subscription_states.md)
await notifyOperatorOfPaymentFailure(invoice)
```

---

## Helper: mapPriceToTier

```ts
const PRICE_TO_TIER: Record<string, string> = {
  [STRIPE_PRICE_PATRON_MONTHLY]: 'patron',
  [STRIPE_PRICE_PRO_MONTHLY]: 'pro',
  [STRIPE_PRICE_PRO_YEARLY]: 'pro',
  [STRIPE_PRICE_CIRCLE_SPONSOR]: 'circle_sponsor',
}

function mapPriceToTier(priceId: string): string {
  return PRICE_TO_TIER[priceId] || 'unknown'
}
```

---

## Failure recovery

If webhook processing crashes mid-flight:

1. Stripe will retry (exponential backoff up to 3 days)
2. Idempotency key (event_id) prevents double-processing
3. Manual recovery: `stripe events resend evt_xxx`
4. Worst case: weekly cron job reconciles subscriptions table against Stripe API

```ts
// Reconciliation cron (weekly)
async function reconcileSubscriptions() {
  const localSubs = await db.query('SELECT subscription_id FROM subscriptions WHERE status != $1', ['canceled'])
  for (const localSub of localSubs) {
    const remoteSub = await stripe.subscriptions.retrieve(localSub.subscription_id)
    if (remoteSub.status !== localSub.status) {
      console.warn(`drift detected: ${localSub.subscription_id}`)
      await syncSubscriptionState(remoteSub)
    }
  }
}
```

---

## Security notes

- Webhook secret rotated quarterly
- Edge function uses environment-bound secrets only (never in source)
- All webhook events logged to `audit_log` for forensic review
- PII (email, name) only stored if customer explicitly provides — Stripe Customer ID is the join key
