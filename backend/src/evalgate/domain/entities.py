from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class MetricType(str, Enum):
    CORRECTNESS = "correctness"
    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    HALLUCINATION = "hallucination"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    LATENCY_MS = "latency_ms"
    TOKEN_COST = "token_cost"


class GateVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


class GateSeverity(str, Enum):
    BLOCKER = "BLOCKER"
    WARNING = "WARNING"


class ComparisonStatus(str, Enum):
    IMPROVEMENT = "IMPROVEMENT"
    REGRESSION = "REGRESSION"
    NEGLIGIBLE = "NEGLIGIBLE"


class TestCase(BaseModel):
    __test__ = False
    id: str
    suite_id: str
    name: str
    prompt: str
    context: str | None = None
    expected_output: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestSuite(BaseModel):
    __test__ = False
    id: str
    name: str
    description: str
    default_model: str = "qwen2.5:0.5b"
    test_cases: list[TestCase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunResult(BaseModel):
    id: str
    run_id: str
    case_id: str
    case_name: str
    prompt: str
    model_output: str
    reference_output: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0
    tokens_used: int = 0
    passed: bool = True
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricSummary(BaseModel):
    mean: float
    std_dev: float
    median: float
    p95: float
    min: float
    max: float


class EvaluationRun(BaseModel):
    id: str
    suite_id: str
    label: str
    model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "COMPLETED"
    results: list[RunResult] = Field(default_factory=list)
    summary_metrics: dict[str, MetricSummary] = Field(default_factory=dict)


class MetricRegression(BaseModel):
    metric_name: str
    baseline_mean: float
    candidate_mean: float
    delta: float
    relative_change_pct: float
    t_statistic: float
    p_value: float
    is_significant: bool
    cohens_d: float
    mann_whitney_u: float
    ci_95_low: float
    ci_95_high: float
    status: ComparisonStatus


class DiffToken(BaseModel):
    type: str  # "added", "removed", "unchanged"
    text: str


class CaseDiff(BaseModel):
    case_id: str
    case_name: str
    prompt: str
    baseline_output: str
    candidate_output: str
    diff_tokens: list[DiffToken] = Field(default_factory=list)
    score_deltas: dict[str, float] = Field(default_factory=dict)


class KdePoint(BaseModel):
    x: float
    baseline_density: float
    candidate_density: float


class BoxPlotStats(BaseModel):
    min: float
    q1: float
    median: float
    q3: float
    max: float


class QualityGateRule(BaseModel):
    rule_id: str
    name: str
    metric: str
    operator: str  # ">=", "<=", "delta_max", "delta_min", "p_value_min"
    threshold: float
    severity: GateSeverity = GateSeverity.BLOCKER
    enabled: bool = True
    description: str = ""


class GateBreach(BaseModel):
    rule_id: str
    name: str
    metric: str
    observed_value: float
    threshold: float
    severity: GateSeverity
    message: str


class GateEvaluationReport(BaseModel):
    passed: bool
    verdict: GateVerdict
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_rules: int
    passed_rules: int
    breaches: list[GateBreach] = Field(default_factory=list)


class RegressionComparison(BaseModel):
    baseline_run_id: str
    candidate_run_id: str
    baseline_label: str
    candidate_label: str
    sample_size: int
    metrics: dict[str, MetricRegression] = Field(default_factory=dict)
    case_diffs: list[CaseDiff] = Field(default_factory=list)
    kde_points: dict[str, list[KdePoint]] = Field(default_factory=dict)
    box_plots: dict[str, dict[str, BoxPlotStats]] = Field(default_factory=dict)
    gate_report: GateEvaluationReport | None = None
    overall_verdict: GateVerdict = GateVerdict.PASS
