from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from src.evalgate.main import app

client = TestClient(app)


def test_lab_interactive_run_with_live_ollama() -> None:
    payload = {
        "prompt": "Answer in one sentence: What is the primary purpose of unit testing in software development?",
        "context": "Unit testing verifies that individual components of software work as expected in isolation.",
        "reference_output": "Unit testing verifies that individual components work as expected.",
        "model": "qwen2.5:0.5b",
        "assertions": {
            "faithfulness": 0.50,
            "answer_relevance": 0.50,
        },
    }

    res = client.post("/api/v1/lab/run", json=payload)
    # If Ollama is available, it returns 200 with real completion and metrics
    if res.status_code == 200:
        data = res.json()
        assert data["model"] == "qwen2.5:0.5b"
        assert len(data["completion"]) > 0
        assert data["latency_ms"] > 0
        assert "faithfulness" in data["metrics"]
        assert len(data["assertion_results"]) >= 2
    else:
        # If upstream is unreachable in CI environment, RFC 7807 503 is returned
        assert res.status_code == 503
        data = res.json()
        assert "detail" in data
