"""
Consensus Engine Orchestrator for Consensus Intelligence Engine.

Simulates an institutional investment committee by aggregating agent results, applying weights,
detecting conflicts, compiling evidence, computing agreement & confidence scores, generating
structured explanations, reasoning graphs, and audit records.
"""

from decimal import Decimal
from typing import Any

from packages.ai.consensus.audit import AuditRecorder
from packages.ai.consensus.confidence import ConfidenceEngine, EvidenceAggregator
from packages.ai.consensus.conflicts import ConflictDetector
from packages.ai.consensus.explanation import DecisionExplainer
from packages.ai.consensus.models import ConsensusIntelligenceDecision
from packages.ai.consensus.weighting import WeightedConsensusStrategy
from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.research import RecommendationType
from packages.domain.research.consensus import (
    AgentOpinion,
    AgentVote,
    ConsensusDecision,
)
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class ConsensusEngine:
    """
    Institutional Investment Committee Consensus Intelligence Engine.
    """

    def __init__(
        self,
        weighting_strategy: WeightedConsensusStrategy | None = None,
        conflict_detector: ConflictDetector | None = None,
        confidence_engine: ConfidenceEngine | None = None,
        evidence_aggregator: EvidenceAggregator | None = None,
        explainer: DecisionExplainer | None = None,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self.weighting_strategy = weighting_strategy or WeightedConsensusStrategy()
        self.conflict_detector = conflict_detector or ConflictDetector()
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.evidence_aggregator = evidence_aggregator or EvidenceAggregator()
        self.explainer = explainer or DecisionExplainer()
        self.audit_recorder = audit_recorder or AuditRecorder()

    def evaluate_committee_decision(
        self,
        results: list[AgentResult],
        session_id: str = "default-session",
        weights_override: dict[str, Decimal | float | str] | None = None,
    ) -> ConsensusIntelligenceDecision:
        """
        Execute full consensus intelligence pipeline for a multi-agent investment committee.

        Steps:
            1. Aggregate all AgentResult items & apply agent weights
            2. Detect conflicting recommendations & assumptions
            3. Aggregate & deduplicate evidence
            4. Compute agreement score & penalized composite confidence score
            5. Generate structured explanation payload (no free-form unformatted text)
            6. Build reasoning graph
            7. Generate cryptographically signed audit record

        Returns:
            ConsensusIntelligenceDecision: Output consensus payload.
        """
        if not results:
            empty_rec = RecommendationScore(Decimal("0.0"))
            empty_conf = ConfidenceScore(Decimal("0.50"))
            empty_explanation = self.explainer.explain(RecommendationType.HOLD, [], [])
            empty_graph = self.audit_recorder.build_reasoning_graph([], RecommendationType.HOLD)
            empty_audit = self.audit_recorder.record_audit(
                session_id=session_id,
                results=[],
                applied_weights={},
                conflict_count=0,
                final_recommendation=RecommendationType.HOLD,
                consensus_score=0.0,
                confidence_score=0.50,
                agreement_score=0.0,
            )
            return ConsensusIntelligenceDecision(
                recommendation=RecommendationType.HOLD,
                score=empty_rec,
                confidence=empty_conf,
                agreement_score=0.0,
                evidence=[],
                conflicts=[],
                explanation=empty_explanation,
                reasoning_graph=empty_graph,
                audit_record=empty_audit,
            )

        # 1. Apply weighting & compute score, recommendation direction, agreement ratio
        (
            rec_score,
            winning_rec,
            agreement_ratio,
            applied_weights,
        ) = self.weighting_strategy.compute_weighted_score(results, weights_override)

        # 2. Detect conflicting recommendations, assumptions, missing evidence, low confidence
        conflicts = self.conflict_detector.detect_conflicts(results)

        # 3. Aggregate evidence
        evidence_list = self.evidence_aggregator.aggregate_evidence(results)

        # 4. Compute composite confidence score
        composite_confidence = self.confidence_engine.compute_composite_confidence(
            results=results,
            conflicts=conflicts,
            applied_weights=applied_weights,
        )

        # 5. Generate structured explanation
        explanation = self.explainer.explain(
            recommendation=winning_rec,
            results=results,
            conflicts=conflicts,
        )

        # 6. Generate reasoning graph
        reasoning_graph = self.audit_recorder.build_reasoning_graph(
            results=results,
            winning_rec=winning_rec,
        )

        # 7. Generate audit record
        audit_record = self.audit_recorder.record_audit(
            session_id=session_id,
            results=results,
            applied_weights=applied_weights,
            conflict_count=len(conflicts),
            final_recommendation=winning_rec,
            consensus_score=float(rec_score.value),
            confidence_score=float(composite_confidence.value),
            agreement_score=agreement_ratio,
        )

        return ConsensusIntelligenceDecision(
            recommendation=winning_rec,
            score=rec_score,
            confidence=composite_confidence,
            agreement_score=agreement_ratio,
            evidence=evidence_list,
            conflicts=conflicts,
            explanation=explanation,
            reasoning_graph=reasoning_graph,
            audit_record=audit_record,
        )

    def compute_consensus(
        self,
        results: list[AgentResult],
        agent_weights: dict[str, Any] | None = None,
    ) -> ConsensusDecision:
        """
        Backward-compatible method returning domain ConsensusDecision entity.
        """
        if not results:
            return ConsensusDecision(
                opinions=[],
                votes=[],
                consensus_score=RecommendationScore(Decimal("0.0")),
                confidence=ConfidenceScore(Decimal("0.5")),
                summary="No agent results provided for consensus calculation.",
            )

        intel = self.evaluate_committee_decision(
            results=results,
            weights_override=agent_weights,
        )

        opinions: list[AgentOpinion] = []
        votes: list[AgentVote] = []

        weights = agent_weights or {}

        for res in results:
            w_val = weights.get(res.agent_type.value, Decimal("1.0"))
            w = Decimal(str(w_val))
            opinions.append(
                AgentOpinion(
                    agent_type=res.agent_type,
                    recommendation=res.recommendation,
                    reasoning=res.reasoning,
                    confidence=res.confidence,
                    supporting_evidence=[e.fact for e in res.evidence],
                )
            )
            votes.append(
                AgentVote(
                    agent_type=res.agent_type,
                    recommendation=res.recommendation,
                    weight=w,
                )
            )

        summary = (
            f"Committee Consensus: {intel.recommendation.value} (Score: {intel.score.value}, "
            f"Confidence: {intel.confidence.value}, Agreement: {round(intel.agreement_score * 100, 1)}%)."
        )

        return ConsensusDecision(
            opinions=opinions,
            votes=votes,
            consensus_score=intel.score,
            confidence=intel.confidence,
            summary=summary,
        )
