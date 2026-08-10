"""
FastAPI Router for Platform Alerting & Notification Gateway.

Exposes REST endpoints for dispatching, recording, and querying system and trading alerts
originating from n8n orchestration workflows or internal microservices.
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from packages.api.dependencies import verify_automation_key
from packages.infrastructure.database.models import SystemMetadataModel
from packages.infrastructure.database.session import DatabaseManager

router = APIRouter(prefix="/api/v1/alerts", tags=["Platform Alerting"])
db_manager = DatabaseManager()
logger = logging.getLogger("ihf_ai.alerts")


class DispatchAlertRequest(BaseModel):
    """Alert dispatch payload specification."""

    alert_type: str = Field(
        description="Alert category: MARKET_DATA_FAILURE, YAHOO_FAILURE, BROKER_FAILURE, AI_FAILURE, IMPORT_FAILURE, BACKTEST_COMPLETED, COMMITTEE_COMPLETED, ORDER_REJECTION, CRITICAL_SYSTEM_FAILURE"
    )
    severity: str = Field(
        default="ERROR", description="Severity level: CRITICAL, ERROR, WARNING, INFO"
    )
    source: str = Field(
        default="n8n_orchestrator", description="Component or workflow generating alert"
    )
    title: str = Field(description="Short human-readable summary")
    message: str = Field(description="Detailed alert message or error traceback")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary context data")


class AlertResponse(BaseModel):
    alert_id: str
    status: str
    timestamp: str
    recorded: bool


@router.post(
    "/dispatch",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Dispatch & Record System Alert",
    description="Receive and record system alerts from n8n workflows and dispatch to notification channels.",
)
def dispatch_alert(payload: DispatchAlertRequest) -> AlertResponse:
    """
    Ingest, log, and persist platform alerts.
    """
    alert_id = str(uuid.uuid4())
    now_utc = datetime.now(UTC)

    # Log according to severity
    log_msg = f"[{payload.severity.upper()}] [{payload.alert_type}] {payload.title}: {payload.message} (Source: {payload.source})"
    if payload.severity.upper() == "CRITICAL":
        logger.critical(log_msg)
    elif payload.severity.upper() == "ERROR":
        logger.error(log_msg)
    elif payload.severity.upper() == "WARNING":
        logger.warning(log_msg)
    else:
        logger.info(log_msg)

    # Persist alert record into system_metadata
    recorded = False
    try:
        alert_record = {
            "alert_id": alert_id,
            "alert_type": payload.alert_type.upper(),
            "severity": payload.severity.upper(),
            "source": payload.source,
            "title": payload.title,
            "message": payload.message,
            "metadata": payload.metadata,
            "timestamp": now_utc.isoformat(),
        }
        with db_manager.session() as session:
            key_name = f"alert_{now_utc.strftime('%Y%m%d_%H%M%S')}_{alert_id[:8]}"
            entry = SystemMetadataModel(
                id=alert_id,
                key=key_name,
                value=json.dumps(alert_record),
                description=f"Alert: {payload.alert_type}",
                updated_at=now_utc,
            )
            session.add(entry)
        recorded = True
    except Exception as exc:
        logger.error("Failed to persist alert to database: %s", exc)

    return AlertResponse(
        alert_id=alert_id,
        status="DISPATCHED",
        timestamp=now_utc.isoformat(),
        recorded=recorded,
    )


@router.get(
    "/recent",
    status_code=status.HTTP_200_OK,
    summary="Get Recent Platform Alerts",
    description="Retrieve list of recent system and automation alert records.",
)
def list_recent_alerts(limit: int = Query(default=20, le=100)) -> list[dict[str, Any]]:
    """Retrieve recent alerts recorded in system metadata."""
    with db_manager.session() as session:
        stmt = (
            select(SystemMetadataModel)
            .where(SystemMetadataModel.key.like("alert_%"))
            .order_by(SystemMetadataModel.updated_at.desc())
            .limit(limit)
        )
        rows = list(session.scalars(stmt).all())
        alerts: list[dict[str, Any]] = []
        for r in rows:
            try:
                alerts.append(json.loads(r.value))
            except Exception:
                continue
        return alerts
