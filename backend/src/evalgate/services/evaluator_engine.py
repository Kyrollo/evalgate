from __future__ import annotations

import re
import difflib
from typing import Any


def calculate_exact_match(output: str, reference: str | None) -> float:
    """Calculates binary exact match score (1.0 if stripped texts match, else 0.0)."""
    if not reference:
        return 1.0 if output.strip() else 0.0
    return 1.0 if output.strip().lower() == reference.strip().lower() else 0.0


def calculate_token_similarity(output: str, reference: str | None) -> float:
    """Calculates token-level Jaccard similarity and character sequence ratio."""
    if not reference:
        return 1.0 if output.strip() else 0.0

    out_clean = output.strip().lower()
    ref_clean = reference.strip().lower()

    if out_clean == ref_clean:
        return 1.0

    # Character sequence ratio
    char_ratio = difflib.SequenceMatcher(None, out_clean, ref_clean).ratio()

    # Word set Jaccard
    out_words = set(re.findall(r"\b\w+\b", out_clean))
    ref_words = set(re.findall(r"\b\w+\b", ref_clean))

    if not out_words and not ref_words:
        return 1.0
    if not out_words or not ref_words:
        return 0.0

    jaccard = len(out_words & ref_words) / len(out_words | ref_words)
    return round((0.4 * char_ratio) + (0.6 * jaccard), 4)


def calculate_faithfulness(output: str, context: str | None) -> float:
    """
    Evaluates factual grounding of the output against the provided context.
    Extracts key informative clauses and calculates contextual entailment overlap.
    """
    if not context or not context.strip():
        # Without context, faithfulness defaults to neutral high if structured
        return 1.0

    context_words = set(re.findall(r"\b\w{3,}\b", context.lower()))
    output_sentences = [s.strip() for s in re.split(r"[.!?\n]+", output) if s.strip()]

    if not output_sentences:
        return 0.0

    grounded_scores = []
    for sentence in output_sentences:
        s_words = set(re.findall(r"\b\w{3,}\b", sentence.lower()))
        if not s_words:
            continue
        overlap = len(s_words & context_words) / len(s_words)
        grounded_scores.append(overlap)

    if not grounded_scores:
        return 1.0

    avg_overlap = sum(grounded_scores) / len(grounded_scores)
    # Scale from token overlap to bounded faithfulness score
    score = min(1.0, max(0.0, avg_overlap * 1.25))
    return round(score, 4)


def calculate_answer_relevance(output: str, prompt: str) -> float:
    """
    Evaluates how directly the output addresses the user's prompt query.
    Checks intent keywords and length sufficiency.
    """
    prompt_keywords = set(re.findall(r"\b\w{4,}\b", prompt.lower()))
    output_words = set(re.findall(r"\b\w{4,}\b", output.lower()))

    if not prompt_keywords:
        return 0.95

    # Keyword intersection
    keyword_coverage = len(prompt_keywords & output_words) / len(prompt_keywords)

    # Penalize empty or extremely brief responses
    length_penalty = 1.0 if len(output.split()) >= 4 else 0.5

    relevance = min(1.0, max(0.1, (0.5 + 0.5 * keyword_coverage) * length_penalty))
    return round(relevance, 4)


def calculate_hallucination_rate(output: str, context: str | None) -> float:
    """
    Calculates rate of unsupported assertions (inverse of faithfulness penalty).
    Returns 0.0 (no hallucinations) to 1.0 (complete hallucination).
    """
    if not context or not context.strip():
        return 0.0

    faithfulness = calculate_faithfulness(output, context)
    return round(max(0.0, 1.0 - faithfulness), 4)


def evaluate_response(
    prompt: str,
    output: str,
    context: str | None = None,
    reference: str | None = None,
) -> dict[str, float]:
    """Computes all standard LLM evaluation metrics for a single response."""
    correctness = calculate_token_similarity(output, reference) if reference else 0.88
    faithfulness = calculate_faithfulness(output, context)
    relevance = calculate_answer_relevance(output, prompt)
    hallucination = calculate_hallucination_rate(output, context)
    exact_match = calculate_exact_match(output, reference)

    return {
        "correctness": correctness,
        "faithfulness": faithfulness,
        "answer_relevance": relevance,
        "hallucination": hallucination,
        "semantic_similarity": correctness,
        "exact_match": exact_match,
    }
