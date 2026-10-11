from __future__ import annotations

from typing import Sequence
from src.evalgate.domain.entities import (
    GateBreach,
    GateEvaluationReport,
    GateSeverity,
    GateVerdict,
    MetricRegression,
    QualityGateRule,
)


def get_default_gate_rules() -> list[QualityGateRule]:
    """Default CI quality gate criteria."""
    return [
        QualityGateRule(
            rule_id="RULE-CORR-01",
            name="Minimum Correctness Score",
            metric="correctness",
            operator=">=",
            threshold=0.80,
            severity=GateSeverity.BLOCKER,
            description="Candidate correctness mean must exceed 80%",
        ),
        QualityGateRule(
            rule_id="RULE-FAITH-01",
            name="Minimum Faithfulness",
            metric="faithfulness",
            operator=">=",
            threshold=0.85,
            severity=GateSeverity.BLOCKER,
            description="Candidate faithfulness mean must exceed 85%",
        ),
        QualityGateRule(
            rule_id="RULE-HALL-01",
            name="Max Hallucination Delta",
            metric="hallucination",
            operator="delta_max",
            threshold=0.03,
            severity=GateSeverity.BLOCKER,
            description="Hallucination increase must not exceed +0.03 delta",
        ),
        QualityGateRule(
            rule_id="RULE-STAT-01",
            name="Statistically Significant Regression",
            metric="correctness",
            operator="sig_regression_max",
            threshold=-0.03,
            severity=GateSeverity.BLOCKER,
            description="Regression greater than 3% with p < 0.05 blocks CI merge",
        ),
        QualityGateRule(
            rule_id="RULE-LAT-01",
            name="Latency Degradation Alert",
            metric="latency_ms",
            operator="delta_max",
            threshold=250.0,
            severity=GateSeverity.WARNING,
            description="Latency increase over 250ms generates CI warning",
        ),
    ]


def evaluate_quality_gates(
    metrics: dict[str, MetricRegression],
    rules: Sequence[QualityGateRule],
) -> GateEvaluationReport:
    """Evaluate quality gate criteria against regression analysis metrics."""
    breaches: list[GateBreach] = []
    total_evaluated = 0

    for rule in rules:
        if not rule.enabled:
            continue

        metric_stat = metrics.get(rule.metric)
        if not metric_stat:
            continue

        total_evaluated += 1
        observed_val = metric_stat.candidate_mean
        is_breached = False
        message = ""

        if rule.operator == ">=":
            if observed_val < rule.threshold:
                is_breached = True
                message = f"{rule.metric} ({observed_val:.3f}) fell below minimum required threshold {rule.threshold:.3f}"
        elif rule.operator == "<=":
            if observed_val > rule.threshold:
                is_breached = True
                message = f"{rule.metric} ({observed_val:.3f}) exceeded maximum allowed threshold {rule.threshold:.3f}"
        elif rule.operator == "delta_max":
            if metric_stat.delta > rule.threshold:
                is_breached = True
                message = f"{rule.metric} delta (+{metric_stat.delta:.3f}) exceeded allowed increase {rule.threshold:.3f}"
        elif rule.operator == "sig_regression_max":
            # Breached if statistically significant (p < 0.05) and delta is worse than threshold
            if metric_stat.is_significant and metric_stat.delta < rule.threshold:
                is_breached = True
                message = (
                    f"Statistically significant regression in {rule.metric}: delta {metric_stat.delta:.3f} "
                    f"with p={metric_stat.p_value:.4f} (threshold: {rule.threshold:.3f})"
                )

        if is_breached:
            breaches.append(
                GateBreach(
                    rule_id=rule.rule_id,
                    name=rule.name,
                    metric=rule.metric,
                    observed_value=observed_val,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    message=message,
                )
            )

    has_blockers = any(b.severity == GateSeverity.BLOCKER for b in breaches)
    has_warnings = any(b.severity == GateSeverity.WARNING for b in breaches)

    if has_blockers:
        verdict = GateVerdict.FAIL
    elif has_warnings:
        verdict = GateVerdict.WARN
    else:
        verdict = GateVerdict.PASS

    return GateEvaluationReport(
        passed=(verdict != GateVerdict.FAIL),
        verdict=verdict,
        total_rules=total_evaluated,
        passed_rules=total_evaluated - len(breaches),
        breaches=breaches,
    )
