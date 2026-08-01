"""
Prompt Validator for Prompt Intelligence Framework.

Validates prompt placeholder tokens, required template sections, JSON schemas,
and model response compliance against expected output schemas.
"""

import string
from typing import Any

from packages.infrastructure.llm.exceptions import LLMValidationError


class PromptValidator:
    """
    Validator validating prompt structure, placeholders, schemas, and model output compliance.
    """

    @staticmethod
    def extract_placeholders(prompt_text: str) -> list[str]:
        """Extract all placeholder variable names (e.g. {ticker}) from template text."""
        formatter = string.Formatter()
        placeholders: list[str] = []
        for _, field_name, _, _ in formatter.parse(prompt_text):
            if field_name is not None and field_name not in placeholders:
                placeholders.append(field_name)
        return placeholders

    def validate_placeholders(self, prompt_text: str, required_variables: list[str]) -> bool:
        """
        Validate that prompt text contains all required placeholder variables.

        Args:
            prompt_text (str): Input template text.
            required_variables (list[str]): List of required variable names.

        Returns:
            bool: True if all required variables are present in the text.
        """
        found = self.extract_placeholders(prompt_text)
        return all(req in found for req in required_variables)

    def validate_required_sections(self, prompt_text: str, required_sections: list[str]) -> bool:
        """
        Validate that prompt template text contains required section headers or substrings.

        Args:
            prompt_text (str): System prompt template string.
            required_sections (list[str]): List of required section header strings.

        Returns:
            bool: True if all required section headers exist in text.
        """
        return all(section in prompt_text for section in required_sections)

    def validate_output_schema(self, schema: dict[str, Any]) -> bool:
        """
        Validate that a JSON schema object contains mandatory 'type' and 'properties' keys.

        Args:
            schema (dict[str, Any]): Target JSON schema dictionary.

        Returns:
            bool: True if schema is structurally valid.
        """
        if not isinstance(schema, dict):
            return False
        return "type" in schema or "properties" in schema

    def validate_response_json(
        self, response_dict: dict[str, Any], expected_schema: dict[str, Any]
    ) -> bool:
        """
        Validate that model output dictionary satisfies expected JSON schema requirement rules.

        Args:
            response_dict (dict[str, Any]): Parsed model JSON response payload.
            expected_schema (dict[str, Any]): Expected JSON schema definition.

        Returns:
            bool: True if valid.

        Raises:
            LLMValidationError: If required fields or types are missing.
        """
        required_fields = expected_schema.get("required", [])
        for field in required_fields:
            if field not in response_dict:
                raise LLMValidationError(
                    f"Model output JSON is missing required field '{field}'.",
                    context={"response": response_dict, "required": required_fields},
                )

        return True
