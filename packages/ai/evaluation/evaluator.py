"""
Agent Evaluator for AI Core Framework.

Evaluates agent reasoning quality, confidence calibration, and output schema compliance.
"""

from typing import Any

from packages.ai.models.agent_result import AgentResult
from packages.domain.research.consensus import ConsensusDecision


class AgentEvaluator:
    """
    Evaluator assessing research agent accuracy and compliance.
    """

    def evaluate_result(self, result: AgentResult) -> dict[str, Any]:
        """
        Evaluate a single AgentResult payload.

        Returns:
            dict[str, Any]: Evaluation report.
        """
        is_valid_score = -1.0 <= float(result.score.value) <= 1.0
        is_valid_confidence = 0.0 <= float(result.confidence.value) <= 1.0
        has_reasoning = bool(result.reasoning and result.reasoning.strip())

        return {
            "agent_type": result.agent_type.value,
            "is_valid_score": is_valid_score,
            "is_valid_confidence": is_valid_confidence,
            "has_reasoning": has_reasoning,
            "evidence_count": len(result.evidence),
            "is_compliant": is_valid_score and is_valid_confidence and has_reasoning,
        }

    def evaluate_consensus(self, consensus: ConsensusDecision) -> dict[str, Any]:
        """
        Evaluate a ConsensusDecision payload.

        Returns:
            dict[str, Any]: Evaluation report.
        """
        return {
            "opinions_count": len(consensus.opinions),
            "votes_count": len(consensus.votes),
            "consensus_score": float(consensus.consensus_score.value),
            "confidence": float(consensus.confidence.value),
            "is_valid": len(consensus.opinions) > 0,
        }
