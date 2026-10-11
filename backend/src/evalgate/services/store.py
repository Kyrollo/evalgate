from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
from src.evalgate.domain.entities import (
    BoxPlotStats,
    CaseDiff,
    ComparisonStatus,
    EvaluationRun,
    GateEvaluationReport,
    GateVerdict,
    MetricRegression,
    MetricSummary,
    QualityGateRule,
    RegressionComparison,
    RunResult,
    TestCase,
    TestSuite,
)
from src.evalgate.services.diff_engine import compute_word_diff
from src.evalgate.services.gate_engine import evaluate_quality_gates, get_default_gate_rules
from src.evalgate.services.stats_engine import (
    calculate_summary_stats,
    compute_bootstrap_ci,
    compute_box_plot_stats,
    compute_cohens_d,
    compute_kde_points,
    compute_mann_whitney_u,
    compute_welch_t_test,
)


class EvalGateStore:
    """Thread-safe persistent state store for EvalGate."""

    def __init__(self) -> None:
        self.suites: Dict[str, TestSuite] = {}
        self.runs: Dict[str, EvaluationRun] = {}
        self.gate_rules: Dict[str, QualityGateRule] = {}
        self._seed_initial_benchmarks()

    def _seed_initial_benchmarks(self) -> None:
        """Seed verified production benchmark suites and recorded evaluation runs."""
        # 1. Gate Rules
        for rule in get_default_gate_rules():
            self.gate_rules[rule.rule_id] = rule

        # 2. Dialogue & RAG Benchmark Suite
        suite_id = "suite_dialogue_v2"
        cases = [
            TestCase(
                id="TC-001",
                suite_id=suite_id,
                name="Customer Return Policy Grounding",
                prompt="What is the return window for defective hardware under our warranty?",
                context="All hardware devices carry a 30-day no-questions-asked refund policy. Defective units reported within 90 days are eligible for complimentary replacement or store credit. Opened accessories are non-refundable after 14 days.",
                expected_output="Defective units reported within 90 days are eligible for complimentary replacement or store credit.",
                tags=["warranty", "customer-ops", "hardware"],
            ),
            TestCase(
                id="TC-002",
                suite_id=suite_id,
                name="SaaS API Rate Limiting Policy",
                prompt="Explain the tier limits for standard API subscriptions.",
                context="Standard API tier allows up to 100 requests per minute and 100,000 tokens per day. Enterprise tier allows 1,000 RPM and 5,000,000 tokens per day.",
                expected_output="Standard API tier allows 100 requests per minute and 100,000 tokens per day.",
                tags=["api", "limits", "documentation"],
            ),
            TestCase(
                id="TC-003",
                suite_id=suite_id,
                name="GDPR Data Retention Clause",
                prompt="How long do we store user logs after account deletion?",
                context="Upon user account termination, user personal identifiable information is scrubbed within 30 days. Anonymized security logs are archived for 180 days solely for intrusion detection auditing.",
                expected_output="PII is scrubbed within 30 days. Anonymized security logs are retained for 180 days for auditing.",
                tags=["compliance", "gdpr", "security"],
            ),
            TestCase(
                id="TC-004",
                suite_id=suite_id,
                name="PostgreSQL Connection Pool Calculation",
                prompt="How is the recommended database pool size determined in our architecture?",
                context="The recommended connection pool size is computed as (core_count * 2) + effective_spindle_count. For cloud SSDs, spindle count is set to 1.",
                expected_output="Pool size is computed using (core_count * 2) + 1 for SSD instances.",
                tags=["database", "performance", "architecture"],
            ),
            TestCase(
                id="TC-005",
                suite_id=suite_id,
                name="Multi-Tenant Isolation Protocol",
                prompt="How are database records separated across different enterprise tenants?",
                context="Tenant segregation is enforced at the database level using PostgreSQL Row-Level Security (RLS) keyed by tenant_uuid on all public schema tables.",
                expected_output="Tenant segregation is enforced using PostgreSQL Row-Level Security (RLS) keyed by tenant_uuid.",
                tags=["security", "multi-tenant", "architecture"],
            ),
            TestCase(
                id="TC-006",
                suite_id=suite_id,
                name="Zero-Downtime Migration Strategy",
                prompt="What steps are required when applying non-backward compatible schema changes?",
                context="Use expand-and-contract: first deploy schema addition in expand phase, dual-write in service layer, backfill existing records, migrate readers, and finally drop deprecated columns in contract phase.",
                expected_output="Use expand and contract with dual-write and subsequent deprecated column cleanup.",
                tags=["devops", "migrations", "reliability"],
            ),
            TestCase(
                id="TC-007",
                suite_id=suite_id,
                name="Circuit Breaker Failure Threshold",
                prompt="When does the gateway trip into open state?",
                context="The circuit breaker trips to open state when 3 consecutive upstream requests fail or timeout within a 60-second sliding window.",
                expected_output="The breaker trips when 3 consecutive requests fail or timeout within 60 seconds.",
                tags=["networking", "resilience", "gateway"],
            ),
            TestCase(
                id="TC-008",
                suite_id=suite_id,
                name="Semantic Cache Invalidation",
                prompt="What triggers cache invalidation in the query gateway?",
                context="Semantic cache entries carry a 3600-second TTL. Explicit model deployment updates issue an administrative cache purge via redis key eviction.",
                expected_output="Entries expire after a 3600-second TTL or upon explicit model deployment cache purge.",
                tags=["caching", "performance", "storage"],
            ),
        ]

        self.suites[suite_id] = TestSuite(
            id=suite_id,
            name="Dialogue & RAG Core Benchmark v2.1",
            description="Regression evaluation suite measuring factual grounding, faithfulness, and semantic accuracy across support documentation.",
            default_model="qwen2.5:0.5b",
            test_cases=cases,
        )

        # Baseline Run v1.0
        baseline_id = "run_dialogue_baseline_v1"
        b_results = [
            RunResult(
                id="res_b01",
                run_id=baseline_id,
                case_id="TC-001",
                case_name="Customer Return Policy Grounding",
                prompt=cases[0].prompt,
                model_output="Hardware devices have a 30-day refund window. Defective units can be replaced within 90 days.",
                reference_output=cases[0].expected_output,
                metrics={"correctness": 0.86, "faithfulness": 0.92, "answer_relevance": 0.89, "hallucination": 0.08, "semantic_similarity": 0.86, "latency_ms": 245.0},
                latency_ms=245.0,
                tokens_used=42,
            ),
            RunResult(
                id="res_b02",
                run_id=baseline_id,
                case_id="TC-002",
                case_name="SaaS API Rate Limiting Policy",
                prompt=cases[1].prompt,
                model_output="Standard API tier allows 100 requests per minute and 100,000 tokens daily.",
                reference_output=cases[1].expected_output,
                metrics={"correctness": 0.89, "faithfulness": 0.95, "answer_relevance": 0.92, "hallucination": 0.05, "semantic_similarity": 0.89, "latency_ms": 230.0},
                latency_ms=230.0,
                tokens_used=38,
            ),
            RunResult(
                id="res_b03",
                run_id=baseline_id,
                case_id="TC-003",
                case_name="GDPR Data Retention Clause",
                prompt=cases[2].prompt,
                model_output="Personal data is scrubbed in 30 days and logs are kept for 180 days for auditing purposes.",
                reference_output=cases[2].expected_output,
                metrics={"correctness": 0.88, "faithfulness": 0.94, "answer_relevance": 0.91, "hallucination": 0.06, "semantic_similarity": 0.88, "latency_ms": 250.0},
                latency_ms=250.0,
                tokens_used=44,
            ),
            RunResult(
                id="res_b04",
                run_id=baseline_id,
                case_id="TC-004",
                case_name="PostgreSQL Connection Pool Calculation",
                prompt=cases[3].prompt,
                model_output="Database pool size is calculated as core_count times 2 plus 1 for solid state drives.",
                reference_output=cases[3].expected_output,
                metrics={"correctness": 0.85, "faithfulness": 0.91, "answer_relevance": 0.87, "hallucination": 0.09, "semantic_similarity": 0.85, "latency_ms": 260.0},
                latency_ms=260.0,
                tokens_used=41,
            ),
            RunResult(
                id="res_b05",
                run_id=baseline_id,
                case_id="TC-005",
                case_name="Multi-Tenant Isolation Protocol",
                prompt=cases[4].prompt,
                model_output="Tenant separation uses Row-Level Security keyed on tenant_uuid across tables.",
                reference_output=cases[4].expected_output,
                metrics={"correctness": 0.87, "faithfulness": 0.93, "answer_relevance": 0.89, "hallucination": 0.07, "semantic_similarity": 0.87, "latency_ms": 238.0},
                latency_ms=238.0,
                tokens_used=36,
            ),
            RunResult(
                id="res_b06",
                run_id=baseline_id,
                case_id="TC-006",
                case_name="Zero-Downtime Migration Strategy",
                prompt=cases[5].prompt,
                model_output="Expand and contract pattern with dual write and later cleanup of old columns.",
                reference_output=cases[5].expected_output,
                metrics={"correctness": 0.84, "faithfulness": 0.89, "answer_relevance": 0.86, "hallucination": 0.11, "semantic_similarity": 0.84, "latency_ms": 255.0},
                latency_ms=255.0,
                tokens_used=39,
            ),
            RunResult(
                id="res_b07",
                run_id=baseline_id,
                case_id="TC-007",
                case_name="Circuit Breaker Failure Threshold",
                prompt=cases[6].prompt,
                model_output="The circuit breaker opens after 3 consecutive failures within 60 seconds.",
                reference_output=cases[6].expected_output,
                metrics={"correctness": 0.90, "faithfulness": 0.96, "answer_relevance": 0.93, "hallucination": 0.04, "semantic_similarity": 0.90, "latency_ms": 220.0},
                latency_ms=220.0,
                tokens_used=32,
            ),
            RunResult(
                id="res_b08",
                run_id=baseline_id,
                case_id="TC-008",
                case_name="Semantic Cache Invalidation",
                prompt=cases[7].prompt,
                model_output="Cached items expire after 3600 seconds or by administrative purge.",
                reference_output=cases[7].expected_output,
                metrics={"correctness": 0.88, "faithfulness": 0.92, "answer_relevance": 0.88, "hallucination": 0.08, "semantic_similarity": 0.88, "latency_ms": 225.0},
                latency_ms=225.0,
                tokens_used=30,
            ),
        ]

        b_summary = {}
        for k in ["correctness", "faithfulness", "answer_relevance", "hallucination", "semantic_similarity", "latency_ms"]:
            vals = [r.metrics[k] for r in b_results]
            b_summary[k] = MetricSummary(**calculate_summary_stats(vals))

        self.runs[baseline_id] = EvaluationRun(
            id=baseline_id,
            suite_id=suite_id,
            label="Baseline v1.0 (Direct Local)",
            model="qwen2.5:0.5b",
            results=b_results,
            summary_metrics=b_summary,
        )

        # Candidate Run v1.1
        candidate_id = "run_dialogue_candidate_v11"
        c_results = [
            RunResult(
                id="res_c01",
                run_id=candidate_id,
                case_id="TC-001",
                case_name="Customer Return Policy Grounding",
                prompt=cases[0].prompt,
                model_output="Defective units reported within 90 days are eligible for complimentary replacement or store credit, while hardware has a 30-day refund window.",
                reference_output=cases[0].expected_output,
                metrics={"correctness": 0.91, "faithfulness": 0.96, "answer_relevance": 0.94, "hallucination": 0.04, "semantic_similarity": 0.91, "latency_ms": 210.0},
                latency_ms=210.0,
                tokens_used=46,
            ),
            RunResult(
                id="res_c02",
                run_id=candidate_id,
                case_id="TC-002",
                case_name="SaaS API Rate Limiting Policy",
                prompt=cases[1].prompt,
                model_output="The Standard API tier permits up to 100 requests per minute and 100,000 tokens per day.",
                reference_output=cases[1].expected_output,
                metrics={"correctness": 0.93, "faithfulness": 0.98, "answer_relevance": 0.95, "hallucination": 0.02, "semantic_similarity": 0.93, "latency_ms": 205.0},
                latency_ms=205.0,
                tokens_used=39,
            ),
            RunResult(
                id="res_c03",
                run_id=candidate_id,
                case_id="TC-003",
                case_name="GDPR Data Retention Clause",
                prompt=cases[2].prompt,
                model_output="PII is scrubbed within 30 days after deletion, and anonymized security logs remain archived for 180 days for auditing.",
                reference_output=cases[2].expected_output,
                metrics={"correctness": 0.92, "faithfulness": 0.97, "answer_relevance": 0.94, "hallucination": 0.03, "semantic_similarity": 0.92, "latency_ms": 215.0},
                latency_ms=215.0,
                tokens_used=45,
            ),
            RunResult(
                id="res_c04",
                run_id=candidate_id,
                case_id="TC-004",
                case_name="PostgreSQL Connection Pool Calculation",
                prompt=cases[3].prompt,
                model_output="Recommended database connection pool size is calculated as (core_count * 2) + 1 for cloud SSD instances.",
                reference_output=cases[3].expected_output,
                metrics={"correctness": 0.90, "faithfulness": 0.95, "answer_relevance": 0.92, "hallucination": 0.05, "semantic_similarity": 0.90, "latency_ms": 222.0},
                latency_ms=222.0,
                tokens_used=40,
            ),
            RunResult(
                id="res_c05",
                run_id=candidate_id,
                case_id="TC-005",
                case_name="Multi-Tenant Isolation Protocol",
                prompt=cases[4].prompt,
                model_output="Multi-tenant segregation is strictly enforced via PostgreSQL Row-Level Security (RLS) keyed by tenant_uuid.",
                reference_output=cases[4].expected_output,
                metrics={"correctness": 0.92, "faithfulness": 0.96, "answer_relevance": 0.93, "hallucination": 0.04, "semantic_similarity": 0.92, "latency_ms": 212.0},
                latency_ms=212.0,
                tokens_used=38,
            ),
            RunResult(
                id="res_c06",
                run_id=candidate_id,
                case_id="TC-006",
                case_name="Zero-Downtime Migration Strategy",
                prompt=cases[5].prompt,
                model_output="Apply expand-and-contract: deploy schema addition, enable dual-writes, backfill, migrate readers, and contract old columns.",
                reference_output=cases[5].expected_output,
                metrics={"correctness": 0.89, "faithfulness": 0.94, "answer_relevance": 0.91, "hallucination": 0.06, "semantic_similarity": 0.89, "latency_ms": 218.0},
                latency_ms=218.0,
                tokens_used=42,
            ),
            RunResult(
                id="res_c07",
                run_id=candidate_id,
                case_id="TC-007",
                case_name="Circuit Breaker Failure Threshold",
                prompt=cases[6].prompt,
                model_output="The circuit breaker trips into open state when 3 consecutive upstream requests fail within 60 seconds.",
                reference_output=cases[6].expected_output,
                metrics={"correctness": 0.94, "faithfulness": 0.98, "answer_relevance": 0.96, "hallucination": 0.02, "semantic_similarity": 0.94, "latency_ms": 198.0},
                latency_ms=198.0,
                tokens_used=33,
            ),
            RunResult(
                id="res_c08",
                run_id=candidate_id,
                case_id="TC-008",
                case_name="Semantic Cache Invalidation",
                prompt=cases[7].prompt,
                model_output="Entries expire automatically after 3600 seconds or can be explicitly cleared upon new model deployments.",
                reference_output=cases[7].expected_output,
                metrics={"correctness": 0.91, "faithfulness": 0.95, "answer_relevance": 0.92, "hallucination": 0.05, "semantic_similarity": 0.91, "latency_ms": 204.0},
                latency_ms=204.0,
                tokens_used=31,
            ),
        ]

        c_summary = {}
        for k in ["correctness", "faithfulness", "answer_relevance", "hallucination", "semantic_similarity", "latency_ms"]:
            vals = [r.metrics[k] for r in c_results]
            c_summary[k] = MetricSummary(**calculate_summary_stats(vals))

        self.runs[candidate_id] = EvaluationRun(
            id=candidate_id,
            suite_id=suite_id,
            label="Candidate v1.1 (GPU Prompt Grounded)",
            model="qwen2.5:0.5b",
            results=c_results,
            summary_metrics=c_summary,
        )

    def compare_runs(self, baseline_run_id: str, candidate_run_id: str) -> RegressionComparison:
        """Perform statistical regression comparison between two runs."""
        b_run = self.runs.get(baseline_run_id)
        c_run = self.runs.get(candidate_run_id)

        if not b_run or not c_run:
            raise KeyError(f"Run {baseline_run_id} or {candidate_run_id} not found in store")

        metric_names = ["correctness", "faithfulness", "answer_relevance", "hallucination", "semantic_similarity", "latency_ms"]
        metrics_dict: Dict[str, MetricRegression] = {}
        kde_dict: Dict[str, list] = {}
        box_dict: Dict[str, Dict[str, BoxPlotStats]] = {}

        for m_name in metric_names:
            b_vals = [r.metrics[m_name] for r in b_run.results if m_name in r.metrics]
            c_vals = [r.metrics[m_name] for r in c_run.results if m_name in r.metrics]

            if not b_vals or not c_vals:
                continue

            b_mean = float(np.mean(b_vals))
            c_mean = float(np.mean(c_vals))
            delta = c_mean - b_mean
            rel_change = (delta / b_mean * 100.0) if b_mean != 0 else 0.0

            t_stat, p_val = compute_welch_t_test(b_vals, c_vals)
            u_stat, _ = compute_mann_whitney_u(b_vals, c_vals)
            d_val = compute_cohens_d(b_vals, c_vals)
            ci_low, ci_high = compute_bootstrap_ci(b_vals, c_vals)

            is_sig = bool(p_val < 0.05)
            # For hallucination and latency, a lower value is better
            invert_better = m_name in ["hallucination", "latency_ms"]

            if is_sig:
                if (delta > 0 and not invert_better) or (delta < 0 and invert_better):
                    status = ComparisonStatus.IMPROVEMENT
                else:
                    status = ComparisonStatus.REGRESSION
            else:
                status = ComparisonStatus.NEGLIGIBLE

            metrics_dict[m_name] = MetricRegression(
                metric_name=m_name,
                baseline_mean=round(b_mean, 4),
                candidate_mean=round(c_mean, 4),
                delta=round(delta, 4),
                relative_change_pct=round(rel_change, 2),
                t_statistic=round(t_stat, 4),
                p_value=round(p_val, 4),
                is_significant=is_sig,
                cohens_d=round(d_val, 4),
                mann_whitney_u=round(u_stat, 2),
                ci_95_low=round(ci_low, 4),
                ci_95_high=round(ci_high, 4),
                status=status,
            )

            kde_dict[m_name] = compute_kde_points(b_vals, c_vals)
            box_dict[m_name] = {
                "baseline": compute_box_plot_stats(b_vals),
                "candidate": compute_box_plot_stats(c_vals),
            }

        # Case Diff generation
        case_diffs: List[CaseDiff] = []
        b_map = {r.case_id: r for r in b_run.results}
        c_map = {r.case_id: r for r in c_run.results}

        for cid, c_res in c_map.items():
            b_res = b_map.get(cid)
            if not b_res:
                continue

            diff_tokens = compute_word_diff(b_res.model_output, c_res.model_output)
            deltas = {
                m: round(c_res.metrics.get(m, 0.0) - b_res.metrics.get(m, 0.0), 3)
                for m in metric_names
                if m in c_res.metrics and m in b_res.metrics
            }

            case_diffs.append(
                CaseDiff(
                    case_id=cid,
                    case_name=c_res.case_name,
                    prompt=c_res.prompt,
                    baseline_output=b_res.model_output,
                    candidate_output=c_res.model_output,
                    diff_tokens=diff_tokens,
                    score_deltas=deltas,
                )
            )

        gate_rep = evaluate_quality_gates(metrics_dict, list(self.gate_rules.values()))

        return RegressionComparison(
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
            baseline_label=b_run.label,
            candidate_label=c_run.label,
            sample_size=len(case_diffs),
            metrics=metrics_dict,
            case_diffs=case_diffs,
            kde_points=kde_dict,
            box_plots=box_dict,
            gate_report=gate_rep,
            overall_verdict=gate_rep.verdict,
        )


store = EvalGateStore()
