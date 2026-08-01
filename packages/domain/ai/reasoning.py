"""
Reasoning Chain, Evidence, Citations, Tool Invocations, Agent Decisions, and Model Responses
for the Indian AI Hedge Fund Platform.

Provides pure domain models capturing agent chain-of-thought reasoning, citations,
tool execution traces, and LLM model response telemetry. Zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.ai import ModelProvider
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.domain.value_objects.metrics.scores import ConfidenceScore


@dataclass(frozen=True, slots=True)
class Citation:
    """
    Immutable value object representing a document or regulatory source citation.

    Attributes:
        document_id (DocumentId): ID of cited document.
        source_title (str): Title or headline of cited source.
        snippet (str): Relevant quote snippet or excerpt text.
        page_number (Optional[int]): Page number reference if applicable.
    """

    document_id: DocumentId
    source_title: str
    snippet: str
    page_number: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.document_id, DocumentId):
            object.__setattr__(self, "document_id", DocumentId(self.document_id))

    def to_dict(self) -> dict[str, Any]:
        """Serialize Citation to dictionary."""
        return {
            "document_id": self.document_id.to_dict(),
            "source_title": self.source_title,
            "snippet": self.snippet,
            "page_number": self.page_number,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Citation":
        """Deserialize dictionary to Citation."""
        return cls(
            document_id=DocumentId.from_dict(data["document_id"]),
            source_title=data["source_title"],
            snippet=data["snippet"],
            page_number=data.get("page_number"),
        )


@dataclass(frozen=True, slots=True)
class Evidence:
    """
    Immutable value object representing extracted factual evidence backed by citations.

    Attributes:
        fact (str): Extracted factual statement or metric.
        confidence (ConfidenceScore): Fact extraction confidence score [0, 1].
        citations (List[Citation]): Supporting source citations.
    """

    fact: str
    confidence: ConfidenceScore
    citations: list[Citation] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.confidence, ConfidenceScore):
            object.__setattr__(self, "confidence", ConfidenceScore(self.confidence))

    def to_dict(self) -> dict[str, Any]:
        """Serialize Evidence to dictionary."""
        return {
            "fact": self.fact,
            "confidence": self.confidence.to_dict(),
            "citations": [c.to_dict() for c in self.citations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        """Deserialize dictionary to Evidence."""
        citations = [Citation.from_dict(c) for c in data.get("citations", [])]
        return cls(
            fact=data["fact"],
            confidence=ConfidenceScore.from_dict(data["confidence"]),
            citations=citations,
        )


@dataclass(frozen=True, slots=True)
class ToolInvocation:
    """
    Immutable value object capturing an agent tool invocation execution event.

    Attributes:
        tool_name (str): Name of invoked tool (e.g. 'get_financial_ratios').
        arguments (Dict[str, Any]): Arguments passed to tool.
        result (Any): Output payload returned by tool.
        execution_time_ms (float): Tool execution duration in milliseconds.
        status (str): Execution status ('SUCCESS', 'ERROR').
    """

    tool_name: str
    arguments: dict[str, Any]
    result: Any
    execution_time_ms: float
    status: str = "SUCCESS"

    def to_dict(self) -> dict[str, Any]:
        """Serialize ToolInvocation to dictionary."""
        return {
            "tool_name": self.tool_name,
            "arguments": dict(self.arguments),
            "result": self.result,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolInvocation":
        """Deserialize dictionary to ToolInvocation."""
        return cls(
            tool_name=data["tool_name"],
            arguments=dict(data["arguments"]),
            result=data.get("result"),
            execution_time_ms=float(data["execution_time_ms"]),
            status=data.get("status", "SUCCESS"),
        )


@dataclass(frozen=True, slots=True)
class AgentDecision:
    """
    Immutable value object representing an agent's final action decision.

    Attributes:
        action (str): Proposed action name.
        confidence (ConfidenceScore): Action decision confidence [0, 1].
        rationale (str): Decision rationale.
        tools_used (List[ToolInvocation]): Tools executed to reach this decision.
    """

    action: str
    confidence: ConfidenceScore
    rationale: str
    tools_used: list[ToolInvocation] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.confidence, ConfidenceScore):
            object.__setattr__(self, "confidence", ConfidenceScore(self.confidence))

    def to_dict(self) -> dict[str, Any]:
        """Serialize AgentDecision to dictionary."""
        return {
            "action": self.action,
            "confidence": self.confidence.to_dict(),
            "rationale": self.rationale,
            "tools_used": [t.to_dict() for t in self.tools_used],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentDecision":
        """Deserialize dictionary to AgentDecision."""
        tools = [ToolInvocation.from_dict(t) for t in data.get("tools_used", [])]
        return cls(
            action=data["action"],
            confidence=ConfidenceScore.from_dict(data["confidence"]),
            rationale=data.get("rationale", ""),
            tools_used=tools,
        )


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """
    Immutable value object capturing an LLM provider completion response.

    Attributes:
        provider (ModelProvider): Provider enum (ANTHROPIC, OPENAI, GOOGLE, etc.).
        model_name (str): Specific model version (e.g. 'claude-3-5-sonnet', 'gpt-4o').
        content (str): Generated response text content.
        prompt_tokens (int): Prompt token usage count.
        completion_tokens (int): Completion token usage count.
        latency_ms (float): Model response latency in milliseconds.
    """

    provider: ModelProvider
    model_name: str
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.provider, ModelProvider):
            object.__setattr__(self, "provider", ModelProvider(self.provider))

    @property
    def total_tokens(self) -> int:
        """Return total token usage count."""
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict[str, Any]:
        """Serialize ModelResponse to dictionary."""
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "content": self.content,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelResponse":
        """Deserialize dictionary to ModelResponse."""
        return cls(
            provider=ModelProvider(data["provider"]),
            model_name=data["model_name"],
            content=data["content"],
            prompt_tokens=int(data.get("prompt_tokens", 0)),
            completion_tokens=int(data.get("completion_tokens", 0)),
            latency_ms=float(data.get("latency_ms", 0.0)),
        )


@dataclass(frozen=True, slots=True)
class ReasoningTrace:
    """
    Immutable value object representing a single step in an agent's reasoning chain.

    Attributes:
        step_index (int): Step order index.
        thought (str): Internal chain-of-thought text.
        tool_invocations (List[ToolInvocation]): Tool calls executed in this step.
        evidence (List[Evidence]): Evidence items gathered in this step.
    """

    step_index: int
    thought: str
    tool_invocations: list[ToolInvocation] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize ReasoningTrace to dictionary."""
        return {
            "step_index": self.step_index,
            "thought": self.thought,
            "tool_invocations": [t.to_dict() for t in self.tool_invocations],
            "evidence": [e.to_dict() for e in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReasoningTrace":
        """Deserialize dictionary to ReasoningTrace."""
        tools = [ToolInvocation.from_dict(t) for t in data.get("tool_invocations", [])]
        ev = [Evidence.from_dict(e) for e in data.get("evidence", [])]
        return cls(
            step_index=int(data["step_index"]),
            thought=data["thought"],
            tool_invocations=tools,
            evidence=ev,
        )


@dataclass(frozen=True, slots=True)
class ReasoningChain:
    """
    Immutable value object encapsulating an end-to-end multi-step agent reasoning trajectory.

    Attributes:
        traces (List[ReasoningTrace]): Ordered sequence of reasoning step traces.
        final_decision (Optional[AgentDecision]): Final decision outcome if completed.
    """

    traces: list[ReasoningTrace] = field(default_factory=list)
    final_decision: AgentDecision | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize ReasoningChain to dictionary."""
        return {
            "traces": [t.to_dict() for t in self.traces],
            "final_decision": self.final_decision.to_dict() if self.final_decision else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReasoningChain":
        """Deserialize dictionary to ReasoningChain."""
        traces = [ReasoningTrace.from_dict(t) for t in data.get("traces", [])]
        decision = (
            AgentDecision.from_dict(data["final_decision"]) if data.get("final_decision") else None
        )
        return cls(traces=traces, final_decision=decision)
