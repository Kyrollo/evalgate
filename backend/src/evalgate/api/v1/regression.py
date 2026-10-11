from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from src.evalgate.domain.entities import RegressionComparison
from src.evalgate.services.stats_engine import (
    calculate_summary_stats,
    compute_bootstrap_ci,
    compute_cohens_d,
    compute_kde_points,
    compute_mann_whitney_u,
    compute_welch_t_test,
)
from src.evalgate.services.store import store

router = APIRouter(prefix="/regression", tags=["regression"])


class CustomStatsRequest(BaseModel):
    baseline_values: list[float]
    candidate_values: list[float]
    metric_name: str = "custom_metric"


class CustomStatsResponse(BaseModel):
    metric_name: str
    baseline_summary: dict[str, float]
    candidate_summary: dict[str, float]
    delta: float
    relative_change_pct: float
    welch_t_stat: float
    welch_p_val: float
    is_significant: bool
    mann_whitney_u: float
    mann_whitney_p_val: float
    cohens_d: float
    ci_95: list[float]


@router.get("/compare", response_model=RegressionComparison)
async def compare_runs(
    baseline_id: str = Query(..., description="ID of baseline evaluation run"),
    candidate_id: str = Query(..., description="ID of candidate evaluation run"),
) -> RegressionComparison:
    """
    Perform statistical significance testing and regression comparison between two runs.
    Calculates Welch's t-test, Mann-Whitney U, Cohen's d, KDE curves, and word-level diffs.
    """
    try:
        return store.compare_runs(baseline_id, candidate_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/stats", response_model=CustomStatsResponse)
async def compute_custom_stats(req: CustomStatsRequest) -> CustomStatsResponse:
    """Calculate statistical significance metrics on arbitrary numeric observation sets."""
    if len(req.baseline_values) < 2 or len(req.candidate_values) < 2:
        raise HTTPException(status_code=400, detail="Minimum of 2 observations required per distribution")

    b_summary = calculate_summary_stats(req.baseline_values)
    c_summary = calculate_summary_stats(req.candidate_values)

    b_mean = b_summary["mean"]
    c_mean = c_summary["mean"]
    delta = c_mean - b_mean
    rel_change = (delta / b_mean * 100.0) if b_mean != 0 else 0.0

    t_stat, p_val = compute_welch_t_test(req.baseline_values, req.candidate_values)
    u_stat, u_pval = compute_mann_whitney_u(req.baseline_values, req.candidate_values)
    d_val = compute_cohens_d(req.baseline_values, req.candidate_values)
    ci_low, ci_high = compute_bootstrap_ci(req.baseline_values, req.candidate_values)

    return CustomStatsResponse(
        metric_name=req.metric_name,
        baseline_summary=b_summary,
        candidate_summary=c_summary,
        delta=round(delta, 4),
        relative_change_pct=round(rel_change, 2),
        welch_t_stat=round(t_stat, 4),
        welch_p_val=round(p_val, 4),
        is_significant=bool(p_val < 0.05),
        mann_whitney_u=round(u_stat, 2),
        mann_whitney_p_val=round(u_pval, 4),
        cohens_d=round(d_val, 4),
        ci_95=[round(ci_low, 4), round(ci_high, 4)],
    )
