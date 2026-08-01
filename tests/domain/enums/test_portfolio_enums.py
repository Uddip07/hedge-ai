"""
Unit tests for Portfolio Domain Enums.
"""

import unittest

from packages.domain.enums.portfolio import (
    AllocationMethod,
    CorporateActionType,
    PortfolioType,
    TaxType,
)


class TestPortfolioEnums(unittest.TestCase):
    """Test suite for Portfolio Enums."""

    def test_portfolio_type_helpers(self):
        self.assertTrue(PortfolioType.LIVE.is_real_money())
        self.assertTrue(PortfolioType.PAPER.is_simulation())
        self.assertTrue(PortfolioType.BACKTEST.is_simulation())

    def test_allocation_method_helpers(self):
        self.assertTrue(AllocationMethod.RISK_PARITY.is_risk_based())
        self.assertFalse(AllocationMethod.EQUAL_WEIGHT.is_risk_based())

    def test_corporate_action_type_helpers(self):
        self.assertTrue(CorporateActionType.STOCK_SPLIT.affects_share_quantity())
        self.assertTrue(CorporateActionType.DIVIDEND.generates_cash())

    def test_tax_type_helpers(self):
        self.assertTrue(TaxType.STT.is_transaction_tax())
        self.assertTrue(TaxType.LTCG.is_capital_gains())
        self.assertTrue(TaxType.STCG.is_capital_gains())


if __name__ == "__main__":
    unittest.main()
