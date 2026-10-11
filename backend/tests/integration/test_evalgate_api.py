from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from src.evalgate.main import app

client = TestClient(app)


def test_system_info() -> None:
    res = client.get("/api/v1/info")
    assert res.status_code == 200
    data = res.json()
    assert data["slug"] == "evalgate"


def test_list_suites() -> None:
    res = client.get("/api/v1/suites")
    assert res.status_code == 200
    suites = res.json()
    assert len(suites) >= 1
    assert suites[0]["id"] == "suite_dialogue_v2"


def test_get_suite_detail() -> None:
    res = client.get("/api/v1/suites/suite_dialogue_v2")
    assert res.status_code == 200
    suite = res.json()
    assert len(suite["test_cases"]) == 8


def test_add_test_case() -> None:
    payload = {
        "name": "Integration Test Case",
        "prompt": "Explain database indexes.",
        "context": "Indexes speed up read queries using B-Tree structures.",
        "expected_output": "Indexes speed up read queries using B-Trees.",
        "tags": ["db", "testing"],
    }
    res = client.post("/api/v1/suites/suite_dialogue_v2/cases", json=payload)
    assert res.status_code == 200
    case = res.json()
    assert case["name"] == "Integration Test Case"


def test_list_and_compare_runs() -> None:
    res = client.get("/api/v1/runs")
    assert res.status_code == 200
    runs = res.json()
    assert len(runs) >= 2

    # Compare baseline and candidate runs
    cmp_res = client.get(
        "/api/v1/regression/compare?baseline_id=run_dialogue_baseline_v1&candidate_id=run_dialogue_candidate_v11"
    )
    assert cmp_res.status_code == 200
    comp = cmp_res.json()
    assert comp["sample_size"] == 8
    assert "correctness" in comp["metrics"]
    assert comp["metrics"]["correctness"]["delta"] > 0
    assert len(comp["case_diffs"]) == 8
    assert comp["overall_verdict"] == "PASS"


def test_custom_stats_endpoint() -> None:
    payload = {
        "baseline_values": [0.70, 0.72, 0.71, 0.73, 0.69],
        "candidate_values": [0.90, 0.92, 0.91, 0.94, 0.89],
        "metric_name": "accuracy",
    }
    res = client.post("/api/v1/regression/stats", json=payload)
    assert res.status_code == 200
    stats = res.json()
    assert stats["is_significant"] is True
    assert stats["welch_p_val"] < 0.01
    assert stats["delta"] > 0.15


def test_gates_endpoints() -> None:
    rules_res = client.get("/api/v1/gates/rules")
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert len(rules) >= 4

    eval_res = client.post(
        "/api/v1/gates/evaluate",
        json={
            "baseline_id": "run_dialogue_baseline_v1",
            "candidate_id": "run_dialogue_candidate_v11",
        },
    )
    assert eval_res.status_code == 200
    report = eval_res.json()
    assert report["passed"] is True
