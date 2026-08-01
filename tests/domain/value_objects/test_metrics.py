"""
Unit tests for Metrics Value Objects (RiskScore, ConfidenceScore, RecommendationScore, SharpeRatio, SortinoRatio, Drawdown, Volatility, ATR, RSI, MACD).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.research import RecommendationType
from packages.domain.enums.risk import RiskLevel
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.metrics import (
    ATR,
    MACD,
    RSI,
    ConfidenceScore,
    Drawdown,
    RecommendationScore,
    RiskScore,
    SharpeRatio,
    SortinoRatio,
    Volatility,
)


class TestMetricsValueObjects(unittest.TestCase):
    """Test suite for metrics value objects."""

    def test_risk_score_bounds_and_mapping(self):
        rs_low = RiskScore(Decimal("0.10"))
        self.assertEqual(rs_low.risk_level(), RiskLevel.LOW)

        rs_crit = RiskScore(Decimal("0.85"))
        self.assertEqual(rs_crit.risk_level(), RiskLevel.CRITICAL)

        with self.assertRaises(ValidationError):
            RiskScore(Decimal("1.5"))  # Out of range

    def test_confidence_score_bounds_and_helpers(self):
        cs = ConfidenceScore(Decimal("0.80"))
        self.assertTrue(cs.is_high_confidence(Decimal("0.75")))
        self.assertFalse(cs.is_high_confidence(Decimal("0.90")))

        with self.assertRaises(ValidationError):
            ConfidenceScore(Decimal("-0.1"))

    def test_recommendation_score_mapping(self):
        rc_buy = RecommendationScore(Decimal("0.8"))
        self.assertEqual(rc_buy.recommendation_type(), RecommendationType.STRONG_BUY)

        rc_sell = RecommendationScore(Decimal("-0.5"))
        self.assertEqual(rc_sell.recommendation_type(), RecommendationType.SELL)

        with self.assertRaises(ValidationError):
            RecommendationScore(Decimal("2.0"))

    def test_sharpe_and_sortino_ratios(self):
        sh = SharpeRatio(Decimal("1.85"))
        self.assertTrue(sh.is_acceptable())
        self.assertFalse(sh.is_excellent())

        so = SortinoRatio(Decimal("2.10"))
        self.assertTrue(so.is_acceptable())

    def test_drawdown_and_volatility(self):
        dd = Drawdown.from_value("15.5")
        self.assertEqual(dd.value, Decimal("15.5"))
        self.assertTrue(dd.is_breached(Percentage(Decimal("10.0"))))
        self.assertFalse(dd.is_breached(Percentage(Decimal("20.0"))))

        vol = Volatility.from_value("18.2")
        self.assertEqual(vol.value, Decimal("18.2"))

    def test_indicators_atr_rsi_macd(self):
        atr = ATR(Decimal("25.4"), period=14)
        self.assertEqual(atr.value, Decimal("25.4"))

        rsi_ob = RSI(Decimal("75.0"))
        self.assertTrue(rsi_ob.is_overbought())
        self.assertFalse(rsi_ob.is_oversold())

        rsi_os = RSI(Decimal("25.0"))
        self.assertTrue(rsi_os.is_oversold())

        macd = MACD(macd_line=Decimal("2.5"), signal_line=Decimal("1.0"), histogram=Decimal("1.5"))
        self.assertTrue(macd.is_bullish())
        self.assertFalse(macd.is_bearish())


if __name__ == "__main__":
    unittest.main()
