Goal: Build the full SigRank Next.js app from existing specs.

Read in order:
1. MODERATOR_NOTE.md
2. 1_sigrank/1.1_layer-0-ground/build/CANON.md
3. 1_sigrank/1.3_layer-2-mechanics/db_schema.md
4. 1_sigrank/1.3_layer-2-mechanics/api_spec.md
5. 1_sigrank/1.3_layer-2-mechanics/scoring_formula.md
6. 1_sigrank/1.4_layer-3-frontend/site_architecture.md
7. All files in 1_sigrank/1.5_components/sigrank/

Build the full app: free tier + Pro tier + sig_army integration 
+ Stripe billing + leaderboard pages + operator profile + 
local telemetry agent.

For the 7 open decisions in MODERATOR_NOTE.md: use the most 
conservative default, implement it, mark with TODO + canonical ID 
so operator can override. Do not skip — make a decision and build it.

RS.xx proprietary parameters: use placeholder values marked 
OPERATOR_OVERRIDE_REQUIRED.

Target: clean build, all pages render, Supabase schema applied, 
Stripe wired in test mode.