"""
Task Graph Engine for Committee Execution.

Manages directed acyclic graph (DAG) construction, topological sorting, dependency checks,
cycle detection, and task status management.
"""

from collections import deque

from packages.ai.committee.exceptions import TaskGraphError
from packages.ai.committee.models import ResearchTask, TaskGraph, TaskStatus


class TaskGraphEngine:
    """
    Engine for creating, validating, and topological sorting of TaskGraph instances.
    """

    @staticmethod
    def create_graph(graph_id: str, tasks: list[ResearchTask]) -> TaskGraph:
        """Create and validate a new TaskGraph."""
        graph = TaskGraph(graph_id=graph_id)
        for t in tasks:
            graph.add_task(t)

        TaskGraphEngine.validate_and_sort(graph)
        return graph

    @staticmethod
    def validate_and_sort(graph: TaskGraph) -> list[str]:
        """
        Validate DAG for cycles and compute topological execution order (Kahn's Algorithm).

        Returns:
            list[str]: Ordered list of task IDs.
        """
        in_degree: dict[str, int] = {tid: 0 for tid in graph.tasks}
        adj: dict[str, list[str]] = {tid: [] for tid in graph.tasks}

        for tid, task in graph.tasks.items():
            for dep in task.dependencies:
                if dep not in graph.tasks:
                    raise TaskGraphError(
                        f"Task '{tid}' depends on non-existent task '{dep}'.",
                        details={"task_id": tid, "missing_dep": dep},
                    )
                adj[dep].append(tid)
                in_degree[tid] += 1

        queue: deque[str] = deque([tid for tid, deg in in_degree.items() if deg == 0])
        order: list[str] = []

        while queue:
            curr = queue.popleft()
            order.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(graph.tasks):
            raise TaskGraphError(
                "Cycle detected in TaskGraph dependencies.",
                details={"graph_id": graph.graph_id},
            )

        graph.execution_order = order
        return order

    @staticmethod
    def get_ready_tasks(graph: TaskGraph) -> list[ResearchTask]:
        """Return all tasks whose dependencies are completed and status is PENDING."""
        ready: list[ResearchTask] = []
        for task in graph.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            deps_satisfied = True
            for dep_id in task.dependencies:
                dep_task = graph.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    deps_satisfied = False
                    break

            if deps_satisfied:
                ready.append(task)

        # Sort ready tasks by priority (higher priority first)
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready
