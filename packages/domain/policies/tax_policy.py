"""
TaxPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates Indian Income Tax Act capital gains taxation (STCG 20%, LTCG 12.5% for holding > 365 days)
and Securities Transaction Tax (STT). Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.enums.portfolio import TaxType
from packages.domain.enums.trading import TradeType
from packages.domain.utils.math import round_currency
from packages.domain.value_objects.core.money import Money


@dataclass(frozen=True, slots=True)
class TaxPolicy:
    """
    Immutable domain policy enforcing Indian market capital gains taxation rules.

    Attributes:
        stcg_rate_pct (Decimal): Short-Term Capital Gains tax rate (default 20% under Finance Act 2024).
        ltcg_rate_pct (Decimal): Long-Term Capital Gains tax rate (default 12.5% under Finance Act 2024).
        stt_equity_delivery_sell_pct (Decimal): STT rate on delivery equity sell trade (default 0.1%).
        equity_ltcg_threshold_days (int): Minimum holding period days for equity LTCG classification (default 365 days).
    """

    stcg_rate_pct: Decimal = Decimal("20.0")
    ltcg_rate_pct: Decimal = Decimal("12.5")
    stt_equity_delivery_sell_pct: Decimal = Decimal("0.1")
    equity_ltcg_threshold_days: int = 365

    def calculate_trade_stt(self, trade_type: TradeType, gross_amount: Money) -> Money:
        """
        Calculate Securities Transaction Tax (STT).
        In India equity delivery, STT (0.1%) applies primarily on sell trades.
        """
        if trade_type.is_buy():
            return Money(Decimal("0.00"), currency=gross_amount.currency)

        stt_amt = gross_amount.amount * (self.stt_equity_delivery_sell_pct / Decimal("100"))
        return Money(round_currency(stt_amt), currency=gross_amount.currency)

    def calculate_capital_gains_tax(
        self,
        realized_profit: Money,
        holding_period_days: int,
    ) -> dict[TaxType, Money]:
        """
        Calculate STCG or LTCG tax liability on realized capital gains.

        Returns:
            Dict[TaxType, Money]: Tax type mapping to tax liability amount.
        """
        if realized_profit.is_zero() or realized_profit.is_negative():
            zero = Money(Decimal("0.00"), currency=realized_profit.currency)
            return {TaxType.STCG: zero, TaxType.LTCG: zero}

        if holding_period_days > self.equity_ltcg_threshold_days:
            tax_amt = realized_profit.amount * (self.ltcg_rate_pct / Decimal("100"))
            return {
                TaxType.STCG: Money(Decimal("0.00"), currency=realized_profit.currency),
                TaxType.LTCG: Money(round_currency(tax_amt), currency=realized_profit.currency),
            }
        else:
            tax_amt = realized_profit.amount * (self.stcg_rate_pct / Decimal("100"))
            return {
                TaxType.STCG: Money(round_currency(tax_amt), currency=realized_profit.currency),
                TaxType.LTCG: Money(Decimal("0.00"), currency=realized_profit.currency),
            }
