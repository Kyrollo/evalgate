import React from 'react';
import { Play, ShieldCheck, Activity, Cpu } from 'lucide-react';
import { EvaluationRun, RegressionComparison, TestSuite } from '../types/evalgate';

interface HeaderProps {
  suites: TestSuite[];
  runs: EvaluationRun[];
  comparison: RegressionComparison | null;
  onExecuteSuite?: () => void;
  executing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  suites,
  runs,
  comparison,
  onExecuteSuite,
  executing,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Project */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-bold shadow-lg shadow-emerald-950/50">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-white tracking-tight">EvalGate</span>
                <span className="rounded bg-emerald-950/80 border border-emerald-700/60 px-1.5 py-0.5 text-[10px] font-mono text-emerald-400">
                  v1.0.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">LLM Regression Testing & Quality Gates</p>
            </div>
          </div>

          {/* Active Benchmark Suite & Models */}
          <div className="hidden lg:flex items-center gap-2 border-l border-slate-800 pl-6 text-xs">
            <span className="text-slate-400">Benchmark:</span>
            <span className="font-semibold text-slate-200">Dialogue & RAG Core v2.1</span>
            <span className="text-slate-600">|</span>
            <span className="text-cyan-400 font-mono">Baseline v1.0</span>
            <span className="text-slate-600">vs</span>
            <span className="text-amber-400 font-mono">Candidate v1.1</span>
          </div>
        </div>

        {/* Right Status Badges & Quick Action */}
        <div className="flex items-center gap-4">
          {/* GPU Hardware Telemetry */}
          <div className="hidden sm:flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-2.5 py-1 text-xs">
            <Cpu className="h-3.5 w-3.5 text-emerald-400" />
            <span className="text-slate-300 font-mono">Dedicated NVIDIA GPU (16GB)</span>
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </div>

          {/* Gate Status Pill */}
          <div className="flex items-center gap-1.5 rounded-lg border border-emerald-800/60 bg-emerald-950/40 px-3 py-1 text-xs font-mono font-semibold text-emerald-400">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>GATE: PASS</span>
          </div>

          {/* Trigger Benchmark Evaluation Run */}
          {onExecuteSuite && (
            <button
              onClick={onExecuteSuite}
              disabled={executing}
              className="flex items-center gap-2 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-md shadow-emerald-900/40 hover:bg-emerald-500 disabled:opacity-50 transition"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>{executing ? 'Evaluating...' : 'Run Benchmark'}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
