import React, { useMemo, useRef, useState } from "react";
import {
  Activity,
  CheckCircle,
  Copy,
  Cpu,
  Fingerprint,
  Radio,
  Server,
  ShieldCheck,
  Target,
  Terminal,
  User,
  Waves,
  Zap,
} from "lucide-react";
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

import html2canvas from "html2canvas";

type EngineId = "gemini" | "claude" | "gpt" | "grok" | "deepseek" | "perplexity";

type Metrics = {
  Density: number;
  Clarity: number;
  Fidelity: number;
  Brevity: number;
  Impact: number;
};

type Analysis = {
  echo: string;
  signal: string;
  metrics: Metrics;
  score: number;
  engine: EngineId;
  chart: { subject: keyof Metrics; A: number }[];
};

type FeedItem = {
  id: string;
  username: string;
  signalScore: number;
  engine: EngineId;
  snippet: string;
  timestamp: number;
};

const ENGINES: Record<Uppercase<EngineId>, { id: EngineId; name: string; color: string; border: string; bg: string }> = {
  GEMINI: {
    id: "gemini",
    name: "Gemini 1.5 Pro",
    color: "text-blue-400",
    border: "border-blue-500/30",
    bg: "bg-blue-500/10",
  },
  CLAUDE: {
    id: "claude",
    name: "Claude 3.5 Sonnet",
    color: "text-amber-400",
    border: "border-amber-500/30",
    bg: "bg-amber-500/10",
  },
  GPT: {
    id: "gpt",
    name: "GPT-4o",
    color: "text-emerald-400",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/10",
  },
  GROK: {
    id: "grok",
    name: "Grok-1",
    color: "text-slate-200",
    border: "border-slate-500/30",
    bg: "bg-slate-500/10",
  },
  DEEPSEEK: {
    id: "deepseek",
    name: "DeepSeek-V3",
    color: "text-purple-400",
    border: "border-purple-500/30",
    bg: "bg-purple-500/10",
  },
  PERPLEXITY: {
    id: "perplexity",
    name: "Perplexity Pro",
    color: "text-cyan-400",
    border: "border-cyan-500/30",
    bg: "bg-cyan-500/10",
  },
};

function clamp01To100(v: number) {
  if (Number.isNaN(v)) return 0;
  return Math.max(0, Math.min(100, Math.round(v)));
}

function scoreFromMetrics(m: Metrics) {
  return Math.round(
    m.Density * 0.3 + m.Clarity * 0.2 + m.Fidelity * 0.2 + m.Brevity * 0.15 + m.Impact * 0.15,
  );
}

function generateLocalResult(text: string, engine: EngineId): Analysis {
  const normalized = text.trim();
  const len = normalized.length;
  const words = normalized ? normalized.split(/\s+/).filter(Boolean) : [];
  const wordCount = words.length;
  const avgWord = wordCount ? words.join("").length / wordCount : 0;

  const baseClarity = 55 + Math.min(20, Math.max(-20, (12 - avgWord) * 4));
  const brevity = 100 - Math.min(65, Math.max(0, (wordCount - 30) * 1.6));
  const density = 55 + Math.min(25, Math.max(-25, (wordCount / 16) * 6 - 12));
  const fidelity = 62 + Math.min(18, Math.max(-18, (len > 240 ? 10 : 0) - (len < 80 ? 8 : 0)));
  const impact = 58 + Math.min(22, Math.max(-22, (normalized.match(/!|\bnow\b|\bmust\b|\bship\b/gi)?.length || 0) * 6 - 6));

  let engineBias: Partial<Metrics> = {};
  if (engine === "gemini") engineBias = { Clarity: 6, Fidelity: 4, Brevity: 0, Impact: -1, Density: 2 };
  if (engine === "claude") engineBias = { Clarity: 8, Fidelity: 6, Brevity: -6, Impact: -2, Density: 1 };
  if (engine === "gpt") engineBias = { Clarity: 4, Fidelity: 3, Brevity: 0, Impact: 0, Density: 0 };
  if (engine === "grok") engineBias = { Clarity: -2, Fidelity: -3, Brevity: 10, Impact: 10, Density: 2 };
  if (engine === "deepseek") engineBias = { Clarity: 5, Fidelity: 2, Brevity: 2, Impact: 5, Density: 8 };
  if (engine === "perplexity") engineBias = { Clarity: 10, Fidelity: 10, Brevity: -2, Impact: 2, Density: -2 };

  const metrics: Metrics = {
    Density: clamp01To100(density + (engineBias.Density ?? 0)),
    Clarity: clamp01To100(baseClarity + (engineBias.Clarity ?? 0)),
    Fidelity: clamp01To100(fidelity + (engineBias.Fidelity ?? 0)),
    Brevity: clamp01To100(brevity + (engineBias.Brevity ?? 0)),
    Impact: clamp01To100(impact + (engineBias.Impact ?? 0)),
  };

  const echo =
    engine === "claude"
      ? `Analysis identifies high-entropy clusters in your input. The narrative structure suggests a 74% correlation with academic standardizing: ${normalized.slice(0, 180)}${len > 180 ? "…" : ""}`
      : engine === "grok"
        ? `I see what you're doing. You're hedging. Let's drop the corporate speak and get real about this: ${normalized.slice(0, 160)}${len > 160 ? "…" : ""}`
        : engine === "deepseek"
          ? `Optimization phase 1 complete. Logic gates mapped. Redundancy detected at 42% threshold: ${normalized.slice(0, 190)}${len > 190 ? "…" : ""}`
          : engine === "perplexity"
            ? `Found 12 matching data points in existing repositories. Cross-referencing against primary claims: ${normalized.slice(0, 175)}${len > 175 ? "…" : ""}`
            : engine === "gpt"
              ? `Processing based on standard alignment protocols. Tone is neutral and structured for maximum clarity: ${normalized.slice(0, 170)}${len > 170 ? "…" : ""}`
              : `Echo: ${normalized.slice(0, 170)}${len > 170 ? "…" : ""}`;

  const signal =
    engine === "grok"
      ? `STOP POSTURING. You're trying to say: "${words.slice(0, 15).join(" ")}..." but with too many napkins. Use fewer words next time.`
      : engine === "deepseek"
        ? `REASONING PATH [V3]: High-density vector detected. Core logic branch found at: ${words.slice(0, 20).join(" ")}... (Pruning complete)`
        : engine === "perplexity"
          ? `FACT-CHECKED CORE: Verified. Supporting data confirms the primary premise: "${words.slice(0, 22).join(" ")}..." No contradictions found.`
          : engine === "claude"
            ? `NUANCED CLAIM: While complex, the underlying thesis appears to be: "${words.slice(0, 22).join(" ")}..." This requires further qualification.`
            : engine === "gpt"
              ? `EXECUTIVE SUMMARY: To optimize for stakeholder alignment, emphasize: "${words.slice(0, 26).join(" ")}..." Focus on the value proposition.`
              : `SIGNAL: ${words.slice(0, 24).join(" ")}${wordCount > 24 ? " …" : ""}`;

  const score = scoreFromMetrics(metrics);

  return {
    echo,
    signal,
    metrics,
    score,
    engine,
    chart: (Object.keys(metrics) as (keyof Metrics)[]).map((k) => ({ subject: k, A: metrics[k] })),
  };
}

function formatTime(ts: number) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function SignalArena() {
  const [displayName, setDisplayName] = useState("");
  const [claimedName, setClaimedName] = useState<string | null>(null);
  const [inputPost, setInputPost] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<Analysis | null>(null);
  const [copyStatus, setCopyStatus] = useState("Copy Certificate");
  const [selectedEngine, setSelectedEngine] = useState<EngineId>("gemini");

  const feedSeed = useRef<FeedItem[]>([
    {
      id: "seed-1",
      username: "Anonymous_User",
      signalScore: 82,
      engine: "gpt",
      snippet: "We should ship a simpler onboarding…",
      timestamp: Date.now() - 1000 * 60 * 8,
    },
    {
      id: "seed-2",
      username: "Nova",
      signalScore: 76,
      engine: "gemini",
      snippet: "Here’s the concrete plan + timeline…",
      timestamp: Date.now() - 1000 * 60 * 14,
    },
    {
      id: "seed-3",
      username: "Rook",
      signalScore: 91,
      engine: "grok",
      snippet: "Stop hedging. Do X, then measure Y…",
      timestamp: Date.now() - 1000 * 60 * 22,
    },
    {
      id: "seed-4",
      username: "Selene",
      signalScore: 79,
      engine: "claude",
      snippet: "We need to specify constraints first…",
      timestamp: Date.now() - 1000 * 60 * 35,
    },
  ]);

  const [feed, setFeed] = useState<FeedItem[]>(() =>
    [...feedSeed.current].sort((a, b) => b.timestamp - a.timestamp).slice(0, 10),
  );

  const [isExporting, setIsExporting] = useState(false);

  const activeEngine = useMemo(() => ENGINES[selectedEngine.toUpperCase() as Uppercase<EngineId>], [selectedEngine]);

  const claimIdentity = () => {
    const name = displayName.trim();
    if (!name) return;
    setClaimedName(name);
  };

  const runAnalysis = async () => {
    if (!inputPost || isAnalyzing) return;
    setIsAnalyzing(true);
    setResults(null);

    await new Promise((r) => setTimeout(r, 650));

    const res = generateLocalResult(inputPost, selectedEngine);
    setResults(res);

    const newItem: FeedItem = {
      id: `local-${Date.now()}`,
      username: claimedName ?? "Anonymous_User",
      signalScore: res.score,
      engine: selectedEngine,
      snippet: inputPost.trim().slice(0, 40),
      timestamp: Date.now(),
    };

    setFeed((prev) => [newItem, ...prev].sort((a, b) => b.timestamp - a.timestamp).slice(0, 10));

    setIsAnalyzing(false);
  };

  const copyToClipboard = async () => {
    if (!results) return;
    const eng = ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].name;
    const text = `SIGNAL PURITY: ${results.score}%\nEngine: ${eng}\n[ ${results.signal.substring(0, 100)}... ]`;

    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("Copied!");
      setTimeout(() => setCopyStatus("Copy Certificate"), 2000);
    } catch {
      setCopyStatus("Copy failed");
      setTimeout(() => setCopyStatus("Copy Certificate"), 2000);
    }
  };

  const downloadSticker = async () => {
    const element = document.getElementById("signal-certificate");
    if (!element) return;
    setIsExporting(true);
    try {
      const canvas = await html2canvas(element, {
        backgroundColor: "#050507",
        scale: 2,
        logging: false,
        useCORS: true,
      });
      const dataUrl = canvas.toDataURL("image/png");
      const link = document.createElement("a");
      link.download = `signal-cert-${results?.score}-${selectedEngine}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const aura =
    selectedEngine === "gemini"
      ? "from-blue-500/20 via-emerald-500/12 to-transparent"
      : selectedEngine === "claude"
        ? "from-amber-500/20 via-emerald-500/10 to-transparent"
        : selectedEngine === "gpt"
          ? "from-emerald-500/22 via-teal-500/10 to-transparent"
          : selectedEngine === "deepseek"
            ? "from-purple-500/20 via-blue-500/10 to-transparent"
            : selectedEngine === "perplexity"
              ? "from-cyan-500/20 via-blue-500/10 to-transparent"
              : "from-slate-200/16 via-emerald-500/10 to-transparent";

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-emerald-500/30 relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 sa-grid opacity-70" />
      <div className="pointer-events-none absolute inset-0 sa-noise opacity-[0.35]" />
      <div className={`pointer-events-none absolute -top-40 left-1/2 h-[520px] w-[920px] -translate-x-1/2 rounded-full blur-3xl bg-gradient-to-b ${aura}`} />
      <div className="max-w-7xl mx-auto p-4 md:p-10 relative">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-2xl shadow-[0_0_30px_rgba(16,185,129,0.12)] sa-glow">
              <Radio className="text-emerald-400" size={24} />
            </div>
            <div>
              <h1 data-testid="text-title" className="text-2xl font-black uppercase italic tracking-tighter text-white">
                Signal<span className="text-emerald-400">Arena</span>
              </h1>
              <p data-testid="text-subtitle" className="text-[10px] font-semibold text-slate-500 uppercase tracking-[0.34em]">
                Multi-Model Evaluation • Prototype
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-card/60 backdrop-blur px-2 py-2 rounded-2xl border border-border shadow-lg">
            <div className="flex items-center px-2 gap-2">
              <User size={14} className="text-slate-500" />
              <input
                data-testid="input-display-name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Unclaimed Identity"
                className="bg-transparent border-none outline-none text-[11px] font-bold text-white w-40 placeholder:text-slate-700"
              />
            </div>
            <button
              data-testid="button-claim-identity"
              onClick={claimIdentity}
              className="px-4 py-2 bg-emerald-500/90 hover:bg-emerald-400 text-black text-[10px] font-black uppercase rounded-xl transition-all active:scale-[0.98]"
            >
              Claim
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-8 space-y-8">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
              {Object.values(ENGINES).map((eng) => (
                <button
                  data-testid={`button-engine-${eng.id}`}
                  key={eng.id}
                  onClick={() => setSelectedEngine(eng.id)}
                  className={`p-4 rounded-2xl border-2 transition-all duration-300 flex flex-col items-center gap-2 group hover:translate-y-[-1px] active:translate-y-[0px] ${
                    selectedEngine === eng.id
                      ? `${eng.border} ${eng.bg} opacity-100 scale-[1.02] shadow-[0_12px_35px_rgba(0,0,0,0.35)]`
                      : "border-border bg-card/40 backdrop-blur opacity-70 hover:opacity-90"
                  }`}
                >
                  <Cpu size={20} className={selectedEngine === eng.id ? eng.color : "text-slate-600"} />
                  <span
                    className={`text-[10px] font-black uppercase tracking-widest ${
                      selectedEngine === eng.id ? "text-white" : "text-slate-500"
                    }`}
                  >
                    {eng.name.split('-')[0]}
                  </span>
                </button>
              ))}
            </div>

            <section
              className={`bg-card/55 backdrop-blur border-2 rounded-[2rem] p-8 shadow-2xl relative overflow-hidden transition-colors duration-500 ${activeEngine.border}`}
            >
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute -right-20 -top-16 h-64 w-64 rounded-full bg-emerald-500/12 blur-2xl" />
                <div className="absolute -left-24 bottom-0 h-72 w-72 rounded-full bg-blue-500/8 blur-3xl" />
              </div>

              <div className="absolute top-0 right-0 p-8 opacity-5">
                <Target size={120} />
              </div>

              <div className="flex items-center gap-2 mb-4 relative">
                <Terminal size={14} className={activeEngine.color} />
                <span
                  data-testid="text-active-engine"
                  className={`text-[10px] font-black uppercase tracking-widest ${activeEngine.color}`}
                >
                  Injecting into {activeEngine.name} Context
                </span>
              </div>

              <textarea
                data-testid="input-post"
                value={inputPost}
                onChange={(e) => setInputPost(e.target.value)}
                placeholder={`Paste content to benchmark on ${activeEngine.name}…`}
                className="w-full h-40 bg-black/35 border border-border/70 rounded-2xl p-6 text-slate-200 focus:border-white/20 outline-none transition-all resize-none font-medium text-lg leading-relaxed"
              />

              <button
                data-testid="button-run-analysis"
                onClick={runAnalysis}
                disabled={isAnalyzing || !inputPost}
                className={`w-full mt-6 text-white font-black py-5 rounded-2xl uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all active:scale-[0.98] ${
                  isAnalyzing
                    ? "bg-slate-800 cursor-not-allowed"
                    : "bg-emerald-600 hover:bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.2)]"
                }`}
              >
                {isAnalyzing ? <Activity className="animate-pulse" /> : <ShieldCheck size={20} />}
                {isAnalyzing ? `Running ${activeEngine.name} Inference…` : "Run Signal Analysis"}
              </button>

              <div className="mt-4 flex items-center justify-between gap-3 text-[10px] uppercase tracking-[0.2em] text-slate-500 font-semibold">
                <span data-testid="text-mode">Local simulation</span>
                <span data-testid="text-feed-status">Live feed: demo</span>
              </div>
            </section>

            {results && (
              <section className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                <div
                  id="signal-certificate"
                  className={`bg-gradient-to-br from-card to-background border-2 rounded-[2.5rem] overflow-hidden shadow-2xl relative ${
                    ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].border
                  }`}
                >
                  <div
                    data-testid="badge-engine-watermark"
                    className={`absolute top-6 right-8 text-[10px] font-black uppercase tracking-[0.3em] px-3 py-1 rounded-full border ${
                      ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].border
                    } ${ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color}`}
                  >
                    Processed via {ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].name}
                  </div>

                  <div className="p-10 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
                    <div className="space-y-6">
                      <div className="flex items-center gap-2">
                        <Fingerprint
                          className={
                            ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color
                          }
                          size={18}
                        />
                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">
                          Fidelity Cert
                        </span>
                      </div>

                      <div className="relative inline-block">
                        <h2 data-testid="text-signal-score" className="text-8xl md:text-9xl font-black text-white italic leading-none tracking-tighter">
                          {results.score}
                        </h2>
                        <span
                          className={`absolute -top-2 -right-10 text-4xl font-black italic ${
                            ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color
                          }`}
                        >
                          %
                        </span>
                      </div>

                      <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">
                        Composite Signal Purity
                      </p>

                      <div className="flex flex-col sm:flex-row gap-3">
                        <button
                          data-testid="button-copy-certificate"
                          onClick={copyToClipboard}
                          className="flex items-center gap-3 bg-white/5 hover:bg-white/10 text-white text-[10px] font-black py-3 px-6 rounded-xl border border-white/10 transition-all uppercase tracking-widest active:scale-[0.98]"
                        >
                          {copyStatus === "Copied!" ? (
                            <CheckCircle size={16} className="text-emerald-400" />
                          ) : (
                            <Copy size={16} />
                          )}
                          <span data-testid="text-copy-status">{copyStatus}</span>
                        </button>
                        <button
                          data-testid="button-download-sticker"
                          onClick={downloadSticker}
                          disabled={isExporting}
                          className="flex items-center gap-3 bg-emerald-500 hover:bg-emerald-400 text-black text-[10px] font-black py-3 px-6 rounded-xl border border-emerald-400/20 transition-all uppercase tracking-widest active:scale-[0.98] disabled:opacity-50"
                        >
                          {isExporting ? <Activity className="animate-pulse" size={16} /> : <Zap size={16} />}
                          <span>{isExporting ? "Generating..." : "Share Sticker"}</span>
                        </button>
                      </div>
                    </div>

                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={results.chart}>
                          <PolarGrid stroke="#2d2d35" />
                          <PolarAngleAxis
                            dataKey="subject"
                            tick={{ fill: "#64748b", fontSize: 10, fontWeight: "900" }}
                          />
                          <Radar
                            dataKey="A"
                            stroke={
                              results.engine === "claude"
                                ? "#fbbf24"
                                : results.engine === "gpt"
                                  ? "#10b981"
                                  : results.engine === "grok"
                                    ? "#e2e8f0"
                                    : results.engine === "deepseek"
                                      ? "#a855f7"
                                      : results.engine === "perplexity"
                                        ? "#22d3ee"
                                        : "#3b82f6"
                            }
                            fillOpacity={0.5}
                            fill="currentColor"
                            className={
                              ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color
                            }
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-card/50 backdrop-blur border border-border p-6 rounded-2xl relative">
                    <Waves className="absolute top-6 right-6 text-slate-800" size={20} />
                    <h4 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest">
                      Mirror Echo
                    </h4>
                    <p data-testid="text-echo" className="text-sm text-slate-400 leading-relaxed italic">
                      {results.echo}
                    </p>
                  </div>
                  <div
                    className={`bg-card/50 backdrop-blur border p-6 rounded-2xl relative ${
                      ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].border
                    }`}
                  >
                    <Zap
                      className={`absolute top-6 right-6 opacity-50 ${
                        ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color
                      }`}
                      size={20}
                    />
                    <h4
                      className={`text-[10px] font-black uppercase mb-4 tracking-widest ${
                        ENGINES[results.engine.toUpperCase() as Uppercase<EngineId>].color
                      }`}
                    >
                      Refracted Signal
                    </h4>
                    <p data-testid="text-signal" className="text-sm text-slate-200 leading-relaxed font-bold whitespace-pre-wrap">
                      {results.signal}
                    </p>
                  </div>
                </div>
              </section>
            )}
          </div>

          <div className="lg:col-span-4">
            <aside className="bg-card/55 backdrop-blur border border-border rounded-[2rem] p-6 h-full flex flex-col shadow-2xl">
              <div className="flex items-center justify-between gap-3 mb-8">
                <div className="flex items-center gap-2">
                  <Server className="text-slate-500" size={16} />
                  <h2 data-testid="text-feed-title" className="text-[10px] font-black uppercase tracking-[0.2em] text-white">
                    Global Arena Feed
                  </h2>
                </div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-semibold">
                  <span data-testid="text-feed-count">{feed.length}</span>
                </div>
              </div>

              <div className="space-y-4 flex-1">
                {feed.map((item, index) => {
                  const eng = ENGINES[item.engine.toUpperCase() as Uppercase<EngineId>];
                  return (
                    <div
                      data-testid={`row-feed-${index}`}
                      key={item.id}
                      className="group p-5 bg-black/35 border border-border/70 rounded-2xl flex items-center justify-between hover:border-slate-600/60 transition-all"
                    >
                      <div className="overflow-hidden mr-4">
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${eng.color.replace("text-", "bg-")}`}
                          />
                          <span className={`text-[9px] font-black uppercase tracking-widest ${eng.color}`}>
                            {eng.name}
                          </span>
                          <span className="text-[9px] font-bold uppercase tracking-widest text-slate-600">
                            {formatTime(item.timestamp)}
                          </span>
                        </div>
                        <p data-testid={`text-feed-username-${index}`} className="text-[11px] font-bold text-slate-200 truncate">
                          {item.username}
                        </p>
                        <p data-testid={`text-feed-snippet-${index}`} className="text-[11px] truncate text-[#ffffff]">
                          {item.snippet}
                        </p>
                      </div>
                      <div className="text-right">
                        <span data-testid={`text-feed-score-${index}`} className={`text-xl font-black italic leading-none ${eng.color}`}>
                          {item.signalScore}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-6 border-t border-border pt-4 text-[10px] text-slate-500 leading-relaxed">
                <p data-testid="text-feed-footnote">
                  In this prototype, scores + feed are simulated in-memory (no accounts, no external calls).
                </p>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  );
}
