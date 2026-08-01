"""
Agent Orchestrator for AI Core Framework.

Coordinates multi-agent swarm execution, session memory persistence, and committee consensus synthesis.
"""

from typing import Any

from packages.ai.agents.base import BaseAgent
from packages.ai.agents.fundamental_agent import FundamentalAgent
from packages.ai.agents.macro_agent import MacroAgent
from packages.ai.agents.news_agent import NewsAgent
from packages.ai.agents.risk_agent import RiskAgent
from packages.ai.agents.technical_agent import TechnicalAgent
from packages.ai.consensus.consensus_engine import ConsensusEngine
from packages.ai.memory.conversation_store import ConversationStore
from packages.ai.models.agent_context import AgentContext
from packages.ai.models.agent_result import AgentResult
from packages.domain.research.consensus import ConsensusDecision


class AgentOrchestrator:
    """
    Orchestrator managing multi-agent research swarm execution.
    """

    def __init__(
        self,
        agents: list[BaseAgent] | None = None,
        consensus_engine: ConsensusEngine | None = None,
        memory_store: ConversationStore | None = None,
    ) -> None:
        self.consensus_engine = consensus_engine or ConsensusEngine()
        self.memory_store = memory_store or ConversationStore()

        if agents is not None:
            self.agents = agents
        else:
            self.agents = [
                FundamentalAgent(),
                TechnicalAgent(),
                NewsAgent(),
                RiskAgent(),
                MacroAgent(),
            ]

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new research agent."""
        self.agents.append(agent)

    def run_analysis(self, context: AgentContext) -> tuple[ConsensusDecision, list[AgentResult]]:
        """
        Execute multi-agent research workflow across all registered committee agents.

        Args:
            context (AgentContext): Analysis target context parameters.

        Returns:
            tuple[ConsensusDecision, list[AgentResult]]: Consensus decision and raw agent results.
        """
        results: list[AgentResult] = []
        agent_weights: dict[str, Any] = {}

        for agent in self.agents:
            res = agent.analyze(context)
            results.append(res)
            agent_weights[agent.agent_type.value] = agent.weight

        # Compute weighted consensus decision
        consensus = self.consensus_engine.compute_consensus(
            results=results,
            agent_weights=agent_weights,
        )

        # Store in session memory
        self.memory_store.save_agent_results(context.session_id, results)
        self.memory_store.save_consensus(context.session_id, consensus)
        self.memory_store.add_message(
            context.session_id,
            role="system",
            content=f"Analysis completed for {context.ticker.full_symbol} with score {consensus.consensus_score.value}.",
        )

        return consensus, results
