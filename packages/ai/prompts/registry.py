"""
Prompt Registry for Prompt Intelligence Framework.

Central registry managing template loading from disk, caching, version resolution, and validation.
"""

import json
from pathlib import Path
from typing import Any

from packages.ai.prompts.prompt_registry import PromptTemplate
from packages.ai.prompts.validator import PromptValidator
from packages.ai.prompts.versioning import PromptVersionManager
from packages.domain.enums.ai import AgentType


class PromptRegistry:
    """
    Registry loading, caching, validating, and versioning agent prompt templates.
    """

    AGENT_FOLDER_MAP: dict[AgentType, str] = {
        AgentType.FUNDAMENTAL: "fundamental",
        AgentType.QUANT: "technical",
        AgentType.SENTIMENT: "news",
        AgentType.MACRO: "macro",
        AgentType.RISK: "risk",
        AgentType.PORTFOLIO_MANAGER: "portfolio",
    }

    def __init__(
        self,
        templates_dir: str | Path | None = None,
        validator: PromptValidator | None = None,
        version_manager: PromptVersionManager | None = None,
    ) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        self.templates_dir = Path(templates_dir)
        self.validator = validator or PromptValidator()
        self.version_manager = version_manager or PromptVersionManager()

        self._cache: dict[tuple[AgentType, str], PromptTemplate] = {}
        self._default_templates: dict[AgentType, PromptTemplate] = {}

        self.load_all_templates()

    def load_template_from_dir(self, agent_type: AgentType, folder_name: str) -> PromptTemplate:
        """
        Load system prompt, examples, output_schema, and metadata from disk directory.

        Args:
            agent_type (AgentType): Specialized agent role.
            folder_name (str): Directory name under templates/.

        Returns:
            PromptTemplate: Loaded template entity.
        """
        dir_path = self.templates_dir / folder_name
        system_file = dir_path / "system.md"
        examples_file = dir_path / "examples.md"
        schema_file = dir_path / "output_schema.json"
        meta_file = dir_path / "metadata.yaml"

        # System prompt text
        if system_file.exists():
            system_text = system_file.read_text(encoding="utf-8")
        else:
            system_text = f"You are a specialized financial analyst for {agent_type.value}."

        # Examples text
        examples_text = ""
        if examples_file.exists():
            examples_text = examples_file.read_text(encoding="utf-8")

        # Output schema
        output_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "recommendation": {"type": "string"},
                "score": {"type": "number"},
                "confidence": {"type": "number"},
                "reasoning": {"type": "string"},
            },
            "required": ["recommendation", "score", "confidence", "reasoning"],
        }
        if schema_file.exists():
            try:
                output_schema = json.loads(schema_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        # Metadata
        metadata: dict[str, Any] = {"version": "1.0.0", "author": "HedgeFundAI"}
        if meta_file.exists():
            lines = meta_file.read_text(encoding="utf-8").splitlines()
            for line in lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip()

        version_str = metadata.get("version", "1.0.0")

        # Combine system prompt with examples if present
        full_system_text = system_text
        if examples_text:
            full_system_text += f"\n\n## Examples\n{examples_text}"

        template = PromptTemplate(
            agent_type=agent_type,
            system_prompt_location=str(system_file),
            system_prompt_text=full_system_text,
            output_schema=output_schema,
            metadata=metadata,
        )

        # Validate template
        self.validator.validate_output_schema(template.output_schema)
        self.version_manager.record_version(
            agent_type, version_str, f"Loaded template from {dir_path}"
        )

        return template

    def load_all_templates(self) -> None:
        """Scan templates directory and cache all template folders."""
        for agent_type, folder in self.AGENT_FOLDER_MAP.items():
            dir_path = self.templates_dir / folder
            if dir_path.exists():
                tmpl = self.load_template_from_dir(agent_type, folder)
                ver = tmpl.metadata.get("version", "1.0.0")
                self._cache[(agent_type, ver)] = tmpl
                self._default_templates[agent_type] = tmpl

    def register(self, template: PromptTemplate) -> None:
        """Register or override a PromptTemplate in memory cache."""
        ver = template.metadata.get("version", "1.0.0")
        self._cache[(template.agent_type, ver)] = template
        self._default_templates[template.agent_type] = template

    def get_template(self, agent_type: AgentType, version: str | None = None) -> PromptTemplate:
        """
        Fetch PromptTemplate by AgentType and optional version lookup string.

        Args:
            agent_type (AgentType): Specialized agent role.
            version (str | None): Optional target version string (e.g. '1.0.0').

        Returns:
            PromptTemplate: Target cached template entity.
        """
        if version:
            key = (agent_type, version)
            if key in self._cache:
                return self._cache[key]

        if agent_type in self._default_templates:
            return self._default_templates[agent_type]

        raise KeyError(
            f"No PromptTemplate registered for AgentType '{agent_type.value}' version '{version}'."
        )
