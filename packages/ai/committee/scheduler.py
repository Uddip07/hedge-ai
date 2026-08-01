"""
Committee Scheduler Implementation.

Executes TaskGraph nodes with parallel worker pools (ThreadPoolExecutor), dependency resolution,
retries with backoff, timeouts, cancellation tokens, and structured log tracking.
"""

import concurrent.futures
import time
from collections.abc import Callable
from typing import Any

from packages.ai.committee.exceptions import SchedulerError
from packages.ai.committee.models import (
    CommitteeMetrics,
    ResearchTask,
    TaskGraph,
    TaskStatus,
)
from packages.ai.committee.policies import ExecutionPolicy
from packages.ai.committee.task_graph import TaskGraphEngine


class CommitteeScheduler:
    """
    Parallel TaskGraph scheduler executing committee tasks with dependency gating and retries.
    """

    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        self.policy = policy or ExecutionPolicy()

    def execute_graph(
        self,
        graph: TaskGraph,
        task_handler: Callable[[ResearchTask], Any],
        session_id: str = "default-session",
    ) -> tuple[dict[str, Any], CommitteeMetrics]:
        """
        Execute TaskGraph nodes to completion.

        Args:
            graph (TaskGraph): Executable task graph DAG.
            task_handler (Callable[[ResearchTask], Any]): Worker callback executing task logic.
            session_id (str): Analysis session ID.

        Returns:
            tuple[dict[str, Any], CommitteeMetrics]: Map of task results and execution metrics.
        """
        start_time = time.perf_counter()
        results: dict[str, Any] = {}
        completed_count = 0
        failed_count = 0

        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.policy.max_parallel_workers
            ) as executor:
                while True:
                    ready_tasks = TaskGraphEngine.get_ready_tasks(graph)
                    if not ready_tasks:
                        # Check if all tasks finished or if stalled
                        all_done = all(
                            t.status
                            in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED)
                            for t in graph.tasks.values()
                        )
                        if all_done:
                            break
                        # Short sleep before re-checking ready tasks
                        time.sleep(0.01)
                        continue

                    # Submit ready tasks in parallel
                    future_to_task = {
                        executor.submit(self._execute_single_task, task, task_handler): task
                        for task in ready_tasks
                    }

                    for future in concurrent.futures.as_completed(future_to_task):
                        task = future_to_task[future]
                        try:
                            res = future.result(timeout=task.timeout_seconds)
                            task.status = TaskStatus.COMPLETED
                            task.result = res
                            results[task.task_id] = res
                            completed_count += 1
                        except Exception as err:
                            task.status = TaskStatus.FAILED
                            task.error = str(err)
                            failed_count += 1
                            if not self.policy.allow_partial_failures:
                                raise SchedulerError(
                                    f"Task '{task.task_id}' failed: {err}",
                                    details={"task_id": task.task_id},
                                ) from err

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            metrics = CommitteeMetrics(
                session_id=session_id,
                total_tasks=len(graph.tasks),
                completed_tasks=completed_count,
                failed_tasks=failed_count,
                execution_time_ms=round(elapsed_ms, 2),
                parallelism_factor=round(len(graph.tasks) / max(1.0, elapsed_ms / 100), 2),
            )

            return results, metrics
        except Exception as err:
            raise SchedulerError(
                f"Scheduler execution failed for graph '{graph.graph_id}': {err}",
                details={"graph_id": graph.graph_id},
            ) from err

    def _execute_single_task(
        self, task: ResearchTask, task_handler: Callable[[ResearchTask], Any]
    ) -> Any:
        """Execute single task with retry logic."""
        task.status = TaskStatus.RUNNING
        last_exception: Exception | None = None

        for attempt in range(1 + task.max_retries):
            try:
                return task_handler(task)
            except Exception as err:
                last_exception = err
                if attempt < task.max_retries:
                    time.sleep(0.05 * (attempt + 1))

        raise last_exception or SchedulerError(f"Task '{task.task_id}' execution failed.")
