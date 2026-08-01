"""
Company Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Company aggregate persistence.
Pure domain interface with zero infrastructure dependencies.
"""

import uuid
from abc import ABC, abstractmethod

from packages.domain.market.company import Company


class CompanyRepository(ABC):
    """
    Abstract Repository Interface for Company persistence.
    """

    @abstractmethod
    def get_by_id(self, company_id: uuid.UUID) -> Company | None:
        """Fetch Company by unique UUID identifier."""
        pass

    @abstractmethod
    def get_by_cin(self, cin: str) -> Company | None:
        """Fetch Company by Indian Corporate Identification Number (CIN)."""
        pass

    @abstractmethod
    def list_all(self) -> list[Company]:
        """List all registered corporate entities."""
        pass

    @abstractmethod
    def save(self, company: Company) -> None:
        """Persist or update a Company entity."""
        pass

    @abstractmethod
    def delete(self, company_id: uuid.UUID) -> None:
        """Delete a Company entity by ID."""
        pass
