"""
Reasoning Engine for AI Core Framework.

Constructs chain-of-thought traces, evidence aggregations, and citations for multi-agent reasoning.
"""

from decimal import Decimal

from packages.domain.ai.reasoning import Citation, Evidence, ReasoningTrace
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.domain.value_objects.metrics.scores import ConfidenceScore


class ReasoningEngine:
    """
    Engine managing agent chain-of-thought traces and evidence compilation.
    """

    def create_citation(
        self,
        source_title: str,
        snippet: str,
        document_id: DocumentId | None = None,
        page_number: int | None = None,
    ) -> Citation:
        """Construct a Citation instance."""
        doc_id = document_id or DocumentId.generate()
        return Citation(
            document_id=doc_id,
            source_title=source_title,
            snippet=snippet,
            page_number=page_number,
        )

    def create_evidence(
        self,
        fact: str,
        confidence: ConfidenceScore | float | Decimal = Decimal("0.80"),
        citations: list[Citation] | None = None,
    ) -> Evidence:
        """Construct an Evidence instance."""
        conf = (
            confidence
            if isinstance(confidence, ConfidenceScore)
            else ConfidenceScore(Decimal(str(confidence)))
        )
        return Evidence(
            fact=fact,
            confidence=conf,
            citations=citations or [],
        )

    def build_trace(
        self,
        thought_steps: list[str],
        evidence_list: list[Evidence] | None = None,
    ) -> ReasoningTrace:
        """Build a single-step ReasoningTrace summary from thought steps."""
        combined_thought = " -> ".join(thought_steps)
        return ReasoningTrace(
            step_index=1,
            thought=combined_thought,
            evidence=evidence_list or [],
        )
