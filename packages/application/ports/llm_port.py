"""
LLM Port Interface for the Application Layer.

Defines outbound port contracts for invoking Large Language Models, prompt orchestration,
and structured multi-agent reasoning generation.
"""

from abc import ABC, abstractmethod
from typing import Any

from packages.domain.ai.prompt import Prompt
from packages.domain.ai.reasoning import ModelResponse


class LLMPort(ABC):
    """
    Abstract Outbound Port for Large Language Model (LLM) Provider Adapters.
    """

    @abstractmethod
    def generate_response(self, prompt: Prompt) -> ModelResponse:
        """
        Execute an AI prompt against the configured LLM provider and return a typed response.

        Args:
            prompt (Prompt): Prompt aggregate root specifying inputs and parameters.

        Returns:
            ModelResponse: Model execution result entity.
        """

    @abstractmethod
    def generate_structured_output(
        self,
        prompt_text: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate a strictly schema-validated JSON output structure from an LLM.

        Args:
            prompt_text (str): Raw input prompt text.
            response_schema (dict[str, Any]): Expected JSON schema definition.

        Returns:
            dict[str, Any]: Parsed JSON data conforming to response_schema.
        """
