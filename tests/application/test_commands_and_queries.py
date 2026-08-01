"""
Unit tests for CQRS BaseCommand and BaseQuery abstractions.
"""

import unittest
import uuid
from dataclasses import dataclass
from decimal import Decimal

from packages.application.commands import BaseCommand
from packages.application.queries import BaseQuery
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class DepositCashCommand(BaseCommand):
    portfolio_id: uuid.UUID
    amount: Money


@dataclass(frozen=True, kw_only=True)
class GetPortfolioQuery(BaseQuery):
    portfolio_id: uuid.UUID
    ticker_filter: Ticker | None = None


class TestCommandsAndQueries(unittest.TestCase):
    def test_base_command_instantiation_and_serialization(self) -> None:
        p_id = uuid.uuid4()
        u_id = uuid.uuid4()
        amt = Money(Decimal("5000.00"))

        cmd = DepositCashCommand(
            user_id=u_id,
            portfolio_id=p_id,
            amount=amt,
        )

        self.assertEqual(cmd.command_name, "DepositCashCommand")
        self.assertIsInstance(cmd.command_id, uuid.UUID)
        self.assertIsInstance(cmd.timestamp, Timestamp)
        self.assertEqual(cmd.user_id, u_id)
        self.assertEqual(cmd.portfolio_id, p_id)
        self.assertEqual(cmd.amount, amt)

        d = cmd.to_dict()
        self.assertEqual(d["command_name"], "DepositCashCommand")
        self.assertEqual(d["user_id"], str(u_id))
        self.assertEqual(d["command_id"], str(cmd.command_id))

    def test_base_query_instantiation_and_serialization(self) -> None:
        p_id = uuid.uuid4()
        u_id = uuid.uuid4()
        ticker = Ticker("RELIANCE.NSE")

        query = GetPortfolioQuery(
            user_id=u_id,
            portfolio_id=p_id,
            ticker_filter=ticker,
        )

        self.assertEqual(query.query_name, "GetPortfolioQuery")
        self.assertIsInstance(query.query_id, uuid.UUID)
        self.assertIsInstance(query.timestamp, Timestamp)
        self.assertEqual(query.user_id, u_id)
        self.assertEqual(query.portfolio_id, p_id)
        self.assertEqual(query.ticker_filter, ticker)

        d = query.to_dict()
        self.assertEqual(d["query_name"], "GetPortfolioQuery")
        self.assertEqual(d["user_id"], str(u_id))
        self.assertEqual(d["query_id"], str(query.query_id))


if __name__ == "__main__":
    unittest.main()
