"""
Unit tests for Prompt Aggregate Root and child AI models (ReasoningChain, Evidence, Citations, ToolInvocations, ModelResponses).
"""

import unittest
from decimal import Decimal

from packages.domain.ai import (
    AgentDecision,
    Citation,
    Evidence,
    ModelResponse,
    Prompt,
    PromptExecution,
    PromptVersion,
    ReasoningChain,
    ReasoningTrace,
    ToolInvocation,
)
from packages.domain.enums.ai import AgentType, ModelProvider
from packages.domain.value_objects.identifiers import DocumentId
from packages.domain.value_objects.metrics import ConfidenceScore


class TestAIDomain(unittest.TestCase):
    """Test suite for Prompt Aggregate Root and AI domain models."""

    def test_citation_and_evidence_serialization(self):
        doc_id = DocumentId.generate()
        cit = Citation(
            document_id=doc_id,
            source_title="SEBI Master Circular for Algos",
            snippet="Risk checks mandatory for algorithmic order execution.",
            page_number=12,
        )

        ev = Evidence(
            fact="SEBI mandates pre-trade risk checks for algorithmic orders.",
            confidence=ConfidenceScore(Decimal("0.95")),
            citations=[cit],
        )

        ev_dict = ev.to_dict()
        restored = Evidence.from_dict(ev_dict)
        self.assertEqual(restored.fact, ev.fact)
        self.assertEqual(len(restored.citations), 1)
        self.assertEqual(restored.citations[0].source_title, "SEBI Master Circular for Algos")

    def test_model_response_and_tool_invocation(self):
        resp = ModelResponse(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet",
            content="Analysis complete.",
            prompt_tokens=150,
            completion_tokens=50,
            latency_ms=450.0,
        )
        self.assertEqual(resp.total_tokens, 200)

        tool = ToolInvocation(
            tool_name="calculate_sharpe_ratio",
            arguments={"returns": [0.01, 0.02]},
            result=1.85,
            execution_time_ms=12.5,
        )

        decision = AgentDecision(
            action="APPROVE_ALLOCATION",
            confidence=ConfidenceScore(Decimal("0.90")),
            rationale="Sharpe ratio exceeds threshold.",
            tools_used=[tool],
        )

        trace = ReasoningTrace(
            step_index=1,
            thought="Step 1: Calculate risk-adjusted performance.",
            tool_invocations=[tool],
        )
        chain = ReasoningChain(traces=[trace], final_decision=decision)

        chain_dict = chain.to_dict()
        restored_chain = ReasoningChain.from_dict(chain_dict)
        self.assertEqual(len(restored_chain.traces), 1)
        assert restored_chain.final_decision is not None
        self.assertEqual(restored_chain.final_decision.action, "APPROVE_ALLOCATION")

    def test_prompt_aggregate_root_workflow(self):
        prompt = Prompt(
            name="Fundamental Valuation Analyst Prompt", agent_type=AgentType.FUNDAMENTAL
        )

        pv1 = PromptVersion(
            version_number="1.0.0",
            template="Analyze company {ticker} with P/E ratio {pe_ratio}.",
            variables=["ticker", "pe_ratio"],
            changelog="Initial release.",
        )
        prompt.add_version(pv1)
        self.assertEqual(prompt.get_latest_version(), pv1)

        # Test render
        rendered = pv1.render({"ticker": "RELIANCE.NSE", "pe_ratio": "22.5"})
        self.assertIn("RELIANCE.NSE", rendered)

        # Record execution telemetry
        resp = ModelResponse(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            content="Company RELIANCE is reasonably valued.",
            prompt_tokens=100,
            completion_tokens=20,
        )

        exec_telemetry = PromptExecution(
            model_provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            input_variables={"ticker": "RELIANCE.NSE", "pe_ratio": "22.5"},
            response=resp,
        )
        prompt.record_execution(exec_telemetry)
        self.assertEqual(len(prompt.executions), 1)

        # Dict roundtrip
        prompt_dict = prompt.to_dict()
        restored = Prompt.from_dict(prompt_dict)
        self.assertEqual(restored.name, "Fundamental Valuation Analyst Prompt")
        self.assertEqual(len(restored.versions), 1)
        self.assertEqual(len(restored.executions), 1)


if __name__ == "__main__":
    unittest.main()
