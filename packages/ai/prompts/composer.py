"""
Prompt Composer for Prompt Intelligence Framework.

Combines System Prompt, Agent Context, RAG Evidence, Market Data, and User Request into finalized prompt payloads.
"""

from typing import Any

from packages.ai.models.agent_context import AgentContext
from packages.ai.prompts.context_builder import ContextBuilder
from packages.ai.prompts.token_budget import TokenBudgetManager
from packages.ai.prompts.validator import PromptValidator


class PromptComposer:
    """
    Composer combining system prompts, context parameters, market data, and RAG evidence.
    """

    def __init__(
        self,
        context_builder: ContextBuilder | None = None,
        token_budget_manager: TokenBudgetManager | None = None,
        validator: PromptValidator | None = None,
    ) -> None:
        self.context_builder = context_builder or ContextBuilder()
        self.token_budget_manager = token_budget_manager or TokenBudgetManager()
        self.validator = validator or PromptValidator()

    def compose_prompt(
        self,
        system_prompt_template: str,
        agent_context: AgentContext,
        market_data: Any | None = None,
        rag_evidence: list[Any] | None = None,
        user_request: str | None = None,
        max_evidence_tokens: int = 1000,
    ) -> tuple[str, str]:
        """
        Compose final (system_instruction, user_prompt) text tuple for model execution.

        Args:
            system_prompt_template (str): Raw system prompt template text with placeholders.
            agent_context (AgentContext): Context execution environment.
            market_data (Any | None): Market quote object or dict.
            rag_evidence (list[Any] | None): Un-trimmed list of RAG evidence items.
            user_request (str | None): Optional user directive string.
            max_evidence_tokens (int): Max token budget allocated to RAG evidence text.

        Returns:
            tuple[str, str]: (rendered_system_instruction, final_user_prompt)
        """
        # 1. Trim RAG evidence context to fit token budget (preserving highest-ranked items)
        trimmed_evidence = self.token_budget_manager.trim_evidence_context(
            evidence_items=rag_evidence or [],
            max_tokens=max_evidence_tokens,
        )

        # 2. Build full context variable dictionary map
        vars_map = self.context_builder.build_full_context(
            agent_context=agent_context,
            market_data=market_data,
            rag_evidence=trimmed_evidence,
            user_request=user_request,
        )

        # 3. Substitute placeholders into system prompt template
        rendered_system = system_prompt_template
        for key, val in vars_map.items():
            rendered_system = rendered_system.replace(f"{{{key}}}", val)

        user_prompt = vars_map["user_request"]

        return rendered_system, user_prompt
