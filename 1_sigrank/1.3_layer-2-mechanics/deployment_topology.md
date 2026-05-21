# Deployment Topology

How SigRank actually runs in production. The split between open-source layers and private/proprietary layers, and the specific services that host each.

---

## The full stack

```
┌──────────────────────────────────────────────────────────────────┐
│ OPEN SOURCE                                                      │
│ (Privacy / trust / community contribution / funnel)              │
├──────────────────────────────────────────────────────────────────┤
│ • Local Agent       → Python CLI, GitHub public repo             │
│ • Web Frontend      → Next.js + 1_sigrank/1.5_components/sigrank/              │
│ • Snapshot schema   → JSON spec, documented                      │
│ • Adapter SDK       → Community can add new platforms            │
│ • Signing layer     → Standard ed25519, no secret sauce          │
└──────────────────────────────────────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│ SUPABASE (managed — the backbone)                                │
├──────────────────────────────────────────────────────────────────┤
│ • Postgres DB       → All tables from db_schema.md               │
│ • Auth              → Operator accounts, device key registration │
│ • Row-Level Security → Operators only edit their own data        │
│ • Edge Functions    → Ingest validation, sig verify, rate limit  │
│ • Realtime          → Live leaderboard updates (pg replication)  │
│ • Storage           → Badge SVGs, snapshot PDF archives          │
└──────────────────────────────────────────────────────────────────┘
                                ↓ LISTEN/NOTIFY ↓
┌──────────────────────────────────────────────────────────────────┐
│ RAILWAY (private worker — the moat)                              │
├──────────────────────────────────────────────────────────────────┤
│ Repo: sigrank-scoring-worker (separate, PRIVATE GitHub repo)     │
│                                                                  │
│ • FastAPI service                                                │
│   - /score (internal endpoint)                                   │
│   - /health                                                      │
│ • Background worker (always-on)                                  │
│   - Postgres LISTEN on 'new_submission'                          │
│   - Computes Core 5 → SIGNA RATE → class                         │
│   - Writes back to metric_snapshots                              │
│   - Triggers leaderboards_cached regen                           │
│ • Cron jobs                                                      │
│   - 00:00 UTC: daily rank materialization                        │
│   - Every 6h: recency modifier sweep                             │
│   - Every 5min: leaderboard cache rebuild                        │
└──────────────────────────────────────────────────────────────────┘
                                ↓ (precision tier) ↓
┌──────────────────────────────────────────────────────────────────┐
│ MODAL (precision tier audit — Phase 2)                           │
├──────────────────────────────────────────────────────────────────┤
│ • sig_army Python engine                                         │
│ • word_vault classifier (4,900 tokens)                           │
│ • Scales to zero when no audits running                          │
│ • Pay-per-execution (~$0.001/audit)                              │
└──────────────────────────────────────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│ VERCEL (frontend hosting)                                        │
├──────────────────────────────────────────────────────────────────┤
│ • Next.js app — public-facing leaderboard                        │
│ • Components from 1_sigrank/1.5_components/sigrank/                            │
│ • Reads from Supabase (public schema)                            │
│ • Realtime subscription for live updates                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## What lives where — by IP sensitivity

### Public (open source)

| Component | Where | Repo |
|---|---|---|
| Web frontend | Vercel | Public GitHub (this repo) |
| Local agent (Python CLI) | User machines | Public GitHub (this repo) |
| Snapshot payload schema | docs | Public GitHub (this repo) |
| Platform adapters | inside local agent | Public GitHub (this repo) |
| Documentation | docs | Public GitHub (this repo) |
| Class tier definitions | docs | Public GitHub (this repo) |

### Private (proprietary — the moat)

| Component | Where | Repo |
|---|---|---|
| Scoring engine code | Railway worker | Private GitHub: `sigrank-scoring-worker` |
| SIGNA RATE weights | Railway worker (runtime config) | Private |
| Class threshold formulas | Railway worker | Private |
| Anti-gaming detection (Phase 2) | Railway worker | Private |
| Ruleset versioning logic | Railway worker | Private |
| sig_army Python engine | Modal | Private GitHub: `sigrank-sig-army` |
| word_vault (4,900 tokens) | Modal (or Supabase Storage encrypted) | Private |
| Drift Ratio computation | Modal | Private |

### Managed services (we don't host, we configure)

| Component | Service |
|---|---|
| Postgres DB | Supabase |
| Auth | Supabase Auth |
| File storage | Supabase Storage |
| Real-time replication | Supabase Realtime |
| Edge Functions | Supabase Edge (Deno) |

---

## Repos and access model

### Public repos (everyone can see)

```
github.com/SunrisesIllNeverSee/rns           ← this repo
  - components/                                ← UI components
  - 1_sigrank/1.6_agent/                             ← local agent specs
  - 1_sigrank/1.3_layer-2-mechanics/             ← public-facing specs
  - 1_sigrank/1.2_layer-1-foundation/metrics/                  ← metric definitions
  - 2_secondary/                                 ← web app

github.com/SunrisesIllNeverSee/sigrank-cli   ← (future) local Python agent
  - src/
  - tests/
  - pyproject.toml

github.com/SunrisesIllNeverSee/sigrank-web   ← (future) public Next.js app
  - app/
  - components/  (imports from rns/1_sigrank/1.5_components/sigrank)
  - lib/
```

### Private repos (only you + trusted collaborators)

```
github.com/SunrisesIllNeverSee/sigrank-scoring-worker  ← THE MOAT
  - src/
  │   ├── api/                ← FastAPI
  │   ├── scoring/            ← PRIVATE FORMULAS
  │   │   ├── compression.py
  │   │   ├── signa_rate.py
  │   │   ├── class_assignment.py
  │   │   ├── recency.py
  │   │   └── anti_gaming.py
  │   ├── workers/
  │   │   ├── listener.py
  │   │   ├── scorer.py
  │   │   └── cache_rebuild.py
  │   └── db/                 ← Supabase client
  - rulesets/                 ← versioned scoring configs (.json)
  - Procfile
  - railway.json

github.com/SunrisesIllNeverSee/sigrank-sig-army  ← PRECISION TIER
  - src/
  │   ├── word_vault/
  │   ├── classifier/
  │   ├── drift_detection/
  │   └── audit/
  - modal_app.py
  - data/
      └── word_vault.pkl      ← encrypted, the 4,900-token classifier
```

---

## Service costs — MVP

| Service | Tier | Cost/mo |
|---|---|---|
| Supabase | Free → Pro at scale | $0 → $25 |
| Railway | Hobby | $5 (includes $5 credit) |
| Vercel | Hobby → Pro at scale | $0 → $20 |
| Modal | Pay-per-use | $0 (Phase 2 only) |
| GitHub | Free (private repos included) | $0 |
| **Total MVP** | | **$5–$70/mo** |

Production (real traffic):
| Service | Cost/mo |
|---|---|
| Supabase Pro | $25 |
| Railway (scaled) | $20–50 |
| Vercel Pro | $20 |
| Modal (precision tier active) | $10–100 (usage-based) |
| Domain + Cloudflare | $1–20 |
| **Total Production** | **$76–$215/mo** |

Even at production scale this stays under $250/mo until you cross into thousands of daily active operators. The architecture is designed for bootstrap economics.

---

## Why Railway (vs alternatives)

| Platform | Why or why not |
|---|---|
| **Railway** ⭐ | GitHub-push deploys, $5/mo hobby with $5 credit, persistent processes for LISTEN/NOTIFY, native Python, native cron, easy env vars. **Pick this.** |
| Fly.io | Better long-term economics but requires Dockerfile. Migrate here in stage 3. |
| Render | Free tier spins down (kills LISTEN connection). Skip. |
| Vercel Functions | Stateless serverless. Wrong for the worker. |
| AWS Lambda | Cold starts kill LISTEN model. Overcomplicated for MVP. |
| Self-hosted VPS | Cheapest at scale but you manage ops. Not worth it for MVP. |

---

## Why Supabase (vs alternatives)

| Platform | Why or why not |
|---|---|
| **Supabase** ⭐ | Postgres + Auth + Realtime + Edge + Storage. One platform. RLS for privacy. pgvector for future sig_army semantic work. **Pick this.** |
| Plain Postgres on Railway | Loses Auth, Realtime, RLS, Storage, Edge — you'd rebuild all of it. |
| Firebase | Document DB (Firestore) wrong for our relational schema. |
| PlanetScale | MySQL, no Realtime, no Auth, no Edge. |
| Neon | Postgres-only, no Auth/Realtime. Good DB, but you'd add 4 more services. |

Supabase IS the rest of your backend platform. Railway IS the private compute layer. Vercel IS the frontend hosting. Three pieces, clean roles, no overlap.

---

## Why this split protects the IP

### Scenario: a competitor wants to copy SigRank

What they can see (public):
- The Core 5 metric definitions and their formulas at the conceptual level
- The class tier names and threshold ranges
- The UI components and design system
- The local agent and how it submits
- The snapshot payload schema
- The database schema

What they CANNOT see (private):
- The exact composite weights in SIGNA RATE
- The recency modifier curves
- The class threshold runtime logic (with safety checks)
- The anti-gaming detection rules
- The sig_army word_vault (the 4,900-token classifier)
- The PC sub-score extraction algorithm
- Drift Ratio computation
- Ruleset versioning history

Anyone can build A leaderboard. **Nobody can build THIS one** without the moat repo. Even if they reverse-engineer the public components and submit identical payloads, they don't have the scoring engine — they don't know exactly how their score gets computed.

### Scenario: a user wants to verify privacy

What they can verify (public):
- The agent source code: does it ship raw conversations? (No — schema-bound)
- The snapshot payload: what fields actually leave the machine? (Documented exactly)
- The signing process: is it standard cryptography? (Yes — ed25519)

What they don't need to verify (because it doesn't matter):
- How the scoring engine actually computes (their data doesn't go in)
- What runs on the Railway worker (it only sees the schema-bound payload)

The privacy claim is **independently verifiable** because the agent is open source. The scoring moat is **independently protected** because it never sees raw data.

---

## Deployment flow — first launch

### Week 1: Supabase setup
1. Create Supabase project (free tier)
2. Run migrations from `db_schema.md` — all tables created
3. Enable Row-Level Security policies
4. Set up Auth (email magic link)
5. Configure Realtime on `metric_snapshots` and `leaderboards_cached`

### Week 2: Private scoring worker on Railway
1. Create private GitHub repo: `sigrank-scoring-worker`
2. Build FastAPI app + background worker
3. Connect Railway to the private repo
4. Set env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `RULESET_VERSION`
5. Deploy — worker starts LISTENing for new submissions

### Week 3: Public web frontend on Vercel
1. Build Next.js app importing `1_sigrank/1.5_components/sigrank/`
2. Connect to Supabase (anon key, RLS-protected reads)
3. Deploy to Vercel
4. Configure custom domain

### Week 4: Local agent (open source)
1. Build Python CLI in public repo
2. Implement Claude Code adapter first
3. Implement snapshot generation + ed25519 signing
4. Publish to PyPI: `pipx install sigrank-agent`
5. Soft launch — initial operators submit snapshots

### Week 5+: Iterate
- Watch first real submissions hit the Railway worker
- Verify scoring correctness against the MO§ES benchmark as ground truth
- Add more platform adapters (ChatGPT, Cursor, Gemini)
- Iterate on the UI based on real data

---

## Migration path (when you outgrow MVP)

| Stage | Trigger | Move |
|---|---|---|
| MVP | < 100 active operators | Stay on current stack |
| Growth | 100–1,000 operators | Supabase Pro, scale Railway worker |
| Scale | 1,000–10,000 operators | Migrate Railway → Fly.io (cheaper at scale, multi-region) |
| Enterprise | 10,000+ operators | Add dedicated Postgres replicas, dedicated workers per scoring job type, CDN-cached leaderboard reads |

The schema and architecture don't change. Only the hosting topology does.

---

## What NOT to do

1. **Do not put the scoring engine in Supabase Edge Functions.** They're stateless, time-limited, and can't hold LISTEN connections. The scoring worker needs to be its own persistent service.

2. **Do not host the scoring worker in the same repo as this public repo.** The moat is the moat. Separate private repo, no exceptions.

3. **Do not store the word_vault in plaintext in any service.** Encrypted at rest in Modal or Supabase Storage with a key that only Modal accesses.

4. **Do not couple the frontend to the scoring worker directly.** Frontend only talks to Supabase. Supabase tells the scoring worker via NOTIFY. This decouples failure modes — if the scoring worker is down, the leaderboard still serves stale-but-readable data.

5. **Do not skip ruleset versioning.** Every metric_snapshots row records which ruleset_version it was computed under. Future ruleset changes can replay history without destroying existing rankings.

---

## Summary

| Layer | Service | Open / Private | Role |
|---|---|---|---|
| Frontend | Vercel | Open | Public leaderboard, profile pages |
| DB / Auth / Storage | Supabase | Managed | Backbone |
| Edge ingest | Supabase Edge | Open | Schema validation, signature verify |
| Scoring engine | Railway | **Private** | THE MOAT |
| Precision audit | Modal | **Private** | sig_army (Phase 2) |
| Local agent | User machines | Open | Telemetry collector |

That's the deployment. Three managed platforms, two private repos, one philosophy: **open for trust, private for moat**.
