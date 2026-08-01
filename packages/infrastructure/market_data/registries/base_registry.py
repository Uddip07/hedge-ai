"""
Base Provider Registry for Market Data Infrastructure.

Generic abstract registry supporting register, unregister, lookup, and metadata discovery.
"""

from typing import Generic, TypeVar

from packages.infrastructure.market_data.exceptions import ProviderCapabilityError
from packages.infrastructure.market_data.metadata import ProviderMetadata

T = TypeVar("T")


class BaseProviderRegistry(Generic[T]):
    """
    Generic Category Provider Registry for hot-swappable provider management.
    """

    def __init__(self, category_name: str) -> None:
        self.category_name = category_name
        self._providers: dict[str, T] = {}
        self._metadata: dict[str, ProviderMetadata] = {}

    def register(
        self,
        provider_name: str,
        provider: T,
        metadata: ProviderMetadata | None = None,
    ) -> None:
        """
        Register a provider instance with metadata for this category.
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
        """Unregister a provider by name."""
        name_key = provider_name.lower().strip()
        self._providers.pop(name_key, None)
        self._metadata.pop(name_key, None)

    def lookup(self, provider_name: str) -> T:
        """
        Retrieve provider instance by name.
        """
        name_key = provider_name.lower().strip()
        provider = self._providers.get(name_key)
        if provider is None:
            raise ProviderCapabilityError(
                f"No provider '{provider_name}' registered for {self.category_name}.",
                details={"registered_providers": list(self._providers.keys())},
            )
        return provider

    def provider_metadata(self, provider_name: str) -> ProviderMetadata:
        """Get ProviderMetadata for provider."""
        name_key = provider_name.lower().strip()
        meta = self._metadata.get(name_key)
        if meta is None:
            raise ProviderCapabilityError(
                f"No metadata found for provider '{provider_name}' in {self.category_name}.",
                details={"registered_providers": list(self._metadata.keys())},
            )
        return meta

    def list_providers(self) -> list[str]:
        """Return list of registered provider names."""
        return list(self._providers.keys())
