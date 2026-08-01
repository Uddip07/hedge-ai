"""
Asset Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Asset instrument persistence.
Pure domain interface with zero infrastructure dependencies.
"""

import uuid
from abc import ABC, abstractmethod

from packages.domain.market.asset import Asset
from packages.domain.value_objects.identifiers.isin import ISIN
from packages.domain.value_objects.identifiers.ticker import Ticker


class AssetRepository(ABC):
    """
    Abstract Repository Interface for Asset persistence.
    """

    @abstractmethod
    def get_by_id(self, asset_id: uuid.UUID) -> Asset | None:
        """Fetch Asset by unique UUID identifier."""
        pass

    @abstractmethod
    def get_by_ticker(self, ticker: Ticker) -> Asset | None:
        """Fetch Asset by canonical Ticker symbol."""
        pass

    @abstractmethod
    def get_by_isin(self, isin: ISIN) -> Asset | None:
        """Fetch Asset by ISIN code."""
        pass

    @abstractmethod
    def list_all(self) -> list[Asset]:
        """List all tradeable financial assets."""
        pass

    @abstractmethod
    def save(self, asset: Asset) -> None:
        """Persist or update an Asset entity."""
        pass

    @abstractmethod
    def delete(self, asset_id: uuid.UUID) -> None:
        """Delete an Asset entity by ID."""
        pass
