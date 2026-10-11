from __future__ import annotations

import pytest
from src.evalgate.domain.entities import (
    ComparisonStatus,
    GateSeverity,
    GateVerdict,
    MetricRegression,
    QualityGateRule,
)
from src.evalgate.services.diff_engine import compute_word_diff
from src.evalgate.services.gate_engine import evaluate_quality_gates, get_default_gate_rules


def test_word_diff_identical() -> None:
    diff = compute_word_diff("The model answered correctly.", "The model answered correctly.")
    assert len(diff) == 1
    assert diff[0].type == "unchanged"


def test_word_diff_modifications() -> None:
    base = "The latency was 250 milliseconds."
    cand = "The latency was 180 milliseconds today."

    diff = compute_word_diff(base, cand)
    types = [d.type for d in diff]
    assert "removed" in types
    assert "added" in types


def test_quality_gate_all_passed() -> None:
    metrics = {
        "correctness": MetricRegression(
            metric_name="correctness",
            baseline_mean=0.85,
            candidate_mean=0.92,
            delta=0.07,
            relative_change_pct=8.2,
            t_statistic=3.4,
            p_value=0.005,
            is_significant=True,
            cohens_d=1.5,
            mann_whitney_u=25.0,
            ci_95_low=0.03,
            ci_95_high=0.11,
            status=ComparisonStatus.IMPROVEMENT,
        ),
        "faithfulness": MetricRegression(
            metric_name="faithfulness",
            baseline_mean=0.90,
            candidate_mean=0.95,
            delta=0.05,
            relative_change_pct=5.5,
            t_statistic=2.8,
            p_value=0.01,
            is_significant=True,
            cohens_d=1.2,
            mann_whitney_u=24.0,
            ci_95_low=0.02,
            ci_95_high=0.08,
            status=ComparisonStatus.IMPROVEMENT,
        ),
        "hallucination": MetricRegression(
            metric_name="hallucination",
            baseline_mean=0.08,
            candidate_mean=0.04,
            delta=-0.04,
            relative_change_pct=-50.0,
            t_statistic=-2.5,
            p_value=0.02,
            is_significant=True,
            cohens_d=-1.1,
            mann_whitney_u=10.0,
            ci_95_low=-0.06,
            ci_95_high=-0.02,
            status=ComparisonStatus.IMPROVEMENT,
        ),
        "latency_ms": MetricRegression(
            metric_name="latency_ms",
            baseline_mean=240.0,
            candidate_mean=210.0,
            delta=-30.0,
            relative_change_pct=-12.5,
            t_statistic=-1.8,
            p_value=0.08,
            is_significant=False,
            cohens_d=-0.8,
            mann_whitney_u=15.0,
            ci_95_low=-60.0,
            ci_95_high=5.0,
            status=ComparisonStatus.NEGLIGIBLE,
        ),
    }

    rules = get_default_gate_rules()
    report = evaluate_quality_gates(metrics, rules)
    assert report.passed is True
    assert report.verdict == GateVerdict.PASS
    assert len(report.breaches) == 0


def test_quality_gate_blocker_breach() -> None:
    # Low candidate correctness below 0.80 threshold
    metrics = {
        "correctness": MetricRegression(
            metric_name="correctness",
            baseline_mean=0.85,
            candidate_mean=0.68,
            delta=-0.17,
            relative_change_pct=-20.0,
            t_statistic=-4.5,
            p_value=0.001,
            is_significant=True,
            cohens_d=-2.1,
            mann_whitney_u=5.0,
            ci_95_low=-0.22,
            ci_95_high=-0.12,
            status=ComparisonStatus.REGRESSION,
        ),
    }

    rules = [
        QualityGateRule(
            rule_id="RULE-CORR-01",
            name="Minimum Correctness Score",
            metric="correctness",
            operator=">=",
            threshold=0.80,
            severity=GateSeverity.BLOCKER,
        )
    ]

    report = evaluate_quality_gates(metrics, rules)
    assert report.passed is False
    assert report.verdict == GateVerdict.FAIL
    assert len(report.breaches) == 1
    assert report.breaches[0].severity == GateSeverity.BLOCKER
