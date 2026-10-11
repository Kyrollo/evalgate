import React from 'react';
import { BoxPlotStats } from '../types/evalgate';

interface BoxPlotChartProps {
  boxPlots: Record<string, Record<string, BoxPlotStats>>;
  baselineLabel: string;
  candidateLabel: string;
}

export const BoxPlotChart: React.FC<BoxPlotChartProps> = ({
  boxPlots,
  baselineLabel,
  candidateLabel,
}) => {
  const metricKeys = Object.keys(boxPlots).filter((k) => k !== 'latency_ms');

  if (metricKeys.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/50 text-xs text-slate-500">
        No box plot distributions available.
      </div>
    );
  }

  const width = 580;
  const height = 220;
  const padding = { top: 20, right: 25, bottom: 40, left: 45 };

  const yScale = (val: number) =>
    height - padding.bottom - val * (height - padding.top - padding.bottom);

  const slotWidth = (width - padding.left - padding.right) / metricKeys.length;

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold tracking-wide text-slate-200">
            Comparative Five-Number Box Plots
          </h4>
          <p className="text-xs text-slate-400">
            Quartiles (Q1, Median, Q3) and whiskers (Min, Max) per evaluation dimension
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded bg-cyan-500" />
            <span className="text-slate-300">Baseline</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded bg-amber-500" />
            <span className="text-slate-300">Candidate</span>
          </div>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-lg bg-slate-950/70 p-2">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          {/* Y Axis Grid */}
          {[0, 0.2, 0.4, 0.6, 0.8, 1.0].map((v, idx) => {
            const y = yScale(v);
            return (
              <g key={idx}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#334155"
                  strokeDasharray="3 3"
                  strokeWidth="0.8"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-slate-500 text-[10px] font-mono"
                >
                  {v.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Metric Columns */}
          {metricKeys.map((metric, idx) => {
            const xCenter = padding.left + idx * slotWidth + slotWidth / 2;
            const b = boxPlots[metric]?.baseline;
            const c = boxPlots[metric]?.candidate;

            if (!b || !c) return null;

            const boxWidth = Math.min(22, slotWidth * 0.35);
            const bX = xCenter - boxWidth - 3;
            const cX = xCenter + 3;

            return (
              <g key={metric}>
                {/* Baseline Whisker & Box */}
                <line
                  x1={bX + boxWidth / 2}
                  y1={yScale(b.min)}
                  x2={bX + boxWidth / 2}
                  y2={yScale(b.max)}
                  stroke="#06b6d4"
                  strokeWidth="1.5"
                />
                <line
                  x1={bX + 2}
                  y1={yScale(b.min)}
                  x2={bX + boxWidth - 2}
                  y2={yScale(b.min)}
                  stroke="#06b6d4"
                  strokeWidth="1.5"
                />
                <line
                  x1={bX + 2}
                  y1={yScale(b.max)}
                  x2={bX + boxWidth - 2}
                  y2={yScale(b.max)}
                  stroke="#06b6d4"
                  strokeWidth="1.5"
                />
                <rect
                  x={bX}
                  y={yScale(b.q3)}
                  width={boxWidth}
                  height={Math.max(2, yScale(b.q1) - yScale(b.q3))}
                  fill="#083344"
                  stroke="#06b6d4"
                  strokeWidth="1.5"
                  rx="2"
                />
                <line
                  x1={bX}
                  y1={yScale(b.median)}
                  x2={bX + boxWidth}
                  y2={yScale(b.median)}
                  stroke="#38bdf8"
                  strokeWidth="2"
                />

                {/* Candidate Whisker & Box */}
                <line
                  x1={cX + boxWidth / 2}
                  y1={yScale(c.min)}
                  x2={cX + boxWidth / 2}
                  y2={yScale(c.max)}
                  stroke="#f59e0b"
                  strokeWidth="1.5"
                />
                <line
                  x1={cX + 2}
                  y1={yScale(c.min)}
                  x2={cX + boxWidth - 2}
                  y2={yScale(c.min)}
                  stroke="#f59e0b"
                  strokeWidth="1.5"
                />
                <line
                  x1={cX + 2}
                  y1={yScale(c.max)}
                  x2={cX + boxWidth - 2}
                  y2={yScale(c.max)}
                  stroke="#f59e0b"
                  strokeWidth="1.5"
                />
                <rect
                  x={cX}
                  y={yScale(c.q3)}
                  width={boxWidth}
                  height={Math.max(2, yScale(c.q1) - yScale(c.q3))}
                  fill="#451a03"
                  stroke="#f59e0b"
                  strokeWidth="1.5"
                  rx="2"
                />
                <line
                  x1={cX}
                  y1={yScale(c.median)}
                  x2={cX + boxWidth}
                  y2={yScale(c.median)}
                  stroke="#fbbf24"
                  strokeWidth="2"
                />

                {/* Label */}
                <text
                  x={xCenter}
                  y={height - padding.bottom + 18}
                  textAnchor="middle"
                  className="fill-slate-400 text-[10px] font-mono capitalize"
                >
                  {metric.replace('_', ' ')}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
