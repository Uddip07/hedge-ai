"""
Prompt Aggregate Root, PromptVersion, and PromptExecution for the Indian AI Hedge Fund Domain.

Root entity managing agent prompt engineering templates, version releases, and model execution telemetry.
Pure domain entity with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.ai.reasoning import ModelResponse
from packages.domain.enums.ai import AgentType, ModelProvider
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.identifiers.uuid_wrappers import PromptId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, slots=True)
class PromptExecution:
    """
    Immutable value object recording a single model execution telemetry event for a Prompt.

    Attributes:
        execution_id (uuid.UUID): Unique execution identifier.
        model_provider (ModelProvider): Provider enum.
        model_name (str): Model name string.
        input_variables (Dict[str, Any]): Input parameter dictionary passed to prompt template.
        response (ModelResponse): Generated LLM response payload.
        executed_at (Timestamp): Execution timestamp (UTC).
    """

    model_provider: ModelProvider
    model_name: str
    input_variables: dict[str, Any]
    response: ModelResponse
    execution_id: uuid.UUID = field(default_factory=uuid.uuid4)
    executed_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.model_provider, ModelProvider):
            object.__setattr__(self, "model_provider", ModelProvider(self.model_provider))
        if not isinstance(self.response, ModelResponse):
            object.__setattr__(self, "response", ModelResponse(self.response))
        if not isinstance(self.executed_at, Timestamp):
            object.__setattr__(self, "executed_at", Timestamp(self.executed_at))

    def to_dict(self) -> dict[str, Any]:
        """Serialize PromptExecution to dictionary."""
        return {
            "execution_id": str(self.execution_id),
            "model_provider": self.model_provider.value,
            "model_name": self.model_name,
            "input_variables": dict(self.input_variables),
            "response": self.response.to_dict(),
            "executed_at": self.executed_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptExecution":
        """Deserialize dictionary to PromptExecution."""
        return cls(
            execution_id=uuid.UUID(data["execution_id"]),
            model_provider=ModelProvider(data["model_provider"]),
            model_name=data["model_name"],
            input_variables=dict(data.get("input_variables", {})),
            response=ModelResponse.from_dict(data["response"]),
            executed_at=Timestamp.from_dict(data["executed_at"]),
        )


@dataclass(frozen=True, slots=True)
class PromptVersion:
    """
    Immutable value object representing a versioned prompt engineering template.

    Attributes:
        version_number (str): Version release label (e.g. '1.0.0').
        template (str): User/human prompt template containing {variable} placeholders.
        system_prompt (Optional[str]): System instruction prompt template.
        variables (List[str]): Extracted required variable placeholder names.
        created_at (Timestamp): Version creation timestamp (UTC).
        changelog (str): Description of prompt adjustments in this version.
    """

    version_number: str
    template: str
    system_prompt: str | None = None
    variables: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    changelog: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))

        if not self.version_number.strip():
            raise ValidationError("PromptVersion version_number cannot be empty.")
        if not self.template.strip():
            raise ValidationError("PromptVersion template cannot be empty.")

    def render(self, variables: dict[str, Any]) -> str:
        """Render prompt template string with provided variable bindings."""
        try:
            return self.template.format(**variables)
        except KeyError as exc:
            raise ValidationError(
                f"Missing required prompt template variable '{exc.args[0]}'.",
                context={"required": self.variables, "provided": list(variables.keys())},
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        """Serialize PromptVersion to dictionary."""
        return {
            "version_number": self.version_number,
            "template": self.template,
            "system_prompt": self.system_prompt,
            "variables": list(self.variables),
            "created_at": self.created_at.to_dict(),
            "changelog": self.changelog,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptVersion":
        """Deserialize dictionary to PromptVersion."""
        return cls(
            version_number=data["version_number"],
            template=data["template"],
            system_prompt=data.get("system_prompt"),
            variables=list(data.get("variables", [])),
            created_at=Timestamp.from_dict(data["created_at"]),
            changelog=data.get("changelog", ""),
        )


@dataclass
class Prompt:
    """
    Prompt Aggregate Root.

    Attributes:
        id (PromptId): Unique prompt repository identifier.
        name (str): Prompt template name.
        agent_type (AgentType): Associated agent role.
        versions (List[PromptVersion]): Tracked prompt version releases.
        executions (List[PromptExecution]): Historical execution telemetry logs.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    name: str
    agent_type: AgentType
    id: PromptId = field(default_factory=PromptId.generate)
    versions: list[PromptVersion] = field(default_factory=list)
    executions: list[PromptExecution] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, PromptId):
            object.__setattr__(self, "id", PromptId(self.id))
        if not isinstance(self.agent_type, AgentType):
            object.__setattr__(self, "agent_type", AgentType(self.agent_type))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

        if not self.name.strip():
            raise ValidationError("Prompt name cannot be empty.")

    def add_version(self, version: PromptVersion) -> None:
        """Add a new prompt template version."""
        self.versions.append(version)
        self._touch()

    def record_execution(self, execution: PromptExecution) -> None:
        """Record an LLM model execution event."""
        self.executions.append(execution)
        self._touch()

    def get_latest_version(self) -> PromptVersion | None:
        """Return the latest prompt template version if available."""
        return self.versions[-1] if self.versions else None

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize Prompt Aggregate Root to dictionary."""
        return {
            "id": self.id.to_dict(),
            "name": self.name,
            "agent_type": self.agent_type.value,
            "versions": [v.to_dict() for v in self.versions],
            "executions": [e.to_dict() for e in self.executions],
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Prompt":
        """Deserialize dictionary to Prompt Aggregate Root."""
        versions = [PromptVersion.from_dict(v) for v in data.get("versions", [])]
        executions = [PromptExecution.from_dict(e) for e in data.get("executions", [])]

        return cls(
            id=PromptId.from_dict(data["id"]),
            name=data["name"],
            agent_type=AgentType(data["agent_type"]),
            versions=versions,
            executions=executions,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Prompt):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
