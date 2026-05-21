# Stripe Checkout UI

The frontend surface for upgrades, subscription management, and payment flow. Backend processing lives in Layer 2 (`billing/`).

---

## Surfaces

### 1. Upgrade CTA placements

| Placement | Trigger | CTA text |
|---|---|---|
| Profile page header | Always (if not Pro) | "★ Upgrade to Pro" |
| Snapshot publish flow | After first 3 publishes | "Unlock exact scoring → Pro" |
| Drift Ratio locked state | Hover/click on grayed-out C.03 | "See your Drift Ratio → Pro" |
| Compare engine modal | When clicking "Compare unlimited" | "Pro unlocks unlimited compares" |
| Score decomposition view | When clicking "See weights" | "Pro reveals your score breakdown" |
| Home page hero (logged-in non-Pro) | Banner above hero | "[X] operators upgraded this week →" |

---

### 2. Checkout flow

```
User clicks "Upgrade to Pro"
         ↓
Pricing modal opens (3 tiers: Patron / Pro / Circle Sponsor)
         ↓
User selects tier + billing period (monthly / yearly)
         ↓
Frontend calls POST /api/v1/billing/create-checkout-session
         ↓
Server returns Stripe Checkout Session URL
         ↓
Browser redirects to Stripe-hosted checkout
         ↓
User completes payment on Stripe
         ↓
Stripe redirects back to /upgrade/success?session_id=...
         ↓
Frontend shows "🎉 You're now {tier}" + immediate feature unlocks
         ↓
Backend processes webhook (Layer 2), grants rewards
```

### 3. Pricing modal layout

```
┌──────────────────────────────────────────────────────────────┐
│  Upgrade your SigRank                                    [×] │
│                                                              │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐    │
│  │   PATRON       │ │    PRO    ★    │ │  CIRCLE SPONSOR│    │
│  │   $5/mo        │ │   $19/mo       │ │   $99/mo       │    │
│  │                │ │   ($190/yr)    │ │                │    │
│  │ • Ad-free      │ │                │ │ • Pro for all  │    │
│  │ • Patron badge │ │ • All Patron + │ │   circle members│   │
│  │ • Supporter    │ │ • Exact scores │ │ • Carousel logo│    │
│  │   carousel     │ │ • Drift Ratio  │ │ • Recruitment  │    │
│  │                │ │ • API access   │ │   flag         │    │
│  │                │ │ • Audit Verified│ │                │   │
│  │                │ │                │ │                │    │
│  │ [Choose Patron]│ │ [Choose Pro]   │ │ [Contact Sales]│    │
│  └────────────────┘ └────────────────┘ └────────────────┘    │
│                                                              │
│  ✓ Cancel anytime · ✓ Pro-rated · ✓ All taxes included       │
└──────────────────────────────────────────────────────────────┘
```

Featured tier (Pro) has gold accent border, "★" indicator, slight elevation.

---

### 4. Manage subscription surface

`/account/subscription` page shows:

- Current tier + status
- Next billing date
- Card on file (last 4 digits)
- "Update card" → opens Stripe Customer Portal
- "Cancel subscription" → confirmation modal → Stripe portal cancellation
- "Switch to yearly" → updates plan (Stripe handles proration)
- Billing history (invoices) — links to Stripe-hosted invoice PDFs

All "manage" actions redirect to Stripe Customer Portal (we don't replicate Stripe's billing UI).

---

### 5. Success / cancel landing pages

**`/upgrade/success`**

```
🎉 Welcome to {tier}

Your features are unlocking now…

  ✓ Exact scoring via sig_army audit
  ✓ Drift Ratio computed
  ✓ Unlimited history depth
  ✓ Audit Verified badge

Setup is complete. Your next snapshot will use the new scoring.

[ Go to your profile ]  [ Run a test snapshot ]
```

**`/upgrade/canceled`**

```
No worries — you didn't get charged.

Free tier is still good. You can come back anytime.

[ Back to profile ]  [ Read about Pro tier ]
```

---

### 6. Card payment state UI

When subscription enters `past_due`:

```
┌──────────────────────────────────────────────────────────────┐
│ ⚠ Payment failed                                             │
│                                                              │
│ Your last payment didn't go through. We'll retry, but you    │
│ have 7 days to update your card before your tier reverts.    │
│                                                              │
│ [ Update card → Stripe ]    Days remaining: 5                │
└──────────────────────────────────────────────────────────────┘
```

Banner appears at top of every page until resolved.

---

### 7. Component map

| Component | File (proposed) | Used on |
|---|---|---|
| `<UpgradeCTA tier="pro" />` | `components/billing/UpgradeCTA.tsx` | Multiple surfaces |
| `<PricingModal />` | `components/billing/PricingModal.tsx` | Triggered from CTAs |
| `<CheckoutRedirect />` | `components/billing/CheckoutRedirect.tsx` | Pre-redirect spinner |
| `<SubscriptionStatus />` | `components/billing/SubscriptionStatus.tsx` | Profile header |
| `<ManageSubscription />` | `components/billing/ManageSubscription.tsx` | `/account/subscription` |
| `<PastDueBanner />` | `components/billing/PastDueBanner.tsx` | Site-wide banner |
| `<ProGate />` | `components/billing/ProGate.tsx` | Wraps locked features |

---

### 8. ProGate component pattern

Wraps Pro-only features with consistent gating UI:

```tsx
<ProGate
  feature="Drift Ratio (C.03)"
  preview={<BlurredValue value={87.3} />}
  rewardId="RW.21"
>
  <ActualDriftRatioChart />
</ProGate>
```

When user is non-Pro, shows blurred preview + "Pro unlocks this" overlay.
When user is Pro, renders children directly.

---

### 9. Stripe.js integration

Frontend loads Stripe.js from `https://js.stripe.com/v3/`:

```tsx
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
```

Use Stripe Checkout (hosted) rather than Stripe Elements (embedded) for MVP:
- Faster to ship
- Stripe handles PCI scope entirely
- Standard UX users recognize
- Customer Portal handles manage-subscription flows

Move to embedded Elements later if conversion data warrants it.

---

### 10. Analytics events to track

| Event | When |
|---|---|
| `upgrade_cta_clicked` | User clicks any upgrade CTA |
| `pricing_modal_opened` | Modal appears |
| `tier_selected` | User clicks a tier button |
| `checkout_redirected` | Stripe checkout session created |
| `checkout_completed` | Stripe redirects to /success |
| `checkout_canceled` | Stripe redirects to /canceled |
| `subscription_managed` | User clicks "Manage" |
| `payment_failed_banner_seen` | Banner displayed |
| `payment_card_updated` | Card update via portal completes |

Track in Vercel Analytics + send to PostHog (or whatever analytics service).

---

### 11. Mobile considerations

- Pricing modal is bottom-sheet on mobile instead of centered
- Stripe Checkout works mobile-native already
- Manage subscription redirects to Stripe portal which is mobile-optimized
- Past-due banner is dismissible (X button) but reappears next page load

---

## See also

- [`../layer-2-mechanics/billing/stripe_integration.md`](../layer-2-mechanics/billing/stripe_integration.md)
- [`../layer-2-mechanics/billing/webhook_handling.md`](../layer-2-mechanics/billing/webhook_handling.md)
- [`../layer-2-mechanics/billing/subscription_states.md`](../layer-2-mechanics/billing/subscription_states.md)
- [`../layer-1-foundation/rewards/REWARD_TIERS.md`](../layer-1-foundation/rewards/REWARD_TIERS.md)
- [`site_architecture.md`](site_architecture.md) — overall site map
