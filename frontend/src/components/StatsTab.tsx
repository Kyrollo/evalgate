import React, { useState } from 'react';
import { RegressionComparison } from '../types/evalgate';
import { KdeChart } from './KdeChart';
import { BoxPlotChart } from './BoxPlotChart';
import { Activity, BarChart2, Layers } from 'lucide-react';

interface StatsTabProps {
  comparison: RegressionComparison | null;
}

export const StatsTab: React.FC<StatsTabProps> = ({ comparison }) => {
  const [selectedMetric, setSelectedMetric] = useState<string>('correctness');

  if (!comparison) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/30 text-sm text-slate-400">
        Loading statistical distribution data...
      </div>
    );
  }

  const kdePoints = comparison.kde_points[selectedMetric] || [];
  const currentStat = comparison.metrics[selectedMetric];

  return (
    <div className="space-y-6">
      {/* Metric Selector Bar */}
      <div className="flex flex-wrap items-center justify-between rounded-xl border border-slate-800/80 bg-slate-900/40 p-3 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wide">
            Statistical Metric Focus:
          </span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {Object.keys(comparison.metrics).map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMetric(m)}
              className={`rounded-lg px-3 py-1 text-xs font-mono transition capitalize ${
                selectedMetric === m
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm'
                  : 'bg-slate-800/60 text-slate-400 hover:bg-slate-700/60'
              }`}
            >
              {m.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Distribution Curves Row: KDE + Box Plots */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <KdeChart
          points={kdePoints}
          metricName={selectedMetric}
          baselineLabel={comparison.baseline_label}
          candidateLabel={comparison.candidate_label}
        />
        <BoxPlotChart
          boxPlots={comparison.box_plots}
          baselineLabel={comparison.baseline_label}
          candidateLabel={comparison.candidate_label}
        />
      </div>

      {/* Statistical Significance Matrix */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">
              Welch's Two-Sample t-Test & Non-Parametric Significance Matrix
            </h3>
            <p className="text-xs text-slate-400">
              Hypothesis testing parameters, effect size (Cohen's d), and 95% Bootstrap Confidence Intervals
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded bg-emerald-500" />
              <span className="text-slate-300">p &lt; 0.05 (Significant)</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded bg-rose-500" />
              <span className="text-slate-300">p &ge; 0.05 (Inconclusive)</span>
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Metric</th>
                <th className="py-2.5 px-3 text-right">t-Statistic</th>
                <th className="py-2.5 px-3 text-right">p-Value</th>
                <th className="py-2.5 px-3 text-right">Mann-Whitney U</th>
                <th className="py-2.5 px-3 text-right">Cohen's d</th>
                <th className="py-2.5 px-3 text-right">95% Bootstrap CI</th>
                <th className="py-2.5 px-3 text-center">Effect Size</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {Object.entries(comparison.metrics).map(([key, m]) => {
                const isSig = m.p_value < 0.05;
                const absD = Math.abs(m.cohens_d);
                let effectLabel = 'Negligible';
                if (absD >= 0.8) effectLabel = 'Large';
                else if (absD >= 0.5) effectLabel = 'Medium';
                else if (absD >= 0.2) effectLabel = 'Small';

                return (
                  <tr key={key} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-3 font-sans font-medium text-slate-200 capitalize">
                      {m.metric_name.replace('_', ' ')}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-300">
                      {m.t_statistic.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <span
                        className={`px-2 py-0.5 rounded font-bold ${
                          isSig
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/60'
                            : 'bg-rose-950 text-rose-300 border border-rose-700/60'
                        }`}
                      >
                        {m.p_value.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-400">
                      {m.mann_whitney_u.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-200 font-semibold">
                      {m.cohens_d.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-400">
                      [{m.ci_95_low.toFixed(3)}, {m.ci_95_high.toFixed(3)}]
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="font-sans text-[11px] text-slate-300">{effectLabel}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
