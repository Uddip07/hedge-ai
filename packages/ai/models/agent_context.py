"""
AgentContext Model for AI Core Framework.

Encapsulates input state, target asset Ticker, and execution parameters passed to AI agents.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.identifiers.ticker import Ticker


@dataclass(frozen=True)
class AgentContext:
    """
    Input context provided to AI research agents for single-asset or portfolio analysis.

    Attributes:
        ticker (Ticker): Target asset ticker symbol.
        session_id (str): Unique analysis session ID.
        parameters (dict[str, Any]): Additional execution parameters (horizon, risk tolerance, etc.).
        metadata (dict[str, Any]): Session environment metadata.
    """

    ticker: Ticker
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize AgentContext to dictionary."""
        return {
            "ticker": self.ticker.full_symbol,
            "session_id": self.session_id,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }
