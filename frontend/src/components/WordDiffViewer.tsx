import React, { useState } from 'react';
import { CaseDiff } from '../types/evalgate';
import { ChevronRight, FileText, Split, Sparkles } from 'lucide-react';

interface WordDiffViewerProps {
  caseDiffs: CaseDiff[];
}

export const WordDiffViewer: React.FC<WordDiffViewerProps> = ({ caseDiffs }) => {
  const [selectedCaseId, setSelectedCaseId] = useState<string>(
    caseDiffs[0]?.case_id ?? ''
  );
  const [viewMode, setViewMode] = useState<'inline' | 'split'>('inline');

  const activeCase = caseDiffs.find((c) => c.case_id === selectedCaseId) || caseDiffs[0];

  if (!activeCase) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-8 text-center text-slate-500">
        No case diff comparisons available.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
      {/* Test Case Selector Sidebar */}
      <div className="lg:col-span-4 rounded-xl border border-slate-800/80 bg-slate-900/40 p-3 backdrop-blur-sm">
        <div className="mb-2 flex items-center justify-between px-2 pt-1">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Evaluated Cases ({caseDiffs.length})
          </h4>
          <span className="text-[11px] font-mono text-emerald-400">Word Myers Diff</span>
        </div>

        <div className="space-y-1.5 max-h-[460px] overflow-y-auto pr-1">
          {caseDiffs.map((c) => {
            const isSelected = c.case_id === activeCase.case_id;
            const corrDelta = c.score_deltas['correctness'] ?? 0;
            return (
              <button
                key={c.case_id}
                onClick={() => setSelectedCaseId(c.case_id)}
                className={`w-full text-left rounded-lg p-2.5 transition-all text-xs border ${
                  isSelected
                    ? 'border-emerald-500/50 bg-emerald-950/20 text-white shadow-sm'
                    : 'border-transparent bg-slate-900/60 text-slate-300 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono font-semibold text-slate-400">{c.case_id}</span>
                  <span
                    className={`font-mono text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                      corrDelta >= 0
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40'
                        : 'bg-rose-950 text-rose-400 border border-rose-800/40'
                    }`}
                  >
                    {corrDelta >= 0 ? `+${(corrDelta * 100).toFixed(1)}%` : `${(corrDelta * 100).toFixed(1)}%`}
                  </span>
                </div>
                <p className="line-clamp-1 font-medium text-slate-200">{c.case_name}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Diff Inspector Display */}
      <div className="lg:col-span-8 flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
        <div className="mb-3 flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/50">
                {activeCase.case_id}
              </span>
              <h3 className="text-sm font-semibold text-white">{activeCase.case_name}</h3>
            </div>
            <p className="mt-1 text-xs text-slate-400 font-mono line-clamp-1">
              Prompt: "{activeCase.prompt}"
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode(viewMode === 'inline' ? 'split' : 'inline')}
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
            >
              <Split className="h-3.5 w-3.5 text-slate-400" />
              <span>{viewMode === 'inline' ? 'Split View' : 'Inline Diff'}</span>
            </button>
          </div>
        </div>

        {/* Metric Badges */}
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {Object.entries(activeCase.score_deltas).map(([m, delta]) => (
            <div
              key={m}
              className="flex items-center gap-1.5 rounded-md border border-slate-800 bg-slate-950 px-2.5 py-1 text-[11px]"
            >
              <span className="text-slate-400 capitalize">{m.replace('_', ' ')}:</span>
              <span
                className={`font-mono font-semibold ${
                  (m === 'hallucination' || m === 'latency_ms')
                    ? (delta <= 0 ? 'text-emerald-400' : 'text-rose-400')
                    : (delta >= 0 ? 'text-emerald-400' : 'text-rose-400')
                }`}
              >
                {delta > 0 ? `+${delta}` : delta}
              </span>
            </div>
          ))}
        </div>

        {/* Diff Content View */}
        {viewMode === 'inline' ? (
          <div className="rounded-lg border border-slate-800/80 bg-slate-950/90 p-4 font-mono text-xs leading-relaxed overflow-y-auto max-h-[320px]">
            <div className="mb-2 flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-800 pb-1">
              <span>Candidate Output with Myers Word-Level Highlight</span>
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1 text-rose-400">
                  <span className="h-2 w-2 rounded bg-rose-500" /> Removed
                </span>
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="h-2 w-2 rounded bg-emerald-500" /> Added
                </span>
              </div>
            </div>
            <div>
              {activeCase.diff_tokens.map((token, i) => {
                if (token.type === 'added') {
                  return (
                    <span
                      key={i}
                      className="bg-emerald-950 text-emerald-300 font-semibold px-1 py-0.5 rounded mx-0.5 border border-emerald-700/50"
                    >
                      {token.text}
                    </span>
                  );
                }
                if (token.type === 'removed') {
                  return (
                    <span
                      key={i}
                      className="bg-rose-950/80 text-rose-300 line-through px-1 py-0.5 rounded mx-0.5 border border-rose-800/50"
                    >
                      {token.text}
                    </span>
                  );
                }
                return <span key={i} className="text-slate-300">{token.text}</span>;
              })}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[320px] overflow-y-auto">
            {/* Baseline column */}
            <div className="rounded-lg border border-slate-800/80 bg-slate-950/90 p-3 font-mono text-xs">
              <div className="mb-2 text-[11px] font-semibold text-cyan-400 border-b border-slate-800 pb-1">
                Baseline v1.0 Output
              </div>
              <p className="text-slate-300 leading-relaxed">{activeCase.baseline_output}</p>
            </div>
            {/* Candidate column */}
            <div className="rounded-lg border border-slate-800/80 bg-slate-950/90 p-3 font-mono text-xs">
              <div className="mb-2 text-[11px] font-semibold text-amber-400 border-b border-slate-800 pb-1">
                Candidate v1.1 Output
              </div>
              <p className="text-slate-300 leading-relaxed">{activeCase.candidate_output}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
