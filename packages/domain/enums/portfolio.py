"""
Portfolio & Corporate Action Enums for the Indian AI Hedge Fund Domain.

Defines portfolio runtime environments, rebalancing allocation methods,
corporate action categories, and Indian tax classifications (STT, LTCG, STCG, Stamp Duty).
"""

from enum import StrEnum


class PortfolioType(StrEnum):
    """
    Portfolio execution environment mode.
    """

    LIVE = "LIVE"
    PAPER = "PAPER"
    BACKTEST = "BACKTEST"
    BENCHMARK = "BENCHMARK"
    SHADOW = "SHADOW"

    def is_real_money(self) -> bool:
        """Return True if the portfolio connects to live capital."""
        return self == PortfolioType.LIVE

    def is_simulation(self) -> bool:
        """Return True if the portfolio operates in a simulated backtest or paper environment."""
        return self in {PortfolioType.PAPER, PortfolioType.BACKTEST, PortfolioType.SHADOW}


class AllocationMethod(StrEnum):
    """
    Portfolio position weighting and asset allocation algorithms.
    """

    EQUAL_WEIGHT = "EQUAL_WEIGHT"
    CAP_WEIGHT = "CAP_WEIGHT"
    RISK_PARITY = "RISK_PARITY"
    MIN_VARIANCE = "MIN_VARIANCE"
    FACTOR_WEIGHT = "FACTOR_WEIGHT"
    CUSTOM = "CUSTOM"

    def is_risk_based(self) -> bool:
        """Return True if allocation depends on asset volatility or risk contribution."""
        return self in {AllocationMethod.RISK_PARITY, AllocationMethod.MIN_VARIANCE}


class CorporateActionType(StrEnum):
    """
    Corporate action event types affecting equity shares and cash balances.
    """

    DIVIDEND = "DIVIDEND"
    BONUS_ISSUE = "BONUS_ISSUE"
    STOCK_SPLIT = "STOCK_SPLIT"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    BUYBACK = "BUYBACK"
    MERGER = "MERGER"
    DEMERGER = "DEMERGER"

    def affects_share_quantity(self) -> bool:
        """Return True if this corporate action changes total holding share quantity."""
        return self in {
            CorporateActionType.BONUS_ISSUE,
            CorporateActionType.STOCK_SPLIT,
            CorporateActionType.RIGHTS_ISSUE,
            CorporateActionType.BUYBACK,
            CorporateActionType.MERGER,
            CorporateActionType.DEMERGER,
        }

    def generates_cash(self) -> bool:
        """Return True if the action results in direct cash credit (e.g. Dividend)."""
        return self in {CorporateActionType.DIVIDEND, CorporateActionType.BUYBACK}


class TaxType(StrEnum):
    """
    Indian financial tax classifications for trade equity transactions and gains.
    """

    STT = "STT"  # Securities Transaction Tax
    LTCG = "LTCG"  # Long Term Capital Gains (12.5% in India)
    STCG = "STCG"  # Short Term Capital Gains (20% in India)
    STAMP_DUTY = "STAMP_DUTY"
    GST = "GST"
    TDS = "TDS"

    def is_transaction_tax(self) -> bool:
        """Return True if tax is levied per transaction at execution time."""
        return self in {TaxType.STT, TaxType.STAMP_DUTY, TaxType.GST}

    def is_capital_gains(self) -> bool:
        """Return True if tax is levied on realized profit at filing time."""
        return self in {TaxType.LTCG, TaxType.STCG}
