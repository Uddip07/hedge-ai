"""
Mock Portfolio Adapter implementing Application PortfolioPort.
"""

from packages.application.ports.portfolio_port import PortfolioPort
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId


class MockPortfolioAdapter(PortfolioPort):
    """
    In-memory Mock Adapter implementing PortfolioPort.
    """

    def __init__(self) -> None:
        self.portfolios: dict[str, Portfolio] = {}

    def get_portfolio_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        return self.portfolios.get(str(portfolio_id.value))

    def save_portfolio(self, portfolio: Portfolio) -> None:
        self.portfolios[str(portfolio.id.value)] = portfolio

    def get_portfolio_snapshots(self, portfolio_id: PortfolioId) -> list[PortfolioSnapshot]:
        port = self.get_portfolio_by_id(portfolio_id)
        if port:
            return list(port.snapshots)
        return []
