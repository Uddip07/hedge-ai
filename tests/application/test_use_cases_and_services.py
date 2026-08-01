"""
Unit tests for Application BaseUseCase and BaseApplicationService abstractions.
"""

import unittest
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.application.commands import BaseCommand
from packages.application.dto import BaseDTO
from packages.application.services import BaseApplicationService
from packages.application.use_cases import BaseUseCase
from packages.domain.enums.portfolio import PortfolioType
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.core.money import Money


@dataclass(frozen=True, kw_only=True)
class CreatePortfolioCommand(BaseCommand):
    name: str
    portfolio_type: PortfolioType
    initial_deposit: Money


@dataclass(frozen=True)
class CreatePortfolioResponseDTO(BaseDTO):
    portfolio_id: str
    name: str
    balance: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "balance": self.balance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CreatePortfolioResponseDTO":
        return cls(
            portfolio_id=data["portfolio_id"],
            name=data["name"],
            balance=data["balance"],
        )


class CreatePortfolioUseCase(BaseUseCase[CreatePortfolioCommand, CreatePortfolioResponseDTO]):
    def execute(self, request: CreatePortfolioCommand) -> CreatePortfolioResponseDTO:
        portfolio = Portfolio(
            name=request.name,
            portfolio_type=request.portfolio_type,
        )
        if request.initial_deposit.amount > Decimal("0"):
            portfolio.deposit_cash(request.initial_deposit)

        return CreatePortfolioResponseDTO(
            portfolio_id=str(portfolio.id.value),
            name=portfolio.name,
            balance=str(portfolio.cash_balance.amount),
        )


class PortfolioApplicationService(BaseApplicationService):
    def __init__(self, create_use_case: CreatePortfolioUseCase) -> None:
        self.create_use_case = create_use_case

    def create_new_portfolio(
        self, name: str, initial_deposit: Decimal, user_id: uuid.UUID
    ) -> CreatePortfolioResponseDTO:
        cmd = CreatePortfolioCommand(
            user_id=user_id,
            name=name,
            portfolio_type=PortfolioType.LIVE,
            initial_deposit=Money(initial_deposit),
        )
        return self.create_use_case(cmd)


class TestUseCasesAndServices(unittest.TestCase):
    def test_use_case_execution(self) -> None:
        use_case = CreatePortfolioUseCase()
        cmd = CreatePortfolioCommand(
            name="India Alpha Fund",
            portfolio_type=PortfolioType.PAPER,
            initial_deposit=Money(Decimal("500000.00")),
        )

        res = use_case.execute(cmd)
        self.assertEqual(res.name, "India Alpha Fund")
        self.assertEqual(res.balance, "500000.00")
        self.assertTrue(res.portfolio_id)

    def test_use_case_callable_protocol(self) -> None:
        use_case = CreatePortfolioUseCase()
        cmd = CreatePortfolioCommand(
            name="Callable Test",
            portfolio_type=PortfolioType.LIVE,
            initial_deposit=Money(Decimal("1000.00")),
        )

        res = use_case(cmd)
        self.assertEqual(res.name, "Callable Test")
        self.assertEqual(res.balance, "1000.00")

    def test_application_service_orchestration(self) -> None:
        use_case = CreatePortfolioUseCase()
        service = PortfolioApplicationService(use_case)
        u_id = uuid.uuid4()

        res = service.create_new_portfolio(
            name="Hedge Alpha",
            initial_deposit=Decimal("1000000.00"),
            user_id=u_id,
        )

        self.assertEqual(res.name, "Hedge Alpha")
        self.assertEqual(res.balance, "1000000.00")


if __name__ == "__main__":
    unittest.main()
