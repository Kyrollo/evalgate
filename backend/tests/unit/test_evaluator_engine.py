from __future__ import annotations

import pytest
from src.evalgate.services.evaluator_engine import (
    calculate_answer_relevance,
    calculate_exact_match,
    calculate_faithfulness,
    calculate_hallucination_rate,
    calculate_token_similarity,
    evaluate_response,
)


def test_exact_match() -> None:
    assert calculate_exact_match("Result A", "Result A") == 1.0
    assert calculate_exact_match("Result A", "Result B") == 0.0
    assert calculate_exact_match("   Clean   ", "clean") == 1.0


def test_token_similarity() -> None:
    sim_high = calculate_token_similarity(
        "Return window is 30 days for devices.",
        "The return window is 30 days for hardware devices.",
    )
    assert sim_high > 0.7

    sim_zero = calculate_token_similarity("Apple banana", "Vehicle engine")
    assert sim_zero < 0.2


def test_faithfulness_and_hallucination() -> None:
    context = "The API key rate limit is 100 requests per minute. Accounts are locked after 5 failed login attempts."

    # Faithful output grounded in context
    faithful_output = "The rate limit is 100 requests per minute and accounts lock after 5 failed attempts."
    f_score = calculate_faithfulness(faithful_output, context)
    assert f_score > 0.8
    h_score = calculate_hallucination_rate(faithful_output, context)
    assert h_score < 0.2

    # Hallucinatory output containing facts not in context
    unfaithful_output = "Subscribers receive unlimited quantum compute credits and free satellite internet."
    f_unfaithful = calculate_faithfulness(unfaithful_output, context)
    assert f_unfaithful < 0.5


def test_answer_relevance() -> None:
    prompt = "What is the timeout duration for database connections?"
    relevant_output = "The connection timeout duration is configured to 30 seconds."
    rel_score = calculate_answer_relevance(relevant_output, prompt)
    assert rel_score >= 0.7


def test_evaluate_response_all_metrics() -> None:
    prompt = "What is the warranty policy?"
    output = "Hardware carries a 90 day warranty for defective parts."
    context = "All hardware devices carry a 90 day warranty for defective components."
    ref = "Hardware carries a 90 day warranty for defective parts."

    res = evaluate_response(prompt, output, context=context, reference=ref)
    assert "correctness" in res
    assert "faithfulness" in res
    assert "answer_relevance" in res
    assert "hallucination" in res
    assert res["exact_match"] == 1.0
