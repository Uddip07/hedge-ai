"""
Report Generator for AI Evaluation & Benchmarking Framework.

Generates structured JSON evaluation reports and markdown reports.
"""

from typing import Any

from packages.ai.evaluation.models import AgentLeaderboardEntry, EvaluationMetrics


class ReportGenerator:
    """
    Generator creating JSON and Markdown performance evaluation reports.
    """

    def generate_json_report(
        self,
        metrics: EvaluationMetrics,
        leaderboard: list[AgentLeaderboardEntry] | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate structured JSON evaluation report payload.
        """
        report = {
            "metrics": metrics.to_dict(),
            "leaderboard": [e.to_dict() for e in (leaderboard or [])],
            "metadata": extra_metadata or {},
        }
        return report

    def generate_markdown_report(
        self,
        metrics: EvaluationMetrics,
        leaderboard: list[AgentLeaderboardEntry] | None = None,
        title: str = "AI Core Benchmarking & Evaluation Report",
    ) -> str:
        """
        Generate GitHub-Flavored Markdown evaluation report string.
        """
        m_dict = metrics.to_dict()
        lines: list[str] = [
            f"# {title}",
            "",
            "## Aggregate Metrics Summary",
            "",
            "| Metric | Value |",
            "| :--- | :--- |",
            f"| **Agent Accuracy** | `{m_dict['agent_accuracy'] * 100:.1f}%` |",
            f"| **Consensus Accuracy** | `{m_dict['consensus_accuracy'] * 100:.1f}%` |",
            f"| **Prompt Performance Score** | `{m_dict['prompt_performance_score']:.3f}` |",
            f"| **JSON Validation Rate** | `{m_dict['json_validation_rate'] * 100:.1f}%` |",
            f"| **Average Latency** | `{m_dict['avg_latency_ms']:.1f} ms` |",
            f"| **Retry Rate** | `{m_dict['retry_rate'] * 100:.1f}%` |",
            f"| **Expected Calibration Error (ECE)** | `{m_dict['expected_calibration_error']:.4f}` |",
            f"| **Brier Score** | `{m_dict['brier_score']:.4f}` |",
            f"| **Total Evaluation Samples** | `{m_dict['total_evaluations']}` |",
            "",
        ]

        if leaderboard:
            lines.extend(
                [
                    "## Agent Performance Leaderboard",
                    "",
                    "| Rank | Agent Role | Accuracy | Schema Compliance | Avg Latency | Calibration (ECE) |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- |",
                ]
            )
            for entry in leaderboard:
                e_dict = entry.to_dict()
                lines.append(
                    f"| **#{e_dict['rank']}** | `{e_dict['agent_name']}` | "
                    f"`{e_dict['accuracy'] * 100:.1f}%` | `{e_dict['json_validation_rate'] * 100:.1f}%` | "
                    f"`{e_dict['avg_latency_ms']:.1f} ms` | `{e_dict['confidence_calibration']:.4f}` |"
                )
            lines.append("")

        return "\n".join(lines)
