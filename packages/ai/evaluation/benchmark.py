"""
Benchmark Runner for AI Evaluation & Benchmarking Framework.

Executes benchmark test suites against individual agents and consensus decisions.
"""

from packages.ai.consensus.engine import ConsensusEngine
from packages.ai.evaluation.calibration import CalibrationAnalyzer
from packages.ai.evaluation.datasets import DatasetManager
from packages.ai.evaluation.metrics import MetricsCalculator
from packages.ai.evaluation.models import EvaluationMetrics
from packages.ai.models.agent_context import AgentContext
from packages.ai.orchestrator import AgentOrchestrator
from packages.domain.value_objects.identifiers.ticker import Ticker


class BenchmarkRunner:
    """
    Runner executing benchmark evaluation sweeps over test datasets.
    """

    def __init__(
        self,
        dataset_manager: DatasetManager | None = None,
        metrics_calculator: MetricsCalculator | None = None,
        calibration_analyzer: CalibrationAnalyzer | None = None,
    ) -> None:
        self.dataset_manager = dataset_manager or DatasetManager()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        self.calibration_analyzer = calibration_analyzer or CalibrationAnalyzer()

    def run_benchmark(
        self,
        dataset_id: str = "nifty50-mock-v1",
        orchestrator: AgentOrchestrator | None = None,
        consensus_engine: ConsensusEngine | None = None,
    ) -> EvaluationMetrics:
        """
        Execute benchmark evaluation sweep on a dataset.

        Args:
            dataset_id (str): Benchmark dataset ID.
            orchestrator (AgentOrchestrator | None): Optional agent swarm orchestrator.
            consensus_engine (ConsensusEngine | None): Optional consensus engine.

        Returns:
            EvaluationMetrics: Aggregated benchmark metrics object.
        """
        ds = self.dataset_manager.get_dataset(dataset_id)
        orch = orchestrator or AgentOrchestrator()
        engine = consensus_engine or ConsensusEngine()

        agent_preds: list[str] = []
        agent_truths: list[str] = []
        consensus_preds: list[str] = []
        consensus_truths: list[str] = []
        json_validations: list[bool] = []
        latencies_ms: list[float] = []
        confidences: list[float] = []
        outcomes: list[bool] = []

        for sample in ds.samples:
            context = AgentContext(ticker=Ticker(sample.ticker.split(".")[0]))

            # Run swarm analysis
            _, results = orch.run_analysis(context)
            if results:
                top_agent_res = results[0]
                agent_preds.append(top_agent_res.recommendation.value)
                agent_truths.append(sample.ground_truth_recommendation)
                latencies_ms.append(top_agent_res.execution_time_ms)
                json_validations.append(True)

                conf_val = float(top_agent_res.confidence.value)
                is_correct = (
                    top_agent_res.recommendation.value.upper()
                    == sample.ground_truth_recommendation.upper()
                )
                confidences.append(conf_val)
                outcomes.append(is_correct)

            # Run committee consensus evaluation
            decision = engine.evaluate_committee_decision(results)
            consensus_preds.append(decision.recommendation.value)
            consensus_truths.append(sample.ground_truth_recommendation)

        ece = self.calibration_analyzer.compute_expected_calibration_error(confidences, outcomes)
        brier = self.calibration_analyzer.compute_brier_score(confidences, outcomes)

        metrics = self.metrics_calculator.compute_aggregate_metrics(
            agent_predictions=agent_preds,
            agent_ground_truths=agent_truths,
            consensus_predictions=consensus_preds,
            consensus_ground_truths=consensus_truths,
            json_validations=json_validations,
            latencies_ms=latencies_ms,
            retries_count=0,
            total_calls=len(ds.samples),
            ece=ece,
            brier=brier,
        )

        return metrics
