"""
Conflict Detector for Consensus Intelligence Engine.

Detects and surfaces explicit conflicts across agent recommendations, evidence, confidence, and assumptions.
"""

from packages.ai.consensus.models import DetectedConflict
from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.research import RecommendationType


class ConflictDetector:
    """
    Detector identifying recommendation polarities, missing evidence, low confidence, and assumption clashes.
    """

    def detect_conflicts(
        self, results: list[AgentResult], confidence_threshold: float = 0.60
    ) -> list[DetectedConflict]:
        """
        Analyze committee results and return all detected conflicts.

        Args:
            results (list[AgentResult]): List of agent research outputs.
            confidence_threshold (float): Minimum acceptable agent confidence threshold.

        Returns:
            list[DetectedConflict]: Explicit list of detected conflict events.
        """
        conflicts: list[DetectedConflict] = []
        if not results:
            return conflicts

        buy_agents: list[AgentResult] = []
        sell_agents: list[AgentResult] = []
        strong_sell_agents: list[AgentResult] = []

        all_assumptions: dict[str, list[str]] = {}

        for res in results:
            # 1. Track recommendation directions
            if res.recommendation in {RecommendationType.BUY, RecommendationType.STRONG_BUY}:
                buy_agents.append(res)
            elif res.recommendation == RecommendationType.SELL:
                sell_agents.append(res)
            elif res.recommendation == RecommendationType.STRONG_SELL:
                sell_agents.append(res)
                strong_sell_agents.append(res)

            # 2. Check for missing evidence
            if not res.evidence:
                conflicts.append(
                    DetectedConflict(
                        conflict_type="MISSING_EVIDENCE",
                        severity="MEDIUM",
                        description=f"Agent '{res.agent_type.value}' returned analysis without supporting evidence citations.",
                        involved_agents=[res.agent_type],
                    )
                )

            # 3. Check for low confidence
            if float(res.confidence.value) < confidence_threshold:
                conflicts.append(
                    DetectedConflict(
                        conflict_type="LOW_CONFIDENCE",
                        severity="HIGH" if res.agent_type.value == "RISK" else "MEDIUM",
                        description=f"Agent '{res.agent_type.value}' reported low confidence score of {res.confidence.value} (threshold {confidence_threshold}).",
                        involved_agents=[res.agent_type],
                    )
                )

            # Track assumptions for clash detection
            if res.assumptions:
                all_assumptions[res.agent_type.value] = res.assumptions

        # 4. Check BUY vs STRONG_SELL
        if buy_agents and strong_sell_agents:
            b_names = [a.agent_type for a in buy_agents]
            ss_names = [a.agent_type for a in strong_sell_agents]
            conflicts.append(
                DetectedConflict(
                    conflict_type="BUY_VS_STRONG_SELL",
                    severity="CRITICAL",
                    description=(
                        f"Critical polarity clash: Agents {[a.value for a in b_names]} recommended BUY/STRONG_BUY "
                        f"while Agents {[a.value for a in ss_names]} recommended STRONG_SELL."
                    ),
                    involved_agents=b_names + ss_names,
                )
            )

        # 5. Check BUY vs SELL (if not already strong sell critical)
        elif buy_agents and sell_agents:
            b_names = [a.agent_type for a in buy_agents]
            s_names = [a.agent_type for a in sell_agents]
            conflicts.append(
                DetectedConflict(
                    conflict_type="BUY_VS_SELL",
                    severity="HIGH",
                    description=(
                        f"High recommendation conflict: Agents {[a.value for a in b_names]} recommended BUY "
                        f"while Agents {[a.value for a in s_names]} recommended SELL."
                    ),
                    involved_agents=b_names + s_names,
                )
            )

        # 6. Check Conflicting Assumptions
        if len(all_assumptions) >= 2:
            # Check for keyword clashes (e.g. 'bullish' vs 'bearish', 'growth' vs 'recession')
            words_by_agent = {
                agent: " ".join(assump).lower() for agent, assump in all_assumptions.items()
            }
            has_bull = any("bull" in text or "growth" in text for text in words_by_agent.values())
            has_bear = any(
                "bear" in text or "recession" in text or "decline" in text
                for text in words_by_agent.values()
            )
            if has_bull and has_bear:
                conflicts.append(
                    DetectedConflict(
                        conflict_type="CONFLICTING_ASSUMPTIONS",
                        severity="HIGH",
                        description="Conflicting macroeconomic or growth assumptions detected across agent analyses.",
                        involved_agents=[res.agent_type for res in results if res.assumptions],
                    )
                )

        return conflicts
