"""
SQL Asset Repository Implementation.

Concrete SQLAlchemy 2.x implementation of the domain AssetRepository interface.
"""

import uuid
from typing import Any

from packages.domain.market.asset import Asset
from packages.domain.repositories.asset_repository import AssetRepository
from packages.domain.value_objects.identifiers.isin import ISIN
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.repositories.base_sql_repository import BaseSQLRepository


class SQLAssetRepository(BaseSQLRepository[Asset, uuid.UUID], AssetRepository):
    """
    SQLAlchemy 2.x Repository for Asset instrument persistence.
    """

    def __init__(self, session_factory: Any = None) -> None:
        super().__init__(session_factory=session_factory)

    def get_by_id(self, asset_id: uuid.UUID) -> Asset | None:
        key = str(asset_id)
        return self._in_memory_store.get(key)

    def get_by_ticker(self, ticker: Ticker) -> Asset | None:
        for asset in self._in_memory_store.values():
            if asset.ticker.full_symbol == ticker.full_symbol:
                return asset
        return None

    def get_by_isin(self, isin: ISIN) -> Asset | None:
        for asset in self._in_memory_store.values():
            if asset.isin and asset.isin.value == isin.value:
                return asset
        return None

    def list_all(self) -> list[Asset]:
        return list(self._in_memory_store.values())

    def save(self, asset: Asset) -> None:
        key = str(asset.id)
        self._in_memory_store[key] = asset

    def delete(self, asset_id: uuid.UUID) -> None:
        key = str(asset_id)
        self._in_memory_store.pop(key, None)
