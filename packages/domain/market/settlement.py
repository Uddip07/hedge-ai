"""
SettlementCycle Domain Model for the Indian AI Hedge Fund Platform.

Calculates settlement dates (e.g. Indian market T+1 equity settlement) taking into
account weekends and official exchange holidays. Pure domain model with zero infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from packages.domain.enums.market import SettlementStatus, SettlementType
from packages.domain.value_objects.temporal.timestamps import TradingDate


@dataclass(frozen=True, slots=True)
class SettlementCycle:
    """
    Immutable value object for trade settlement cycle tracking and calculation.

    Attributes:
        settlement_type (SettlementType): Settlement protocol (e.g. T_PLUS_1).
        trade_date (TradingDate): Date when the trade executed.
        status (SettlementStatus): Settlement lifecycle status (PENDING, SETTLED, etc.).
    """

    settlement_type: SettlementType
    trade_date: TradingDate
    status: SettlementStatus = SettlementStatus.PENDING

    def __post_init__(self) -> None:
        if not isinstance(self.settlement_type, SettlementType):
            object.__setattr__(self, "settlement_type", SettlementType(self.settlement_type))
        if not isinstance(self.trade_date, TradingDate):
            object.__setattr__(self, "trade_date", TradingDate(self.trade_date))
        if not isinstance(self.status, SettlementStatus):
            object.__setattr__(self, "status", SettlementStatus(self.status))

    def calculate_settlement_date(self, holidays: list[date] | None = None) -> TradingDate:
        """
        Calculate expected settlement TradingDate by advancing N business days (skipping weekends and holidays).
        """
        holiday_dates = set(holidays) if holidays else set()
        needed_days = self.settlement_type.settlement_days()

        current = self.trade_date.value
        added = 0

        while added < needed_days:
            current += timedelta(days=1)
            # Skip Saturday (5) and Sunday (6)
            if current.weekday() in (5, 6):
                continue
            # Skip official exchange holidays
            if current in holiday_dates:
                continue
            added += 1

        return TradingDate(value=current)

    def to_dict(self) -> dict[str, Any]:
        """Serialize SettlementCycle to dictionary."""
        return {
            "settlement_type": self.settlement_type.value,
            "trade_date": self.trade_date.to_dict(),
            "status": self.status.value,
            "expected_settlement_date": self.calculate_settlement_date().to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SettlementCycle":
        """Deserialize dictionary to SettlementCycle."""
        return cls(
            settlement_type=SettlementType(data["settlement_type"]),
            trade_date=TradingDate.from_dict(data["trade_date"]),
            status=SettlementStatus(data.get("status", "PENDING")),
        )
