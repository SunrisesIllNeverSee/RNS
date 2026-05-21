# Badge Ledger — canonical badge catalog

Every badge SigRank can award, with award criteria, rarity, and category. The badge **engine** (evaluator) lives in Layer 2; this is the **catalog** (definitions).

Authoritative ID prefix: `BG.xx`

---

## Categories

| Category | Meaning |
|---|---|
| **Structural** | Awarded for objective metric thresholds (e.g., held all 5 Core metrics) |
| **Event** | Awarded for one-time achievements with a date (e.g., largest 24h rise) |
| **Prestige** | Awarded for sustained excellence over time (e.g., 30-day streak) |
| **Audit** | Awarded for verified status (e.g., Pro-tier audit pass) |
| **Patron** | Awarded for supporter tier (separate from performance) |

---

## Rarity

| Rarity | Award rate target |
|---|---|
| **Common** | >10% of active operators |
| **Rare** | 1–10% |
| **Epic** | 0.1–1% |
| **Legendary** | <0.1% |

---

## The catalog

| ID | Badge | Category | Rarity | Criteria | Glyph |
|---|---|---|---|---|---|
| **BG.01** | 5x Crown | Structural | Epic | Held #1 in all 5 Core metrics simultaneously (single window) | ⭐ |
| **BG.02** | Transmitter Class | Structural | Rare | Compression ≥ 0.85 AND SIGNA RATE ≥ 85 | ◈ |
| **BG.03** | Architect Lock | Prestige | Rare | Sustained ARCHITECT+ class for 14+ days | ▲ |
| **BG.04** | Crossweaver | Structural | Rare | CT score in top 1% for the window | 🌊 |
| **BG.05** | Deep Channel | Structural | Rare | Session Depth raw ≥ 30 sustained 7 days | ⌬ |
| **BG.06** | Compression Forge | Structural | Epic | Compression ≥ 0.85 sustained through MV in top 10% (busy AND clean) | ⚒ |
| **BG.07** | Audit Verified | Audit | Rare | Pro-tier sig_army audit completed and confirmed | 🛡 |
| **BG.08** | Ghost Return | Event | Rare | Reactivation after dormancy (>30d idle, then re-publishes) | 👻 |
| **BG.09** | Lightning Strike | Event | Epic | Largest 24h SIGNA RATE rise on the leaderboard for that day | ⚡ |
| **BG.10** | Quiet Giant | Structural | Rare | Compression ≥ 0.85 AND Message Volume in bottom 50% (low chatter, high signal) | ❄ |
| **BG.11** | Iron Streak | Prestige | Rare | 30+ consecutive active days | 🔥 |
| **BG.12** | Fivefold Hold | Prestige | Legendary | Held BG.01 (5x Crown) for 7+ consecutive days | ⭐⭐⭐⭐⭐ |
| **BG.13** | First Transmitter | Event | Legendary | First-ever Transmitter-class assignment in their platform region | ◈⃝ |
| **BG.14** | Signal Patron | Patron | Common | Active Supporter tier (any payment) | 🍻 |
| **BG.15** | Circle Founder | Event | Rare | Founded a Circle with ≥ 5 active members | 🏛 |
| **BG.16** | Hall of Signal | Event | Legendary | Recipient of any Hall of Signal record | 🏆 |

---

## Award protocol

The badge engine (Layer 2) evaluates criteria on every scoring cycle (daily). On match:

1. INSERT INTO `operator_badges` (operator_id, badge_id, awarded_at, source_snapshot_id)
2. UNIQUE constraint on (operator_id, badge_id) — no duplicate awards of the same badge
3. EXCEPT for Event-category badges, which may be awarded multiple times (each with a unique `awarded_at`)
4. Trigger notification (Layer 2 notification service)
5. Trigger profile re-render (Layer 3)

---

## Display protocol

- **Profile page (Layer 3):** Badge case showing earned badges; locked badges greyed out with criteria visible
- **Leaderboard row:** Top 3 most prestigious badges shown as small glyphs next to codename
- **Hover tooltip:** Show badge name + when awarded
- **Public verifiability:** Each badge award has a `source_snapshot_id` pointing to the snapshot that earned it — verifiable per CANON RS protocol

---

## Adding new badges

When proposing a new badge:

1. Add row to this catalog with next sequential BG.xx
2. Define criteria in terms of existing M.xx / B.xx / C.xx / K.xx values
3. Estimate target rarity
4. Define glyph and category
5. If criteria reference RS.xx proprietary parameters, mark badge as "ruleset-dependent" and version it with the ruleset
6. Note in `comms/decisions/layer-1-decisions.md`
