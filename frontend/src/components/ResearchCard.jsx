import React from 'react';
import { ExternalLink, Cpu, Sparkles, Calendar, Tag } from 'lucide-react';

const IMPACT_CONFIG = {
  high:   { label: 'High Impact', cls: 'bg-journal-terracotta/10 text-journal-terracotta border-journal-terracotta/30' },
  mid:    { label: 'Notable',     cls: 'bg-journal-olive/10 text-journal-olive border-journal-olive/30' },
  low:    { label: 'Standard',    cls: 'bg-journal-card text-journal-secondary border-journal-border' },
};

function getImpactConfig(score) {
  if (score >= 8) return IMPACT_CONFIG.high;
  if (score >= 6) return IMPACT_CONFIG.mid;
  return IMPACT_CONFIG.low;
}

export function ResearchCard({ article, style }) {
  const {
    title          = 'Untitled Paper',
    url            = '#',
    summary        = 'No summary available.',
    justification  = '',
    tech_stack     = '',
    impact_score   = 0,
    category       = 'General',
    source_id      = 'ArXiv',
    published_date = 'Recent',
  } = article;

  const techTags = (typeof tech_stack === 'string' ? tech_stack : '')
    .split(',')
    .map((t) => t.trim())
    .filter((t) => t && t !== 'None' && t !== 'N/A');

  const impact = getImpactConfig(impact_score);

  return (
    <article
      style={style}
      className="group relative flex flex-col bg-journal-card border border-journal-border
                 rounded-lg p-6 shadow-card hover:shadow-card-hover
                 hover:border-journal-terracotta/40
                 transition-all duration-200 ease-smooth animate-fade-up"
    >
      {/* ── Header row ─────────────────────────────── */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Source badge */}
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px]
                           font-mono font-semibold text-journal-terracotta
                           bg-journal-terracotta/10 border border-journal-terracotta/20">
            {source_id}
          </span>
          {/* Category */}
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px]
                           font-medium text-journal-secondary
                           bg-journal-surface border border-journal-border">
            <Tag className="w-3 h-3 opacity-60" />
            {category}
          </span>
        </div>

        {/* Impact score */}
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs
                          font-semibold border shrink-0 ${impact.cls}`}>
          <Sparkles className="w-3 h-3" />
          {impact_score}/10
        </span>
      </div>

      {/* ── Title ──────────────────────────────────── */}
      <h3 className="text-[15px] font-bold font-serif text-journal-primary leading-snug
                     group-hover:text-journal-terracotta transition-colors duration-150">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-start gap-1.5 hover:underline underline-offset-2"
        >
          <span>{title}</span>
          <ExternalLink className="w-3.5 h-3.5 shrink-0 mt-0.5 text-journal-caption
                                   group-hover:text-journal-terracotta transition-colors" />
        </a>
      </h3>

      {/* ── AI Summary box ─────────────────────────── */}
      <div className="mt-4 rounded-lg bg-journal-bg border border-journal-border/70 p-4 flex-1">
        <div className="flex items-center justify-between mb-2.5">
          <span className="flex items-center gap-1.5 text-[10px] font-semibold
                           uppercase tracking-widest text-journal-terracotta">
            <Cpu className="w-3.5 h-3.5" />
            Gemini Summary
          </span>
          {published_date && (
            <span className="flex items-center gap-1 text-[10px] text-journal-caption font-mono">
              <Calendar className="w-3 h-3 opacity-60" />
              {published_date}
            </span>
          )}
        </div>
        <p className="text-[13px] text-journal-secondary leading-relaxed">
          {summary}
        </p>
      </div>

      {/* ── Justification ──────────────────────────── */}
      {justification && (
        <p className="text-xs text-journal-caption leading-relaxed mt-3.5">
          <span className="font-semibold text-journal-tertiary">Why it matters: </span>
          {justification}
        </p>
      )}

      {/* ── Tech Stack ─────────────────────────────── */}
      <div className="mt-5 pt-4 border-t border-journal-border/60 flex flex-wrap gap-1.5 items-center">
        <span className="text-[10px] font-mono text-journal-caption uppercase tracking-wider mr-1">
          Stack
        </span>
        {techTags.length > 0 ? (
          techTags.map((tag, i) => (
            <span
              key={i}
              className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono
                         bg-journal-bg text-journal-secondary border border-journal-border
                         hover:border-journal-terracotta hover:text-journal-terracotta
                         transition-colors duration-150 cursor-default"
            >
              {tag}
            </span>
          ))
        ) : (
          <span className="text-xs text-journal-caption italic">General ML / Algorithmic</span>
        )}
      </div>
    </article>
  );
}
