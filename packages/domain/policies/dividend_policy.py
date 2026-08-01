"""
DividendPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates corporate dividend processing rules (ex-dividend entitlement check
and Indian Income Tax TDS withholding calculation on dividend income). Pure domain policy.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from packages.domain.portfolio.holding import Holding
from packages.domain.utils.math import round_currency
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price


@dataclass(frozen=True, slots=True)
class DividendPolicy:
    """
    Immutable domain policy for corporate dividend entitlement and tax withholding (TDS).

    Attributes:
        tds_withholding_rate_pct (Decimal): Indian Income Tax Section 194 TDS rate on dividend payout (default 10%).
    """

    tds_withholding_rate_pct: Decimal = Decimal("10.0")

    def calculate_net_dividend(
        self,
        holding: Holding,
        dividend_per_share: Price,
        record_date: date,
        holding_as_of_date: date,
    ) -> tuple[Money, Money, Money]:
        """
        Calculate gross dividend, Indian TDS tax withholding, and net receivable cash dividend.

        Returns:
            Tuple[Money, Money, Money]: (gross_dividend, tds_withheld, net_dividend)
        """
        if holding_as_of_date > record_date:
            zero_cash = Money(Decimal("0.00"), currency=dividend_per_share.money.currency)
            return zero_cash, zero_cash, zero_cash

        gross_amt = dividend_per_share.amount * holding.quantity.value
        gross_div = Money(round_currency(gross_amt), currency=dividend_per_share.money.currency)

        tds_amt = gross_div.amount * (self.tds_withholding_rate_pct / Decimal("100"))
        tds_withheld = Money(round_currency(tds_amt), currency=dividend_per_share.money.currency)

        net_div = gross_div - tds_withheld
        return gross_div, tds_withheld, net_div
