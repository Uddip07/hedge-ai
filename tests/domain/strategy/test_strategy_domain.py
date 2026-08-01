"""
Unit tests for Strategy Aggregate Root and child strategy models (Signal, SignalResult, Optimization models).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.strategy import SignalType, StrategyStatus, StrategyType
from packages.domain.strategy import (
    Constraint,
    EvaluationResult,
    ObjectiveFunction,
    Optimization,
    Signal,
    SignalResult,
    Strategy,
    StrategyVersion,
)
from packages.domain.value_objects.core import Percentage
from packages.domain.value_objects.identifiers import StrategyId, Ticker, TradeId
from packages.domain.value_objects.metrics import Drawdown, SharpeRatio
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore
from packages.domain.value_objects.temporal import Timestamp


class TestStrategyDomain(unittest.TestCase):
    """Test suite for Strategy Aggregate Root and strategy models."""

    def test_signal_and_signal_result_serialization(self):
        s_id = StrategyId.generate()
        t = Ticker("RELIANCE.NSE")
        sig = Signal(
            strategy_id=s_id,
            ticker=t,
            signal_type=SignalType.BUY,
            score=ConfidenceScore(Decimal("0.85")),
            strength=RecommendationScore(Decimal("0.80")),
            generated_at=Timestamp.now_utc(),
            reasoning="Golden cross breakout on 50-day EMA.",
        )

        sig_dict = sig.to_dict()
        restored_sig = Signal.from_dict(sig_dict)
        self.assertEqual(restored_sig.ticker.full_symbol, "RELIANCE.NSE")
        self.assertEqual(restored_sig.signal_type, SignalType.BUY)

        result = SignalResult(
            signal=sig,
            executed_trade_id=TradeId.generate(),
            actual_return_pct=Percentage(Decimal("5.2")),
            is_successful=True,
        )
        self.assertTrue(result.is_successful)

    def test_optimization_and_constraints(self):
        c_max_dd = Constraint(
            name="Max Drawdown Limit", constraint_type="MAX_DRAWDOWN", threshold=Decimal("0.15")
        )
        self.assertTrue(c_max_dd.is_satisfied(Decimal("0.10")))
        self.assertFalse(c_max_dd.is_satisfied(Decimal("0.20")))

        obj = ObjectiveFunction(metric_name="SHARPE_RATIO", maximize=True)
        s_id = StrategyId.generate()
        opt = Optimization(strategy_id=s_id, objective=obj)

        res1 = EvaluationResult(
            parameters={"lookback": 20},
            sharpe_ratio=SharpeRatio(Decimal("1.5")),
            cagr=Percentage(Decimal("15.0")),
            max_drawdown=Drawdown.from_value(Decimal("0.10")),
            score=Decimal("1.5"),
        )
        res2 = EvaluationResult(
            parameters={"lookback": 50},
            sharpe_ratio=SharpeRatio(Decimal("2.1")),
            cagr=Percentage(Decimal("22.0")),
            max_drawdown=Drawdown.from_value(Decimal("0.08")),
            score=Decimal("2.1"),
        )

        opt.add_result(res1)
        assert opt.best_result is not None
        self.assertEqual(opt.best_result.score, Decimal("1.5"))

        opt.add_result(res2)
        # res2 has higher score 2.1 -> best_result updated
        assert opt.best_result is not None
        self.assertEqual(opt.best_result.score, Decimal("2.1"))

    def test_strategy_aggregate_root_workflow(self):
        strat = Strategy(name="Nifty Momentum Alpha Strategy", strategy_type=StrategyType.MOMENTUM)
        self.assertEqual(strat.status, StrategyStatus.DRAFT)

        v1 = StrategyVersion(
            version_number="1.0.0",
            parameters={"lookback_days": 20, "stop_loss_pct": 0.05},
            changelog="Initial release.",
        )
        strat.add_version(v1)
        self.assertEqual(strat.get_latest_version(), v1)

        # Generate Signal
        t = Ticker("INFY.NSE")
        sig = strat.generate_signal(
            ticker=t,
            signal_type=SignalType.BUY,
            score=ConfidenceScore(Decimal("0.90")),
            strength=RecommendationScore(Decimal("0.85")),
            reasoning="Momentum score high.",
        )

        self.assertEqual(len(strat.signals), 1)
        self.assertEqual(strat.signals[0].ticker.full_symbol, "INFY.NSE")

        # Update status
        strat.update_status(StrategyStatus.ACTIVE)
        self.assertEqual(strat.status, StrategyStatus.ACTIVE)

        # Dict roundtrip
        strat_dict = strat.to_dict()
        restored = Strategy.from_dict(strat_dict)
        self.assertEqual(restored.name, "Nifty Momentum Alpha Strategy")
        self.assertEqual(len(restored.versions), 1)
        self.assertEqual(len(restored.signals), 1)


if __name__ == "__main__":
    unittest.main()
