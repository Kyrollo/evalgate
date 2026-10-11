from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.evalgate.domain.entities import DiffToken
from src.evalgate.services.diff_engine import compute_word_diff
from src.evalgate.services.evaluator_engine import evaluate_response
from src.evalgate.services.test_runner import UpstreamProviderError, execute_model_inference

router = APIRouter(prefix="/lab", tags=["lab"])


class InteractiveLabRequest(BaseModel):
    prompt: str
    context: str | None = None
    reference_output: str | None = None
    model: str = "qwen2.5:0.5b"
    assertions: dict[str, float] = {
        "faithfulness": 0.80,
        "answer_relevance": 0.75,
        "hallucination": 0.10,
        "semantic_similarity": 0.80,
    }


class AssertionCheckResult(BaseModel):
    metric: str
    threshold: float
    observed_score: float
    passed: bool


class InteractiveLabResponse(BaseModel):
    model: str
    completion: str
    latency_ms: float
    tokens_used: int
    metrics: dict[str, float]
    assertion_results: list[AssertionCheckResult]
    overall_passed: bool
    diff_tokens: list[DiffToken] = []


@router.post("/run", response_model=InteractiveLabResponse)
async def run_interactive_lab(req: InteractiveLabRequest) -> InteractiveLabResponse:
    """
    Execute live interactive assertion evaluation against target LLM.
    Evaluates faithfulness, relevance, hallucination, similarity, and performs word diff.
    """
    try:
        completion, latency_ms, tokens = await execute_model_inference(
            prompt=req.prompt,
            model=req.model,
        )
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

    metrics = evaluate_response(
        prompt=req.prompt,
        output=completion,
        context=req.context,
        reference=req.reference_output,
    )
    metrics["latency_ms"] = latency_ms

    assertion_checks: list[AssertionCheckResult] = []
    overall_passed = True

    for m_name, threshold in req.assertions.items():
        if m_name in metrics:
            observed = metrics[m_name]
            # For hallucination, lower than threshold is passing
            if m_name == "hallucination":
                passed = bool(observed <= threshold)
            else:
                passed = bool(observed >= threshold)

            if not passed:
                overall_passed = False

            assertion_checks.append(
                AssertionCheckResult(
                    metric=m_name,
                    threshold=threshold,
                    observed_score=observed,
                    passed=passed,
                )
            )

    diff_tokens: list[DiffToken] = []
    if req.reference_output:
        diff_tokens = compute_word_diff(req.reference_output, completion)

    return InteractiveLabResponse(
        model=req.model,
        completion=completion,
        latency_ms=latency_ms,
        tokens_used=tokens,
        metrics=metrics,
        assertion_results=assertion_checks,
        overall_passed=overall_passed,
        diff_tokens=diff_tokens,
    )
