"""
Calibration Analyzer for AI Evaluation & Benchmarking Framework.

Computes Expected Calibration Error (ECE) and Brier scores for confidence score calibration.
"""


class CalibrationAnalyzer:
    """
    Analyzer evaluating confidence calibration metrics (ECE and Brier score).
    """

    def compute_brier_score(self, confidences: list[float], outcomes: list[bool]) -> float:
        """
        Compute Brier score: Mean squared error between reported confidence and actual binary accuracy.

        Formula: (1/N) * sum((confidence_i - outcome_i)^2)
        Lower is better (0.0 = perfect calibration).
        """
        if not confidences or len(confidences) != len(outcomes):
            return 0.0

        total_sq_err = sum(
            (conf - (1.0 if correct else 0.0)) ** 2
            for conf, correct in zip(confidences, outcomes, strict=False)
        )
        return total_sq_err / len(confidences)

    def compute_expected_calibration_error(
        self, confidences: list[float], outcomes: list[bool], num_bins: int = 5
    ) -> float:
        """
        Compute Expected Calibration Error (ECE) across confidence probability bins.

        Args:
            confidences (list[float]): List of reported confidence scores [0.0, 1.0].
            outcomes (list[bool]): List of actual prediction correctness flags.
            num_bins (int): Number of calibration probability bins.

        Returns:
            float: ECE score [0.0, 1.0]. Lower is better.
        """
        if not confidences or len(confidences) != len(outcomes):
            return 0.0

        n = len(confidences)
        bin_boundaries = [i / num_bins for i in range(num_bins + 1)]
        ece = 0.0

        for i in range(num_bins):
            lower = bin_boundaries[i]
            upper = bin_boundaries[i + 1]

            # Filter items falling into bin [lower, upper)
            bin_items = [
                (conf, correct)
                for conf, correct in zip(confidences, outcomes, strict=False)
                if (lower <= conf < upper) or (i == num_bins - 1 and lower <= conf <= upper)
            ]

            if not bin_items:
                continue

            bin_size = len(bin_items)
            avg_confidence = sum(c for c, _ in bin_items) / bin_size
            avg_accuracy = sum(1.0 for _, corr in bin_items if corr) / bin_size

            # Weight by bin size / total sample count
            ece += (bin_size / n) * abs(avg_accuracy - avg_confidence)

        return ece
