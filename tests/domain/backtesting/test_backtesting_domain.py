"""
Unit tests for Backtest Aggregate Root and child backtesting models (EquityCurve, TradeLog, Metrics, Result, Run).
"""

import unittest
from datetime import date
from decimal import Decimal

from packages.domain.backtesting import (
    Backtest,
    BacktestMetrics,
    BacktestResult,
    EquityCurve,
    TradeLog,
)
from packages.domain.enums.trading import TradeType
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.portfolio.trade import Trade
from packages.domain.value_objects.core import Money, Percentage, Price, Quantity
from packages.domain.value_objects.identifiers import OrderId, PortfolioId, StrategyId, Ticker
from packages.domain.value_objects.metrics import Drawdown, SharpeRatio, SortinoRatio, Volatility
from packages.domain.value_objects.temporal import Timestamp, TradingDate


class TestBacktestingDomain(unittest.TestCase):
    """Test suite for Backtest Aggregate Root and backtesting models."""

    def test_trade_log_and_equity_curve(self):
        t = Ticker("RELIANCE.NSE")
        ts = Timestamp.now_utc()
        p_id = PortfolioId.generate()
        trade = Trade(
            portfolio_id=p_id,
            order_id=OrderId.generate(),
            ticker=t,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
            fee=Money(Decimal("20.00")),
            tax=Money(Decimal("10.00")),
            executed_at=ts,
        )

        trade_log = TradeLog(trades=[trade])
        self.assertEqual(trade_log.total_trades_count, 1)
        self.assertEqual(trade_log.total_frictions.amount, Decimal("30.00"))

        snap1 = PortfolioSnapshot(
            timestamp=ts,
            total_equity=Money(Decimal("100000.00")),
            cash_balance=Money(Decimal("100000.00")),
            invested_capital=Money(Decimal("0.00")),
            holdings_count=0,
            positions_count=0,
        )
        snap2 = PortfolioSnapshot(
            timestamp=ts,
            total_equity=Money(Decimal("120000.00")),
            cash_balance=Money(Decimal("20000.00")),
            invested_capital=Money(Decimal("100000.00")),
            holdings_count=1,
            positions_count=1,
        )

        eq_curve = EquityCurve(snapshots=[snap1, snap2])
        self.assertEqual(eq_curve.initial_equity.amount, Decimal("100000.00"))
        self.assertEqual(eq_curve.final_equity.amount, Decimal("120000.00"))
        self.assertEqual(eq_curve.total_return_pct.value, Decimal("20.00"))

    def test_backtest_metrics_and_result_serialization(self):
        metrics = BacktestMetrics(
            cagr=Percentage(Decimal("25.0")),
            sharpe_ratio=SharpeRatio(Decimal("1.8")),
            sortino_ratio=SortinoRatio(Decimal("2.2")),
            max_drawdown=Drawdown.from_value(Decimal("0.12")),
            volatility=Volatility.from_value(Decimal("0.15")),
            win_rate=Percentage(Decimal("65.0")),
            total_trades=50,
        )

        ts = Timestamp.now_utc()
        snap = PortfolioSnapshot(
            timestamp=ts,
            total_equity=Money(Decimal("125000.00")),
            cash_balance=Money(Decimal("25000.00")),
            invested_capital=Money(Decimal("100000.00")),
            holdings_count=2,
            positions_count=2,
        )
        eq_curve = EquityCurve(snapshots=[snap])
        trade_log = TradeLog(trades=[])

        result = BacktestResult(
            metrics=metrics,
            equity_curve=eq_curve,
            trade_log=trade_log,
            final_equity=Money(Decimal("125000.00")),
            total_return_pct=Percentage(Decimal("25.0")),
        )

        res_dict = result.to_dict()
        restored = BacktestResult.from_dict(res_dict)
        self.assertEqual(restored.final_equity.amount, Decimal("125000.00"))
        self.assertEqual(restored.metrics.sharpe_ratio.value, Decimal("1.8"))

    def test_backtest_aggregate_root_workflow(self):
        s_id = StrategyId.generate()
        bt = Backtest(
            strategy_id=s_id,
            name="Momentum Strategy 2025 Backtest",
            start_date=TradingDate(date(2025, 1, 1)),
            end_date=TradingDate(date(2025, 12, 31)),
            initial_capital=Money(Decimal("100000.00")),
            benchmark_ticker=Ticker("NIFTY50.NSE"),
        )

        # Start Run #1
        run1 = bt.start_run()
        self.assertEqual(run1.run_number, 1)
        self.assertEqual(run1.status, "RUNNING")

        # Create dummy result and complete run #1
        ts = Timestamp.now_utc()
        snap = PortfolioSnapshot(
            timestamp=ts,
            total_equity=Money(Decimal("115000.00")),
            cash_balance=Money(Decimal("15000.00")),
            invested_capital=Money(Decimal("100000.00")),
            holdings_count=1,
            positions_count=1,
        )
        result = BacktestResult(
            metrics=BacktestMetrics(
                cagr=Percentage(Decimal("15.0")),
                sharpe_ratio=SharpeRatio(Decimal("1.4")),
                sortino_ratio=SortinoRatio(Decimal("1.6")),
                max_drawdown=Drawdown.from_value(Decimal("0.10")),
                volatility=Volatility.from_value(Decimal("0.12")),
                win_rate=Percentage(Decimal("60.0")),
                total_trades=10,
            ),
            equity_curve=EquityCurve(snapshots=[snap]),
            trade_log=TradeLog(trades=[]),
            final_equity=Money(Decimal("115000.00")),
            total_return_pct=Percentage(Decimal("15.0")),
        )

        bt.complete_run(run1.run_id, result)
        self.assertEqual(run1.status, "COMPLETED")
        self.assertIsNotNone(bt.get_latest_result())

        # Dict roundtrip
        bt_dict = bt.to_dict()
        restored_bt = Backtest.from_dict(bt_dict)
        self.assertEqual(restored_bt.name, "Momentum Strategy 2025 Backtest")
        self.assertEqual(len(restored_bt.runs), 1)
        self.assertEqual(restored_bt.runs[0].status, "COMPLETED")


if __name__ == "__main__":
    unittest.main()
