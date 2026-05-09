# SiGlobe — Project Context

## What This Is
SiGlobe is a product suite for real-time AI signal purity analysis and competitive benchmarking. Built by Deric McHenry / Ello LLC as part of the mo§es™ ecosystem.

## Two Apps, One Firebase

### Harness (`harness/SignalHarness.tsx`)
- The **tool** — users paste text, Gemini API analyzes it, returns a Fidelity Certificate with purity score
- Writes to Firestore collection: `artifacts/{appId}/public/data/signal_logs`
- Features: anonymous auth + identity claiming, radar chart (5 signal dimensions), copy certificate, live feed sidebar
- Purity Score formula: `(Density × 0.30) + (Clarity × 0.20) + (Fidelity × 0.20) + (Brevity × 0.15) + (Impact × 0.15)`

### Arena (`arena/GlobalArena.tsx`)
- The **leaderboard** — ranks all users by signal purity scores with engine analytics
- Reads from Firestore collection: `artifacts/{appId}/public/data/signal_arena_logs`
- Features: hero stats, Engine Dominance bar chart, engine filter tabs, ranked table with identity/engine/snippet/score
- Seeds demo data if Firestore is empty

### Note
Harness writes to `signal_logs`, Arena reads from `signal_arena_logs` — these are currently separate collections. Unifying them is a future decision.

## Tech Stack
- React (single-component architecture from Gemini Canvas)
- Firebase (Firestore + Auth — anonymous sign-in)
- Recharts (radar + bar charts)
- Lucide React (icons)
- Tailwind CSS (inline classes, cyberpunk dark theme)
- Gemini API (generativelanguage.googleapis.com) for signal analysis

## Design Language
- Dark-first: `#050507` background, `#0c0c0f` surface
- Signal green: emerald-500 (`#10b981`) as primary accent
- Typography: font-black, uppercase, wide tracking, italic for emphasis
- Engine colors: Gemini=Blue `#60a5fa`, Claude=Amber `#fbbf24`, GPT=Emerald `#10b981`, Grok=Slate `#94a3b8`

## Firebase Config
Both components were built in Gemini Canvas using `__firebase_config` and `__app_id` globals. These need to be adapted to standard env vars (`VITE_FIREBASE_*`) for a standalone Vite deployment.

## Origin
- Original working components built by Gemini in Canvas/Firebase Studio
- Source files are the real deal — not the scaffold that was auto-generated
- Related patent/pitch materials live in `~/Downloads/PP4/`

## Folder Structure
```
SiGlobe/
├── harness/              Working app — signal analysis tool
├── arena/                Working app — global leaderboard
├── reference/            Context docs (outside git tracking intent)
│   ├── GEmini_instructions.md
│   ├── Untitled-1.sh
│   ├── firebase_config.md
│   └── docs/
├── CLAUDE.md
├── .gitignore
└── .git/
```

## Preferences
- Keep reference/context files around — don't delete history
- Harness and Arena are separate products for now, may combine later
- This is a product launch — treat it accordingly
