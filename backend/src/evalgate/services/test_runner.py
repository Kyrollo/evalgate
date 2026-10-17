from __future__ import annotations

import time
import uuid
from typing import Any
import httpx
from src.evalgate.core.config import settings
from src.evalgate.domain.entities import EvaluationRun, MetricSummary, RunResult, TestCase, TestSuite
from src.evalgate.services.evaluator_engine import evaluate_response
from src.evalgate.services.stats_engine import calculate_summary_stats


class UpstreamProviderError(Exception):
    """Raised when upstream LLM provider is unreachable or returns failure."""
    pass


async def execute_model_inference(
    prompt: str,
    system_prompt: str | None = None,
    model: str = "qwen2.5:0.5b",
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> tuple[str, float, int]:
    """
    Executes model inference against local GPU Ollama or OpenAI-compatible endpoint.
    Measures real execution latency and returns (completion_text, latency_ms, tokens_used).
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    start_time = time.perf_counter()
    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise UpstreamProviderError(f"Connection failure to upstream LLM at {url}: {exc}") from exc

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if response.status_code != 200:
        raise UpstreamProviderError(
            f"Upstream provider returned status {response.status_code}: {response.text}"
        )

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise UpstreamProviderError("Upstream provider returned empty completion choices")

    content = choices[0].get("message", {}).get("content", "").strip()
    usage = data.get("usage", {})
    tokens = usage.get("total_tokens", len(content.split()) + len(prompt.split()))

    return content, latency_ms, tokens


async def run_single_test_case(
    test_case: TestCase,
    model: str = "qwen2.5:0.5b",
    run_id: str = "",
) -> RunResult:
    """Execute a single test case and evaluate all quality metrics."""
    result_id = f"res_{uuid.uuid4().hex[:10]}"
    try:
        completion, latency_ms, tokens = await execute_model_inference(
            prompt=test_case.prompt,
            model=model,
        )
        metrics = evaluate_response(
            prompt=test_case.prompt,
            output=completion,
            context=test_case.context,
            reference=test_case.expected_output,
        )
        metrics["latency_ms"] = latency_ms
        metrics["token_cost"] = round(tokens * 0.000002, 6)

        return RunResult(
            id=result_id,
            run_id=run_id,
            case_id=test_case.id,
            case_name=test_case.name,
            prompt=test_case.prompt,
            model_output=completion,
            reference_output=test_case.expected_output,
            metrics=metrics,
            latency_ms=latency_ms,
            tokens_used=tokens,
            passed=True,
            error_message=None,
        )
    except UpstreamProviderError as exc:
        return RunResult(
            id=result_id,
            run_id=run_id,
            case_id=test_case.id,
            case_name=test_case.name,
            prompt=test_case.prompt,
            model_output="",
            reference_output=test_case.expected_output,
            metrics={},
            latency_ms=0.0,
            tokens_used=0,
            passed=False,
            error_message=str(exc),
        )


async def execute_test_suite(
    suite: TestSuite,
    label: str,
    model: str = "qwen2.5:0.5b",
) -> EvaluationRun:
    """Execute all test cases in a test suite sequentially against target model."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    results: list[RunResult] = []

    for case in suite.test_cases:
        res = await run_single_test_case(case, model=model, run_id=run_id)
        results.append(res)

    # Compute summary metrics across successful cases
    successful_cases = [r for r in results if r.passed]
    metric_keys = ["correctness", "faithfulness", "answer_relevance", "hallucination", "semantic_similarity", "latency_ms"]
    summary_metrics: dict[str, MetricSummary] = {}

    for key in metric_keys:
        vals = [r.metrics[key] for r in successful_cases if key in r.metrics]
        if vals:
            raw_summary = calculate_summary_stats(vals)
            summary_metrics[key] = MetricSummary(**raw_summary)

    return EvaluationRun(
        id=run_id,
        suite_id=suite.id,
        label=label,
        model=model,
        status="COMPLETED" if successful_cases else "FAILED",
        results=results,
        summary_metrics=summary_metrics,
    )
