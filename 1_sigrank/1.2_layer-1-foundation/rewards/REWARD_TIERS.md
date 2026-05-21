# Reward Tiers — what operators receive beyond rank

Badges (BG.xx) are recognition. Rewards are tangible benefits that come with class status, supporter tier, or specific achievements.

This document is the **definitions** layer. The reward fulfillment engine (granting / revoking benefits) lives in Layer 2.

Authoritative ID prefix: `RW.xx`

---

## Reward sources

| Source | What it grants | Layer |
|---|---|---|
| **Class tier** (K.01–K.09) | Auto-granted perks based on current class | Foundation |
| **Badge** (BG.xx) | One-time perk on badge award | Foundation |
| **Supporter tier** (paid) | Subscription benefits | Mechanics (billing) |
| **Hall of Signal** | Recognition + persistent perk | Foundation |

---

## Class-tier rewards

When an operator is assigned a class (K.xx), they auto-receive the rewards for that class. Demoting removes them; promoting upgrades.

| Class | RW ID | Reward |
|---|---|---|
| K.01 TRANSMITTER | RW.01 | Featured carousel placement (home page) |
| K.01 TRANSMITTER | RW.02 | Verified badge frame on profile |
| K.01 TRANSMITTER | RW.03 | Priority audit queue access |
| K.02 ARCHITECT+ | RW.04 | Profile glyph upgrade |
| K.02 ARCHITECT+ | RW.05 | Trend chart extended history (365d vs default 90d) |
| K.03 ARCHITECT | RW.06 | Per-metric historical drilldown unlocked |
| K.04 POWER | RW.07 | Compare engine — vs class average |
| K.05 BASE | RW.08 | Standard profile features (baseline) |
| K.06–K.09 | RW.09 | Public profile + leaderboard inclusion |

---

## Badge rewards (one-time on award)

| Badge | RW ID | Reward |
|---|---|---|
| BG.01 5x Crown | RW.10 | Permanent crown glyph on codename |
| BG.07 Audit Verified | RW.11 | "✓ Audit Verified" pill on profile |
| BG.09 Lightning Strike | RW.12 | "⚡ Largest Rise — [date]" stamp |
| BG.12 Fivefold Hold | RW.13 | Hall of Signal nomination (auto) |
| BG.13 First Transmitter | RW.14 | Permanent founder flair (gold border) |
| BG.16 Hall of Signal | RW.15 | Profile page reserved spot in Hall page |

---

## Supporter tier rewards

Separate from performance. Paid via Stripe (Layer 2 billing).

| Supporter tier | RW ID | Reward |
|---|---|---|
| Patron $5/mo | RW.16 | "🍻 Patron" badge (BG.14) |
| Patron $5/mo | RW.17 | Ad-free site (when ads land — currently none) |
| Patron $5/mo | RW.18 | Listed in random supporter carousel |
| Pro $19/mo | RW.19 | All Patron rewards |
| Pro $19/mo | RW.20 | sig_army Pro audit (precision-tier scoring) |
| Pro $19/mo | RW.21 | Drift Ratio (C.03) computed |
| Pro $19/mo | RW.22 | Score decomposition view |
| Pro $19/mo | RW.23 | Unlimited history depth |
| Pro $19/mo | RW.24 | API access (read + submit) |
| Clan/Circle Sponsor $99/mo | RW.25 | Circle logo in supporter carousel (header + footer) |
| Clan/Circle Sponsor $99/mo | RW.26 | All members of circle get Patron-tier rewards |
| Clan/Circle Sponsor $99/mo | RW.27 | Recruitment policy flag on circle page |

---

## Hall of Signal rewards (permanent recognition)

| Hall record | RW ID | Reward |
|---|---|---|
| Highest Compression Ever | RW.28 | Stamped on Hall page with operator codename + date |
| Deepest Single Session | RW.29 | Same |
| Most Cross-Thread Continuity | RW.30 | Same |
| Longest Transmitter Streak | RW.31 | Same |
| Largest 24h Rank Climb | RW.32 | Same |
| First Verified Transmitter | RW.33 | Same |
| Fivefold Hold Recipients | RW.34 | Listed on Hall page (multi-recipient) |

Hall recognitions are **persistent** — even if the operator is later surpassed, their original record stays on the Hall page as historical record.

---

## Grant / revoke protocol

1. **Class-tier rewards** — granted automatically by scoring engine on class assignment, revoked on demotion
2. **Badge rewards** — granted on badge award, NEVER revoked (badges are immutable history)
3. **Supporter rewards** — granted on Stripe webhook subscription.created, revoked on subscription.canceled or payment.failed (with grace period per billing/subscription_states.md)
4. **Hall rewards** — granted on Hall award, never revoked

---

## Reward fulfillment surface

Layer 2 (mechanics) is responsible for:
- Subscribing to badge engine events
- Granting/revoking reward flags in DB
- Triggering Layer 3 re-renders when rewards change
- Stripe webhook handling for supporter rewards

Layer 3 (frontend) is responsible for:
- Reading reward flags from DB
- Rendering reward visuals (glyphs, badges, frame upgrades, Hall sections)
- Showing locked rewards as "next tier unlocks RW.xx"

---

## Adding new rewards

When proposing a new reward:

1. Add row with next sequential RW.xx
2. Specify trigger source (class / badge / supporter / Hall)
3. Specify whether revocable
4. Specify Layer 3 display requirements
5. Note in `5_comms/decisions/layer-1-decisions.md`
