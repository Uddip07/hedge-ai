"""
Unit tests for Risk Domain Enums.
"""

import unittest

from packages.domain.enums.risk import (
    PerformanceMetric,
    RiskLevel,
    RiskMetric,
)


class TestRiskEnums(unittest.TestCase):
    """Test suite for Risk Enums."""

    def test_risk_level_helpers(self):
        self.assertEqual(RiskLevel.LOW.severity_rank(), 1)
        self.assertEqual(RiskLevel.UNACCEPTABLE.severity_rank(), 5)
        self.assertTrue(RiskLevel.CRITICAL.requires_circuit_breaker())
        self.assertFalse(RiskLevel.MEDIUM.requires_circuit_breaker())

    def test_risk_metric_helpers(self):
        self.assertTrue(RiskMetric.VAR_95.is_tail_risk_metric())
        self.assertTrue(RiskMetric.MAX_DRAWDOWN.is_tail_risk_metric())

    def test_performance_metric_helpers(self):
        self.assertTrue(PerformanceMetric.SHARPE_RATIO.is_risk_adjusted())
        self.assertFalse(PerformanceMetric.CAGR.is_risk_adjusted())


if __name__ == "__main__":
    unittest.main()
