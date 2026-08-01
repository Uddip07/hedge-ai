"""
Unit tests for Application BaseDTO and BaseMapper abstractions.
"""

import unittest
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.application.dto import BaseDTO
from packages.application.mappers import BaseMapper
from packages.domain.enums.portfolio import PortfolioType
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers import PortfolioId


@dataclass(frozen=True)
class PortfolioDTO(BaseDTO):
    id: str
    name: str
    portfolio_type: str
    cash_balance: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "portfolio_type": self.portfolio_type,
            "cash_balance": self.cash_balance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PortfolioDTO":
        return cls(
            id=data["id"],
            name=data["name"],
            portfolio_type=data["portfolio_type"],
            cash_balance=data["cash_balance"],
        )


class PortfolioMapper(BaseMapper[Portfolio, PortfolioDTO]):
    def to_dto(self, domain: Portfolio) -> PortfolioDTO:
        return PortfolioDTO(
            id=str(domain.id.value if hasattr(domain.id, "value") else domain.id),
            name=domain.name,
            portfolio_type=domain.portfolio_type.value,
            cash_balance=str(domain.cash_balance.amount),
        )

    def to_domain(self, dto: PortfolioDTO) -> Portfolio:
        return Portfolio(
            id=PortfolioId.from_dict({"id": dto.id}),
            name=dto.name,
            portfolio_type=PortfolioType(dto.portfolio_type),
            cash_balance=Money(Decimal(dto.cash_balance)),
        )


class TestDTOAndMappers(unittest.TestCase):
    def test_dto_serialization(self) -> None:
        dto = PortfolioDTO(
            id=str(uuid.uuid4()),
            name="Alpha Growth Portfolio",
            portfolio_type="PAPER",
            cash_balance="100000.00",
        )
        d = dto.to_dict()
        self.assertEqual(d["name"], "Alpha Growth Portfolio")
        self.assertEqual(d["cash_balance"], "100000.00")

        restored = PortfolioDTO.from_dict(d)
        self.assertEqual(restored, dto)

    def test_mapper_bidirectional_conversion(self) -> None:
        port_id = PortfolioId.generate()
        domain_portfolio = Portfolio(
            id=port_id,
            name="Institutional Strategy Portfolio",
            portfolio_type=PortfolioType.LIVE,
            cash_balance=Money(Decimal("250000.00")),
        )

        mapper = PortfolioMapper()
        dto = mapper.to_dto(domain_portfolio)

        self.assertEqual(dto.name, "Institutional Strategy Portfolio")
        self.assertEqual(dto.portfolio_type, "LIVE")
        self.assertEqual(dto.cash_balance, "250000.00")

        restored_domain = mapper.to_domain(dto)
        self.assertEqual(restored_domain.name, domain_portfolio.name)
        self.assertEqual(restored_domain.portfolio_type, domain_portfolio.portfolio_type)
        self.assertEqual(restored_domain.cash_balance.amount, domain_portfolio.cash_balance.amount)

    def test_mapper_list_conversion(self) -> None:
        p1 = Portfolio(name="Port 1", portfolio_type=PortfolioType.PAPER)
        p2 = Portfolio(name="Port 2", portfolio_type=PortfolioType.LIVE)

        mapper = PortfolioMapper()
        dto_list = mapper.to_dto_list([p1, p2])
        self.assertEqual(len(dto_list), 2)
        self.assertEqual(dto_list[0].name, "Port 1")
        self.assertEqual(dto_list[1].name, "Port 2")

        domain_list = mapper.to_domain_list(dto_list)
        self.assertEqual(len(domain_list), 2)
        self.assertEqual(domain_list[0].name, "Port 1")


if __name__ == "__main__":
    unittest.main()
