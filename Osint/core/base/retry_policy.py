from __future__ import annotations

import asyncio
import random
import time

from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
    Tuple,
    Type
)


@dataclass
class RetryStatistics:

    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0

    total_delay_seconds: float = 0.0

    last_error: Optional[str] = None

    def to_dict(self) -> dict:

        return {
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "total_delay_seconds": round(
                self.total_delay_seconds,
                3
            ),
            "last_error": self.last_error,
        }


@dataclass
class RetryConfig:

    max_retries: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    backoff_factor: float = 2.0

    use_jitter: bool = True

    retry_status_codes: Tuple[int, ...] = (
        429,
        500,
        502,
        503,
        504,
    )

    retry_exceptions: Tuple[Type[Exception], ...] = (
        TimeoutError,
        ConnectionError,
        OSError,
    )


class RetryPolicy:

    def __init__(
        self,
        config: Optional[RetryConfig] = None
    ):

        self.config = config or RetryConfig()

        self.stats = RetryStatistics()

    def reset_statistics(self) -> None:

        self.stats = RetryStatistics()

    def get_statistics(self) -> dict:

        return self.stats.to_dict()

    def should_retry_status(
        self,
        status_code: Optional[int]
    ) -> bool:

        if status_code is None:
            return False

        return status_code in self.config.retry_status_codes

    def calculate_delay(
        self,
        attempt_number: int
    ) -> float:

        delay = (
            self.config.base_delay *
            (
                self.config.backoff_factor **
                max(0, attempt_number - 1)
            )
        )

        delay = min(
            delay,
            self.config.max_delay
        )

        if self.config.use_jitter:

            jitter = random.uniform(
                0,
                delay * 0.25
            )

            delay += jitter

        return round(delay, 3)

    def execute_sync(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:

        last_exception = None

        for attempt in range(
            1,
            self.config.max_retries + 2
        ):

            self.stats.total_attempts += 1

            try:

                result = func(
                    *args,
                    **kwargs
                )

                self.stats.successful_attempts += 1

                return result

            except self.config.retry_exceptions as exc:

                last_exception = exc

                self.stats.last_error = str(exc)

                if attempt > self.config.max_retries:
                    break

                delay = self.calculate_delay(
                    attempt
                )

                self.stats.total_delay_seconds += delay

                time.sleep(delay)

            except Exception as exc:

                self.stats.failed_attempts += 1

                self.stats.last_error = str(exc)

                raise

        self.stats.failed_attempts += 1

        raise last_exception

    async def execute_async(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:

        last_exception = None

        for attempt in range(
            1,
            self.config.max_retries + 2
        ):

            self.stats.total_attempts += 1

            try:

                result = await func(
                    *args,
                    **kwargs
                )

                self.stats.successful_attempts += 1

                return result

            except self.config.retry_exceptions as exc:

                last_exception = exc

                self.stats.last_error = str(exc)

                if attempt > self.config.max_retries:
                    break

                delay = self.calculate_delay(
                    attempt
                )

                self.stats.total_delay_seconds += delay

                await asyncio.sleep(delay)

            except Exception as exc:

                self.stats.failed_attempts += 1

                self.stats.last_error = str(exc)

                raise

        self.stats.failed_attempts += 1

        raise last_exception

    async def execute_http_async(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:

        last_response = None
        last_exception = None

        for attempt in range(
            1,
            self.config.max_retries + 2
        ):

            self.stats.total_attempts += 1

            try:

                response = await func(
                    *args,
                    **kwargs
                )

                last_response = response

                status_code = getattr(
                    response,
                    "status_code",
                    None
                )

                if self.should_retry_status(
                    status_code
                ):

                    if attempt > self.config.max_retries:

                        self.stats.failed_attempts += 1

                        return response

                    delay = self.calculate_delay(
                        attempt
                    )

                    self.stats.total_delay_seconds += delay

                    await asyncio.sleep(delay)

                    continue

                self.stats.successful_attempts += 1

                return response

            except self.config.retry_exceptions as exc:

                last_exception = exc

                self.stats.last_error = str(exc)

                if attempt > self.config.max_retries:
                    break

                delay = self.calculate_delay(
                    attempt
                )

                self.stats.total_delay_seconds += delay

                await asyncio.sleep(delay)

        self.stats.failed_attempts += 1

        if last_exception:
            raise last_exception

        return last_response

    def execute_http_sync(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:

        last_response = None
        last_exception = None

        for attempt in range(
            1,
            self.config.max_retries + 2
        ):

            self.stats.total_attempts += 1

            try:

                response = func(
                    *args,
                    **kwargs
                )

                last_response = response

                status_code = getattr(
                    response,
                    "status_code",
                    None
                )

                if self.should_retry_status(
                    status_code
                ):

                    if attempt > self.config.max_retries:

                        self.stats.failed_attempts += 1

                        return response

                    delay = self.calculate_delay(
                        attempt
                    )

                    self.stats.total_delay_seconds += delay

                    time.sleep(delay)

                    continue

                self.stats.successful_attempts += 1

                return response

            except self.config.retry_exceptions as exc:

                last_exception = exc

                self.stats.last_error = str(exc)

                if attempt > self.config.max_retries:
                    break

                delay = self.calculate_delay(
                    attempt
                )

                self.stats.total_delay_seconds += delay

                time.sleep(delay)

        self.stats.failed_attempts += 1

        if last_exception:
            raise last_exception

        return last_response