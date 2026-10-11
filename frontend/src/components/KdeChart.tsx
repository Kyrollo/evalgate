import React from 'react';
import { KdePoint } from '../types/evalgate';

interface KdeChartProps {
  points: KdePoint[];
  metricName: string;
  baselineLabel: string;
  candidateLabel: string;
}

export const KdeChart: React.FC<KdeChartProps> = ({
  points,
  metricName,
  baselineLabel,
  candidateLabel,
}) => {
  if (!points || points.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/50 text-xs text-slate-500">
        Insufficient distribution observations to render Kernel Density Estimation.
      </div>
    );
  }

  const width = 580;
  const height = 220;
  const padding = { top: 20, right: 30, bottom: 40, left: 45 };

  const xMin = Math.min(...points.map((p) => p.x));
  const xMax = Math.max(...points.map((p) => p.x));
  const maxDensity = Math.max(
    ...points.map((p) => Math.max(p.baseline_density, p.candidate_density)),
    0.01
  );

  const xScale = (x: number) =>
    padding.left + ((x - xMin) / (xMax - xMin || 1)) * (width - padding.left - padding.right);
  const yScale = (y: number) =>
    height - padding.bottom - (y / maxDensity) * (height - padding.top - padding.bottom);

  const baselinePath = points
    .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${xScale(p.x).toFixed(1)} ${yScale(p.baseline_density).toFixed(1)}`)
    .join(' ');

  const candidatePath = points
    .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${xScale(p.x).toFixed(1)} ${yScale(p.candidate_density).toFixed(1)}`)
    .join(' ');

  const baselineArea = `${baselinePath} L ${xScale(points[points.length - 1].x).toFixed(1)} ${height - padding.bottom} L ${xScale(points[0].x).toFixed(1)} ${height - padding.bottom} Z`;
  const candidateArea = `${candidatePath} L ${xScale(points[points.length - 1].x).toFixed(1)} ${height - padding.bottom} L ${xScale(points[0].x).toFixed(1)} ${height - padding.bottom} Z`;

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold tracking-wide text-slate-200">
            Statistical Distribution (KDE) — {metricName.toUpperCase()}
          </h4>
          <p className="text-xs text-slate-400">
            Kernel density estimation across evaluation sample population
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-500 shadow-sm shadow-cyan-500/50" />
            <span className="text-slate-300">{baselineLabel}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
            <span className="text-slate-300">{candidateLabel}</span>
          </div>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-lg bg-slate-950/70 p-2">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          <defs>
            <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="candidateGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const y = height - padding.bottom - pct * (height - padding.top - padding.bottom);
            return (
              <g key={i}>
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
                  {(pct * maxDensity).toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Area fills */}
          <path d={baselineArea} fill="url(#baselineGrad)" />
          <path d={candidateArea} fill="url(#candidateGrad)" />

          {/* Lines */}
          <path
            d={baselinePath}
            fill="none"
            stroke="#06b6d4"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
          <path
            d={candidatePath}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="2.2"
            strokeLinecap="round"
          />

          {/* X Axis ticks */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const val = xMin + pct * (xMax - xMin);
            const x = xScale(val);
            return (
              <g key={i}>
                <line
                  x1={x}
                  y1={height - padding.bottom}
                  x2={x}
                  y2={height - padding.bottom + 5}
                  stroke="#475569"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 16}
                  textAnchor="middle"
                  className="fill-slate-400 text-[10px] font-mono"
                >
                  {val.toFixed(2)}
                </text>
              </g>
            );
          })}

          <text
            x={width / 2}
            y={height - 5}
            textAnchor="middle"
            className="fill-slate-500 text-[11px] font-medium"
          >
            Observation Score Value
          </text>
        </svg>
      </div>
    </div>
  );
};
