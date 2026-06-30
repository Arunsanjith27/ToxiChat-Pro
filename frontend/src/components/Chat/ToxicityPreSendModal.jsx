import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Send, Wand2, X } from 'lucide-react';

export default function ToxicityPreSendModal({ warning, onSendAnyway, onUseRewrite, onCancel }) {
  if (!warning) return null;

  const esc = warning.escalation || {};
  const levelColors = {
    critical: 'border-red-500/50 bg-red-500/10',
    high: 'border-orange-500/50 bg-orange-500/10',
    medium: 'border-amber-500/50 bg-amber-500/10',
    low: 'border-yellow-500/50 bg-yellow-500/10',
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        onClick={onCancel}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={e => e.stopPropagation()}
          className={`glass-panel max-w-md w-full p-6 rounded-2xl border-2 ${levelColors[esc.escalation_level] || levelColors.medium}`}
        >
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="w-8 h-8 text-amber-400 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold theme-text">Toxicity Warning</h3>
              <p className="theme-muted text-sm mt-1">{warning.message}</p>
            </div>
            <button onClick={onCancel} className="ml-auto theme-muted hover:theme-text">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="bg-black/20 rounded-xl p-4 mb-4">
            <p className="theme-text text-sm italic">"{warning.pending_text}"</p>
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-300">
                Score: {(warning.score * 100).toFixed(0)}%
              </span>
              <span className="text-xs px-2 py-1 rounded bg-amber-500/20 text-amber-300 capitalize">
                {warning.label} toxicity
              </span>
              {esc.conversation_health != null && (
                <span className="text-xs px-2 py-1 rounded bg-violet-500/20 text-violet-300">
                  Health: {esc.conversation_health}%
                </span>
              )}
              {esc.is_escalating && (
                <span className="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-300">
                  Escalating ({esc.trend})
                </span>
              )}
            </div>
            {warning.toxic_words?.length > 0 && (
              <p className="text-xs text-red-400 mt-2">
                Flagged words: {warning.toxic_words.join(', ')}
              </p>
            )}
          </div>

          {warning.rewrite && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 mb-4">
              <p className="text-xs text-emerald-400 font-semibold mb-1 flex items-center gap-1">
                <Wand2 className="w-3 h-3" /> Suggested rewrite
              </p>
              <p className="theme-text text-sm">{warning.rewrite}</p>
            </div>
          )}

          <div className="flex flex-col gap-2">
            {warning.rewrite && (
              <button onClick={onUseRewrite} className="btn-primary w-full flex items-center justify-center gap-2">
                <Wand2 className="w-4 h-4" /> Use Suggested Rewrite
              </button>
            )}
            <button onClick={onSendAnyway} className="w-full py-2.5 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 hover:bg-red-500/30 flex items-center justify-center gap-2 text-sm font-medium">
              <Send className="w-4 h-4" /> Send Anyway
            </button>
            <button onClick={onCancel} className="btn-secondary w-full py-2.5 text-sm">
              Cancel
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
