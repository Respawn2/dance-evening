"""System endpoints: liveness and version."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from evenings.config import Settings, get_settings

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    """Liveness answer. Deliberately free of external dependencies."""

    status: Literal["ok"] = "ok"


class VersionResponse(BaseModel):
    """Version of the running code."""

    version: str = Field(examples=["1.2.3"])
    environment: str = Field(examples=["production"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Report that the process is alive.

    This handler must not touch the database, the cache or any other
    external system: a liveness probe that fails because a dependency
    is down causes the orchestrator to restart healthy processes.
    Readiness, which does consult dependencies, appears in ЛР 7.
    """
    return HealthResponse()


@router.get("/version", response_model=VersionResponse, summary="Running version")
async def version(
    settings: Annotated[Settings, Depends(get_settings)],
) -> VersionResponse:
    """Report the version and the environment of the running code."""
    return VersionResponse(version=settings.app_version, environment=settings.environment)
