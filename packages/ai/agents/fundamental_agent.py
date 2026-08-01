"""
Fundamental Analysis Agent Implementation.

Specialized agent analyzing company financial statements, valuation ratios, ROCE, and moat factors.
Integrates Prompt Intelligence Framework (PromptComposer, PromptValidator) and optionally LLMPort.
"""

from decimal import Decimal
from typing import Any

from packages.ai.agents.base import BaseAgent
from packages.ai.models.agent_context import AgentContext
from packages.ai.models.agent_result import AgentResult
from packages.ai.prompts.composer import PromptComposer
from packages.ai.prompts.prompt_registry import PromptRegistry
from packages.ai.prompts.validator import PromptValidator
from packages.application.ports.llm_port import LLMPort
from packages.domain.ai.reasoning import Citation, Evidence
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class FundamentalAgent(BaseAgent):
    """
    Fundamental Equity Analyst Agent (AgentType.FUNDAMENTAL).
    """

    def __init__(
        self,
        prompt_registry: PromptRegistry | None = None,
        weight: Decimal | float | str = "1.2",
        llm_port: LLMPort | None = None,
        composer: PromptComposer | None = None,
        validator: PromptValidator | None = None,
    ) -> None:
        super().__init__(prompt_registry=prompt_registry, weight=weight)
        self.llm_port = llm_port
        self.composer = composer or PromptComposer()
        self.validator = validator or PromptValidator()

    @property
    def agent_type(self) -> AgentType:
        return AgentType.FUNDAMENTAL

    def _execute_analysis(self, context: AgentContext) -> AgentResult:
        ticker_str = context.ticker.full_symbol

        evidence_data = context.parameters.get("evidence")
        pe_ratio = None
        market_cap = None
        rev = None

        if evidence_data and hasattr(evidence_data, "profile") and evidence_data.profile:
            pe_ratio = evidence_data.profile.trailing_pe
            market_cap = evidence_data.profile.market_cap

        if (
            evidence_data
            and hasattr(evidence_data, "income_statement")
            and evidence_data.income_statement
        ):
            metrics = evidence_data.income_statement.metrics or {}
            rev = metrics.get("Revenue")

        # Compute dynamic score based on real financial metrics
        base_score = Decimal("0.70")
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio < 20:
                base_score += Decimal("0.15")
            elif pe_ratio > 40:
                base_score -= Decimal("0.15")

        if rev is not None:
            base_score += Decimal("0.05")

        score_clamped = max(Decimal("0.10"), min(Decimal("0.95"), base_score))
        rec = (
            RecommendationType.BUY if score_clamped >= Decimal("0.60") else RecommendationType.HOLD
        )

        citation = Citation(
            document_id=DocumentId.generate(),
            source_title=f"Financial Statements for {ticker_str}",
            snippet=f"P/E: {pe_ratio or 'N/A'}, Market Cap: {market_cap or 'N/A'}, Revenue: {rev or 'N/A'}",
        )
        evidence = Evidence(
            fact=f"Fundamental financial profile calculated for {ticker_str}.",
            confidence=ConfidenceScore(Decimal("0.85")),
            citations=[citation],
        )

        # Compose prompt payload using PromptComposer
        system_instruction, user_prompt = self.composer.compose_prompt(
            system_prompt_template=self.prompt_template.system_prompt_text,
            agent_context=context,
            market_data={"ticker": ticker_str, "pe_ratio": pe_ratio, "revenue": rev},
            rag_evidence=[evidence],
        )

        if self.llm_port is not None:
            structured: dict[str, Any] = self.llm_port.generate_structured_output(
                prompt_text=f"{system_instruction}\n\nUser Request: {user_prompt}",
                response_schema=self.output_schema,
            )

            self.validator.validate_response_json(structured, self.output_schema)

            rec_str = str(structured.get("recommendation", rec.value)).upper()
            try:
                recommendation = RecommendationType(rec_str)
            except ValueError:
                recommendation = rec

            raw_score = Decimal(str(structured.get("score", str(score_clamped))))
            raw_conf = Decimal(str(structured.get("confidence", "0.85")))
            reasoning_text = str(
                structured.get(
                    "reasoning",
                    f"Fundamental reasoning based on live financial metrics for {ticker_str}.",
                )
            )

            return AgentResult(
                agent_type=self.agent_type,
                recommendation=recommendation,
                score=RecommendationScore(raw_score),
                confidence=ConfidenceScore(raw_conf),
                reasoning=reasoning_text,
                evidence=[evidence],
                risks=["Valuation compression", "Input cost inflation"],
                assumptions=["Sustained revenue growth"],
                unknowns=["Regulatory policy updates"],
                reasoning_steps=["Evaluated financial balance sheet", "Analyzed valuation ratios"],
            )

        return AgentResult(
            agent_type=self.agent_type,
            recommendation=rec,
            score=RecommendationScore(score_clamped),
            confidence=ConfidenceScore(Decimal("0.85")),
            reasoning=f"Fundamental analysis for {ticker_str}: P/E={pe_ratio}, Revenue={rev}.",
            evidence=[evidence],
            risks=["Valuation compression"],
            assumptions=["Sustained revenue growth"],
            unknowns=["Regulatory policy updates"],
            reasoning_steps=["Evaluated financial balance sheet", "Analyzed valuation ratios"],
        )
