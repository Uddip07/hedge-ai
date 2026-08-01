"""
Unit Tests for Execution Pipeline & Paper Trading Isolation.

Validates human-in-the-loop user approval, risk engine gates, execution routing,
and strict context isolation between paper trading and live Zerodha.
"""

from unittest.mock import MagicMock

import pytest

from packages.application.execution import (
    ExecutionMode,
    ExecutionPipeline,
    ExecutionPipelineError,
    PaperTradingIsolationError,
    PaperTradingManager,
    RiskCheckEngine,
    TradeRecommendation,
    UserApprovalRequest,
)


class TestExecutionPipeline:
    def test_rejection_without_user_approval(self):
        pipeline = ExecutionPipeline()
        rec = TradeRecommendation(ticker="RELIANCE.NS", action="BUY", target_quantity=10)
        unapproved = UserApprovalRequest(
            recommendation_id="r1",
            approved=False,
            approved_by_user_id="user1",
        )

        pid = "12345678-1234-5678-1234-567812345678"
        bid = "87654321-4321-8765-4321-876543218765"

        with pytest.raises(ExecutionPipelineError) as exc_info:
            pipeline.process_execution(rec, unapproved, pid, bid)
        assert "not approved" in str(exc_info.value)

    def test_risk_check_engine_limit_exceeded(self):
        engine = RiskCheckEngine(max_order_value_inr=10000.0)
        order_params = {"quantity": 10, "price": 2000.0}  # Value = 20,000 > 10,000

        with pytest.raises(ExecutionPipelineError) as exc_info:
            engine.validate(order_params)
        assert "exceeds maximum risk limit" in str(exc_info.value)

    def test_paper_execution_routing(self):
        pipeline = ExecutionPipeline()
        rec = TradeRecommendation(
            ticker="INFY.NS",
            action="BUY",
            target_quantity=5,
            order_type="LIMIT",
            suggested_price=1400.0,
        )
        approval = UserApprovalRequest(
            recommendation_id="r2",
            approved=True,
            approved_by_user_id="user1",
            execution_mode=ExecutionMode.PAPER,
        )

        pid = "12345678-1234-5678-1234-567812345678"
        bid = "87654321-4321-8765-4321-876543218765"
        order = pipeline.process_execution(rec, approval, pid, bid)
        assert order.ticker.symbol == "INFY"
        assert str(order.portfolio_id.value) == pid

    def test_live_zerodha_execution_routing(self):
        mock_order_service = MagicMock()
        mock_order_service.place_order.return_value = "MOCK_ORDER"

        pipeline = ExecutionPipeline(zerodha_order_service=mock_order_service)
        rec = TradeRecommendation(
            ticker="TCS.NS",
            action="BUY",
            target_quantity=2,
            order_type="LIMIT",
            suggested_price=3500.0,
        )
        approval = UserApprovalRequest(
            recommendation_id="r3",
            approved=True,
            approved_by_user_id="user1",
            execution_mode=ExecutionMode.LIVE_ZERODHA,
        )

        pid = "12345678-1234-5678-1234-567812345678"
        bid = "87654321-4321-8765-4321-876543218765"
        res = pipeline.process_execution(rec, approval, pid, bid)
        assert res == "MOCK_ORDER"
        mock_order_service.place_order.assert_called_once()


class TestPaperTradingIsolation:
    def test_isolation_breach_detection(self):
        mgr = PaperTradingManager()
        paper_ctx = mgr.create_paper_portfolio_context("p1")
        live_ctx = mgr.create_live_zerodha_context("z1")

        # Attempt to run live trade on paper context -> should raise PaperTradingIsolationError
        with pytest.raises(PaperTradingIsolationError):
            paper_ctx.validate_isolation(target_is_live=True)

        with pytest.raises(PaperTradingIsolationError):
            live_ctx.validate_isolation(target_is_live=False)

        # Matching context should pass
        paper_ctx.validate_isolation(target_is_live=False)
        live_ctx.validate_isolation(target_is_live=True)
