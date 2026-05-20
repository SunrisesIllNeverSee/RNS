# SiGlobe — Product Flow Map

> Working demo built in Gemini Canvas. This maps the product as designed.
> Updated: 2026-02-26

---

## The Product

SiGlobe measures signal purity in X posts. User drops an X post URL into the Harness,
an AI engine runs it through a Signal-to-Noise Refraction process, and it comes out the
other side with a Fidelity Certificate — a 5-vector radar profile and composite purity
score. Results go to a global leaderboard (Arena) where posts, users, and engines are
ranked against each other.

Built for every AI engine to participate. The engine is the variable — the scoring rubric
is the constant. "Which AI evaluates signal purity best?" is the Arena's question.

This implements Module 3 (SigXRank) from PPA4 under the MO§ES framework.

---

## The Refraction Model

The Harness runs a **Token Discriminator** that separates input into:

- **Structural Tokens** (verbs, nouns, quantifiers) = The Signal
- **Modifier Tokens** (adverbs, filler, meta-commentary) = The Noise

### The 5 Hardwired Vectors

| Vector | Metric | How It's Calculated |
| ------ | ------ | ------------------- |
| Density | N-to-T Ratio | Nouns/Verbs (signal) divided by total tokens. Higher ratio = higher density. |
| Clarity | Ambiguity Index | Count of vague quantifiers (some, maybe, approximately) and passive voice. More ambiguity = lower score. |
| Fidelity | Semantic Drift | Cosine similarity between raw source embedding and extracted signal embedding. Measures meaning preserved. |
| Brevity | Compression Factor | (Source chars - Signal chars) / Source chars. Efficiency of extraction. |
| Impact | Deontic Intensity | Scans for deontic modals (must, shall, will) and imperative verbs. Rewards definitive claims over conditional ones. |

### The Refraction Output

Every analysis produces two extractions:

- **Echo** (Noise) — what the LLM thinks it should say. Conversational filler, mirroring, posturing.
- **Signal** (Pure) — the extracted raw facts. The enforcement logic output.

### Purity Score Formula

```text
Score = (Density x 0.30) + (Clarity x 0.20) + (Fidelity x 0.20) + (Brevity x 0.15) + (Impact x 0.15)
```

Weights are hidden from the user (by design — per the build conversation).

---

## Harness Flow (`SignalHarness.tsx`)

### Step 1: Auth (MO§ES Rule 3)

`Lines 28-45`

Anonymous Firebase auth on page load. Canvas handles session via `__initial_auth_token`.
Outside Canvas, falls back to `signInAnonymously`. `onAuthStateChanged` syncs user state
and populates displayName if previously claimed.

### Step 2: Live Feed (MO§ES Rules 1 & 2)

`Lines 47-56`

Subscribes to `signal_logs` via `onSnapshot`. Pulls docs, sorts by timestamp desc,
displays the 10 most recent. This is the "Live Frequency" sidebar — a real-time
chronological feed of all tests across all users.

### Step 3: Input — Drop the X Post

`Lines 160-181`

Label: "Source Waveform"
User pastes an X post URL into the textarea.
Button: "Isolate Signal"

The original build conversation says "drop their X posts" — the field accepts the URL.
Gemini built it as "X-Post Scraper Simulation" accepting URL or text.

### Step 4: Processing Engine — Refraction

`Lines 72-109`

The input goes to the AI engine (currently Gemini API at
`generativelanguage.googleapis.com`). The prompt asks for:

```json
{
  "echo": "string (the noise extraction)",
  "signal": "string (the pure signal extraction)",
  "metrics": {
    "Density": "0-100",
    "Clarity": "0-100",
    "Fidelity": "0-100",
    "Brevity": "0-100",
    "Impact": "0-100"
  }
}
```

Response is parsed, purity score calculated from the weighted formula, and results go
to state.

On success, writes to Firestore `signal_logs`:

```json
{ "username", "userId", "signalScore", "snippet" (40 chars), "timestamp" }
```

### Step 5: Fidelity Certificate ("The Sticker")

`Lines 183-251`

The certificate renders:

- Giant score display (e.g., "94%") with "Composite Signal Purity" label
- Radar chart showing the 5-vector profile
- Copy Certificate button
- **Mirror Echo** card — the noise the engine extracted
- **Hardwired Signal** card — the pure content the engine extracted
- Identity claim notification bar (if anonymous): "Result live as Anonymous. Claim now?"

### Step 6: Identity Claiming (Step 3 in code)

`Lines 58-70`

User types a name in the header or the notification bar, clicks Claim. Updates Firebase
Auth profile + the most recent Firestore doc's username. Scores are tied to User ID.
Anonymous scores can be claimed retroactively in that session.

### Step 7: Copy Certificate

`Lines 111-121`

Copies: `SIGNAL PURITY: {score}% / Refracted via Signal Harness. / [{signal preview}]`

---

## Arena Flow (`GlobalArena.tsx`)

### Step 1: Auth + Data Stream

`Lines 36-73`

Anonymous auth, then subscribes to `signal_arena_logs`. If empty, seeds 8 demo entries
across all 4 engines (Gemini, Claude, GPT, Grok) so the dashboard has data to show.

### Step 2: Analytics Engine

`Lines 97-123`

Groups entries by engine, calculates average purity per engine, sorts by score.
Produces: total probes, global avg purity, per-engine stats array.

### Step 3: Hero Section

`Lines 133-165`

"GLOBAL ARENA" with live data indicator. Hero stats: Total Probes + Global Avg Purity.

### Step 4: Engine Dominance Chart

`Lines 172-201`

Horizontal bar chart — average purity score per engine. Color-coded:

- Gemini = Blue `#60a5fa`
- Claude = Amber `#fbbf24`
- GPT = Emerald `#10b981`
- Grok = Slate `#94a3b8`

### Step 5: Engine Stats Cards

`Lines 203-221`

Per-engine cards: name, test count, average score. Color-matched.

### Step 6: Signal Rankings Table

`Lines 226-313`

Filter tabs: ALL / GEMINI / CLAUDE / GPT / GROK
Table: Rank, Identity + Engine, Snippet, Purity Score. Color-coded by engine.

### Step 7: Engine Metadata

`Lines 22-27`

```text
GEMINI: Gemini 1.5 Pro   | Blue   #60a5fa
CLAUDE: Claude 3.5 Sonnet | Amber  #fbbf24
GPT:    GPT-4o            | Green  #10b981
GROK:   Grok-1            | Slate  #94a3b8
```

---

## What's Real vs Simulated

| Area | Status | Notes |
| ---- | ------ | ----- |
| Firebase Auth | Real | Anonymous sign-in, identity claiming |
| Firestore reads/writes | Real | Live subscriptions, real persistence |
| Fidelity Certificate UI | Real | Renders from analysis results |
| Radar chart | Real | Recharts, data from 5 vectors |
| Echo / Signal extraction | Real | Displayed in certificate |
| Live feed sidebar | Real | Firestore onSnapshot |
| Copy certificate | Real | Clipboard write |
| Arena leaderboard | Real | Reads + ranks from Firestore |
| Engine Dominance chart | Real | Calculated from data |
| Engine filter tabs | Real | Client-side filtering |
| API key | Simulated | Empty in repo, live in Canvas |
| Engine selection | Not built | Harness is Gemini-only, no picker yet |
| Arena seed data | Simulation | 8 demo entries across 4 engines |
| X post URL extraction | Simulated | Textarea accepts URL/text for demo |

---

## What Needs Building (Not Fixing)

These aren't bugs — they're the next pieces of the product.

1. **Multi-engine support in Harness** — Engine selector UI, API routing per engine
   (Gemini/Claude/GPT/Grok endpoints), selected engine written to Firestore with each
   entry.

2. **Standardized rubric prompt** — The 5 vectors have defined computational logic
   (N-to-T ratio, Ambiguity Index, Semantic Drift, Compression Factor, Deontic Intensity).
   The prompt sent to each engine should communicate these definitions so every engine
   scores against the same rubric. This is what makes cross-engine comparison valid.

3. **Data flow between apps** — Harness writes to `signal_logs`, Arena reads
   `signal_arena_logs`. For the full story (score in Harness → see it in Arena), these
   need to connect. Either unify the collection or bridge them.

4. **`engine` field in Harness writes** — Arena depends on `item.engine` for filtering,
   colors, and Engine Dominance. Harness doesn't write it yet.

5. **Post URL storage** — When input becomes a URL, store it in Firestore so the
   certificate and leaderboard can reference the source post.

---

## Notes

- Purity Score formula is correct and matches PPA4 patent.
- Weights are intentionally hidden from the UI.
- "Rules" in code comments (Rule 1, 2, 3) are MO§ES framework rules.
- Reference docs (architecture.md, getting-started.md) are Gemini-generated scaffolding
  from the build conversation, not the source of truth.
- Entity name: CLAUDE.md says "Ello LLC", patents say "Ello Cello LLC". Verify.
