"""
Base Validator Interface for Market Data Infrastructure.

Reusable validation filter ensuring raw provider responses are valid before
reaching normalizers and mappers.
"""

from typing import Any

from packages.infrastructure.market_data.exceptions import ValidationMarketDataError


class ResponseValidator:
    """
    Generic Response Payload Validator.
    """

    @staticmethod
    def ensure_dict(payload: Any, context: str = "Payload") -> dict[str, Any]:
        """Validate payload is a dictionary."""
        if not isinstance(payload, dict):
            raise ValidationMarketDataError(
                f"{context} must be a dictionary object (got {type(payload).__name__}).",
                details={"payload": str(payload)},
            )
        return payload

    @staticmethod
    def ensure_list(payload: Any, context: str = "Payload") -> list[Any]:
        """Validate payload is a list."""
        if not isinstance(payload, list):
            raise ValidationMarketDataError(
                f"{context} must be a list (got {type(payload).__name__}).",
                details={"payload": str(payload)},
            )
        return payload

    @staticmethod
    def ensure_required_keys(
        payload: dict[str, Any], keys: list[str], context: str = "Payload"
    ) -> None:
        """Validate presence of required key fields."""
        missing = [k for k in keys if k not in payload or payload[k] is None]
        if missing:
            raise ValidationMarketDataError(
                f"{context} is missing required fields: {missing}.",
                details={"missing_keys": missing, "payload": payload},
            )

    @staticmethod
    def ensure_numeric(val: Any, name: str = "Value") -> None:
        """Validate value can be converted to numeric float/decimal."""
        try:
            float(str(val))
        except (ValueError, TypeError) as err:
            raise ValidationMarketDataError(
                f"{name} must be numeric (got {val}).",
                details={"value": str(val)},
            ) from err
