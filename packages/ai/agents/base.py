"""
Base Agent Abstraction for AI Core Framework.

Defines the abstract BaseAgent interface enforcing provider-agnostic execution, prompt registry lookup,
and structured AgentResult responses.
"""

import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from packages.ai.models.agent_context import AgentContext
from packages.ai.models.agent_result import AgentResult
from packages.ai.prompts.prompt_registry import PromptRegistry, PromptTemplate
from packages.domain.enums.ai import AgentType


class BaseAgent(ABC):
    """
    Abstract Base Class for all specialized AI research agents.

    Attributes:
        prompt_registry (PromptRegistry): Central prompt template registry.
        weight (Decimal): Committee voting weight.
    """

    def __init__(
        self,
        prompt_registry: PromptRegistry | None = None,
        weight: Decimal | float | str = "1.0",
    ) -> None:
        self.prompt_registry = prompt_registry or PromptRegistry()
        self.weight = Decimal(str(weight))

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return specialized AgentType enum value."""

    @property
    def prompt_template(self) -> PromptTemplate:
        """Retrieve registered PromptTemplate for this agent."""
        return self.prompt_registry.get_template(self.agent_type)

    @property
    def system_prompt_location(self) -> str:
        """Return location path of system prompt file."""
        return self.prompt_template.system_prompt_location

    @property
    def output_schema(self) -> dict[str, Any]:
        """Return expected JSON output schema."""
        return self.prompt_template.output_schema

    @property
    def metadata(self) -> dict[str, Any]:
        """Return prompt template metadata."""
        return self.prompt_template.metadata

    @abstractmethod
    def _execute_analysis(self, context: AgentContext) -> AgentResult:
        """Internal analysis implementation overridden by specialized agents."""

    def analyze(self, context: AgentContext) -> AgentResult:
        """
        Public execution entrypoint timing processing duration.

        Args:
            context (AgentContext): Execution context parameters.

        Returns:
            AgentResult: Analysis output payload.
        """
        start_time = time.perf_counter()
        result = self._execute_analysis(context)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AgentResult(
            agent_type=result.agent_type,
            recommendation=result.recommendation,
            score=result.score,
            confidence=result.confidence,
            reasoning=result.reasoning,
            evidence=result.evidence,
            reasoning_trace=result.reasoning_trace,
            execution_time_ms=round(elapsed_ms, 2),
        )
