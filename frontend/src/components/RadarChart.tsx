import React from 'react';
import { MetricRegression } from '../types/evalgate';

interface RadarChartProps {
  metrics: Record<string, MetricRegression>;
}

export const RadarChart: React.FC<RadarChartProps> = ({ metrics }) => {
  const keys = ['correctness', 'faithfulness', 'answer_relevance', 'semantic_similarity', 'hallucination'];
  const labels = ['Correctness', 'Faithfulness', 'Relevance', 'Similarity', '1 - Hallucination'];

  const size = 260;
  const center = size / 2;
  const radius = size * 0.38;
  const totalAxes = keys.length;

  const getCoordinates = (value: number, index: number) => {
    const angle = (Math.PI * 2 / totalAxes) * index - Math.PI / 2;
    const r = Math.max(0, Math.min(1, value)) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  const getAxisPoints = (index: number) => {
    const angle = (Math.PI * 2 / totalAxes) * index - Math.PI / 2;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
      labelX: center + (radius + 22) * Math.cos(angle),
      labelY: center + (radius + 22) * Math.sin(angle),
    };
  };

  const baselinePoints = keys.map((key, idx) => {
    let val = metrics[key]?.baseline_mean ?? 0.85;
    if (key === 'hallucination') val = Math.max(0, 1 - val);
    return getCoordinates(val, idx);
  });

  const candidatePoints = keys.map((key, idx) => {
    let val = metrics[key]?.candidate_mean ?? 0.92;
    if (key === 'hallucination') val = Math.max(0, 1 - val);
    return getCoordinates(val, idx);
  });

  const baselinePolygon = baselinePoints.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const candidatePolygon = candidatePoints.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');

  return (
    <div className="flex flex-col items-center rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="mb-2 text-center">
        <h4 className="text-sm font-semibold tracking-wide text-slate-200">Metric Radar Alignment</h4>
        <p className="text-xs text-slate-400">Holistic multi-dimensional evaluation quality</p>
      </div>

      <div className="relative">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Concentric Polygons */}
          {[0.25, 0.5, 0.75, 1.0].map((ring) => {
            const points = Array.from({ length: totalAxes }).map((_, idx) => {
              const angle = (Math.PI * 2 / totalAxes) * idx - Math.PI / 2;
              return `${(center + radius * ring * Math.cos(angle)).toFixed(1)},${(center + radius * ring * Math.sin(angle)).toFixed(1)}`;
            }).join(' ');

            return (
              <polygon
                key={ring}
                points={points}
                fill="none"
                stroke="#334155"
                strokeWidth="0.8"
                strokeDasharray="2 2"
              />
            );
          })}

          {/* Axes */}
          {Array.from({ length: totalAxes }).map((_, idx) => {
            const axis = getAxisPoints(idx);
            return (
              <g key={idx}>
                <line
                  x1={center}
                  y1={center}
                  x2={axis.x}
                  y2={axis.y}
                  stroke="#334155"
                  strokeWidth="0.8"
                />
                <text
                  x={axis.labelX}
                  y={axis.labelY}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className="fill-slate-400 text-[10px] font-mono"
                >
                  {labels[idx]}
                </text>
              </g>
            );
          })}

          {/* Baseline Polygon */}
          <polygon
            points={baselinePolygon}
            fill="#06b6d4"
            fillOpacity="0.2"
            stroke="#06b6d4"
            strokeWidth="2"
          />

          {/* Candidate Polygon */}
          <polygon
            points={candidatePolygon}
            fill="#10b981"
            fillOpacity="0.25"
            stroke="#10b981"
            strokeWidth="2.2"
          />

          {/* Data Points */}
          {candidatePoints.map((p, idx) => (
            <circle
              key={idx}
              cx={p.x}
              cy={p.y}
              r="3.5"
              fill="#10b981"
              className="drop-shadow-sm shadow-emerald-500"
            />
          ))}
        </svg>
      </div>

      <div className="mt-2 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-cyan-400" />
          <span className="text-slate-300">Baseline</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-slate-300">Candidate</span>
        </div>
      </div>
    </div>
  );
};
