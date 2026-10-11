# Data Model & Entity Specifications

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    TestSuite ||--|{ TestCase : contains
    TestSuite ||--|{ EvaluationRun : executes
    EvaluationRun ||--|{ RunResult : records
    TestCase ||--|{ RunResult : targets

    EvaluationRun ||--o{ RegressionComparison : "baseline for"
    EvaluationRun ||--o{ RegressionComparison : "candidate for"
    RegressionComparison ||--|{ MetricRegression : calculates
    RegressionComparison ||--|{ CaseDiff : compares
    RegressionComparison ||--o| GateEvaluationReport : evaluates
    QualityGateRule ||--o{ GateBreach : triggers
    GateEvaluationReport ||--|{ GateBreach : contains

    TestSuite {
        string id PK
        string name
        string description
        string default_model
        timestamp created_at
    }

    TestCase {
        string id PK
        string suite_id FK
        string name
        string prompt
        string context
        string expected_output
        string_array tags
    }

    EvaluationRun {
        string id PK
        string suite_id FK
        string label
        string model
        string status
        timestamp created_at
    }

    RunResult {
        string id PK
        string run_id FK
        string case_id FK
        string model_output
        float latency_ms
        int tokens_used
        json metrics
    }

    RegressionComparison {
        string baseline_run_id FK
        string candidate_run_id FK
        int sample_size
        string overall_verdict
    }

    MetricRegression {
        string metric_name
        float baseline_mean
        float candidate_mean
        float delta
        float t_statistic
        float p_value
        float cohens_d
        float mann_whitney_u
        string status
    }

    QualityGateRule {
        string rule_id PK
        string name
        string metric
        string operator
        float threshold
        string severity
        boolean enabled
    }

    GateEvaluationReport {
        boolean passed
        string verdict
        int total_rules
        int passed_rules
    }

    GateBreach {
        string rule_id FK
        string metric
        float observed_value
        float threshold
        string severity
        string message
    }
```

---

## 2. Statistical Metric Definitions

| Metric Field | Type | Description |
| :--- | :--- | :--- |
| `correctness` | float [0, 1] | Hybrid character token sequence alignment and Jaccard token overlap against reference ground truth. |
| `faithfulness` | float [0, 1] | Propositional grounding verification measuring factual agreement with context document. |
| `answer_relevance`| float [0, 1] | Semantic keyword intent overlap and length sufficiency answering prompt query. |
| `hallucination` | float [0, 1] | Inverse factual grounding rate ($1.0 - \text{faithfulness}$) detecting ungrounded claims. |
| `p_value` | float [0, 1] | Two-tailed Welch's $t$-test probability value under null hypothesis of identical distributions. |
| `cohens_d` | float | Standardized mean difference effect size measuring practical significance ($d \ge 0.8$ is large). |
| `mann_whitney_u` | float | Non-parametric rank-sum test statistic invariant to distribution non-normality. |
| `ci_95` | tuple [low, high]| 95% Bootstrap empirical percentile confidence interval for $\mu_{\text{candidate}} - \mu_{\text{baseline}}$. |
