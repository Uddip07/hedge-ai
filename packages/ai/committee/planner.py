"""
Committee Planner Implementation.

Interprets user research requests, determines investment horizon and style, selects required
evidence and necessary specialist agents, and produces an optimized TaskGraph.
Minimizes unnecessary agent execution.
"""

import uuid

from packages.ai.committee.exceptions import PlanningError
from packages.ai.committee.models import (
    InvestmentHorizon,
    ResearchPlan,
    ResearchRequest,
    ResearchTask,
    TaskGraph,
)
from packages.ai.committee.task_graph import TaskGraphEngine
from packages.domain.enums.ai import AgentType


class CommitteePlanner:
    """
    Intelligent planner constructing optimized execution task graphs based on investment intent.
    """

    def create_plan_and_graph(self, request: ResearchRequest) -> tuple[ResearchPlan, TaskGraph]:
        """
        Parse ResearchRequest, create ResearchPlan, and build executable TaskGraph.

        Args:
            request (ResearchRequest): User investment research request payload.

        Returns:
            tuple[ResearchPlan, TaskGraph]: Generated research plan and task graph.
        """
        try:
            horizon = request.horizon
            style = request.style
            query = request.user_query.upper()

            # 1. Determine necessary agent types and evidence requirements based on horizon & style
            required_agents: list[AgentType] = []
            required_evidence: list[str] = []

            if horizon == InvestmentHorizon.INTRADAY:
                # Intraday requires Technical (QUANT) and News (SENTIMENT) agents only; no long-term fundamental analysis
                required_agents = [AgentType.QUANT, AgentType.SENTIMENT]
                required_evidence = ["REALTIME_QUOTES", "INTRADAY_BARS", "BREAKING_NEWS"]
            elif horizon == InvestmentHorizon.LONG_TERM:
                # Long term requires Fundamental, Macro, and Risk agents; no intraday bars
                required_agents = [AgentType.FUNDAMENTAL, AgentType.MACRO, AgentType.RISK]
                required_evidence = ["ANNUAL_REPORTS", "QUARTERLY_RESULTS", "MACRO_INDICATORS"]
            else:
                # SWING / DAILY / BALANCED requires all 5 committee agents
                required_agents = [
                    AgentType.FUNDAMENTAL,
                    AgentType.QUANT,
                    AgentType.SENTIMENT,
                    AgentType.MACRO,
                    AgentType.RISK,
                ]
                required_evidence = [
                    "QUOTES",
                    "FINANCIAL_STATEMENTS",
                    "NEWS_SENTIMENT",
                    "MACRO_SERIES",
                    "FILINGS",
                ]

            plan_id = f"plan-{uuid.uuid4().hex[:8]}"
            plan = ResearchPlan(
                plan_id=plan_id,
                session_id=request.session_id,
                ticker=request.ticker,
                horizon=horizon,
                style=style,
                required_agent_types=required_agents,
                required_evidence_types=required_evidence,
                estimated_duration_ms=float(len(required_agents) * 150),
            )

            # 2. Build DAG Tasks: Data Stage -> Agent Stage -> Critic/Judge Stage
            graph_id = f"graph-{uuid.uuid4().hex[:8]}"
            tasks: list[ResearchTask] = []

            # Stage 0: Data & Evidence Retrieval
            data_task_id = "task-data-retrieval"
            tasks.append(
                ResearchTask(
                    task_id=data_task_id,
                    name="Retrieve Market Data & RAG Evidence",
                    priority=10,
                )
            )

            # Stage 1: Specialist Agent Tasks (depend on data_task_id)
            agent_task_ids: list[str] = []
            for agent_type in required_agents:
                tid = f"task-agent-{agent_type.value.lower()}"
                agent_task_ids.append(tid)
                tasks.append(
                    ResearchTask(
                        task_id=tid,
                        name=f"Execute {agent_type.value} Agent Analysis",
                        agent_type=agent_type,
                        dependencies=[data_task_id],
                        priority=5,
                    )
                )

            # Stage 2: Critic Evaluation (depends on all agent tasks)
            critic_task_id = "task-critic-eval"
            tasks.append(
                ResearchTask(
                    task_id=critic_task_id,
                    name="Run Committee Critic Evaluation",
                    dependencies=list(agent_task_ids),
                    priority=3,
                )
            )

            # Stage 3: Judge Synthesis (depends on critic evaluation)
            judge_task_id = "task-judge-eval"
            tasks.append(
                ResearchTask(
                    task_id=judge_task_id,
                    name="Run Committee Judge Synthesis",
                    dependencies=[critic_task_id],
                    priority=2,
                )
            )

            graph = TaskGraphEngine.create_graph(graph_id=graph_id, tasks=tasks)
            return plan, graph
        except Exception as err:
            raise PlanningError(
                f"Failed to plan research request for '{request.ticker.full_symbol}': {err}",
                details={"ticker": request.ticker.full_symbol},
            ) from err
