"""
Mock Notification Adapter for Infrastructure Layer.

Logs and captures notifications in-memory for testing.
"""

from packages.application.ports.notification_port import NotificationPort
from packages.domain.enums.system import NotificationPriority
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId


class MockNotificationAdapter(NotificationPort):
    """
    Mock Adapter implementing NotificationPort.
    """

    def __init__(self) -> None:
        self.sent_alerts: list[dict[str, str]] = []
        self.sent_reports: list[dict[str, str]] = []

    def send_alert(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> bool:
        self.sent_alerts.append({"title": title, "message": message, "priority": priority.value})
        return True

    def send_trade_report(
        self,
        portfolio_id: PortfolioId,
        report_summary: str,
    ) -> bool:
        self.sent_reports.append(
            {"portfolio_id": str(portfolio_id.value), "summary": report_summary}
        )
        return True
