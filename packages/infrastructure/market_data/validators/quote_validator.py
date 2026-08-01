"""
Specific Response Validators for Quote, Fundamental, News, Macro, and Corporate Action payloads.
"""

from typing import Any

from packages.infrastructure.market_data.validators.base_validator import ResponseValidator


class QuoteValidator(ResponseValidator):
    """Validator for Quote and Historical Candle responses."""

    @classmethod
    def validate_quote(cls, payload: Any) -> dict[str, Any]:
        d = cls.ensure_dict(payload, "Quote payload")
        # Ensure at least one price field is present
        if "price" in d:
            cls.ensure_numeric(d["price"], "price")
        elif "close" in d:
            cls.ensure_numeric(d["close"], "close price")
        elif "last_price" in d:
            cls.ensure_numeric(d["last_price"], "last_price")
        return d

    @classmethod
    def validate_candles(cls, payload: Any) -> list[Any]:
        items = cls.ensure_list(payload, "Candles payload")
        for idx, item in enumerate(items):
            d = cls.ensure_dict(item, f"Candle item [{idx}]")
            for price_key in ("open", "high", "low", "close"):
                if price_key in d:
                    cls.ensure_numeric(d[price_key], f"Candle [{idx}] {price_key}")
        return items


class FundamentalValidator(ResponseValidator):
    """Validator for Balance Sheet, Income Statement, Cash Flow, and Key Metrics payloads."""

    @classmethod
    def validate_financials(cls, payload: Any) -> list[Any] | dict[str, Any]:
        if isinstance(payload, list):
            return [cls.ensure_dict(item, "Financial statement item") for item in payload]
        return cls.ensure_dict(payload, "Financial statement payload")


class NewsValidator(ResponseValidator):
    """Validator for News and Sentiment payloads."""

    @classmethod
    def validate_news(cls, payload: Any) -> list[Any]:
        items = cls.ensure_list(payload, "News payload")
        for idx, item in enumerate(items):
            cls.ensure_dict(item, f"News item [{idx}]")
        return items


class MacroValidator(ResponseValidator):
    """Validator for Macroeconomic Series & Calendar payloads."""

    @classmethod
    def validate_macro(cls, payload: Any) -> list[Any] | dict[str, Any]:
        if isinstance(payload, list):
            return [cls.ensure_dict(item, "Macro series item") for item in payload]
        return cls.ensure_dict(payload, "Macro payload")


class CorporateActionValidator(ResponseValidator):
    """Validator for Corporate Actions payloads."""

    @classmethod
    def validate_corporate_actions(cls, payload: Any) -> list[Any]:
        items = cls.ensure_list(payload, "Corporate actions payload")
        for idx, item in enumerate(items):
            cls.ensure_dict(item, f"Corporate action item [{idx}]")
        return items
