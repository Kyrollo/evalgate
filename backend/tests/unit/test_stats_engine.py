from __future__ import annotations

import pytest
from src.evalgate.services.stats_engine import (
    calculate_summary_stats,
    compute_bootstrap_ci,
    compute_box_plot_stats,
    compute_cohens_d,
    compute_kde_points,
    compute_mann_whitney_u,
    compute_welch_t_test,
)


def test_calculate_summary_stats() -> None:
    vals = [0.8, 0.85, 0.9, 0.95, 1.0]
    stats = calculate_summary_stats(vals)
    assert stats["mean"] == pytest.approx(0.9, abs=0.01)
    assert stats["min"] == 0.8
    assert stats["max"] == 1.0
    assert stats["median"] == 0.9


def test_welch_t_test_significant_difference() -> None:
    # Baseline with lower scores, Candidate with clearly higher scores
    baseline = [0.70, 0.72, 0.71, 0.69, 0.73, 0.70, 0.71]
    candidate = [0.92, 0.94, 0.91, 0.95, 0.93, 0.94, 0.92]

    t_stat, p_val = compute_welch_t_test(baseline, candidate)
    assert t_stat > 10.0
    assert p_val < 0.001


def test_welch_t_test_no_difference() -> None:
    group1 = [0.85, 0.86, 0.84, 0.85, 0.87]
    group2 = [0.85, 0.84, 0.86, 0.85, 0.85]

    t_stat, p_val = compute_welch_t_test(group1, group2)
    assert abs(t_stat) < 1.0
    assert p_val > 0.05


def test_mann_whitney_u() -> None:
    baseline = [1.0, 2.0, 3.0, 4.0, 5.0]
    candidate = [6.0, 7.0, 8.0, 9.0, 10.0]

    u_stat, p_val = compute_mann_whitney_u(baseline, candidate)
    assert u_stat == 25.0
    assert p_val < 0.05


def test_cohens_d_large_effect() -> None:
    baseline = [0.5, 0.52, 0.49, 0.51]
    candidate = [0.9, 0.92, 0.89, 0.91]

    d = compute_cohens_d(baseline, candidate)
    assert d > 5.0  # Huge effect size


def test_bootstrap_ci() -> None:
    baseline = [0.80, 0.82, 0.81]
    candidate = [0.90, 0.92, 0.91]

    ci_low, ci_high = compute_bootstrap_ci(baseline, candidate, confidence=0.95, n_resamples=500)
    assert ci_low > 0.05
    assert ci_high > ci_low


def test_box_plot_stats() -> None:
    vals = [10.0, 20.0, 30.0, 40.0, 50.0]
    bp = compute_box_plot_stats(vals)
    assert bp.min == 10.0
    assert bp.median == 30.0
    assert bp.max == 50.0
    assert bp.q1 == 20.0
    assert bp.q3 == 40.0


def test_kde_points() -> None:
    b = [0.81, 0.84, 0.83, 0.82, 0.85]
    c = [0.89, 0.91, 0.90, 0.92, 0.88]

    points = compute_kde_points(b, c, points=30)
    assert len(points) == 30
    assert all(p.baseline_density >= 0 for p in points)
    assert all(p.candidate_density >= 0 for p in points)
