import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  Loader2,
  Layers,
  RefreshCw,
  Sparkles,
  BookOpen,
  TrendingUp,
  Rss,
} from 'lucide-react';
import { ResearchCard } from './components/ResearchCard';
import { Toast } from './components/Toast';
import { useSSE } from './hooks/useSSE';

// Dynamic base URL: env var in production, localhost for dev
const API_BASE   = import.meta.env.VITE_API_BASE_URL   || 'http://127.0.0.1:8000/api/v1';
const STREAM_URL = import.meta.env.VITE_STREAM_URL     || 'http://127.0.0.1:8000/stream';

const CATEGORIES = ['All', 'NLP', 'Vision', 'Robotics', 'Reinforcement Learning', 'Multimodal'];

const SCORE_FILTERS = [
  { label: 'All Papers',      min: 1,  color: 'primary' },
  { label: 'Notable  (6+)',   min: 6,  color: 'olive'   },
  { label: 'High Impact (8+)', min: 8, color: 'terracotta' },
];

export default function App() {
  const [articles,          setArticles]         = useState([]);
  const [loading,           setLoading]           = useState(true);
  const [triggering,        setTriggering]        = useState(false);
  const [selectedCategory,  setSelectedCategory]  = useState('All');
  const [minScore,          setMinScore]          = useState(1);
  const [toastMessage,      setToastMessage]      = useState(null);
  const [apiSuccessMsg,     setApiSuccessMsg]     = useState('');
  const [stats,             setStats]             = useState({ total: 0, highImpact: 0, categories: 0 });

  // ── Live SSE stream ──────────────────────────────────────
  const handleLiveArticle = useCallback((newArticle) => {
    setArticles((prev) => [newArticle, ...prev]);
    setToastMessage(newArticle);
    setStats((s) => ({ ...s, total: s.total + 1 }));
  }, []);

  const { isConnected } = useSSE(STREAM_URL, handleLiveArticle);

  // ── Fetch articles ───────────────────────────────────────
  const fetchArticles = useCallback(async () => {
    setLoading(true);
    try {
      const catQ = selectedCategory !== 'All' ? `&category=${encodeURIComponent(selectedCategory)}` : '';
      const res  = await fetch(`${API_BASE}/articles?min_score=${minScore}${catQ}`);
      const data = await res.json();
      setArticles(data);

      // Derive stats
      const hi   = data.filter((a) => (a.impact_score || 0) >= 8).length;
      const cats = new Set(data.map((a) => a.category)).size;
      setStats({ total: data.length, highImpact: hi, categories: cats });
    } catch (err) {
      console.error('Failed to fetch articles:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, minScore]);

  useEffect(() => { fetchArticles(); }, [fetchArticles]);

  // ── Trigger pipeline ─────────────────────────────────────
  const handleTriggerPipeline = async () => {
    setTriggering(true);
    setApiSuccessMsg('');
    try {
      const headers = { 'Content-Type': 'application/json' };
      const secret = import.meta.env.VITE_PIPELINE_SECRET;
      if (secret) headers['X-Pipeline-Secret'] = secret;

      const res  = await fetch(`${API_BASE}/trigger-pipeline`, { method: 'POST', headers });
      if (res.status === 401) {
        setApiSuccessMsg('⚠️ Unauthorized — check VITE_PIPELINE_SECRET');
        return;
      }
      const data = await res.json();
      setApiSuccessMsg(data.message || 'Pipeline triggered successfully!');
      setTimeout(() => setApiSuccessMsg(''), 8000);
    } catch (err) {
      console.error('Error triggering pipeline:', err);
    } finally {
      setTriggering(false);
    }
  };

  // ── Helpers ─────────────────────────────────────────────
  const activeScoreFilter = SCORE_FILTERS.find((f) => f.min === minScore) || SCORE_FILTERS[0];

  return (
    <div className="min-h-screen bg-journal-bg text-journal-primary flex flex-col grain-overlay">

      {/* ── Navigation ──────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-journal-bg/90 backdrop-blur-md border-b border-journal-border shadow-nav">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-[60px] flex items-center justify-between gap-4">

          <div className="flex items-center gap-3 select-none">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-journal-primary font-serif leading-none">
                Metis
              </h1>
              <p className="text-sm text-journal-caption font-mono uppercase tracking-widest leading-none mt-0.5">
                AI Research Intelligence
              </p>
            </div>
          </div>

          {/* Right cluster */}
          <div className="flex items-center gap-3">
            {/* Live indicator */}
            <div className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium border transition-all ${
              isConnected
                ? 'bg-journal-olive/8 border-journal-olive/25 text-journal-olive'
                : 'bg-journal-card border-journal-border text-journal-caption'
            }`}>
              <Rss className={`w-3 h-3 ${isConnected ? 'animate-pulse-soft' : 'opacity-40'}`} />
              {isConnected ? 'Live Stream' : 'Reconnecting'}
            </div>

            {/* Run Pipeline */}
            <button
              id="trigger-pipeline-btn"
              onClick={handleTriggerPipeline}
              disabled={triggering}
              className="inline-flex items-center gap-2 px-4 py-2 rounded text-xs font-semibold
                         bg-journal-terracotta text-white border border-journal-terracotta
                         hover:bg-journal-rust active:scale-95
                         transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed
                         shadow-sm"
            >
              {triggering ? (
                <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Ingesting…</>
              ) : (
                <><Play className="w-3.5 h-3.5 fill-current" /> Run Pipeline</>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* ── Hero / Stats Bar ────────────────────────────── */}
      <section className="border-b border-journal-border bg-journal-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold font-serif text-journal-primary leading-snug">
              Research Digest
            </h2>
            <p className="text-sm text-journal-caption mt-1">
              AI-curated papers from ArXiv, scored &amp; summarised by Gemini in real time.
            </p>
          </div>

          {/* Stat pills */}
          {!loading && (
            <div className="flex items-center gap-3 flex-wrap">
              <StatPill icon={<BookOpen className="w-3.5 h-3.5" />} value={stats.total} label="papers" />
              <StatPill icon={<TrendingUp className="w-3.5 h-3.5" />} value={stats.highImpact} label="high impact" accent />
              <StatPill icon={<Layers className="w-3.5 h-3.5" />} value={stats.categories} label="fields" />
            </div>
          )}
        </div>
      </section>

      {/* ── Main content ────────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">

        {/* Pipeline success banner */}
        {apiSuccessMsg && (
          <div className="mb-6 flex items-center justify-between gap-3 p-4 rounded-lg
                          bg-journal-olive/8 border border-journal-olive/25
                          text-journal-olive text-sm animate-fade-up">
            <span className="flex items-center gap-2 font-medium">
              <Sparkles className="w-4 h-4 shrink-0" />
              {apiSuccessMsg}
            </span>
            <span className="text-[11px] font-mono opacity-70 shrink-0">Background task dispatched</span>
          </div>
        )}

        {/* ── Filter bar ──────────────────────────────── */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-8
                        pb-6 border-b border-journal-border">

          {/* Category chips */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] font-mono text-journal-caption uppercase tracking-wider mr-1">
              Field
            </span>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                id={`cat-${cat.replace(/\s+/g, '-').toLowerCase()}`}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-150 border ${
                  selectedCategory === cat
                    ? 'bg-journal-primary text-white border-journal-primary'
                    : 'bg-journal-card border-journal-border text-journal-secondary hover:border-journal-terracotta hover:text-journal-terracotta'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Score filter + refresh */}
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-journal-caption uppercase tracking-wider">
              Impact
            </span>
            <div className="flex items-center gap-1 bg-journal-card rounded border border-journal-border p-1">
              {SCORE_FILTERS.map((f) => (
                <button
                  key={f.min}
                  id={`score-${f.min}`}
                  onClick={() => setMinScore(f.min)}
                  className={`px-3 py-1 rounded text-xs font-medium transition-all duration-150 ${
                    minScore === f.min
                      ? f.color === 'terracotta'
                        ? 'bg-journal-terracotta text-white'
                        : f.color === 'olive'
                        ? 'bg-journal-olive text-white'
                        : 'bg-journal-primary text-white'
                      : 'text-journal-secondary hover:text-journal-primary'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            <button
              id="refresh-btn"
              onClick={fetchArticles}
              title="Refresh"
              className="p-2 rounded border border-journal-border bg-journal-card
                         text-journal-caption hover:text-journal-terracotta hover:border-journal-terracotta
                         transition-all duration-150"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin-slow' : ''}`} />
            </button>
          </div>
        </div>

        {/* ── Grid ────────────────────────────────────── */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-72 rounded-lg skeleton" />
            ))}
          </div>
        ) : articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {articles.map((art, idx) => (
              <ResearchCard
                key={art.id || idx}
                article={art}
                style={{ animationDelay: `${idx * 60}ms` }}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            category={selectedCategory}
            minScore={minScore}
            onTrigger={handleTriggerPipeline}
            triggering={triggering}
          />
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────── */}
      <footer className="border-t border-journal-border py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row
                        items-center justify-between gap-2 text-[11px] text-journal-caption font-mono">
          <span>© 2025 Metis · AI Research Intelligence</span>
          <span className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-journal-olive' : 'bg-journal-muted'}`} />
            {isConnected ? 'Live stream connected' : 'Stream offline'}
          </span>
        </div>
      </footer>

      {/* ── Toast ───────────────────────────────────────── */}
      <Toast toast={toastMessage} onClose={() => setToastMessage(null)} />
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────── */

function StatPill({ icon, value, label, accent }) {
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${
      accent
        ? 'bg-journal-terracotta/8 border-journal-terracotta/20 text-journal-terracotta'
        : 'bg-journal-card border-journal-border text-journal-secondary'
    }`}>
      <span className="opacity-70">{icon}</span>
      <span className="font-bold text-[13px]">{value}</span>
      <span className="opacity-70">{label}</span>
    </div>
  );
}

function EmptyState({ category, minScore, onTrigger, triggering }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center
                    bg-journal-surface rounded-xl border border-dashed border-journal-border animate-fade-up">
      <h3 className="text-lg font-bold font-serif text-journal-primary">No papers found</h3>
      <p className="text-sm text-journal-caption mt-2 max-w-xs leading-relaxed">
        No curated articles match <strong>{category}</strong> with impact score ≥{minScore}.
        Run the ingestion pipeline to fetch new papers.
      </p>
      <button
        onClick={onTrigger}
        disabled={triggering}
        className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded
                   bg-journal-terracotta text-white text-sm font-semibold
                   hover:bg-journal-rust active:scale-95 transition-all duration-150
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {triggering ? (
          <><Loader2 className="w-4 h-4 animate-spin" /> Running…</>
        ) : (
          <><Play className="w-4 h-4 fill-current" /> Run Pipeline</>
        )}
      </button>
    </div>
  );
}
