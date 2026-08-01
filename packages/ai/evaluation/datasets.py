"""
Dataset Manager for AI Evaluation & Benchmarking Framework.

Creates, registers, and manages benchmark datasets and mock test suites.
"""

from packages.ai.evaluation.models import BenchmarkDataset, BenchmarkSample


class DatasetManager:
    """
    Manager maintaining benchmark datasets.
    """

    def __init__(self) -> None:
        self._datasets: dict[str, BenchmarkDataset] = {}
        self._register_default_mock_datasets()

    def register_dataset(self, dataset: BenchmarkDataset) -> None:
        """Register a BenchmarkDataset instance."""
        self._datasets[dataset.dataset_id] = dataset

    def get_dataset(self, dataset_id: str) -> BenchmarkDataset:
        """Fetch BenchmarkDataset by dataset_id."""
        if dataset_id not in self._datasets:
            raise KeyError(f"BenchmarkDataset '{dataset_id}' not found.")
        return self._datasets[dataset_id]

    def list_datasets(self) -> list[dict[str, str]]:
        """List registered datasets summary."""
        return [
            {
                "dataset_id": ds.dataset_id,
                "name": ds.name,
                "description": ds.description,
                "sample_count": str(len(ds.samples)),
            }
            for ds in self._datasets.values()
        ]

    def _register_default_mock_datasets(self) -> None:
        """Initialize mock benchmark dataset representing NIFTY 50 institutional test cases."""
        mock_samples = [
            BenchmarkSample(
                sample_id="sample-reliance-001",
                ticker="RELIANCE.NS",
                ground_truth_recommendation="BUY",
                expected_score_min=0.50,
                expected_score_max=1.0,
                metadata={"sector": "Energy", "earnings_growth": "18.5%"},
            ),
            BenchmarkSample(
                sample_id="sample-tcs-002",
                ticker="TCS.NS",
                ground_truth_recommendation="BUY",
                expected_score_min=0.40,
                expected_score_max=0.90,
                metadata={"sector": "IT Services", "roce": "22.4%"},
            ),
            BenchmarkSample(
                sample_id="sample-infosys-003",
                ticker="INFY.NS",
                ground_truth_recommendation="HOLD",
                expected_score_min=-0.20,
                expected_score_max=0.30,
                metadata={"sector": "IT Services", "guidance": "Conservative"},
            ),
            BenchmarkSample(
                sample_id="sample-hdfcbank-004",
                ticker="HDFCBANK.NS",
                ground_truth_recommendation="BUY",
                expected_score_min=0.50,
                expected_score_max=0.95,
                metadata={"sector": "Banking", "npa": "Low"},
            ),
            BenchmarkSample(
                sample_id="sample-icicibank-005",
                ticker="ICICIBANK.NS",
                ground_truth_recommendation="BUY",
                expected_score_min=0.60,
                expected_score_max=1.0,
                metadata={"sector": "Banking", "nim_expansion": "Positive"},
            ),
        ]

        default_ds = BenchmarkDataset(
            dataset_id="nifty50-mock-v1",
            name="NIFTY 50 Mock Benchmark Dataset",
            description="Institutional ground truth test cases for top Indian equities.",
            samples=mock_samples,
        )
        self.register_dataset(default_ds)
