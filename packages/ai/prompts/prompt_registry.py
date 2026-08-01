"""
Prompt Management System for AI Core Framework.

Central registry managing system prompt templates, file locations, output JSON schemas,
and metadata per AgentType without hardcoding prompts inside business logic.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.ai import AgentType


@dataclass(frozen=True)
class PromptTemplate:
    """
    Encapsulates prompt template metadata, system prompt location, and expected JSON output schema.

    Attributes:
        agent_type (AgentType): Target specialized agent role.
        system_prompt_location (str): Virtual or disk location path for system prompt file.
        system_prompt_text (str): System prompt template text.
        output_schema (dict[str, Any]): Expected structured output JSON schema.
        metadata (dict[str, Any]): Version release, author, and model compatibility metadata.
    """

    agent_type: AgentType
    system_prompt_location: str
    system_prompt_text: str
    output_schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render_system_prompt(self, **variables: Any) -> str:
        """Render system prompt template with runtime variables."""
        rendered = self.system_prompt_text
        for key, val in variables.items():
            rendered = rendered.replace(f"{{{key}}}", str(val))
        return rendered


class PromptRegistry:
    """
    Central Registry managing agent system prompt templates and output schemas.
    """

    def __init__(self) -> None:
        self._templates: dict[AgentType, PromptTemplate] = {}
        self._register_default_templates()

    def register(self, template: PromptTemplate) -> None:
        """Register or override a PromptTemplate."""
        self._templates[template.agent_type] = template

    def get_template(self, agent_type: AgentType) -> PromptTemplate:
        """Fetch PromptTemplate by AgentType."""
        if agent_type not in self._templates:
            raise KeyError(f"No PromptTemplate registered for AgentType '{agent_type.value}'.")
        return self._templates[agent_type]

    def _register_default_templates(self) -> None:
        """Initialize default system prompt templates for all core research agents."""
        # Fundamental Agent Template
        self.register(
            PromptTemplate(
                agent_type=AgentType.FUNDAMENTAL,
                system_prompt_location="prompts/system/fundamental_agent_v1.txt",
                system_prompt_text=(
                    "You are an Institutional Fundamental Equity Analyst for Indian markets. "
                    "Analyze balance sheets, earnings growth, P/E ratio, ROCE, and moat for {ticker}."
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
                metadata={"version": "1.0.0", "author": "HedgeFundAI"},
            )
        )

        # Technical Agent (Quant) Template
        self.register(
            PromptTemplate(
                agent_type=AgentType.QUANT,
                system_prompt_location="prompts/system/technical_agent_v1.txt",
                system_prompt_text=(
                    "You are a Quantitative Technical Analyst for Indian equities. "
                    "Analyze momentum indicators, RSI, MACD, volume trends, and moving averages for {ticker}."
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
                metadata={"version": "1.0.0", "author": "HedgeFundAI"},
            )
        )

        # News & Sentiment Agent Template
        self.register(
            PromptTemplate(
                agent_type=AgentType.SENTIMENT,
                system_prompt_location="prompts/system/news_agent_v1.txt",
                system_prompt_text=(
                    "You are a News and Corporate Announcement Sentiment Analyst for Indian markets. "
                    "Evaluate SEBI disclosures, news streams, and market sentiment for {ticker}."
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
                metadata={"version": "1.0.0", "author": "HedgeFundAI"},
            )
        )

        # Risk Management Agent Template
        self.register(
            PromptTemplate(
                agent_type=AgentType.RISK,
                system_prompt_location="prompts/system/risk_agent_v1.txt",
                system_prompt_text=(
                    "You are an Institutional Risk Manager enforcing mandate limits, stop-loss rules, "
                    "volatility bounds, and circuit breaker compliance for {ticker}."
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
                metadata={"version": "1.0.0", "author": "HedgeFundAI"},
            )
        )

        # Macroeconomic Agent Template
        self.register(
            PromptTemplate(
                agent_type=AgentType.MACRO,
                system_prompt_location="prompts/system/macro_agent_v1.txt",
                system_prompt_text=(
                    "You are a Macroeconomic Strategist parsing RBI interest rate policies, CPI inflation, "
                    "GDP trends, and USD/INR forex dynamics affecting {ticker}."
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendation": {"type": "string"},
                        "score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
                metadata={"version": "1.0.0", "author": "HedgeFundAI"},
            )
        )
