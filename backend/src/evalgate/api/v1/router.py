from __future__ import annotations

from fastapi import APIRouter
from src.evalgate.api.v1.auth import router as auth_router
from src.evalgate.api.v1.gates import router as gates_router
from src.evalgate.api.v1.health import router as health_router
from src.evalgate.api.v1.lab import router as lab_router
from src.evalgate.api.v1.regression import router as regression_router
from src.evalgate.api.v1.runs import router as runs_router
from src.evalgate.api.v1.suites import router as suites_router
from src.evalgate.api.v1.files import router as files_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(suites_router)
api_v1_router.include_router(runs_router)
api_v1_router.include_router(regression_router)
api_v1_router.include_router(gates_router)
api_v1_router.include_router(lab_router)
api_v1_router.include_router(files_router)


@api_v1_router.get("/info", tags=["info"])
async def get_system_info() -> dict[str, str]:
    return {
        "name": "EvalGate",
        "slug": "evalgate",
        "archetype": "CI test report",
        "version": "1.0.0",
        "description": "LLM Regression Testing & Quality Gates: statistical significance testing, automated evaluations, and CI quality gates",
    }
