"""
Base UseCase Abstraction for Clean Architecture.

Defines the single-entry execution contract for Application Use Cases.
Pure application workflow orchestration interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from packages.application.commands.base import BaseCommand
from packages.application.queries.base import BaseQuery

TRequest = TypeVar("TRequest", bound=BaseCommand | BaseQuery | Any)
TResponse = TypeVar("TResponse")


class BaseUseCase(ABC, Generic[TRequest, TResponse]):
    """
    Abstract Base Class for all Application Use Cases.

    Enforces Single Responsibility Principle: each Use Case represents a single
    business workflow or application request interaction.
    """

    @abstractmethod
    def execute(self, request: TRequest) -> TResponse:
        """
        Execute the business use case workflow.

        Args:
            request (TRequest): Input Command, Query, or request model.

        Returns:
            TResponse: Output DTO, Result value, or execution response.
        """

    def __call__(self, request: TRequest) -> TResponse:
        """Callable shorthand for execute(request)."""
        return self.execute(request)
