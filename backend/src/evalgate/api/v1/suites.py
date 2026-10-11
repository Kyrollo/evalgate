from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.evalgate.domain.entities import TestCase, TestSuite
from src.evalgate.services.store import store

router = APIRouter(prefix="/suites", tags=["suites"])


class CreateSuiteRequest(BaseModel):
    name: str
    description: str
    default_model: str = "qwen2.5:0.5b"


class CreateCaseRequest(BaseModel):
    name: str
    prompt: str
    context: str | None = None
    expected_output: str | None = None
    tags: list[str] = []


@router.get("", response_model=list[TestSuite])
async def list_suites() -> list[TestSuite]:
    """Retrieve all configured benchmark test suites."""
    return list(store.suites.values())


@router.get("/{suite_id}", response_model=TestSuite)
async def get_suite(suite_id: str) -> TestSuite:
    """Retrieve a specific test suite with all test cases."""
    if suite_id not in store.suites:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id} not found")
    return store.suites[suite_id]


@router.post("", response_model=TestSuite)
async def create_suite(req: CreateSuiteRequest) -> TestSuite:
    """Create a new evaluation test suite."""
    suite_id = f"suite_{uuid.uuid4().hex[:8]}"
    new_suite = TestSuite(
        id=suite_id,
        name=req.name,
        description=req.description,
        default_model=req.default_model,
        test_cases=[],
    )
    store.suites[suite_id] = new_suite
    return new_suite


@router.post("/{suite_id}/cases", response_model=TestCase)
async def add_test_case(suite_id: str, req: CreateCaseRequest) -> TestCase:
    """Append a new test case into an existing test suite."""
    if suite_id not in store.suites:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id} not found")

    case_id = f"TC-{len(store.suites[suite_id].test_cases) + 1:03d}"
    case = TestCase(
        id=case_id,
        suite_id=suite_id,
        name=req.name,
        prompt=req.prompt,
        context=req.context,
        expected_output=req.expected_output,
        tags=req.tags,
    )
    store.suites[suite_id].test_cases.append(case)
    return case


@router.delete("/{suite_id}/cases/{case_id}")
async def delete_test_case(suite_id: str, case_id: str) -> dict[str, str]:
    """Remove a test case from a suite."""
    if suite_id not in store.suites:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id} not found")

    suite = store.suites[suite_id]
    suite.test_cases = [c for c in suite.test_cases if c.id != case_id]
    return {"status": "deleted", "case_id": case_id}
