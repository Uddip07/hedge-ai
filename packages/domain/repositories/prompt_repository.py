"""
Prompt Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Prompt Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.ai.prompt import Prompt
from packages.domain.value_objects.identifiers.uuid_wrappers import PromptId


class PromptRepository(ABC):
    """
    Abstract Repository Interface for Prompt Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, prompt_id: PromptId) -> Prompt | None:
        """Fetch Prompt Aggregate Root by unique PromptId."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Prompt | None:
        """Fetch Prompt template by unique name."""
        pass

    @abstractmethod
    def list_all(self) -> list[Prompt]:
        """List all prompt templates."""
        pass

    @abstractmethod
    def save(self, prompt: Prompt) -> None:
        """Persist or update a Prompt Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, prompt_id: PromptId) -> None:
        """Delete a Prompt Aggregate Root by ID."""
        pass
