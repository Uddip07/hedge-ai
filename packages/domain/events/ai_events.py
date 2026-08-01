"""
AI Agent Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for AI agent reasoning steps and tool execution events.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.ai import AgentType
from packages.domain.events.base import DomainEvent
from packages.domain.value_objects.identifiers.uuid_wrappers import PromptId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class AgentThoughtGeneratedEvent(DomainEvent):
    """
    Emitted when an AI agent generates an intermediate reasoning thought step.
    """

    prompt_id: PromptId
    agent_type: AgentType
    step_index: int
    thought: str

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "prompt_id": self.prompt_id.to_dict(),
                "agent_type": self.agent_type.value,
                "step_index": self.step_index,
                "thought": self.thought,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentThoughtGeneratedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            prompt_id=PromptId.from_dict(data["prompt_id"]),
            agent_type=AgentType(data["agent_type"]),
            step_index=int(data["step_index"]),
            thought=data["thought"],
        )


@dataclass(frozen=True, kw_only=True)
class ToolExecutedEvent(DomainEvent):
    """
    Emitted when an AI agent completes execution of an external tool.
    """

    tool_name: str
    execution_time_ms: float
    status: str = "SUCCESS"

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "tool_name": self.tool_name,
                "execution_time_ms": self.execution_time_ms,
                "status": self.status,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolExecutedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            tool_name=data["tool_name"],
            execution_time_ms=float(data["execution_time_ms"]),
            status=data.get("status", "SUCCESS"),
        )
