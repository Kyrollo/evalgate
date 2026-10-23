import {
  EvaluationRun,
  GateEvaluationReport,
  InteractiveLabResponse,
  QualityGateRule,
  RegressionComparison,
  TestSuite,
} from '../types/evalgate';

const API_BASE = '/api/v1';

export async function fetchSuites(): Promise<TestSuite[]> {
  const res = await fetch(`${API_BASE}/suites`);
  if (!res.ok) throw new Error(`Failed to fetch suites: ${res.statusText}`);
  return res.json();
}

export async function fetchRuns(): Promise<EvaluationRun[]> {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error(`Failed to fetch runs: ${res.statusText}`);
  return res.json();
}

export async function fetchRegressionComparison(
  baselineId: string,
  candidateId: string
): Promise<RegressionComparison> {
  const res = await fetch(
    `${API_BASE}/regression/compare?baseline_id=${encodeURIComponent(baselineId)}&candidate_id=${encodeURIComponent(candidateId)}`
  );
  if (!res.ok) throw new Error(`Failed to fetch comparison: ${res.statusText}`);
  return res.json();
}

export async function fetchGateRules(): Promise<QualityGateRule[]> {
  const res = await fetch(`${API_BASE}/gates/rules`);
  if (!res.ok) throw new Error(`Failed to fetch gate rules: ${res.statusText}`);
  return res.json();
}

export async function evaluateGateRules(
  baselineId: string,
  candidateId: string
): Promise<GateEvaluationReport> {
  const res = await fetch(`${API_BASE}/gates/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ baseline_id: baselineId, candidate_id: candidateId }),
  });
  if (!res.ok) throw new Error(`Failed to evaluate gates: ${res.statusText}`);
  return res.json();
}

export async function runInteractiveLab(payload: {
  prompt: string;
  context?: string | null;
  reference_output?: string | null;
  model: string;
  assertions: Record<string, number>;
}): Promise<InteractiveLabResponse> {
  const res = await fetch(`${API_BASE}/lab/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorJson = await res.json().catch(() => ({}));
    const message = errorJson.detail?.detail || errorJson.detail || res.statusText;
    throw new Error(`Inference Lab failed: ${message}`);
  }
  return res.json();
}

export async function executeEvaluationRun(payload: {
  suite_id: string;
  label: string;
  model: string;
}): Promise<EvaluationRun> {
  const res = await fetch(`${API_BASE}/runs/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Run execution failed: ${err.detail?.detail || res.statusText}`);
  }
  return res.json();
}
