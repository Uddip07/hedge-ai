"""
Committee Orchestrator Implementation.

Main reasoning orchestrator connecting Planner, TaskGraph, Scheduler, Specialist Agents,
Critic, Judge, ConsensusEngine, and InvestmentMemory.
"""

import uuid
from typing import Any

from packages.ai.agents.fundamental_agent import FundamentalAgent
from packages.ai.agents.macro_agent import MacroAgent
from packages.ai.agents.news_agent import NewsAgent
from packages.ai.agents.risk_agent import RiskAgent
from packages.ai.agents.technical_agent import TechnicalAgent
from packages.ai.committee.critic import CommitteeCritic
from packages.ai.committee.exceptions import CommitteeError
from packages.ai.committee.explanation import CommitteeExplainer
from packages.ai.committee.judge import CommitteeJudge
from packages.ai.committee.memory import InvestmentMemory
from packages.ai.committee.models import (
    CommitteeDecision,
    MemoryEntry,
    ResearchRequest,
    ResearchTask,
)
from packages.ai.committee.planner import CommitteePlanner
from packages.ai.committee.scheduler import CommitteeScheduler
from packages.ai.consensus.engine import ConsensusEngine
from packages.ai.models.agent_context import AgentContext
from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.value_objects.temporal.timestamps import Timestamp


class CommitteeOrchestrator:
    """
    Orchestration engine coordinating the complete Intelligent Investment Committee reasoning lifecycle.
    """

    def __init__(
        self,
        planner: CommitteePlanner | None = None,
        scheduler: CommitteeScheduler | None = None,
        critic: CommitteeCritic | None = None,
        judge: CommitteeJudge | None = None,
        consensus_engine: ConsensusEngine | None = None,
        memory: InvestmentMemory | None = None,
        explainer: CommitteeExplainer | None = None,
    ) -> None:
        self.planner = planner or CommitteePlanner()
        self.scheduler = scheduler or CommitteeScheduler()
        self.critic = critic or CommitteeCritic()
        self.judge = judge or CommitteeJudge()
        self.consensus_engine = consensus_engine or ConsensusEngine()
        self.memory = memory or InvestmentMemory()
        self.explainer = explainer or CommitteeExplainer()

        # Initialize specialist agent instances
        self.agents = {
            AgentType.FUNDAMENTAL: FundamentalAgent(),
            AgentType.QUANT: TechnicalAgent(),
            AgentType.SENTIMENT: NewsAgent(),
            AgentType.MACRO: MacroAgent(),
            AgentType.RISK: RiskAgent(),
        }

    def execute_committee_analysis(
        self, request: ResearchRequest
    ) -> tuple[CommitteeDecision, dict[str, Any]]:
        """
        Execute full end-to-end committee reasoning workflow for a ResearchRequest.

        Args:
            request (ResearchRequest): User research request.

        Returns:
            tuple[CommitteeDecision, dict[str, Any]]: Committee decision aggregate and explanation.
        """
        try:
            # 1. Planner generates ResearchPlan and TaskGraph
            plan, graph = self.planner.create_plan_and_graph(request)

            from packages.ai.evidence.evidence_builder import InvestmentEvidenceBuilder

            evidence_builder = InvestmentEvidenceBuilder()
            evidence = evidence_builder.build_evidence(request.ticker)

            # Context for agent execution with real live market evidence
            agent_ctx = AgentContext(
                ticker=request.ticker,
                session_id=request.session_id,
                parameters={"evidence": evidence},
            )

            agent_results: list[AgentResult] = []

            # Task handler callback for TaskGraph execution
            def handle_task(task: ResearchTask) -> Any:
                if task.agent_type and task.agent_type in self.agents:
                    agent = self.agents[task.agent_type]
                    res = agent.analyze(agent_ctx)
                    agent_results.append(res)
                    return res
                return {"status": "SUCCESS", "task_id": task.task_id}

            # 2. Scheduler executes TaskGraph
            task_results, metrics = self.scheduler.execute_graph(
                graph=graph,
                task_handler=handle_task,
                session_id=request.session_id,
            )

            # 3. Critic evaluates agent results for contradictions and weaknesses
            critiques = self.critic.generate_critiques(agent_results)

            # 4. Judge synthesizes evidence quality and source coverage
            judgement = self.judge.evaluate_judgement(agent_results, critiques)

            # 5. Reuse ConsensusEngine to evaluate committee decision
            consensus_intel = self.consensus_engine.evaluate_committee_decision(
                results=agent_results,
                session_id=request.session_id,
            )

            # 6. Build CommitteeDecision payload
            dec_id = f"dec-{uuid.uuid4().hex[:8]}"
            decision = CommitteeDecision(
                decision_id=dec_id,
                session_id=request.session_id,
                ticker=request.ticker,
                winning_recommendation=consensus_intel.recommendation,
                consensus_score=float(consensus_intel.score.value),
                confidence=judgement.overall_confidence,
                agreement_ratio=consensus_intel.agreement_score,
                judgement=judgement,
                critiques=critiques,
                agent_results=agent_results,
                audit_signature=consensus_intel.audit_record.hash_signature,
                timestamp=Timestamp.now_utc(),
            )

            # 7. Generate structured explanation
            explanation = self.explainer.generate_explanation(
                plan=plan,
                graph=graph,
                agent_results=agent_results,
                critiques=critiques,
                judgement=judgement,
                consensus_decision=consensus_intel,
            )

            # 8. Store reasoning into persistent InvestmentMemory
            mem_entry = MemoryEntry(
                entry_id=f"mem-{dec_id}",
                session_id=request.session_id,
                ticker=request.ticker.full_symbol,
                decision_timestamp=decision.timestamp.isoformat(),
                recommendation=decision.winning_recommendation.value,
                confidence=decision.confidence,
                evidence_summary=[e.fact for res in agent_results for e in res.evidence],
                reasoning=str(explanation.get("consensus_summary", "")),
            )
            self.memory.store_entry(mem_entry)

            return decision, explanation
        except Exception as err:
            raise CommitteeError(
                f"Committee orchestration failed for '{request.ticker.full_symbol}': {err}",
                details={"ticker": request.ticker.full_symbol},
            ) from err
