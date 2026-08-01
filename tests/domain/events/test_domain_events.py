"""
Unit tests for Domain Events across all bounded contexts.
"""

import unittest
import uuid
from decimal import Decimal

from packages.domain.enums.ai import AgentType
from packages.domain.enums.market import ExchangeType, MarketSession
from packages.domain.enums.risk import RiskLevel
from packages.domain.enums.trading import OrderType, TradeType
from packages.domain.events import (
    AgentThoughtGeneratedEvent,
    CashDepositedEvent,
    MarketSessionChangedEvent,
    OrderFilledEvent,
    OrderPlacedEvent,
    PositionClosedEvent,
    RiskLimitExceededEvent,
)
from packages.domain.value_objects.core import Money, Price, Quantity
from packages.domain.value_objects.identifiers import (
    ExecutionId,
    OrderId,
    PortfolioId,
    PromptId,
    Ticker,
)


class TestDomainEvents(unittest.TestCase):
    """Test suite for Domain Events."""

    def test_market_session_changed_event_serialization(self):
        event = MarketSessionChangedEvent(
            aggregate_id="NSE",
            exchange=ExchangeType.NSE,
            previous_session=MarketSession.PRE_MARKET,
            new_session=MarketSession.NORMAL,
        )

        self.assertEqual(event.event_type, "MarketSessionChangedEvent")
        event_dict = event.to_dict()
        restored = MarketSessionChangedEvent.from_dict(event_dict)
        self.assertEqual(restored.exchange, ExchangeType.NSE)
        self.assertEqual(restored.new_session, MarketSession.NORMAL)

    def test_order_placed_and_filled_events(self):
        o_id = OrderId.generate()
        p_id = PortfolioId.generate()
        t = Ticker("RELIANCE.NSE")

        evt_placed = OrderPlacedEvent(
            aggregate_id=str(o_id),
            order_id=o_id,
            portfolio_id=p_id,
            ticker=t,
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
        )
        self.assertEqual(evt_placed.order_id, o_id)
        restored_placed = OrderPlacedEvent.from_dict(evt_placed.to_dict())
        assert restored_placed.price is not None
        self.assertEqual(restored_placed.price.amount, Decimal("2500.00"))

        ex_id = ExecutionId.generate()
        evt_filled = OrderFilledEvent(
            aggregate_id=str(o_id),
            order_id=o_id,
            execution_id=ex_id,
            filled_quantity=Quantity(Decimal("10")),
            fill_price=Price.from_amount("2500"),
            fee=Money(Decimal("20.00")),
            tax=Money(Decimal("10.00")),
        )
        restored_filled = OrderFilledEvent.from_dict(evt_filled.to_dict())
        self.assertEqual(restored_filled.fee.amount, Decimal("20.00"))

    def test_portfolio_cash_and_position_events(self):
        p_id = PortfolioId.generate()
        evt_cash = CashDepositedEvent(
            aggregate_id=str(p_id),
            portfolio_id=p_id,
            amount=Money(Decimal("50000.00")),
            new_balance=Money(Decimal("50000.00")),
        )
        restored_cash = CashDepositedEvent.from_dict(evt_cash.to_dict())
        self.assertEqual(restored_cash.new_balance.amount, Decimal("50000.00"))

        pos_id = uuid.uuid4()
        t = Ticker("INFY.NSE")
        evt_pos = PositionClosedEvent(
            aggregate_id=str(p_id),
            portfolio_id=p_id,
            position_id=pos_id,
            ticker=t,
            realized_pnl=Money(Decimal("5000.00")),
        )
        restored_pos = PositionClosedEvent.from_dict(evt_pos.to_dict())
        self.assertEqual(restored_pos.realized_pnl.amount, Decimal("5000.00"))

    def test_risk_limit_exceeded_event(self):
        p_id = PortfolioId.generate()
        evt_risk = RiskLimitExceededEvent(
            aggregate_id=str(p_id),
            portfolio_id=p_id,
            metric_name="MaxDrawdown",
            current_value=Decimal("0.18"),
            limit_threshold=Decimal("0.15"),
            severity=RiskLevel.HIGH,
        )
        restored_risk = RiskLimitExceededEvent.from_dict(evt_risk.to_dict())
        self.assertEqual(restored_risk.severity, RiskLevel.HIGH)

    def test_ai_agent_thought_event(self):
        pr_id = PromptId.generate()
        evt_ai = AgentThoughtGeneratedEvent(
            aggregate_id=str(pr_id),
            prompt_id=pr_id,
            agent_type=AgentType.QUANT,
            step_index=1,
            thought="Analyzing momentum alpha factor signals.",
        )
        restored_ai = AgentThoughtGeneratedEvent.from_dict(evt_ai.to_dict())
        self.assertEqual(restored_ai.step_index, 1)


if __name__ == "__main__":
    unittest.main()
