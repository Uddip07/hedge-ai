"""
Leaderboard for AI Evaluation & Benchmarking Framework.

Maintains rankings and performance scorecards for individual agent roles and models.
"""

from packages.ai.evaluation.models import AgentLeaderboardEntry


class Leaderboard:
    """
    Leaderboard maintaining ranked performance table for AI research agents.
    """

    def __init__(self) -> None:
        self._entries: dict[str, AgentLeaderboardEntry] = {}

    def add_or_update_entry(
        self,
        agent_name: str,
        accuracy: float,
        json_validation_rate: float,
        avg_latency_ms: float,
        confidence_calibration: float,
    ) -> None:
        """Add or update an agent leaderboard record."""
        entry = AgentLeaderboardEntry(
            agent_name=agent_name,
            accuracy=accuracy,
            json_validation_rate=json_validation_rate,
            avg_latency_ms=avg_latency_ms,
            confidence_calibration=confidence_calibration,
        )
        self._entries[agent_name] = entry

    def get_ranked_leaderboard(self) -> list[AgentLeaderboardEntry]:
        """
        Get all entries ranked by composite performance score:
        Score = 0.5 * accuracy + 0.3 * json_validation_rate - 0.2 * confidence_calibration
        """
        entries_list = list(self._entries.values())

        def score_func(e: AgentLeaderboardEntry) -> float:
            return (
                (0.5 * e.accuracy)
                + (0.3 * e.json_validation_rate)
                - (0.2 * e.confidence_calibration)
            )

        entries_list.sort(key=score_func, reverse=True)

        ranked: list[AgentLeaderboardEntry] = []
        for idx, entry in enumerate(entries_list, start=1):
            ranked.append(
                AgentLeaderboardEntry(
                    agent_name=entry.agent_name,
                    accuracy=entry.accuracy,
                    json_validation_rate=entry.json_validation_rate,
                    avg_latency_ms=entry.avg_latency_ms,
                    confidence_calibration=entry.confidence_calibration,
                    rank=idx,
                )
            )

        return ranked
