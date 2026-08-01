"""
In-Memory Conversation and Reasoning Store for AI Core Framework.

Stores session analysis histories, agent outputs, and reasoning traces without external database dependencies.
"""

from typing import Any

from packages.ai.models.agent_result import AgentResult
from packages.domain.research.consensus import ConsensusDecision


class ConversationStore:
    """
    In-memory storage for session conversations, agent results, and consensus decisions.
    """

    def __init__(self) -> None:
        self._session_agent_results: dict[str, list[AgentResult]] = {}
        self._session_consensus: dict[str, ConsensusDecision] = {}
        self._session_history: dict[str, list[dict[str, Any]]] = {}

    def save_agent_results(self, session_id: str, results: list[AgentResult]) -> None:
        """Store agent results for a session."""
        if session_id not in self._session_agent_results:
            self._session_agent_results[session_id] = []
        self._session_agent_results[session_id].extend(results)

    def get_agent_results(self, session_id: str) -> list[AgentResult]:
        """Retrieve stored agent results for a session."""
        return self._session_agent_results.get(session_id, [])

    def save_consensus(self, session_id: str, decision: ConsensusDecision) -> None:
        """Store consensus decision for a session."""
        self._session_consensus[session_id] = decision

    def get_consensus(self, session_id: str) -> ConsensusDecision | None:
        """Retrieve consensus decision for a session."""
        return self._session_consensus.get(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append a conversation message to session history."""
        if session_id not in self._session_history:
            self._session_history[session_id] = []
        self._session_history[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve full conversation message history for a session."""
        return self._session_history.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """Clear all stored data for a session."""
        self._session_agent_results.pop(session_id, None)
        self._session_consensus.pop(session_id, None)
        self._session_history.pop(session_id, None)

    def clear_all(self) -> None:
        """Clear all stored sessions."""
        self._session_agent_results.clear()
        self._session_consensus.clear()
        self._session_history.clear()
