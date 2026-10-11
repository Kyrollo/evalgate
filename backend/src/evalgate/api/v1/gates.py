from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.evalgate.domain.entities import (
    GateEvaluationReport,
    GateSeverity,
    QualityGateRule,
)
from src.evalgate.services.gate_engine import evaluate_quality_gates
from src.evalgate.services.store import store

router = APIRouter(prefix="/gates", tags=["gates"])


class CreateGateRuleRequest(BaseModel):
    name: str
    metric: str
    operator: str
    threshold: float
    severity: GateSeverity = GateSeverity.BLOCKER
    enabled: bool = True
    description: str = ""


class EvaluateGateRequest(BaseModel):
    baseline_id: str
    candidate_id: str


@router.get("/rules", response_model=list[QualityGateRule])
async def list_gate_rules() -> list[QualityGateRule]:
    """List all active and configured quality gate criteria."""
    return list(store.gate_rules.values())


@router.post("/rules", response_model=QualityGateRule)
async def create_gate_rule(req: CreateGateRuleRequest) -> QualityGateRule:
    """Create or register a new CI quality gate rule."""
    rule_id = f"RULE-{uuid.uuid4().hex[:6].upper()}"
    rule = QualityGateRule(
        rule_id=rule_id,
        name=req.name,
        metric=req.metric,
        operator=req.operator,
        threshold=req.threshold,
        severity=req.severity,
        enabled=req.enabled,
        description=req.description,
    )
    store.gate_rules[rule_id] = rule
    return rule


@router.post("/evaluate", response_model=GateEvaluationReport)
async def evaluate_run_gates(req: EvaluateGateRequest) -> GateEvaluationReport:
    """Evaluate quality gate status between baseline and candidate runs."""
    try:
        comparison = store.compare_runs(req.baseline_id, req.candidate_id)
        if comparison.gate_report:
            return comparison.gate_report
        return evaluate_quality_gates(comparison.metrics, list(store.gate_rules.values()))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
