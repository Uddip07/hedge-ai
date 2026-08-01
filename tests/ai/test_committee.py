"""
Unit and Integration tests for Intelligent Investment Committee Engine.

Tests Planner, Task Graph Engine, Scheduler, Critic, Judge, Committee Orchestration,
Investment Memory, Decision History, and Company Intelligence Integration.
"""

import unittest

from packages.ai.committee import (
    CommitteeCritic,
    CommitteeDecision,
    CommitteeJudge,
    CommitteePlanner,
    CommitteeScheduler,
    IntelligentInvestmentCommittee,
    InvestmentHorizon,
    InvestmentMemory,
    InvestmentStyle,
    ResearchRequest,
    ResearchTask,
    TaskGraphEngine,
    TaskGraphError,
)
from packages.domain.enums.ai import AgentType
from packages.domain.value_objects.identifiers.ticker import Ticker


class TestCommitteeEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker = Ticker("RELIANCE.NSE")
        self.planner = CommitteePlanner()
        self.scheduler = CommitteeScheduler()
        self.critic = CommitteeCritic()
        self.judge = CommitteeJudge()
        self.committee = IntelligentInvestmentCommittee()

    def test_planner_minimizes_agents_for_intraday(self) -> None:
        req = ResearchRequest(
            ticker=self.ticker,
            horizon=InvestmentHorizon.INTRADAY,
            style=InvestmentStyle.TECHNICAL,
        )
        plan, graph = self.planner.create_plan_and_graph(req)
        self.assertEqual(len(plan.required_agent_types), 2)
        self.assertIn(AgentType.QUANT, plan.required_agent_types)
        self.assertIn(AgentType.SENTIMENT, plan.required_agent_types)
        self.assertNotIn(AgentType.FUNDAMENTAL, plan.required_agent_types)

    def test_planner_minimizes_agents_for_long_term(self) -> None:
        req = ResearchRequest(
            ticker=self.ticker,
            horizon=InvestmentHorizon.LONG_TERM,
            style=InvestmentStyle.VALUE,
        )
        plan, graph = self.planner.create_plan_and_graph(req)
        self.assertEqual(len(plan.required_agent_types), 3)
        self.assertIn(AgentType.FUNDAMENTAL, plan.required_agent_types)
        self.assertIn(AgentType.MACRO, plan.required_agent_types)
        self.assertIn(AgentType.RISK, plan.required_agent_types)
        self.assertNotIn(AgentType.QUANT, plan.required_agent_types)

    def test_task_graph_topological_sort_and_cycle_detection(self) -> None:
        t1 = ResearchTask(task_id="t1", name="Task 1")
        t2 = ResearchTask(task_id="t2", name="Task 2", dependencies=["t1"])
        t3 = ResearchTask(task_id="t3", name="Task 3", dependencies=["t2"])

        graph = TaskGraphEngine.create_graph("g1", [t1, t2, t3])
        self.assertEqual(graph.execution_order, ["t1", "t2", "t3"])

        # Test cycle detection
        t_cycle_1 = ResearchTask(task_id="c1", name="C1", dependencies=["c2"])
        t_cycle_2 = ResearchTask(task_id="c2", name="C2", dependencies=["c1"])
        with self.assertRaises(TaskGraphError):
            TaskGraphEngine.create_graph("g_cycle", [t_cycle_1, t_cycle_2])

    def test_scheduler_executes_task_graph(self) -> None:
        t1 = ResearchTask(task_id="t1", name="Task 1")
        t2 = ResearchTask(task_id="t2", name="Task 2", dependencies=["t1"])
        graph = TaskGraphEngine.create_graph("g2", [t1, t2])

        def dummy_handler(t: ResearchTask) -> str:
            return f"Done {t.task_id}"

        results, metrics = self.scheduler.execute_graph(graph, dummy_handler)
        self.assertEqual(metrics.completed_tasks, 2)
        self.assertEqual(results["t1"], "Done t1")
        self.assertEqual(results["t2"], "Done t2")

    def test_end_to_end_committee_evaluation(self) -> None:
        decision, explanation = self.committee.evaluate_investment_request(
            ticker_symbol="INFY.NSE",
            horizon=InvestmentHorizon.LONG_TERM,
            style=InvestmentStyle.GROWTH,
        )

        self.assertIsInstance(decision, CommitteeDecision)
        self.assertEqual(decision.ticker.full_symbol, "INFY.NSE")
        self.assertGreater(decision.confidence, 0.0)
        self.assertIsNotNone(decision.judgement)
        self.assertGreater(len(decision.critiques), 0)
        self.assertIn("planning_process", explanation)
        self.assertIn("task_graph_execution", explanation)

    def test_investment_memory_and_outcome_update(self) -> None:
        memory = InvestmentMemory()
        from packages.ai.committee.models import MemoryEntry

        entry = MemoryEntry(
            entry_id="mem-101",
            session_id="sess-101",
            ticker="SBIN.NSE",
            decision_timestamp="2026-07-24T00:00:00Z",
            recommendation="BUY",
            confidence=0.85,
            evidence_summary=["ROCE expanding"],
            reasoning="Solid fundamentals",
        )
        memory.store_entry(entry)
        self.assertEqual(len(memory.search_by_ticker("SBIN.NSE")), 1)

        updated = memory.update_outcome("mem-101", "OUTPERFORMED", 0.95)
        self.assertEqual(updated.actual_outcome, "OUTPERFORMED")
        self.assertEqual(updated.accuracy_score, 0.95)

    def test_company_intelligence_committee_integration(self) -> None:
        from packages.application.company_intelligence import CompanyIntelligenceOrchestrator

        ci_orchestrator = CompanyIntelligenceOrchestrator()
        report = ci_orchestrator.analyze_company("RELIANCE.NSE")

        # Now evaluate committee analysis for the same ticker
        decision, explanation = self.committee.evaluate_investment_request(
            ticker_symbol="RELIANCE.NSE",
            horizon=InvestmentHorizon.LONG_TERM,
            style=InvestmentStyle.VALUE,
        )

        self.assertEqual(decision.ticker.full_symbol, report.ticker)
        self.assertGreater(decision.confidence, 0.0)
        self.assertIn("planning_process", explanation)


if __name__ == "__main__":
    unittest.main()
