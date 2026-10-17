# System Architecture & Technical Design

## 1. Overview
**EvalGate** provides automated LLM regression testing and statistical quality gate enforcement for enterprise CI/CD workflows. It executes prompt suites across model versions, measures qualitative and factual metrics (faithfulness, answer relevance, hallucination rate, semantic similarity), runs two-sample Welch's t-tests and non-parametric Mann-Whitney U hypothesis tests, and issues deterministic CI pass/fail status codes.

---

## 2. C4 Container Diagram

```mermaid
flowchart TD
    subgraph CI_Pipeline ["Continuous Integration / Developer Workflow"]
        GH["GitHub Actions / GitLab CI"]
        Dev["AI Engineer / Prompt Developer"]
    end

    subgraph EvalGate_Platform ["EvalGate Architecture"]
        Frontend["Frontend SPA (React 19 + Tailwind v4)\nPort 3002"]
        APIServer["EvalGate FastAPI Service\nPort 8002"]

        subgraph Core_Services ["Domain & Service Layer"]
            Runner["Test Runner Service\n(Orchestration & Tracing)"]
            Evaluator["Evaluator Engine\n(Faithfulness, Relevance, Hallucination)"]
            Stats["Stats Engine\n(Welch's t-test, Cohen's d, KDE)"]
            Gate["Quality Gate Engine\n(Blocker & Warning Rules)"]
            Diff["Myers Word Diff Engine"]
            Store[("In-Memory & Persistent State\nTest Suites & Run History")]
        end
    end

    subgraph Hardware_Inference ["Inference Targets"]
        OllamaGPU["Local NVIDIA Dedicated NVIDIA GPU\nOllama: qwen2.5:0.5b / llama3.2"]
        CloudLLM["Cloud OpenAI / Anthropic Endpoints\n(Optional Failover)"]
    end

    GH -->|POST /runs/execute & /gates/evaluate| APIServer
    Dev -->|Interactive Dashboard| Frontend
    Frontend -->|REST API Requests| APIServer
    APIServer --> Runner
    APIServer --> Stats
    APIServer --> Gate
    APIServer --> Diff

    Runner --> OllamaGPU
    Runner --> CloudLLM
    Runner --> Evaluator
    Evaluator --> Stats
    Stats --> Gate
    Gate --> Store
```

---

## 3. CI/CD Quality Gate Pipeline Sequence

```mermaid
sequenceDiagram
    autonumber
    actor CI as CI Runner (GitHub Action)
    participant API as EvalGate API
    participant Runner as Test Runner
    participant GPU as Local Ollama GPU (Dedicated NVIDIA GPU)
    participant Eval as Evaluator Engine
    participant Stats as Stats Engine
    participant Gate as Quality Gate Engine

    CI->>API: POST /runs/execute (suite_id, candidate_model)
    API->>Runner: execute_test_suite(suite, model)
    loop For each test case
        Runner->>GPU: POST /chat/completions (prompt, max_tokens)
        GPU-->>Runner: 200 OK (completion, latency_ms)
        Runner->>Eval: evaluate_response(prompt, completion, context, reference)
        Eval-->>Runner: metrics (faithfulness, relevance, hallucination)
    end
    Runner-->>API: EvaluationRun (Candidate Results)

    CI->>API: GET /regression/compare?baseline_id=...&candidate_id=...
    API->>Stats: compute_welch_t_test(baseline, candidate)
    Stats->>Stats: compute_cohens_d & bootstrap_ci
    Stats-->>API: MetricRegression (p-values, deltas)

    API->>Gate: evaluate_quality_gates(metrics, rules)
    alt Any Blocker Breach Detected
        Gate-->>API: GateReport (verdict=FAIL, exit_code=1)
        API-->>CI: 200 OK (verdict=FAIL) -> CI Job Breaks
    else No Blocker Breaches
        Gate-->>API: GateReport (verdict=PASS, exit_code=0)
        API-->>CI: 200 OK (verdict=PASS) -> CI Job Merges
    end
```

---

## 4. Quality Gate State Machine

```mermaid
stateDiagram-v2
    [*] --> EvaluationComplete: Suite Runs Evaluated
    EvaluationComplete --> StatisticalTesting: Compute Welch's t-test & Mann-Whitney U
    StatisticalTesting --> RuleCheck: Compare observed deltas to configured thresholds

    state RuleCheck {
        [*] --> CheckBlockers
        CheckBlockers --> BlockerBreached: Any BLOCKER breached
        CheckBlockers --> CheckWarnings: No BLOCKER breached
        CheckWarnings --> WarningBreached: WARNING breached
        CheckWarnings --> CleanPass: No WARNING breached
    }

    BlockerBreached --> FAIL: CI Exit Code 1
    WarningBreached --> WARN: CI Exit Code 0 with alerts
    CleanPass --> PASS: CI Exit Code 0 Clean Merge

    FAIL --> [*]
    WARN --> [*]
    PASS --> [*]
```
