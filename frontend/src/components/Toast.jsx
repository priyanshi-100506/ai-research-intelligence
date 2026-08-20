import React, { useEffect } from 'react';
import { Sparkles, X, ExternalLink, Zap } from 'lucide-react';

export function Toast({ toast, onClose }) {
  // Auto-dismiss after 8 seconds
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(onClose, 8000);
    return () => clearTimeout(t);
  }, [toast, onClose]);

  if (!toast) return null;

  return (
    <div
      role="alert"
      aria-live="polite"
      className="fixed bottom-6 right-6 z-50 max-w-sm w-full
                 bg-journal-card border border-journal-terracotta/40
                 rounded-xl shadow-toast
                 animate-slide-in-right"
    >
      {/* Top accent line */}
      <div className="h-0.5 w-full bg-gradient-to-r from-journal-terracotta to-journal-gold rounded-t-xl" />

      <div className="p-4 flex items-start gap-3">
        {/* Icon */}
        <div className="shrink-0 w-9 h-9 rounded-lg bg-journal-terracotta/10
                        border border-journal-terracotta/20
                        flex items-center justify-center">
          <Zap className="w-4 h-4 text-journal-terracotta" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-journal-terracotta">
              New paper curated
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full
                             bg-journal-olive/12 text-journal-olive border border-journal-olive/25">
              {toast.impact_score}/10
            </span>
          </div>

          <h4 className="text-sm font-bold font-serif text-journal-primary leading-snug line-clamp-2">
            {toast.title}
          </h4>

          <p className="text-[12px] text-journal-secondary leading-relaxed mt-1 line-clamp-2">
            {toast.summary}
          </p>

          {toast.url && (
            <a
              href={toast.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-[11px] font-semibold
                         text-journal-terracotta hover:underline mt-2"
            >
              View Paper <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>

        {/* Close */}
        <button
          onClick={onClose}
          aria-label="Dismiss notification"
          className="shrink-0 p-1 rounded text-journal-caption
                     hover:text-journal-primary hover:bg-journal-surface
                     transition-colors duration-150"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
