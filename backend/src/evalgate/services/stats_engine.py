from __future__ import annotations

import math
from typing import Any
import numpy as np
import scipy.stats as stats
from src.evalgate.domain.entities import BoxPlotStats, KdePoint


def calculate_summary_stats(values: list[float]) -> dict[str, float]:
    """Calculate descriptive statistics for a distribution."""
    if not values:
        return {"mean": 0.0, "std_dev": 0.0, "median": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}

    arr = np.array(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "std_dev": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "median": float(np.median(arr)),
        "p95": float(np.percentile(arr, 95)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def compute_welch_t_test(baseline: list[float], candidate: list[float]) -> tuple[float, float]:
    """Perform Welch's two-sample t-test (unequal variances assumed)."""
    if len(baseline) < 2 or len(candidate) < 2:
        return 0.0, 1.0

    b_arr = np.array(baseline, dtype=float)
    c_arr = np.array(candidate, dtype=float)

    # Identical values edge case
    if np.all(b_arr == b_arr[0]) and np.all(c_arr == c_arr[0]):
        if b_arr[0] == c_arr[0]:
            return 0.0, 1.0
        return float("inf") if c_arr[0] > b_arr[0] else float("-inf"), 0.0

    res = stats.ttest_ind(c_arr, b_arr, equal_var=False)
    t_stat = float(res.statistic) if not math.isnan(res.statistic) else 0.0
    p_val = float(res.pvalue) if not math.isnan(res.pvalue) else 1.0
    return t_stat, p_val


def compute_mann_whitney_u(baseline: list[float], candidate: list[float]) -> tuple[float, float]:
    """Perform Mann-Whitney U rank-sum test."""
    if len(baseline) < 2 or len(candidate) < 2:
        return 0.0, 1.0

    try:
        res = stats.mannwhitneyu(candidate, baseline, alternative="two-sided")
        u_stat = float(res.statistic) if not math.isnan(res.statistic) else 0.0
        p_val = float(res.pvalue) if not math.isnan(res.pvalue) else 1.0
        return u_stat, p_val
    except ValueError:
        return 0.0, 1.0


def compute_cohens_d(baseline: list[float], candidate: list[float]) -> float:
    """Calculate Cohen's d effect size between candidate and baseline."""
    if len(baseline) < 2 or len(candidate) < 2:
        return 0.0

    b = np.array(baseline, dtype=float)
    c = np.array(candidate, dtype=float)

    n1 = len(b)
    n2 = len(c)
    s1 = np.var(b, ddof=1)
    s2 = np.var(c, ddof=1)

    s_pooled = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if s_pooled == 0.0:
        return 0.0

    return float((np.mean(c) - np.mean(b)) / s_pooled)


def compute_bootstrap_ci(
    baseline: list[float],
    candidate: list[float],
    confidence: float = 0.95,
    n_resamples: int = 1000,
) -> tuple[float, float]:
    """Calculate bootstrap confidence interval for difference in means (candidate - baseline)."""
    if not baseline or not candidate:
        return 0.0, 0.0

    b = np.array(baseline, dtype=float)
    c = np.array(candidate, dtype=float)

    rng = np.random.default_rng(seed=42)
    deltas = []
    for _ in range(n_resamples):
        b_sample = rng.choice(b, size=len(b), replace=True)
        c_sample = rng.choice(c, size=len(c), replace=True)
        deltas.append(np.mean(c_sample) - np.mean(b_sample))

    alpha = (1.0 - confidence) / 2.0
    low_pct = alpha * 100
    high_pct = (1.0 - alpha) * 100

    low = float(np.percentile(deltas, low_pct))
    high = float(np.percentile(deltas, high_pct))
    return low, high


def compute_box_plot_stats(values: list[float]) -> BoxPlotStats:
    """Compute box plot five-number summary."""
    if not values:
        return BoxPlotStats(min=0.0, q1=0.0, median=0.0, q3=0.0, max=0.0)

    arr = np.array(values, dtype=float)
    return BoxPlotStats(
        min=float(np.min(arr)),
        q1=float(np.percentile(arr, 25)),
        median=float(np.median(arr)),
        q3=float(np.percentile(arr, 75)),
        max=float(np.max(arr)),
    )


def compute_kde_points(
    baseline: list[float],
    candidate: list[float],
    points: int = 40,
) -> list[KdePoint]:
    """Compute Kernel Density Estimation curves for visualization."""
    if len(baseline) < 2 or len(candidate) < 2:
        return []

    b = np.array(baseline, dtype=float)
    c = np.array(candidate, dtype=float)

    all_vals = np.concatenate([b, c])
    v_min = float(np.min(all_vals))
    v_max = float(np.max(all_vals))

    margin = (v_max - v_min) * 0.1 if v_max > v_min else 0.1
    x_grid = np.linspace(v_min - margin, v_max + margin, points)

    try:
        kde_b = stats.gaussian_kde(b)
        kde_c = stats.gaussian_kde(c)
        dens_b = kde_b(x_grid)
        dens_c = kde_c(x_grid)
    except Exception:
        # Fallback to empirical histogram density if zero-variance
        hist_b, bin_edges = np.histogram(b, bins=points, range=(x_grid[0], x_grid[-1]), density=True)
        hist_c, _ = np.histogram(c, bins=points, range=(x_grid[0], x_grid[-1]), density=True)
        dens_b = np.interp(x_grid, bin_edges[:-1], hist_b)
        dens_c = np.interp(x_grid, bin_edges[:-1], hist_c)

    return [
        KdePoint(
            x=round(float(x), 4),
            baseline_density=round(float(db), 4),
            candidate_density=round(float(dc), 4),
        )
        for x, db, dc in zip(x_grid, dens_b, dens_c)
    ]
