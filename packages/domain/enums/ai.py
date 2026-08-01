"""
AI & Multi-Agent Swarm Enums for the Indian AI Hedge Fund Domain.

Defines LLM foundation model providers and specialized agent roles inside the
hedge fund multi-agent swarm architecture.
"""

from enum import StrEnum


class ModelProvider(StrEnum):
    """
    LLM and Foundation Model Provider services.
    """

    DEEPMIND = "DEEPMIND"
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    MISTRAL = "MISTRAL"
    LOCAL = "LOCAL"
    CUSTOM = "CUSTOM"

    def is_cloud(self) -> bool:
        """Return True if model execution relies on external cloud APIs."""
        return self in {
            ModelProvider.DEEPMIND,
            ModelProvider.OPENAI,
            ModelProvider.ANTHROPIC,
            ModelProvider.MISTRAL,
        }

    def is_local(self) -> bool:
        """Return True if model executes on local GPU/edge infrastructure."""
        return self == ModelProvider.LOCAL


class AgentType(StrEnum):
    """
    Specialized agent roles within the multi-agent hedge fund committee.
    """

    DIRECTOR = "DIRECTOR"
    QUANT = "QUANT"
    SENTIMENT = "SENTIMENT"
    RISK = "RISK"
    EXECUTION = "EXECUTION"
    FUNDAMENTAL = "FUNDAMENTAL"
    MACRO = "MACRO"
    PORTFOLIO_MANAGER = "PORTFOLIO_MANAGER"

    def is_orchestrator(self) -> bool:
        """Return True if the agent coordinates handoffs between other agents."""
        return self in {AgentType.DIRECTOR, AgentType.PORTFOLIO_MANAGER}

    def is_specialist(self) -> bool:
        """Return True if the agent performs domain-specific research or execution tasks."""
        return self in {
            AgentType.QUANT,
            AgentType.SENTIMENT,
            AgentType.RISK,
            AgentType.EXECUTION,
            AgentType.FUNDAMENTAL,
            AgentType.MACRO,
        }

    def default_role_description(self) -> str:
        """Return a human-readable role summary for prompt orchestration."""
        descriptions = {
            AgentType.DIRECTOR: "Swarm director overseeing task routing and executive summary synthesis.",
            AgentType.QUANT: "Quantitative analyst specializing in factor models, backtesting, and technical signals.",
            AgentType.SENTIMENT: "Sentiment analyst evaluating news streams, social sentiment, and SEC/SEBI filings.",
            AgentType.RISK: "Risk manager enforcing mandate compliance, stop losses, VaR limits, and circuit breakers.",
            AgentType.EXECUTION: "Execution specialist optimizing broker routing, slippage control, and order safety.",
            AgentType.FUNDAMENTAL: "Fundamental analyst parsing financial statements, balance sheets, and earnings calls.",
            AgentType.MACRO: "Macroeconomic analyst examining interest rates, RBI policy, inflation, and global trends.",
            AgentType.PORTFOLIO_MANAGER: "Portfolio manager making final allocation decisions based on committee consensus.",
        }
        return descriptions[self]
