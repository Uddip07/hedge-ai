"""
Main FastAPI Application Entrypoint for MONEYYYYYY API.

Configures Title, Version, OpenAPI, Lifespan events, Middlewares, Exception Handlers, and Routers.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from packages.api.config import APIConfig
from packages.api.exception_handlers import (
    application_exception_handler,
    domain_exception_handler,
    domain_validation_exception_handler,
    global_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
)
from packages.api.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    TimingMiddleware,
    UnhandledExceptionMiddleware,
)
from packages.api.routers import (
    alert_router,
    analyze_router,
    auth_router,
    backtest_router,
    broker_router,
    committee_router,
    company_intelligence_router,
    debug_router,
    health_router,
    market_data_router,
    market_router,
    user_router,
    ws_market_router,
)
from packages.application.exceptions import ApplicationException
from packages.domain.exceptions import DomainError, ValidationError
from packages.infrastructure.logging import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan context manager for startup and shutdown events.
    """
    logger = get_logger(name="ihf_ai.api")
    logger.info("Initializing Indian Hedge Fund AI API platform lifecycle...")
    yield
    logger.info("Shutting down Indian Hedge Fund AI API platform lifecycle...")


def create_app(config: APIConfig | None = None) -> FastAPI:
    """
    FastAPI Application Factory.

    Args:
        config (APIConfig | None): API configuration settings.

    Returns:
        FastAPI: Initialized and wired FastAPI application instance.
    """
    cfg = config or APIConfig()

    app = FastAPI(
        title=cfg.title,
        version=cfg.version,
        description=cfg.description,
        docs_url=cfg.docs_url,
        redoc_url=cfg.redoc_url,
        openapi_url=cfg.openapi_url,
        lifespan=lifespan,
    )

    # Add Middlewares (executed in reverse order of addition)
    app.add_middleware(UnhandledExceptionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(ApplicationException, application_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, domain_validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(status.HTTP_404_NOT_FOUND, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(status.HTTP_405_METHOD_NOT_ALLOWED, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, global_exception_handler)

    # Include Routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(broker_router)
    app.include_router(user_router)
    app.include_router(analyze_router)
    app.include_router(market_router)
    app.include_router(market_data_router)
    app.include_router(ws_market_router)
    app.include_router(company_intelligence_router)
    app.include_router(committee_router)
    app.include_router(backtest_router)
    app.include_router(alert_router)
    app.include_router(debug_router)

    return app


app = create_app()
