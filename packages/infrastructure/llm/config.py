"""
LLM Configuration for Infrastructure Layer.

Defines Pydantic configuration settings for Gemini and foundation model providers.
Reads environment variables prefixed with 'GEMINI_' or 'LLM_'.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """
    LLM Provider Configuration Model.

    Attributes:
        api_key (str): Gemini API key string.
        model_name (str): Gemini model identifier.
        timeout_seconds (float): Execution timeout limit in seconds.
        max_retries (int): Maximum exponential backoff retry attempts.
        backoff_factor (float): Retry exponential backoff multiplier.
        temperature (float): Model sampling temperature.
        top_p (float): Model top_p nucleus sampling threshold.
        enabled (bool): Provider activation flag.
    """

    api_key: str = Field(default="mock_gemini_api_key", validation_alias="GEMINI_API_KEY")
    model_name: str = Field(default="gemini-1.5-pro", validation_alias="GEMINI_MODEL_NAME")
    timeout_seconds: float = Field(default=30.0, validation_alias="LLM_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, validation_alias="LLM_MAX_RETRIES")
    backoff_factor: float = Field(default=2.0, validation_alias="LLM_BACKOFF_FACTOR")
    temperature: float = Field(default=0.2, validation_alias="LLM_TEMPERATURE")
    top_p: float = Field(default=0.95, validation_alias="LLM_TOP_P")
    enabled: bool = Field(default=False, validation_alias="LLM_ENABLED")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
