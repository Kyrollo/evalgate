export interface TestCase {
  id: string;
  suite_id: string;
  name: string;
  prompt: string;
  context?: string | null;
  expected_output?: string | null;
  tags: string[];
}

export interface TestSuite {
  id: string;
  name: string;
  description: string;
  default_model: string;
  test_cases: TestCase[];
}

export interface RunResult {
  id: string;
  run_id: string;
  case_id: string;
  case_name: string;
  prompt: string;
  model_output: string;
  reference_output?: string | null;
  metrics: Record<string, number>;
  latency_ms: number;
  tokens_used: number;
  passed: boolean;
  error_message?: string | null;
}

export interface MetricSummary {
  mean: number;
  std_dev: number;
  median: number;
  p95: number;
  min: number;
  max: number;
}

export interface EvaluationRun {
  id: string;
  suite_id: string;
  label: string;
  model: string;
  created_at: string;
  status: string;
  results: RunResult[];
  summary_metrics: Record<string, MetricSummary>;
}

export interface MetricRegression {
  metric_name: string;
  baseline_mean: number;
  candidate_mean: number;
  delta: number;
  relative_change_pct: number;
  t_statistic: number;
  p_value: number;
  is_significant: boolean;
  cohens_d: number;
  mann_whitney_u: number;
  ci_95_low: number;
  ci_95_high: number;
  status: 'IMPROVEMENT' | 'REGRESSION' | 'NEGLIGIBLE';
}

export interface DiffToken {
  type: 'added' | 'removed' | 'unchanged';
  text: string;
}

export interface CaseDiff {
  case_id: string;
  case_name: string;
  prompt: string;
  baseline_output: string;
  candidate_output: string;
  diff_tokens: DiffToken[];
  score_deltas: Record<string, number>;
}

export interface KdePoint {
  x: number;
  baseline_density: number;
  candidate_density: number;
}

export interface BoxPlotStats {
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
}

export interface QualityGateRule {
  rule_id: string;
  name: string;
  metric: string;
  operator: string;
  threshold: number;
  severity: 'BLOCKER' | 'WARNING';
  enabled: boolean;
  description: string;
}

export interface GateBreach {
  rule_id: string;
  name: string;
  metric: string;
  observed_value: number;
  threshold: number;
  severity: 'BLOCKER' | 'WARNING';
  message: string;
}

export interface GateEvaluationReport {
  passed: boolean;
  verdict: 'PASS' | 'FAIL' | 'WARN';
  evaluated_at: string;
  total_rules: number;
  passed_rules: number;
  breaches: GateBreach[];
}

export interface RegressionComparison {
  baseline_run_id: string;
  candidate_run_id: string;
  baseline_label: string;
  candidate_label: string;
  sample_size: number;
  metrics: Record<string, MetricRegression>;
  case_diffs: CaseDiff[];
  kde_points: Record<string, KdePoint[]>;
  box_plots: Record<string, Record<string, BoxPlotStats>>;
  gate_report: GateEvaluationReport | null;
  overall_verdict: 'PASS' | 'FAIL' | 'WARN';
}

export interface AssertionCheckResult {
  metric: string;
  threshold: number;
  observed_score: number;
  passed: boolean;
}

export interface InteractiveLabResponse {
  model: string;
  completion: string;
  latency_ms: number;
  tokens_used: number;
  metrics: Record<string, number>;
  assertion_results: AssertionCheckResult[];
  overall_passed: boolean;
  diff_tokens: DiffToken[];
}
