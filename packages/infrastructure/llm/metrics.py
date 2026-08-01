"""
LLM Telemetry and Metrics for Infrastructure Layer.

Tracks Model name, Latency, Token usage, Retry count, Prompt version, Timestamp, and Request ID.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class LLMMetrics:
    """
    Observability telemetry data structure capturing single LLM invocation metrics.

    Attributes:
        model_name (str): Target model identifier string.
        latency_ms (float): Execution duration in milliseconds.
        prompt_tokens (int): Input prompt token count.
        completion_tokens (int): Output response token count.
        total_tokens (int): Total combined token count.
        retry_count (int): Number of backoff retries performed.
        prompt_version (str): Prompt template version string.
        timestamp (str): Execution timestamp string (ISO-8601 UTC).
        request_id (str): Unique tracking correlation ID.
    """

    model_name: str
    latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    retry_count: int = 0
    prompt_version: str = "1.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Serialize LLMMetrics to dictionary."""
        return {
            "model_name": self.model_name,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens or (self.prompt_tokens + self.completion_tokens),
            "retry_count": self.retry_count,
            "prompt_version": self.prompt_version,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
        }
