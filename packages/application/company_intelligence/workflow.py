"""
Company Intelligence Workflow Implementation.

Defines execution topology, state transition logging, and pipeline orchestration controls.
"""

import time
from typing import Any

from packages.application.company_intelligence.exceptions import CompanyIntelligenceError
from packages.application.company_intelligence.pipeline import CompanyIntelligencePipeline


class CompanyIntelligenceWorkflow:
    """
    Stateful workflow coordinator executing Company Intelligence pipeline stages.
    """

    def __init__(self, pipeline: CompanyIntelligencePipeline) -> None:
        self.pipeline = pipeline

    def run_workflow(self, ticker_symbol: str, session_id: str | None = None) -> dict[str, Any]:
        """
        Execute Company Intelligence workflow with state tracking and performance timing.

        Args:
            ticker_symbol (str): Target stock ticker symbol.
            session_id (str | None): Optional analysis session UUID string.

        Returns:
            dict[str, Any]: Compiled pipeline stage payload.
        """
        start_time = time.perf_counter()
        try:
            results = self.pipeline.execute_pipeline(ticker_symbol, session_id=session_id)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            results["workflow_execution_time_ms"] = round(elapsed_ms, 2)
            return results
        except Exception as err:
            raise CompanyIntelligenceError(
                f"Workflow execution failed for '{ticker_symbol}': {err}",
                details={"ticker": ticker_symbol},
            ) from err
