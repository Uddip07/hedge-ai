"""
Market Data Provider Registry.

Thread-safe registry managing lookups and capabilities for
all market data providers (Mock, Yahoo, NSE, BSE).
"""

from packages.infrastructure.market_data.exceptions import ProviderCapabilityError
from packages.infrastructure.market_data.metadata import ProviderMetadata
from packages.infrastructure.market_data.providers.base import MarketDataProvider


class MarketDataProviderRegistry:
    """
    Registry for dynamic market data provider lifecycle management.
    """

    def __init__(self) -> None:
        self._providers: dict[str, MarketDataProvider] = {}
        self._metadata: dict[str, ProviderMetadata] = {}

    def register(
        self,
        provider_name: str,
        provider: MarketDataProvider,
        metadata: ProviderMetadata | None = None,
    ) -> None:
        """
        Register a MarketDataProvider instance with optional metadata.

        Args:
            provider_name (str): Unique provider registration key.
            provider (MarketDataProvider): Concrete provider instance.
            metadata (ProviderMetadata | None): Provider metadata descriptor.
        """
        name_key = provider_name.lower().strip()
        self._providers[name_key] = provider

        if metadata is not None:
            self._metadata[name_key] = metadata
        else:
            self._metadata[name_key] = ProviderMetadata(
                provider_name=provider_name,
                provider_version="1.0.0",
            )

    def unregister(self, provider_name: str) -> None:
        """
        Unregister a provider by name key.

        Args:
            provider_name (str): Unique provider registration key.
        """
        name_key = provider_name.lower().strip()
        self._providers.pop(name_key, None)
        self._metadata.pop(name_key, None)

    def lookup(self, provider_name: str) -> MarketDataProvider:
        """
        Retrieve registered MarketDataProvider by name.

        Args:
            provider_name (str): Target provider name key.

        Returns:
            MarketDataProvider: Registered provider instance.

        Raises:
            ProviderCapabilityError: If provider is not registered.
        """
        name_key = provider_name.lower().strip()
        provider = self._providers.get(name_key)
        if provider is None:
            raise ProviderCapabilityError(
                f"Market Data Provider '{provider_name}' is not registered in registry.",
                details={"registered_providers": list(self._providers.keys())},
            )
        return provider

    def provider_metadata(self, provider_name: str) -> ProviderMetadata:
        """
        Get ProviderMetadata for a registered provider.

        Args:
            provider_name (str): Target provider name key.

        Returns:
            ProviderMetadata: Registered provider metadata descriptor.

        Raises:
            ProviderCapabilityError: If metadata for provider is not found.
        """
        name_key = provider_name.lower().strip()
        metadata = self._metadata.get(name_key)
        if metadata is None:
            raise ProviderCapabilityError(
                f"Metadata for Market Data Provider '{provider_name}' is not registered.",
                details={"registered_providers": list(self._metadata.keys())},
            )
        return metadata

    def list_providers(self) -> list[str]:
        """Return list of all registered provider names."""
        return list(self._providers.keys())
