# SigRank Build Layers — The Full Ecosystem Map

The complete build surface. Every layer, every component, every dependency. Organized for independent build + review.

**This is not MVP.** This is the full vision. Layers tagged with phase so the build can stage cleanly.

---

## How to read this document

Each layer has:
- **Purpose** — what it does in one line
- **Repo** — public `rns` / private `sigrank-scoring-worker` / private `sigrank-sig-army` / new separate repo
- **Tech** — language / framework / service
- **Depends on** — which other layers must exist first
- **Status** — `mvp` / `v2` / `v3` / `always-on`
- **Effort** — `S` (1-3d) / `M` (1-2w) / `L` (1-2mo) / `XL` (3mo+)
- **Acceptance** — what "done" looks like

---

## A. Algorithm Core (the moat)

The math. Pure logic. No infrastructure dependencies. This is the IP.

### A1. Algo Library
- **Purpose**: Pure functions implementing Core 5 + composite formulas
- **Repo**: `sigrank-scoring-worker` (private) — packaged as importable Python module
- **Tech**: Python 3.11+, pure functions, pydantic models, pytest
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `M`
- **Acceptance**: All formulas from `scoring_formula.md` implemented + unit tested; can compute SIGNA RATE end-to-end from a sample payload deterministically

### A2. Ruleset Versioning + Replay Engine
- **Purpose**: Versioned scoring rules so history can be recomputed when formulas change
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python, JSON-versioned rulesets, idempotent replay job
- **Depends on**: A1, B1 (database)
- **Status**: `mvp` (skeleton) → `v2` (full replay)
- **Effort**: `M`
- **Acceptance**: Every `metric_snapshots` row records `ruleset_version`; can re-score all submissions under a new ruleset and produce a diff

### A3. Class Assignment + Tier Logic
- **Purpose**: The 9-tier hierarchy (TRANSMITTER → IGNITER) assignment logic
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python, rule-based with promotion-stickiness logic (3-cycle sustained threshold)
- **Depends on**: A1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Matches `class_tiers.md` exactly; promotions require 3 consecutive cycles; demotions immediate

### A4. Anti-Gaming Detection
- **Purpose**: Spam penalty, redundancy penalty, synthetic inflation flags
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python statistical heuristics
- **Depends on**: A1, B3 (rank history)
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Spam patterns detected; penalties applied; flagged operators visible in admin dashboard

### A5. Precision Tier — sig_army Engine
- **Purpose**: Word/token level signal-vs-noise classification using the 4,900-token word_vault
- **Repo**: `sigrank-sig-army` (private, separate from scoring worker)
- **Tech**: Python, Modal serverless, sklearn / custom classifier
- **Depends on**: A1
- **Status**: `v2` (upsell tier)
- **Effort**: `L`
- **Acceptance**: Given raw session text, produces exact Compression Ratio (vs token-proxy) + full PC sub-score breakdown + Drift Ratio

### A6. Confidence Scoring
- **Purpose**: Flag each metric with confidence based on data quality (proxy vs exact, sample size, etc.)
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python
- **Depends on**: A1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Every metric has a confidence flag (`high` / `medium` / `low` / `~`); displayed on leaderboard as `~` prefix when low

---

## B. Backend Services

Infrastructure. Stateful. Operates the system.

### B1. Database (Supabase Postgres)
- **Purpose**: Source of truth for all data
- **Repo**: Migrations in `rns/1_sigrank/1.3_layer-2-mechanics/migrations/` (public)
- **Tech**: Supabase Postgres, RLS policies, Realtime, pgvector
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: All tables from `db_schema.md` created; RLS policies enforce operator-only writes; Realtime enabled on `metric_snapshots` and `leaderboards_cached`

### B2. Scoring Machine (Railway worker)
- **Purpose**: Listens for submissions, runs algos, writes back scores
- **Repo**: `sigrank-scoring-worker` (private)
- **Tech**: FastAPI + Postgres LISTEN/NOTIFY + asyncio
- **Depends on**: A1, A3, B1
- **Status**: `mvp`
- **Effort**: `M`
- **Acceptance**: Inserts to `snapshot_submissions` trigger scoring; `metric_snapshots` row written within 5s of submission

### B3. Ingest API
- **Purpose**: Public endpoint receiving signed snapshots
- **Repo**: Supabase Edge Functions (deployed from `rns`)
- **Tech**: Deno + ed25519 verification
- **Depends on**: B1, C2 (device keys)
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `POST /api/v1/snapshots` accepts signed payload, verifies signature, validates schema, inserts to DB, returns submission ID

### B4. Leaderboard Cache Generator
- **Purpose**: Pre-computed leaderboard tables so frontend reads are fast
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python cron job (every 5 min)
- **Depends on**: B2, B1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `leaderboards_cached` rows refreshed every 5 min; frontend reads it directly, no live JOINs

### B5. Rank History + Movement Tracker
- **Purpose**: Daily rank snapshots, 24h/7d delta computation
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python cron (00:00 UTC daily)
- **Depends on**: B4
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `rank_history` row per operator per day; `movement_24h` and `movement_7d` on `metric_snapshots`

### B6. Badge Engine
- **Purpose**: Evaluates criteria on each scoring cycle, awards badges
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python, rule definitions in JSON
- **Depends on**: B2, B5
- **Status**: `mvp` (3-5 badges) → `v2` (full catalog)
- **Effort**: `M`
- **Acceptance**: 5x Crown, Transmitter-Class, Audit Verified evaluated daily; new badges → `operator_badges` row

### B7. Hall of Signal Aggregator
- **Purpose**: Tracks all-time records per metric, special badge recipients
- **Repo**: `sigrank-scoring-worker`
- **Tech**: Python cron (daily)
- **Depends on**: B2, B6
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: `/hall` page reads from materialized records table; updates daily

### B8. Compare Engine
- **Purpose**: Computes operator-vs-operator, operator-vs-avg comparisons
- **Repo**: `sigrank-scoring-worker` (or Edge Function)
- **Tech**: Python / SQL
- **Depends on**: B2
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: `/compare?a=X&b=Y` returns diff JSON; includes class averages, platform medians

### B9. Search Engine
- **Purpose**: Type-ahead codename / circle search
- **Repo**: Supabase Edge Function + Postgres trigram indexes
- **Tech**: Postgres pg_trgm + Deno
- **Depends on**: B1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `/search?q=trans` returns matching operators within 100ms

### B10. Notification Service
- **Purpose**: Email on class promotion, rank movement, audit result
- **Repo**: Supabase Edge Function + Resend/Postmark
- **Tech**: Deno + transactional email service
- **Depends on**: B1, B2
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Class change events trigger email; operator can configure notification preferences

### B11. Billing (Stripe)
- **Purpose**: Precision tier subscriptions, supporter donations
- **Repo**: Supabase Edge Functions
- **Tech**: Stripe SDK + webhooks → Postgres
- **Depends on**: B1, C1 (auth)
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Stripe checkout for precision tier; subscription state syncs to `user_subscriptions`; precision-tier features gated correctly

### B12. Webhooks (outbound)
- **Purpose**: Operator-configurable webhooks for class change, rank movement, badge award
- **Repo**: Supabase Edge Function
- **Tech**: Deno + signed webhook delivery
- **Depends on**: B1, B10
- **Status**: `v3`
- **Effort**: `M`
- **Acceptance**: Operator can register webhook URL; events delivered with HMAC signature

### B13. Public API
- **Purpose**: Programmatic access for partners (read leaderboard, read profile, submit programmatically)
- **Repo**: Supabase Edge Functions or dedicated FastAPI service
- **Tech**: REST + OpenAPI spec
- **Depends on**: B1, B2, C1
- **Status**: `v3`
- **Effort**: `L`
- **Acceptance**: Documented REST API with rate limits + API key auth; OpenAPI spec published

### B14. Audit Trail
- **Purpose**: Immutable log of all scoring events for debugging + dispute resolution
- **Repo**: Postgres (within B1)
- **Tech**: Append-only `audit_log` table + triggers
- **Depends on**: B1
- **Status**: `mvp` (basic) → `v2` (full)
- **Effort**: `S`
- **Acceptance**: Every score computation logged; every class change logged; cannot be deleted

---

## C. Identity & Verification

The trust layer. Cryptographic.

### C1. Auth (Supabase Auth)
- **Purpose**: Operator account creation, email magic link, session management
- **Repo**: Supabase config
- **Tech**: Supabase Auth (Postgres-backed)
- **Depends on**: B1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Operator can claim a codename via email magic link

### C2. Device Key Registration
- **Purpose**: Each local agent device registers an ed25519 public key on first publish
- **Repo**: Supabase Edge Function + B3 logic
- **Tech**: Deno + ed25519 + Postgres `devices` table
- **Depends on**: B1, C1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: First snapshot from new device triggers key registration flow; subsequent publishes verified against stored key

### C3. Ed25519 Signing Infrastructure
- **Purpose**: Agent-side keypair generation, snapshot signing
- **Repo**: `sigrank-agent` (public) — uses pynacl
- **Tech**: Python, pynacl, OS keychain integration
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `sigrank init` generates keypair; every `sigrank publish` signs payload; signature verifies server-side

### C4. Snapshot Hash + Merkle Proofs
- **Purpose**: Verifiable proof of inclusion — anyone can verify a snapshot was actually submitted
- **Repo**: `sigrank-scoring-worker` + frontend
- **Tech**: Python (Merkle tree generation), SHA-256
- **Depends on**: B1, B14
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Each daily batch produces a Merkle root; published publicly; individual snapshots provable

### C5. Public Verifiability Page
- **Purpose**: Anyone can paste a snapshot ID + signature and verify authenticity
- **Repo**: `rns` (frontend)
- **Tech**: Client-side verification (ed25519-js or noble)
- **Depends on**: C4
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: `/verify` page accepts snapshot, displays valid/invalid + signing key

### C6. Cross-Platform Identity Bridging
- **Purpose**: Prove same operator across Claude + ChatGPT + Gemini (when desired)
- **Repo**: Multiple — agent supports it, server stores linked identities
- **Tech**: Ed25519 key derivation + linked-device proof
- **Depends on**: C2, C3
- **Status**: `v3`
- **Effort**: `L`
- **Acceptance**: Operator can prove "Claude TVO" = "ChatGPT TVO" via signed cross-claim

---

## D. Data Collection — Multiple Paths

How operators get data INTO the system. Many paths. All converge on the same snapshot payload schema.

### D1. Local Agent (Python CLI) — Primary Path
- **Purpose**: Standalone CLI users install via pipx
- **Repo**: `sigrank-agent` (new public repo)
- **Tech**: Python 3.11+, Typer/Click, SQLite, pynacl, httpx, rich
- **Depends on**: C3, D9 (snapshot schema)
- **Status**: `mvp`
- **Effort**: `L`
- **Acceptance**: Full CLI per `cli_commands.md`; end-to-end submit works

### D2. MCP Server (Model Context Protocol)
- **Purpose**: Operators' AI assistants can query their own SigRank stats AND submit on their behalf via MCP tools
- **Repo**: `sigrank-mcp` (new public repo)
- **Tech**: TypeScript or Python MCP SDK
- **Depends on**: D1 (uses agent internals), B13 (public API)
- **Status**: `mvp` (this is huge for Claude Code operators specifically)
- **Effort**: `M`
- **Acceptance**: Claude Code / Cursor / any MCP client can:
  - `sigrank.get_profile()` — read operator's current stats
  - `sigrank.preview_snapshot()` — compute current window without submitting
  - `sigrank.publish()` — submit signed snapshot
  - `sigrank.leaderboard()` — read public leaderboard
  - `sigrank.compare(other)` — compare against another operator

### D3. Claude Code Plugin / Slash Commands
- **Purpose**: Native Claude Code commands like `/sigrank publish`, `/sigrank rank`
- **Repo**: `sigrank-claude-plugin` (new public repo)
- **Tech**: Claude Code plugin format
- **Depends on**: D2 (MCP) or D1 (CLI)
- **Status**: `mvp` (highest-value plugin given audience)
- **Effort**: `S`
- **Acceptance**: Published to Claude Code plugin registry; operators can `/sigrank publish` inside Claude Code

### D4. Cursor Extension
- **Purpose**: Cursor IDE integration with sidebar SigRank panel + submit button
- **Repo**: `sigrank-cursor-extension`
- **Tech**: Cursor extension format (VSCode-compatible)
- **Depends on**: D2 or D1
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Available in Cursor's extension marketplace

### D5. VSCode Extension
- **Purpose**: General VSCode users (Continue, Cody, etc.)
- **Repo**: `sigrank-vscode-extension`
- **Tech**: VSCode extension API
- **Depends on**: D2 or D1
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Available in VSCode Marketplace

### D6. Web Submission Form (vCard generator)
- **Purpose**: Manual entry fallback for operators without CLI access
- **Repo**: `rns` (frontend, part of Next.js app)
- **Tech**: React form + client-side ed25519 (web crypto)
- **Depends on**: B3
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `/submit/manual` form — operator types in metrics, gets ranked. Low-confidence flag on the resulting score.

### D7. Browser Extension (auto-capture)
- **Purpose**: Captures ChatGPT / Claude.ai web sessions automatically
- **Repo**: `sigrank-browser-extension`
- **Tech**: Chrome/Firefox extension, content scripts
- **Depends on**: D1 (or its parsing logic)
- **Status**: `v2`
- **Effort**: `L`
- **Acceptance**: Operator installs extension → it captures usage on chat.openai.com and claude.ai → snapshots submitted automatically

### D8. Tracing Platform Adapters
- **Purpose**: Pull stats from observability platforms operators already use
- **Repo**: `sigrank-agent` (as adapter modules) + standalone connectors
- **Tech**: Per-platform: Helicone API, PromptLayer, Langfuse, LangSmith, OpenAI usage API, Anthropic usage API, OpenTelemetry
- **Depends on**: D1
- **Status**: `mvp` (3-4 adapters) → `v2` (all)
- **Effort**: `M` per adapter
- **Acceptance**: Operator can configure `sigrank source add helicone <api-key>` and pull stats directly from Helicone

### D9. Snapshot Payload Schema + SDK
- **Purpose**: The canonical schema + client libraries to build payloads
- **Repo**: `rns` (schema) + separate language repos for SDKs
- **Tech**: JSON Schema + language-specific SDKs
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S` (schema) + `M` (per SDK)
- **Acceptance**: Published JSON Schema; Python SDK; TypeScript SDK; one external developer builds an adapter using only the schema docs

### D10. API Direct Submission
- **Purpose**: Power users / partners submit programmatically without the agent
- **Repo**: Documented in `rns` API docs
- **Tech**: REST + signed payload
- **Depends on**: B3, C3
- **Status**: `mvp` (works because B3 exists)
- **Effort**: `S` (docs only)
- **Acceptance**: A developer can submit a snapshot using curl + their own signing logic

### D11. ChatGPT Custom GPT
- **Purpose**: A custom GPT operators can chat with to submit their stats
- **Repo**: `sigrank-chatgpt-gpt` (config + actions)
- **Tech**: ChatGPT Actions calling public API
- **Depends on**: B13
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Listed in ChatGPT GPT Store; operators can submit via chat

### D12. Obsidian / Raycast / Alfred Plugins
- **Purpose**: Power-user productivity tool integrations
- **Repo**: Separate per plugin
- **Tech**: Per platform
- **Depends on**: B13
- **Status**: `v3`
- **Effort**: `S` each
- **Acceptance**: Operators can check rank from Raycast quicklaunch, etc.

---

## E. Frontend (Next.js)

The public face.

### E1. Main Web App
- **Purpose**: Public leaderboard, operator profiles, all the BlitzStars-style pages
- **Repo**: `sigrank-web` (new public repo, imports `rns/1_sigrank/1.5_components/sigrank/`)
- **Tech**: Next.js App Router + TypeScript + Tailwind + Supabase client + Realtime
- **Depends on**: B1, B4
- **Status**: `mvp`
- **Effort**: `L`
- **Acceptance**: All routes from `site_architecture.md` implemented; homepage, operators list, operator profile, metrics pages, compare, hall, submit

### E2. Operator Profile (the deepest page)
- **Purpose**: WN8-equivalent profile depth — hero SIGNA RATE, Core 5 grid, analytics, drilldowns
- **Repo**: `sigrank-web`
- **Tech**: Next.js page + analytics dashboard components
- **Depends on**: E1, B2, B5
- **Status**: `mvp`
- **Effort**: `M`
- **Acceptance**: Matches the wireframe in `site_architecture.md` exactly

### E3. Pro Dashboard (Signalgeist Pro)
- **Purpose**: Paid tier features — full history, score decomposition, drift detection
- **Repo**: `sigrank-web`
- **Tech**: Gated behind subscription check
- **Depends on**: E1, B11
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Subscribed operators see deeper analytics; non-subscribers see paywall

### E4. Admin Dashboard
- **Purpose**: Internal tool — view all operators, manual badge award, ruleset deployment, ban/suspend
- **Repo**: `sigrank-web` (gated route) or separate `sigrank-admin`
- **Tech**: Next.js + admin-only routes
- **Depends on**: B1, B2
- **Status**: `mvp` (minimal) → `v2` (full)
- **Effort**: `M`
- **Acceptance**: You (operator-zero) can view all submissions, override scores, award badges

### E5. Marketing Landing Page
- **Purpose**: The thing that explains SigRank to first-time visitors
- **Repo**: Separate `sigrank-landing` (different repo, different stack OK)
- **Tech**: Static site (Next.js export or Astro) — emphasis on speed + SEO
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `M`
- **Acceptance**: Explains SigRank in 30 seconds; CTA to submit; lives at root domain, app at `/app` or subdomain

### E6. Documentation / Methodology Site
- **Purpose**: How scoring works (high level), privacy stance, API docs, methodology
- **Repo**: `sigrank-docs` (Nextra or similar) or path on E5
- **Tech**: Nextra / Docusaurus / Astro Starlight
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `M`
- **Acceptance**: Operators can read how the metric stack works without reading source code

### E7. Embeddable Badge Widget
- **Purpose**: Operators embed their SigRank badge on their own site / GitHub README / Twitter bio
- **Repo**: `sigrank-web` (serves images) + small SDK
- **Tech**: Dynamic SVG / OG image generation
- **Depends on**: B2
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: `<img src="sigrank.io/badge/TVO.svg">` displays current class + rank

### E8. Shareable vCard Generator
- **Purpose**: Operators generate downloadable PDF / image with their current stats for social media
- **Repo**: `sigrank-web` + server-side renderer
- **Tech**: Puppeteer / Playwright PDF generation, or static SVG export
- **Depends on**: B2
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Operator clicks "Share" → downloads PDF / PNG with their stats; matches the v1 prototype vCard aesthetic

### E9. PDF Daily Reports
- **Purpose**: Daily leaderboard snapshot PDFs — the K2 Signal Report tradition continues
- **Repo**: `sigrank-scoring-worker` cron job
- **Tech**: Python PDF generation (ReportLab / WeasyPrint)
- **Depends on**: B4
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: PDF generated daily, archived in Supabase Storage, accessible from `/community`

---

## F. Observability & Tracing

The system that watches the system.

### F1. Application Observability
- **Purpose**: Server-side error tracking, performance traces
- **Repo**: All — Sentry SDK in every service
- **Tech**: Sentry or Datadog
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: All exceptions captured; performance traces on scoring engine

### F2. Operator-Facing Traces Dashboard
- **Purpose**: Operator can see WHY they got their score — which submission produced which output, when, with which ruleset
- **Repo**: `sigrank-web`
- **Tech**: Next.js page reading from `audit_log`
- **Depends on**: B14, E1
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Operator profile has "Score Trace" tab showing the path from submission → computation → final score

### F3. Scoring Engine Internal Tracing
- **Purpose**: Detailed per-submission trace of every computation step (which input → which intermediate value → which output)
- **Repo**: `sigrank-scoring-worker`
- **Tech**: OpenTelemetry / structured logs
- **Depends on**: B2
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Can replay any submission and see the exact computation path

### F4. Realtime Metrics Dashboard
- **Purpose**: Live system health — operators per minute, submissions per hour, scoring latency, error rate
- **Repo**: `sigrank-web` (admin) or external (Grafana)
- **Tech**: Postgres metrics + Realtime
- **Depends on**: B1
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Admin dashboard shows live throughput

### F5. Status Page
- **Purpose**: Public service status (uptime, current issues)
- **Repo**: External — statuspage.io / instatus
- **Tech**: Third-party service
- **Depends on**: F1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: status.sigrank.io shows current uptime

### F6. Cost Monitoring
- **Purpose**: Track Supabase / Railway / Vercel / Modal spend
- **Repo**: Internal dashboard or external (Cloudability, etc.)
- **Tech**: Provider APIs
- **Depends on**: nothing
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Daily cost report; alerts on spend spikes

---

## G. Developer Ecosystem

What makes SigRank a platform, not just a product.

### G1. Python SDK
- **Purpose**: Standalone Python library for programmatic SigRank access
- **Repo**: `sigrank-python` (new public repo)
- **Tech**: Python 3.9+
- **Depends on**: B13
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: `pip install sigrank` → `from sigrank import Client; c = Client(); c.leaderboard()`

### G2. TypeScript SDK
- **Purpose**: JS/TS library for web + Node integrations
- **Repo**: `sigrank-ts`
- **Tech**: TypeScript + ESM/CJS dual export
- **Depends on**: B13
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: `npm install @sigrank/sdk`

### G3. Go SDK
- **Purpose**: Go library for backend integrations
- **Repo**: `sigrank-go`
- **Tech**: Go 1.21+
- **Depends on**: B13
- **Status**: `v3`
- **Effort**: `M`
- **Acceptance**: `go get github.com/sigrank/sigrank-go`

### G4. Adapter SDK
- **Purpose**: Framework for community contributors to add new platform adapters
- **Repo**: Part of `sigrank-agent`
- **Tech**: Python plugin entry-points
- **Depends on**: D1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: External developer can publish `sigrank-adapter-mistral` to PyPI and it auto-discovers in the agent

### G5. API Reference Docs
- **Purpose**: Generated REST API documentation
- **Repo**: `sigrank-docs`
- **Tech**: OpenAPI + Stoplight / Mintlify
- **Depends on**: B13
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Interactive API docs; users can try requests in the browser

### G6. Quickstart Guides per Platform
- **Purpose**: 5-minute setup docs for each platform (Claude Code, ChatGPT, Cursor, etc.)
- **Repo**: `sigrank-docs`
- **Tech**: Markdown
- **Depends on**: D1-D12
- **Status**: `mvp` (Claude Code) → `v2` (all)
- **Effort**: `S` each
- **Acceptance**: Each platform has a 5-step "from zero to ranked" guide

---

## H. Distribution

How operators install and update.

### H1. PyPI Package (sigrank-agent)
- **Purpose**: `pipx install sigrank-agent`
- **Repo**: `sigrank-agent`
- **Tech**: PyPI publish via GitHub Actions
- **Depends on**: D1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: `pipx install sigrank-agent` works on Mac/Linux/Windows

### H2. npm Package (sigrank-sdk)
- **Purpose**: `npm install @sigrank/sdk`
- **Repo**: `sigrank-ts`
- **Tech**: npm publish
- **Depends on**: G2
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: TypeScript SDK installable from npm

### H3. Homebrew Formula
- **Purpose**: `brew install sigrank`
- **Repo**: `homebrew-sigrank` (tap)
- **Tech**: Homebrew formula
- **Depends on**: H1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: macOS users can install via Homebrew

### H4. Curl Install Script
- **Purpose**: `curl -sSL install.sigrank.io | bash`
- **Repo**: `rns` (install script in /scripts/)
- **Tech**: bash
- **Depends on**: H1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: One-line install works on Mac/Linux

### H5. Auto-Update Mechanism
- **Purpose**: Agent checks for updates and self-upgrades (with operator consent)
- **Repo**: `sigrank-agent`
- **Tech**: Version check against PyPI; in-CLI upgrade prompt
- **Depends on**: D1, H1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: `sigrank check-update` shows new version; `sigrank upgrade` updates self

---

## I. Operations / Infrastructure

The plumbing that keeps it running.

### I1. Domain + DNS
- **Purpose**: sigrank.io / sigrank.ai / signal-leaderboard.com — pick one
- **Repo**: external (registrar) + Cloudflare
- **Tech**: Cloudflare DNS
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Domain registered, Cloudflare proxying to Vercel + Railway + Supabase

### I2. Email Infrastructure
- **Purpose**: Transactional emails (magic links, notifications)
- **Repo**: Supabase + Resend/Postmark account
- **Tech**: Resend or Postmark
- **Depends on**: nothing
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Emails deliver to inbox (not spam); SPF/DKIM/DMARC configured

### I3. Image CDN
- **Purpose**: Serve badges, avatars, OG images
- **Repo**: Supabase Storage + Cloudflare in front
- **Tech**: Supabase Storage with public bucket + CF caching
- **Depends on**: I1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Badge images load fast from edge cache

### I4. Database Migration Runner
- **Purpose**: Apply schema changes safely
- **Repo**: `rns` migrations folder + supabase CLI
- **Tech**: Supabase migrations
- **Depends on**: B1
- **Status**: `mvp`
- **Effort**: `S`
- **Acceptance**: Migrations applied via `supabase db push` or CI; rollback path documented

### I5. Backup + Recovery
- **Purpose**: Daily Postgres backups, restore tested
- **Repo**: Supabase managed
- **Tech**: Supabase point-in-time recovery (Pro tier)
- **Depends on**: B1
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Restore tested at least once; documented runbook

---

## J. Community / Trust

The social layer.

### J1. Become a Supporter
- **Purpose**: Donation / monthly support tier (the BlitzStars supporters equivalent)
- **Repo**: `sigrank-web` + Stripe
- **Tech**: Stripe Donations
- **Depends on**: B11
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Supporters get a flag on profile; listed on home page

### J2. Verified Operator Program
- **Purpose**: Manual verification for high-profile operators (similar to Twitter blue check)
- **Repo**: `sigrank-web` (form) + B14 (audit)
- **Tech**: Manual review process
- **Depends on**: E4
- **Status**: `v2`
- **Effort**: `S`
- **Acceptance**: Application form; admin can approve/deny; verified flag on profile

### J3. Hall of Signal Nominations
- **Purpose**: Community nominates operators for honors
- **Repo**: `sigrank-web`
- **Tech**: Form + admin review
- **Depends on**: B7
- **Status**: `v3`
- **Effort**: `S`
- **Acceptance**: Form lets users nominate; admin reviews; awarded badges appear in Hall

### J4. Audit Request Flow
- **Purpose**: Operator requests precision audit; pays per audit or via subscription
- **Repo**: `sigrank-web` + B11 + A5
- **Tech**: Form + Stripe + Modal trigger
- **Depends on**: A5, B11
- **Status**: `v2`
- **Effort**: `M`
- **Acceptance**: Operator pays → Modal job runs → exact scores written → notification sent

### J5. Bug Bounty / Responsible Disclosure
- **Purpose**: Security researchers can report issues safely
- **Repo**: `sigrank-docs`
- **Tech**: Docs page + dedicated email
- **Depends on**: nothing
- **Status**: `mvp` (page) → `v2` (paid bounty program)
- **Effort**: `S`
- **Acceptance**: SECURITY.md published; disclosure process documented

---

## K. Cross-Cutting Concerns

Always-on, applies across all layers.

### K1. Privacy / GDPR Compliance
- Right to deletion (operator can delete account + all data)
- Data export (operator can download all their data)
- Privacy policy
- Cookie consent (if applicable in EU)
- **Status**: `mvp` (basic) → `v2` (full)

### K2. Security
- HTTPS everywhere
- API rate limiting
- SQL injection prevention (handled by Supabase + RLS)
- XSS prevention (React handles)
- CSRF (for any state-changing operations)
- Dependency vulnerability scanning (Dependabot)
- **Status**: `mvp`

### K3. Legal
- Terms of Service
- Privacy Policy
- Acceptable Use Policy
- DMCA process
- **Status**: `mvp`

### K4. Internationalization
- English-first MVP
- i18n framework for v2 (Chinese, Spanish, etc.)
- **Status**: `v3`

---

## Build sequence (the actual order)

This is the order I'd actually build in. Each step is independently demoable.

### Sprint 1: Foundation (1 week)
- I1 (Domain)
- I2 (Email)
- B1 (Database)
- C1 (Auth)
- E5 (Landing page — placeholder OK)

### Sprint 2: Algo + Scoring (1 week)
- A1 (Algo Library)
- A3 (Class assignment)
- A6 (Confidence scoring)
- A2 (Ruleset versioning — skeleton)

### Sprint 3: Backend Pipeline (1 week)
- B2 (Scoring Machine — Railway worker)
- B3 (Ingest API)
- C2 (Device key registration)
- C3 (Agent-side signing — basics)
- F1 (Sentry — basic)
- F3 (Scoring tracing)

### Sprint 4: Local Agent (1.5 weeks)
- D1 (Local Agent CLI — Claude Code adapter only)
- H1 (PyPI publish)
- H4 (Curl install script)
- G6 (Claude Code quickstart)

**MILESTONE 1: First end-to-end submission works.** You publish a snapshot from your own Claude Code → it lands in Supabase → it gets scored → SIGNA RATE computed. No frontend yet.

### Sprint 5: Frontend Core (2 weeks)
- E1 (Main web app — homepage + /operators + /metrics)
- B4 (Leaderboard cache generator)
- B9 (Search)
- E2 (Operator profile page)

### Sprint 6: Frontend Depth (1.5 weeks)
- E2 (full operator profile with all components)
- B5 (Rank history)
- B6 (Badge engine — 3-5 badges)
- E6 (Docs site — basics)

**MILESTONE 2: Public soft launch.** Real URL, real operators (10-20 invited beta).

### Sprint 7: MCP + Plugins (2 weeks)
- D2 (MCP server)
- D3 (Claude Code plugin)
- D9 (SDK schema)
- D6 (Web manual submission form)
- D10 (API direct submission docs)

### Sprint 8: Trace + Verify (1.5 weeks)
- C4 (Merkle proofs)
- C5 (Public verifiability page)
- F2 (Operator score trace dashboard)
- B14 (Full audit trail)

### Sprint 9: Adapters (2 weeks)
- D8 (Helicone adapter)
- D8 (PromptLayer adapter)
- D8 (Langfuse adapter)
- D8 (OpenAI usage API adapter)
- G4 (Adapter SDK)

**MILESTONE 3: Public launch.** Marketing landing page live, multiple platform integrations, signed snapshots verifiable.

### Sprint 10: Compare + Hall (1 week)
- B8 (Compare engine)
- B7 (Hall of Signal aggregator)
- E1 (Compare page + Hall page)

### Sprint 11: Pro Tier Launch (2 weeks)
- A5 (sig_army on Modal)
- B11 (Stripe billing)
- E3 (Pro dashboard)
- J4 (Audit request flow)

**MILESTONE 4: Revenue.** First paying customer.

### Sprint 12+: Plugins, Polish, Scale
- D4 (Cursor extension)
- D5 (VSCode extension)
- D7 (Browser extension)
- E7 (Badge widget)
- E8 (Shareable vCard)
- E9 (Daily PDF)
- G1 (Python SDK)
- G2 (TypeScript SDK)

---

## Repo plan

| Repo | Visibility | Contents |
|---|---|---|
| `rns` | public (this repo) | components, specs, schemas, adapter SDK reference, ingest API edge functions |
| `sigrank-scoring-worker` | **private** | algo library, Railway worker, scoring engine, ruleset config, badge engine |
| `sigrank-sig-army` | **private** | precision tier, word_vault, Drift Ratio, sig_army engine |
| `sigrank-agent` | public | Python CLI, adapters, signing |
| `sigrank-web` | public | Next.js app — imports `rns/1_sigrank/1.5_components/sigrank/` |
| `sigrank-mcp` | public | MCP server |
| `sigrank-claude-plugin` | public | Claude Code plugin |
| `sigrank-landing` | public | Marketing site |
| `sigrank-docs` | public | Methodology + API docs |
| `sigrank-python` | public | Standalone Python SDK |
| `sigrank-ts` | public | TypeScript SDK |
| `sigrank-go` | public | Go SDK |
| `sigrank-cursor-extension` | public | Cursor IDE extension |
| `sigrank-vscode-extension` | public | VSCode extension |
| `sigrank-browser-extension` | public | Chrome/Firefox extension |
| `sigrank-chatgpt-gpt` | public | Custom GPT config |
| `homebrew-sigrank` | public | Homebrew tap |

**17 repos total.** 2 private (the moat). 15 public.

---

## Total surface count

- **A. Algorithm Core**: 6 components
- **B. Backend Services**: 14 components
- **C. Identity & Verification**: 6 components
- **D. Data Collection paths**: 12 components
- **E. Frontend**: 9 components
- **F. Observability**: 6 components
- **G. Developer Ecosystem**: 6 components
- **H. Distribution**: 5 components
- **I. Operations**: 5 components
- **J. Community / Trust**: 5 components
- **K. Cross-Cutting**: 4 concerns

**78 distinct buildable components.** ~30 in MVP. ~30 in v2. ~18 in v3.

Each is independently shippable. None is blocked by more than 2 others. Devin (or any builder) can pick up any layer marked `mvp` and ship it within 1-2 weeks.

---

## What gets reviewed when

When Devin reviews:
1. **Read this document first** — gives them the whole map
2. **Read `deployment_topology.md`** — gives them the deployment shape
3. **Read `site_architecture.md`** — gives them the frontend page-by-page spec
4. **Read `scoring_formula.md`** — gives them the algo
5. **Read `db_schema.md`** — gives them the data model
6. **Read individual metric files** — gives them per-metric depth
7. **Read `token_metric_bridge.md`** — gives them the free vs precision tier model

That's the full briefing. Everything else is implementation detail.
