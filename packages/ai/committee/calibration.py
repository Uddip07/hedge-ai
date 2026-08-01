"""
Confidence Calibrator.

Calibrates specialist agent voting weights and confidence adjustments using historical prediction accuracy.
"""

from decimal import Decimal

from packages.ai.committee.memory import InvestmentMemory


class ConfidenceCalibrator:
    """
    Calibrator evaluating historical accuracy to adjust future committee voting weights.
    """

    def __init__(self, memory: InvestmentMemory) -> None:
        self.memory = memory

    def compute_calibrated_weights(self, base_weights: dict[str, Decimal]) -> dict[str, Decimal]:
        """
        Compute updated agent weights based on historical accuracy records.

        Args:
            base_weights (dict[str, Decimal]): Initial base weights.

        Returns:
            dict[str, Decimal]: Calibrated weights.
        """
        entries = self.memory.get_all_entries()
        evaluated_entries = [e for e in entries if e.accuracy_score is not None]

        if not evaluated_entries:
            return dict(base_weights)

        avg_accuracy = sum(e.accuracy_score for e in evaluated_entries if e.accuracy_score) / len(
            evaluated_entries
        )

        calibrated: dict[str, Decimal] = {}
        for agent_str, w in base_weights.items():
            # Adjust weight by accuracy factor (bounded between 0.5x and 1.5x)
            factor = Decimal(str(max(0.5, min(1.5, avg_accuracy))))
            calibrated[agent_str] = round(w * factor, 2)

        return calibrated
