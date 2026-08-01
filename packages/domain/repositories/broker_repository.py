"""
BrokerAccount Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for BrokerAccount Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.brokerage.broker_account import BrokerAccount
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId


class BrokerAccountRepository(ABC):
    """
    Abstract Repository Interface for BrokerAccount Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, broker_id: BrokerId) -> BrokerAccount | None:
        """Fetch BrokerAccount Aggregate Root by unique BrokerId."""
        pass

    @abstractmethod
    def get_by_account_number(self, account_number: str) -> BrokerAccount | None:
        """Fetch BrokerAccount by external broker account identification string."""
        pass

    @abstractmethod
    def list_all(self) -> list[BrokerAccount]:
        """List all configured broker accounts."""
        pass

    @abstractmethod
    def save(self, account: BrokerAccount) -> None:
        """Persist or update a BrokerAccount Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, broker_id: BrokerId) -> None:
        """Delete a BrokerAccount Aggregate Root by ID."""
        pass
