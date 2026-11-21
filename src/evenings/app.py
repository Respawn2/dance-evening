"""Application factory."""

import structlog
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from evenings.api import registrations, system
from evenings.api.middleware import request_context
from evenings.config import Settings, get_settings
from evenings.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application.

    Settings are an argument rather than a global so that tests can
    build the application with a configuration of their own.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.environment)

    app = FastAPI(
        title="Evenings API",
        version=settings.app_version,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=request_context)
    app.include_router(system.router)
    app.include_router(registrations.router)

    app.dependency_overrides.setdefault(get_settings, lambda: settings)

    structlog.get_logger().info(
        "service_started",
        version=settings.app_version,
        environment=settings.environment,
        port=settings.port,
    )
    return app
