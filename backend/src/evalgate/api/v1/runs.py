from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.evalgate.domain.entities import EvaluationRun
from src.evalgate.services.store import store
from src.evalgate.services.test_runner import UpstreamProviderError, execute_test_suite

router = APIRouter(prefix="/runs", tags=["runs"])


class ExecuteRunRequest(BaseModel):
    suite_id: str
    label: str
    model: str = "qwen2.5:0.5b"


@router.get("", response_model=list[EvaluationRun])
async def list_runs() -> list[EvaluationRun]:
    """List all completed and recorded evaluation runs."""
    return list(store.runs.values())


@router.get("/{run_id}", response_model=EvaluationRun)
async def get_run(run_id: str) -> EvaluationRun:
    """Retrieve full results and metrics for a specific evaluation run."""
    run = store.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@router.post("/execute", response_model=EvaluationRun)
async def execute_run(req: ExecuteRunRequest) -> EvaluationRun:
    """Execute a test suite against the target LLM inference engine."""
    suite = store.suites.get(req.suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail=f"Suite {req.suite_id} not found")

    try:
        run = await execute_test_suite(suite, label=req.label, model=req.model)
        store.runs[run.id] = run
        return run
    except UpstreamProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "type": "https://evalgate.dev/errors/upstream-unavailable",
                "title": "LLM Inference Engine Unavailable",
                "status": 503,
                "detail": str(exc),
            },
        )
