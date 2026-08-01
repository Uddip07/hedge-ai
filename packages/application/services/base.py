"""
Base Application Service Abstraction.

Application Services coordinate cross-cutting orchestration, workflow execution,
and port interactions across multiple domain entities and repositories.
"""

from abc import ABC


class BaseApplicationService(ABC):
    """
    Abstract Base Class for Application Services.

    Coordinates use case execution steps, transaction boundaries, and port dispatching.
    Application services do NOT contain domain business logic (which resides in domain entities/services).
    """
