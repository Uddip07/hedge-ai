"""
Intelligent Investment Committee Router.

Provides POST /committee/evaluate endpoint for triggering multi-agent committee evaluation.
"""

from fastapi import APIRouter, Depends, status

from packages.ai.committee import (
    IntelligentInvestmentCommittee,
    InvestmentHorizon,
    InvestmentStyle,
)
from packages.api.dependencies import get_investment_committee
from packages.api.schemas.request import EvaluateCommitteeRequest
from packages.api.schemas.response import EvaluateCommitteeResponse

router = APIRouter(prefix="/committee", tags=["Intelligent Investment Committee"])


@router.post(
    "/evaluate",
    response_model=EvaluateCommitteeResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Committee Decision",
    description="Trigger Planner, Task Graph execution, Specialist Agents, Adversarial Critic, Judicial Evaluation, and Consensus Engine decision.",
)
async def evaluate_committee(
    body: EvaluateCommitteeRequest,
    committee: IntelligentInvestmentCommittee = Depends(get_investment_committee),
) -> EvaluateCommitteeResponse:
    """
    Execute Intelligent Investment Committee evaluation.

    Args:
        body (EvaluateCommitteeRequest): Request payload.
        committee (IntelligentInvestmentCommittee): Injected committee facade.

    Returns:
        EvaluateCommitteeResponse: Committee decision response payload.
    """
    decision, explanation = committee.evaluate_investment_request(
        ticker_symbol=body.ticker,
        horizon=InvestmentHorizon(body.horizon),
        style=InvestmentStyle(body.style),
        user_query=body.user_query,
    )

    return EvaluateCommitteeResponse(
        decision_id=decision.decision_id,
        session_id=decision.session_id,
        ticker=decision.ticker.full_symbol,
        winning_recommendation=decision.winning_recommendation.value,
        consensus_score=decision.consensus_score,
        confidence=decision.confidence,
        agreement_ratio=decision.agreement_ratio,
        verdict_summary=decision.judgement.verdict_summary,
        audit_signature=decision.audit_signature,
        timestamp=decision.timestamp.isoformat(),
        explanation=explanation,
    )
