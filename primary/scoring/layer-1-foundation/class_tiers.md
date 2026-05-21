# Class Tier System

The nine-class hierarchy that defines operator identity in SigRank. Recovered from the v2 Signal Codex and the December 2025 HTML prototypes.

---

## The Nine Classes

| Class | Compression range | Composite range | Meaning |
|---|---|---|---|
| **TRANSMITTER** | ≥ 0.85 | ≥ 85% | You don't just use the system. You are the system. |
| **ARCHITECT+** | 0.75 – 0.84 | 75 – 84% | Precision creators. Structure from signal. |
| **ARCHITECT** | 0.65 – 0.74 | 65 – 74% | System builders. Coherent operators. |
| **POWER** | 0.50 – 0.64 | 50 – 64% | Forming forge. Active but noisy. |
| **BASE** | 0.40 – 0.49 | 40 – 49% | Signal breaking through. Clarity is emerging. |
| **SEEKER** | 0.30 – 0.39 | 30 – 39% | Active explorers. High prompts, low refinement. |
| **REFINER** | 0.20 – 0.29 | 20 – 29% | Practicing with purpose. Consistent mid-tier. |
| **BEARER** | 0.15 – 0.24 | 15 – 24% | Quiet insight holders. Deep threads, low activity. |
| **IGNITER** | < 0.15 | < 15% | Dormant potential. The still soul. Waiting. |

---

## Assignment logic

A class is assigned based on **both** Compression Ratio and SIGNA RATE composite — whichever is more restrictive wins.

```
function assign_class(compression, signa_rate) {
  if (compression >= 0.85 && signa_rate >= 85) return "TRANSMITTER"
  if (compression >= 0.75 && signa_rate >= 75) return "ARCHITECT+"
  if (compression >= 0.65 && signa_rate >= 65) return "ARCHITECT"
  if (compression >= 0.50 && signa_rate >= 50) return "POWER"
  if (compression >= 0.40) return "BASE"
  if (compression >= 0.30) return "SEEKER"
  if (compression >= 0.20) return "REFINER"
  if (compression >= 0.15) return "BEARER"
  return "IGNITER"
}
```

**Why both checks for top classes:** prevents someone from gaming into TRANSMITTER class with a perfectly curated compression but low actual SIGNA RATE.

---

## Class colors (for UI)

Locked in `components/sigrank/tokens.ts`:

| Class | Hex | Use |
|---|---|---|
| TRANSMITTER | `#f5a020` | Gold — flagship |
| ARCHITECT+ | `#5ba4f5` | Light blue |
| ARCHITECT | `#4a8fd4` | Blue |
| POWER | `#9d7fe8` | Purple |
| BASE | `#6b7f96` | Slate |
| SEEKER | `#2ec4a0` | Teal — exploration |
| REFINER | `#f07030` | Orange — refinement |
| BEARER | `#6876db` | Indigo — quiet depth |
| IGNITER | `#3a4f68` | Dim — dormant |

---

## Class glyphs

| Class | Glyph |
|---|---|
| TRANSMITTER | ◈ |
| ARCHITECT+ | ▲ |
| ARCHITECT | ▽ |
| POWER | ⬡ |
| BASE | ↓ |
| SEEKER | ◎ |
| REFINER | ⟳ |
| BEARER | ◇ |
| IGNITER | · |

---

## Class population assumptions

Approximate expected distribution (from v2 K2 Signal Index snapshot):

| Class | Expected % of active operators |
|---|---|
| TRANSMITTER | < 1% |
| ARCHITECT+ | 1 – 3% |
| ARCHITECT | 3 – 8% |
| POWER | 8 – 15% |
| BASE | 15 – 25% |
| SEEKER | 20 – 30% |
| REFINER | 15 – 25% |
| BEARER | 5 – 15% |
| IGNITER | 5 – 20% |

The pyramid shape is intentional. TRANSMITTER must remain rare.

---

## Tier vs class

**Class** is identity — what kind of operator you are.
**Rank** is your current position relative to others in that class.
**Tier** is the SigRank product tier (free / precision / pro).

A TRANSMITTER-class operator can be #1 in class or #50 in class. The class stays TRANSMITTER as long as Compression holds.

---

## Class promotions / demotions

- Class is re-evaluated on every scoring cycle (daily).
- Demotions take effect immediately.
- Promotions require **sustained threshold** for 3 consecutive scoring cycles to prevent flash promotions on a single hot day. This is the **Architect Lock** equivalent.

---

## Deprecated class names

Earlier vCard generator used Kabbalah terminology — these are **deprecated**:

| Deprecated | Current |
|---|---|
| KETER | TRANSMITTER |
| BINAH | ARCHITECT+ |
| CHOKMAH | ARCHITECT |
| YESOD | POWER |

Do not surface deprecated terms in new UI. They remain in [../../prototypes/v1_tools/vcardgenerator.html](../../prototypes/v1_tools/vcardgenerator.html) for historical reference only.
