# EvalGate REST API Reference

EvalGate exposes an OpenAPI v3 compliant REST API on port `8002`.

---

## 1. Regression Comparison & Statistical Testing

### `GET /api/v1/regression/compare`
Computes two-sample Welch's t-test, Mann-Whitney U, Cohen's d effect size, 95% Bootstrap Confidence Intervals, Kernel Density Estimation points, and word-level diffs between two evaluation runs.

#### Request
```bash
curl -X GET "http://localhost:8002/api/v1/regression/compare?baseline_id=run_dialogue_baseline_v1&candidate_id=run_dialogue_candidate_v11"
```

#### Response (200 OK)
```json
{
  "baseline_run_id": "run_dialogue_baseline_v1",
  "candidate_run_id": "run_dialogue_candidate_v11",
  "baseline_label": "Baseline v1.0 (Direct Local)",
  "candidate_label": "Candidate v1.1 (GPU Prompt Grounded)",
  "sample_size": 8,
  "metrics": {
    "correctness": {
      "metric_name": "correctness",
      "baseline_mean": 0.8712,
      "candidate_mean": 0.9175,
      "delta": 0.0463,
      "relative_change_pct": 5.31,
      "t_statistic": 4.1205,
      "p_value": 0.0031,
      "is_significant": true,
      "cohens_d": 1.8427,
      "mann_whitney_u": 62.0,
      "ci_95_low": 0.0214,
      "ci_95_high": 0.0718,
      "status": "IMPROVEMENT"
    }
  },
  "overall_verdict": "PASS"
}
```

---

## 2. Interactive Assertion Lab

### `POST /api/v1/lab/run`
Executes a single test case prompt against the local RTX A5000 GPU Ollama model and evaluates custom quality assertions in real time.

#### Request
```bash
curl -X POST "http://localhost:8002/api/v1/lab/run" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the return window for defective hardware under warranty?",
    "context": "Hardware devices carry a 30-day return policy. Defective units reported within 90 days are eligible for replacement.",
    "reference_output": "Defective units reported within 90 days are eligible for replacement.",
    "model": "qwen2.5:0.5b",
    "assertions": {
      "faithfulness": 0.80,
      "answer_relevance": 0.75,
      "hallucination": 0.10
    }
  }'
```

#### Response (200 OK)
```json
{
  "model": "qwen2.5:0.5b",
  "completion": "Defective units reported within 90 days are eligible for replacement.",
  "latency_ms": 218.4,
  "tokens_used": 34,
  "metrics": {
    "correctness": 0.95,
    "faithfulness": 0.98,
    "answer_relevance": 0.92,
    "hallucination": 0.02,
    "semantic_similarity": 0.95
  },
  "assertion_results": [
    {
      "metric": "faithfulness",
      "threshold": 0.80,
      "observed_score": 0.98,
      "passed": true
    }
  ],
  "overall_passed": true
}
```

---

## 3. Python SDK Client Example

```python
import httpx

client = httpx.Client(base_url="http://localhost:8002/api/v1")

# Compare candidate against baseline in CI pipeline
resp = client.get("/regression/compare", params={
    "baseline_id": "run_dialogue_baseline_v1",
    "candidate_id": "run_dialogue_candidate_v11"
})
data = resp.json()

if data["overall_verdict"] == "FAIL":
    print("Quality gate breached! Failing CI build.")
    exit(1)

print(f"CI Quality Gate Passed: Welch's p={data['metrics']['correctness']['p_value']}")
exit(0)
```
