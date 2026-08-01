"""
Retry Policy & Exponential Backoff for Market Data Infrastructure.

Provides retry mechanisms filtering for transient network and server errors while
failing fast on validation, business, and unsupported capability errors.
"""

import time
from collections.abc import Callable
from typing import TypeVar

from packages.infrastructure.market_data.exceptions import (
    FeatureNotSupportedError,
    ProviderCapabilityError,
    ProviderConnectionError,
    ProviderTimeoutError,
    ValidationMarketDataError,
)

T = TypeVar("T")


class RetryPolicy:
    """
    Exponential backoff retry policy for market data provider calls.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_sec: float = 0.5,
        backoff_factor: float = 2.0,
        max_delay_sec: float = 5.0,
    ) -> None:
        self.max_retries = max_retries
        self.initial_delay_sec = initial_delay_sec
        self.backoff_factor = backoff_factor
        self.max_delay_sec = max_delay_sec

    def execute(self, func: Callable[[], T]) -> T:
        """
        Execute a function with exponential backoff retries for transient errors.

        Args:
            func (Callable[[], T]): Function execution closure.

        Returns:
            T: Function result payload.

        Raises:
            Exception: Re-raises immediately on non-transient errors or when max retries exceeded.
        """
        delay = self.initial_delay_sec
        attempts = 0

        while True:
            try:
                attempts += 1
                return func()
            except (
                FeatureNotSupportedError,
                ProviderCapabilityError,
                ValidationMarketDataError,
                ValueError,
                TypeError,
            ) as err:
                # Never retry validation or unsupported feature errors
                raise err
            except (
                ProviderConnectionError,
                ProviderTimeoutError,
                TimeoutError,
                ConnectionError,
            ) as err:
                if attempts > self.max_retries:
                    raise err
                time.sleep(delay)
                delay = min(delay * self.backoff_factor, self.max_delay_sec)
            except Exception as err:
                # Fail fast on unspecified non-transient errors
                if attempts > self.max_retries:
                    raise err
                time.sleep(delay)
                delay = min(delay * self.backoff_factor, self.max_delay_sec)
