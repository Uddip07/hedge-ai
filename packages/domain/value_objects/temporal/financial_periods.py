"""
Financial Period Value Objects for the Indian AI Hedge Fund Domain.

Provides FiscalYear and ReportingPeriod (Annual / Quarterly) value objects tailored
for Indian financial reporting cycles (April 1 to March 31).
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

from packages.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class FiscalYear:
    """
    Immutable value object for Indian Fiscal Years (e.g. FY2025-26 starting April 1, 2025).

    Attributes:
        start_year (int): Calendar year when the fiscal year starts (e.g., 2025).
    """

    start_year: int

    def __post_init__(self) -> None:
        if self.start_year < 1900 or self.start_year > 2100:
            raise ValidationError(
                f"FiscalYear start_year out of valid range: {self.start_year}.",
                context={"start_year": str(self.start_year)},
            )

    @property
    def end_year(self) -> int:
        """Return calendar year when the fiscal year ends."""
        return self.start_year + 1

    @property
    def label(self) -> str:
        """Return standard Indian fiscal year label (e.g., 'FY2025-26')."""
        short_end = str(self.end_year)[-2:]
        return f"FY{self.start_year}-{short_end}"

    @property
    def start_date(self) -> date:
        """Return fiscal year start date (April 1)."""
        return date(self.start_year, 4, 1)

    @property
    def end_date(self) -> date:
        """Return fiscal year end date (March 31)."""
        return date(self.end_year, 3, 31)

    def to_dict(self) -> dict[str, Any]:
        """Serialize FiscalYear to dictionary."""
        return {
            "start_year": self.start_year,
            "end_year": self.end_year,
            "label": self.label,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FiscalYear":
        """Deserialize dictionary to FiscalYear."""
        return cls(start_year=int(data["start_year"]))

    def __str__(self) -> str:
        return self.label


@dataclass(frozen=True, slots=True)
class ReportingPeriod:
    """
    Immutable value object for financial reporting periods (Annual or Quarterly Q1..Q4).

    Attributes:
        fiscal_year (FiscalYear): Parent fiscal year.
        quarter (Optional[int]): Quarter 1, 2, 3, 4 or None for Annual reports.
    """

    fiscal_year: FiscalYear
    quarter: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.fiscal_year, FiscalYear):
            object.__setattr__(self, "fiscal_year", FiscalYear(int(self.fiscal_year)))
        if self.quarter is not None:
            if not isinstance(self.quarter, int) or self.quarter not in (1, 2, 3, 4):
                raise ValidationError(
                    f"ReportingPeriod quarter must be 1, 2, 3, 4 or None (Annual). Got {self.quarter}.",
                    context={"quarter": str(self.quarter)},
                )

    def is_annual(self) -> bool:
        """Return True if this represents an Annual financial report period."""
        return self.quarter is None

    def is_quarterly(self) -> bool:
        """Return True if this represents a Quarterly financial report period."""
        return self.quarter is not None

    @property
    def label(self) -> str:
        """Return human-readable period label (e.g. 'Q1 FY2025-26' or 'FY2025-26 Annual')."""
        if self.is_quarterly():
            return f"Q{self.quarter} {self.fiscal_year.label}"
        return f"{self.fiscal_year.label} Annual"

    def to_dict(self) -> dict[str, Any]:
        """Serialize ReportingPeriod to dictionary."""
        return {
            "fiscal_year": self.fiscal_year.to_dict(),
            "quarter": self.quarter,
            "label": self.label,
            "is_annual": self.is_annual(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportingPeriod":
        """Deserialize dictionary to ReportingPeriod."""
        fy = (
            FiscalYear.from_dict(data["fiscal_year"])
            if isinstance(data["fiscal_year"], dict)
            else FiscalYear(int(data["fiscal_year"]))
        )
        quarter = data.get("quarter")
        return cls(fiscal_year=fy, quarter=int(quarter) if quarter is not None else None)

    def __str__(self) -> str:
        return self.label
