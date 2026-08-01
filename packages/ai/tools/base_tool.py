"""
Base Tool Abstraction for AI Core Framework.

Defines the abstract BaseTool contract for agent tool execution capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Abstract Base Class for agent execution tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return unique tool name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Return human-readable tool capability description."""

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> Any:
        """
        Execute tool functionality with input arguments.

        Args:
            arguments (dict[str, Any]): Input parameter dictionary.

        Returns:
            Any: Tool execution output payload.
        """
