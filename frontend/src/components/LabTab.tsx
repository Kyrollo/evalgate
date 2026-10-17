import React, { useState } from 'react';
import { InteractiveLabResponse } from '../types/evalgate';
import { runInteractiveLab } from '../lib/api';
import { Play, Sparkles, Terminal, CheckCircle2, XCircle, Clock, Database, Cpu } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';

export const LabTab: React.FC = () => {
  const [prompt, setPrompt] = useState(
    'What is the return window for defective hardware under our warranty policy?'
  );
  const [context, setContext] = useState(
    'All hardware devices carry a 30-day refund policy. Defective units reported within 90 days are eligible for complimentary replacement or store credit. Opened accessories are non-refundable after 14 days.'
  );
  const [reference, setReference] = useState(
    'Defective units reported within 90 days are eligible for complimentary replacement or store credit.'
  );
  const [model, setModel] = useState('qwen2.5:0.5b');
  const [assertions, setAssertions] = useState({
    faithfulness: 0.80,
    answer_relevance: 0.75,
    hallucination: 0.10,
    semantic_similarity: 0.80,
  });

  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([
    '[SYSTEM] Interactive LLM Assertion Lab ready.',
    '[HARDWARE] Target GPU: Dedicated NVIDIA GPU (16GB VRAM warm).',
    '[MODEL] Default endpoint: Ollama http://127.0.0.1:11434 (model: qwen2.5:0.5b).',
  ]);
  const [result, setResult] = useState<InteractiveLabResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    const now = new Date().toLocaleTimeString();
    setLogs((prev) => [
      ...prev,
      `[${now}] Submitting prompt to ${model} on local GPU...`,
      `[${now}] Awaiting inference stream...`,
    ]);

    try {
      const resp = await runInteractiveLab({
        prompt,
        context,
        reference_output: reference,
        model,
        assertions,
      });
      const endNow = new Date().toLocaleTimeString();
      setResult(resp);
      setLogs((prev) => [
        ...prev,
        `[${endNow}] Completed in ${resp.latency_ms}ms (${resp.tokens_used} tokens).`,
        `[${endNow}] Evaluator metrics: Faithfulness=${resp.metrics.faithfulness}, Rel=${resp.metrics.answer_relevance}, Hall=${resp.metrics.hallucination}, Sim=${resp.metrics.semantic_similarity}`,
        `[${endNow}] Status: ${resp.overall_passed ? 'ALL ASSERTIONS PASSED' : 'ASSERTIONS FAILED'}`,
      ]);
    } catch (err: any) {
      const errNow = new Date().toLocaleTimeString();
      setError(err.message || 'Execution failed');
      setLogs((prev) => [
        ...prev,
        `[${errNow}] ERROR: ${err.message || 'Execution failed'}`,
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-emerald-950 p-2 text-emerald-400 border border-emerald-800">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              Interactive Test Assertion & Metric Evaluation Lab
            </h3>
            <p className="text-xs text-slate-400">
              Run custom prompts with live evaluation assertions on local Dedicated NVIDIA GPU
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 font-mono text-xs text-slate-200 outline-none focus:border-emerald-500"
          >
            <option value="qwen2.5:0.5b">qwen2.5:0.5b (Local GPU Warm)</option>
            <option value="llama3.2:latest">llama3.2:latest (Local Ollama)</option>
            <option value="gpt-4o-mini">gpt-4o-mini (Cloud Provider)</option>
          </select>

          <button
            onClick={handleRun}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white shadow-md shadow-emerald-900/40 hover:bg-emerald-500 disabled:opacity-50 transition"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>{loading ? 'Evaluating...' : 'Run Assertion Test'}</span>
          </button>
        </div>
      </div>

      {/* 3-Column Split Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column: Test Case Builder & Assertion Rules */}
        <div className="lg:col-span-4 space-y-4 rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Prompt & Context Builder
          </h4>

          <div>
            <label className="text-[11px] font-medium text-slate-300">Prompt Query</label>
            <textarea
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 p-2.5 font-mono text-xs text-slate-200 outline-none focus:border-emerald-500 resize-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-medium text-slate-300">Grounding Context (RAG)</label>
            <textarea
              rows={4}
              value={context}
              onChange={(e) => setContext(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 p-2.5 font-mono text-xs text-slate-200 outline-none focus:border-emerald-500 resize-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-medium text-slate-300">Reference Ground Truth Output</label>
            <textarea
              rows={2}
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 p-2.5 font-mono text-xs text-slate-200 outline-none focus:border-emerald-500 resize-none"
            />
          </div>

          {/* Assertion Sliders */}
          <div className="space-y-3 pt-2 border-t border-slate-800">
            <h5 className="text-[11px] font-semibold uppercase text-slate-400">
              Quality Assertion Thresholds
            </h5>

            <div>
              <div className="flex justify-between text-[11px] text-slate-300">
                <span>Faithfulness Threshold</span>
                <span className="font-mono text-emerald-400">{assertions.faithfulness.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={assertions.faithfulness}
                onChange={(e) =>
                  setAssertions({ ...assertions, faithfulness: parseFloat(e.target.value) })
                }
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-300">
                <span>Answer Relevance Threshold</span>
                <span className="font-mono text-emerald-400">{assertions.answer_relevance.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={assertions.answer_relevance}
                onChange={(e) =>
                  setAssertions({ ...assertions, answer_relevance: parseFloat(e.target.value) })
                }
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-300">
                <span>Max Hallucination Ceiling</span>
                <span className="font-mono text-rose-400">{assertions.hallucination.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.4"
                step="0.02"
                value={assertions.hallucination}
                onChange={(e) =>
                  setAssertions({ ...assertions, hallucination: parseFloat(e.target.value) })
                }
                className="w-full accent-rose-500"
              />
            </div>
          </div>
        </div>

        {/* Center Column: Live Terminal Execution */}
        <div className="lg:col-span-4 flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
          <div className="mb-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-emerald-400" />
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Execution Stream
              </h4>
            </div>
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>

          <div className="flex-1 rounded-lg border border-slate-800 bg-slate-950 p-3 font-mono text-[11px] text-slate-400 overflow-y-auto max-h-[380px] space-y-1">
            {logs.map((log, idx) => (
              <div
                key={idx}
                className={
                  log.includes('ERROR')
                    ? 'text-rose-400 font-bold'
                    : log.includes('PASSED')
                    ? 'text-emerald-400 font-bold'
                    : 'text-slate-400'
                }
              >
                {log}
              </div>
            ))}
          </div>

          {result && (
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-2">
                <span className="text-slate-500 text-[10px]">Latency</span>
                <div className="text-emerald-400 font-bold">{result.latency_ms}ms</div>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-2">
                <span className="text-slate-500 text-[10px]">Tokens Used</span>
                <div className="text-amber-400 font-bold">{result.tokens_used} tokens</div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Results, Assertions, and Output Diff */}
        <div className="lg:col-span-4 flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Assertion Verdict
            </h4>
            {result && (
              <span
                className={`flex items-center gap-1 rounded-md px-2 py-0.5 font-mono text-xs font-bold ${
                  result.overall_passed
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    : 'bg-rose-950 text-rose-400 border border-rose-800'
                }`}
              >
                {result.overall_passed ? (
                  <>
                    <CheckCircle2 className="h-3 w-3" /> PASS
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3" /> FAIL
                  </>
                )}
              </span>
            )}
          </div>

          {result ? (
            <div className="space-y-4">
              {/* Assertion Rules Checks */}
              <div className="space-y-1.5">
                {result.assertion_results.map((chk, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/70 p-2 text-xs"
                  >
                    <span className="capitalize text-slate-300">
                      {chk.metric.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2 font-mono">
                      <span className="text-slate-400">
                        Obs: {chk.observed_score.toFixed(2)} (Req: {chk.threshold.toFixed(2)})
                      </span>
                      {chk.passed ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      ) : (
                        <XCircle className="h-3.5 w-3.5 text-rose-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Completion text with Word Diff */}
              <div className="rounded-lg border border-slate-800 bg-slate-950/90 p-3 font-mono text-xs overflow-y-auto min-h-[160px] max-h-[520px]">
                <div className="mb-1 text-[10px] text-slate-500 font-sans font-semibold">
                  Model Output vs Reference Ground Truth:
                </div>
                {result.diff_tokens && result.diff_tokens.length > 0 ? (
                  <div>
                    {result.diff_tokens.map((token, i) => {
                      if (token.type === 'added') {
                        return (
                          <span
                            key={i}
                            className="bg-emerald-950 text-emerald-300 font-semibold px-1 py-0.5 rounded mx-0.5"
                          >
                            {token.text}
                          </span>
                        );
                      }
                      if (token.type === 'removed') {
                        return (
                          <span
                            key={i}
                            className="bg-rose-950 text-rose-300 line-through px-1 py-0.5 rounded mx-0.5"
                          >
                            {token.text}
                          </span>
                        );
                      }
                      return <span key={i} className="text-slate-300">{token.text}</span>;
                    })}
                  </div>
                ) : (
                  <MarkdownRenderer content={result.completion} defaultMaxHeight="max-h-[420px]" />
                )}
              </div>
            </div>
          ) : (
            <div className="flex h-56 flex-col items-center justify-center rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-center text-xs text-slate-500">
              <Sparkles className="h-8 w-8 text-slate-700 mb-2" />
              Click "Run Assertion Test" to trigger live execution against local GPU Ollama.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
