"""
System & Infrastructure Enums for the Indian AI Hedge Fund Domain.

Defines broker integration types (Dhan, Shoonya, Zerodha, etc.), notification priorities,
and supported fiat currency codes.
"""

from enum import StrEnum


class BrokerType(StrEnum):
    """
    Brokerage service connectors supported by the execution gateway.
    Primary focus is Indian stock market brokers.
    """

    DHAN = "DHAN"
    SHOONYA = "SHOONYA"
    ZERODHA = "ZERODHA"
    ANGEL_ONE = "ANGEL_ONE"
    ICICI_DIRECT = "ICICI_DIRECT"
    INTERACTIVE_BROKERS = "INTERACTIVE_BROKERS"
    SIMULATED = "SIMULATED"

    def is_indian_broker(self) -> bool:
        """Return True if the broker operates in Indian stock markets (NSE/BSE)."""
        return self in {
            BrokerType.DHAN,
            BrokerType.SHOONYA,
            BrokerType.ZERODHA,
            BrokerType.ANGEL_ONE,
            BrokerType.ICICI_DIRECT,
        }

    def supports_direct_api(self) -> bool:
        """Return True if the broker exposes REST/WebSocket trading APIs."""
        return self in {
            BrokerType.DHAN,
            BrokerType.SHOONYA,
            BrokerType.ZERODHA,
            BrokerType.ANGEL_ONE,
            BrokerType.INTERACTIVE_BROKERS,
            BrokerType.SIMULATED,
        }


class NotificationPriority(StrEnum):
    """
    System notification and alert priority levels.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def is_urgent(self) -> bool:
        """Return True if the notification requires immediate trader or agent attention."""
        return self in {NotificationPriority.HIGH, NotificationPriority.CRITICAL}


class CurrencyCode(StrEnum):
    """
    ISO-4217 Currency Codes supported by monetary calculations.
    """

    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AED = "AED"
    SGD = "SGD"

    def symbol(self) -> str:
        """Return the standard currency display symbol."""
        symbols = {
            CurrencyCode.INR: "₹",
            CurrencyCode.USD: "$",
            CurrencyCode.EUR: "€",
            CurrencyCode.GBP: "£",
            CurrencyCode.JPY: "¥",
            CurrencyCode.AED: "AED ",
            CurrencyCode.SGD: "S$",
        }
        return symbols[self]

    def is_inr(self) -> bool:
        """Return True if currency is Indian Rupee."""
        return self == CurrencyCode.INR


class UserRole(StrEnum):
    """
    User authorization roles for platform access control.
    """

    USER = "USER"
    ADMIN = "ADMIN"

    def is_admin(self) -> bool:
        """Return True if user has administrative privileges."""
        return self == UserRole.ADMIN
