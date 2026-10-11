import React, { useState } from 'react';
import { GateEvaluationReport, QualityGateRule, RegressionComparison } from '../types/evalgate';
import { CheckCircle2, XCircle, AlertTriangle, Shield, Sliders, Play } from 'lucide-react';

interface GateRulesTabProps {
  comparison: RegressionComparison | null;
  rules: QualityGateRule[];
  report: GateEvaluationReport | null;
  onRefreshGates?: () => void;
}

export const GateRulesTab: React.FC<GateRulesTabProps> = ({
  comparison,
  rules,
  report,
  onRefreshGates,
}) => {
  const [localRules, setLocalRules] = useState<QualityGateRule[]>(rules);

  const toggleRule = (ruleId: string) => {
    setLocalRules((prev) =>
      prev.map((r) => (r.rule_id === ruleId ? { ...r, enabled: !r.enabled } : r))
    );
  };

  const currentReport = report || comparison?.gate_report;
  const isPassed = currentReport?.verdict === 'PASS';
  const isWarn = currentReport?.verdict === 'WARN';

  return (
    <div className="space-y-6">
      {/* CI Gate Status Banner */}
      <div
        className={`rounded-xl border p-5 backdrop-blur-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
          isPassed
            ? 'border-emerald-700/60 bg-emerald-950/20'
            : isWarn
            ? 'border-amber-700/60 bg-amber-950/20'
            : 'border-rose-700/60 bg-rose-950/20'
        }`}
      >
        <div className="flex items-center gap-3">
          <div
            className={`p-2.5 rounded-lg border ${
              isPassed
                ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                : isWarn
                ? 'bg-amber-950 text-amber-400 border-amber-800'
                : 'bg-rose-950 text-rose-400 border-rose-800'
            }`}
          >
            {isPassed ? (
              <CheckCircle2 className="h-6 w-6" />
            ) : isWarn ? (
              <AlertTriangle className="h-6 w-6" />
            ) : (
              <XCircle className="h-6 w-6" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">
                CI/CD Quality Gate Status: {currentReport?.verdict || 'PASS'}
              </h3>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
                exit code: {isPassed ? '0' : '1'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {currentReport
                ? `${currentReport.passed_rules} of ${currentReport.total_rules} rules satisfied. ${currentReport.breaches.length} breaches detected.`
                : 'All criteria evaluated and satisfied.'}
            </p>
          </div>
        </div>

        {onRefreshGates && (
          <button
            onClick={onRefreshGates}
            className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-900/40 hover:bg-emerald-500 transition"
          >
            <Play className="h-3.5 w-3.5" /> Re-Evaluate Gates
          </button>
        )}
      </div>

      {/* Breaches List if any */}
      {currentReport && currentReport.breaches.length > 0 && (
        <div className="rounded-xl border border-rose-800/80 bg-rose-950/30 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-300 mb-2 flex items-center gap-1.5">
            <AlertTriangle className="h-4 w-4" /> Policy Breach Diagnostics
          </h4>
          <div className="space-y-2">
            {currentReport.breaches.map((b, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between rounded-lg border border-rose-900/60 bg-slate-950/80 p-3 text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-rose-400">{b.rule_id}</span>
                    <span className="font-semibold text-slate-200">{b.name}</span>
                    <span className="rounded bg-rose-950 px-1.5 py-0.5 font-mono text-[10px] text-rose-300 border border-rose-800">
                      {b.severity}
                    </span>
                  </div>
                  <p className="mt-1 text-slate-400">{b.message}</p>
                </div>
                <div className="text-right font-mono text-xs">
                  <div className="text-slate-400">Observed: {b.observed_value.toFixed(3)}</div>
                  <div className="text-slate-500">Threshold: {b.threshold.toFixed(3)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rules Configuration Table */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Quality Gate Rules Registry</h3>
            <p className="text-xs text-slate-400">
              Deterministic threshold criteria that enforce LLM reliability in CI pipelines
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {localRules.filter((r) => r.enabled).length} Active Rules
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Rule ID</th>
                <th className="py-2.5 px-3">Criterion Name</th>
                <th className="py-2.5 px-3">Target Metric</th>
                <th className="py-2.5 px-3">Operator</th>
                <th className="py-2.5 px-3 text-right">Threshold</th>
                <th className="py-2.5 px-3 text-center">Severity</th>
                <th className="py-2.5 px-3 text-center">Active</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {localRules.map((r) => (
                <tr key={r.rule_id} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-3 font-bold text-emerald-400">{r.rule_id}</td>
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-200">
                    <div>{r.name}</div>
                    <div className="text-[10px] text-slate-500">{r.description}</div>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 capitalize">{r.metric.replace('_', ' ')}</td>
                  <td className="py-2.5 px-3 text-slate-400">{r.operator}</td>
                  <td className="py-2.5 px-3 text-right text-slate-200 font-semibold">
                    {r.threshold.toFixed(2)}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold uppercase ${
                        r.severity === 'BLOCKER'
                          ? 'bg-rose-950 text-rose-400 border border-rose-800/50'
                          : 'bg-amber-950 text-amber-400 border border-amber-800/50'
                      }`}
                    >
                      {r.severity}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <button
                      onClick={() => toggleRule(r.rule_id)}
                      className={`h-4 w-8 rounded-full transition-colors relative ${
                        r.enabled ? 'bg-emerald-600' : 'bg-slate-700'
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 h-3 w-3 rounded-full bg-white transition-transform ${
                          r.enabled ? 'right-0.5' : 'left-0.5'
                        }`}
                      />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
