"""
Zerodha Alert Management Service.

Manages custom trading alerts, trigger monitoring, and notification rules.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from packages.infrastructure.brokers.zerodha.client import ZerodhaClient

logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.alerts")


@dataclass
class AlertRule:
    """Trading alert rule specification."""

    alert_id: str
    ticker_symbol: str
    condition_type: str  # e.g., 'GREATER_THAN', 'LESS_THAN', 'MARGIN_THRESHOLD'
    target_value: float
    message: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ZerodhaAlertService:
    """
    Alert management service integrated with Zerodha account and trading events.
    """

    def __init__(self, client: ZerodhaClient) -> None:
        self.client = client
        self._alerts: dict[str, AlertRule] = {}
        self._listeners: list[Callable[[AlertRule, float], None]] = []

    def create_alert(
        self,
        alert_id: str,
        ticker_symbol: str,
        condition_type: str,
        target_value: float,
        message: str,
    ) -> AlertRule:
        """Create a new alert rule."""
        rule = AlertRule(
            alert_id=alert_id,
            ticker_symbol=ticker_symbol,
            condition_type=condition_type,
            target_value=float(target_value),
            message=message,
        )
        self._alerts[alert_id] = rule
        logger.info("Created alert rule: %s for %s", alert_id, ticker_symbol)
        return rule

    def cancel_alert(self, alert_id: str) -> bool:
        """Cancel an alert rule."""
        if alert_id in self._alerts:
            self._alerts[alert_id].is_active = False
            logger.info("Cancelled alert rule: %s", alert_id)
            return True
        return False

    def list_alerts(self, active_only: bool = True) -> list[AlertRule]:
        """List stored alert rules."""
        if active_only:
            return [rule for rule in self._alerts.values() if rule.is_active]
        return list(self._alerts.values())

    def register_listener(self, listener: Callable[[AlertRule, float], None]) -> None:
        """Register a callback listener for alert triggers."""
        self._listeners.append(listener)

    def evaluate_price_trigger(self, ticker_symbol: str, current_price: float) -> list[AlertRule]:
        """
        Evaluate price against registered alerts and dispatch trigger notifications.
        Note: Current price evaluation comes from Yahoo Finance market data, NOT Zerodha.
        """
        triggered: list[AlertRule] = []
        for rule in self._alerts.values():
            if not rule.is_active or rule.ticker_symbol.upper() != ticker_symbol.upper():
                continue

            cond = rule.condition_type.upper()
            is_triggered = False
            if cond in ("GREATER_THAN", "ABOVE") and current_price >= rule.target_value:
                is_triggered = True
            elif cond in ("LESS_THAN", "BELOW") and current_price <= rule.target_value:
                is_triggered = True

            if is_triggered:
                logger.info(
                    "Alert triggered: %s for %s at price %s",
                    rule.alert_id,
                    ticker_symbol,
                    current_price,
                )
                rule.is_active = False
                triggered.append(rule)
                for listener in self._listeners:
                    try:
                        listener(rule, current_price)
                    except Exception as exc:
                        logger.error("Error in alert listener callback: %s", str(exc))

        return triggered
