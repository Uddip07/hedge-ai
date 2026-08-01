"""
Notification Port Interface for the Application Layer.

Defines outbound port contracts for broadcasting system notifications,
risk limit breach alerts, and portfolio reports.
"""

from abc import ABC, abstractmethod

from packages.domain.enums.system import NotificationPriority
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId


class NotificationPort(ABC):
    """
    Abstract Outbound Port for Multi-Channel Messaging & Alert Notifications.
    """

    @abstractmethod
    def send_alert(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> bool:
        """
        Send a real-time risk alert or operational notification message.

        Args:
            title (str): Brief summary title of the alert.
            message (str): Full text message body content.
            priority (NotificationPriority): Urgency priority level.

        Returns:
            bool: True if alert dispatch succeeded.
        """

    @abstractmethod
    def send_trade_report(
        self,
        portfolio_id: PortfolioId,
        report_summary: str,
    ) -> bool:
        """
        Dispatch an executive trade summary report for a portfolio.

        Args:
            portfolio_id (PortfolioId): Target portfolio identifier.
            report_summary (str): Formatted trade report text/HTML.

        Returns:
            bool: True if report delivery succeeded.
        """
