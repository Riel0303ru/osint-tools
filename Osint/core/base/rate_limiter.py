# core/base/rate_limiter.py

from __future__ import annotations

import asyncio
import threading
import time

from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(slots=True)
class HostRateRule:

    requests: int
    period: int

    burst_capacity: int = 0

    cooldown_seconds: int = 0


@dataclass(slots=True)
class RateLimitStats:

    allowed_requests: int = 0

    blocked_requests: int = 0

    cooldown_hits: int = 0

    burst_consumed: int = 0

    total_sleep_time: float = 0.0

    host_statistics: Dict[str, dict] = field(default_factory=dict)


class TokenBucket:

    def __init__(
        self,
        capacity: int,
        refill_rate: float
    ):

        self.capacity = capacity

        self.tokens = float(capacity)

        self.refill_rate = refill_rate

        self.last_refill = time.time()

        self._lock = threading.Lock()

    def consume(
        self,
        tokens: float = 1.0
    ) -> bool:

        with self._lock:

            self._refill()

            if self.tokens >= tokens:

                self.tokens -= tokens

                return True

            return False

    def _refill(self):

        now = time.time()

        elapsed = now - self.last_refill

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )

        self.last_refill = now

    def get_tokens(self) -> float:

        with self._lock:

            self._refill()

            return round(self.tokens, 2)


class SlidingWindowLimiter:

    def __init__(
        self,
        max_requests: int,
        period_seconds: int
    ):

        self.max_requests = max_requests

        self.period_seconds = period_seconds

        self.requests = deque()

        self._lock = threading.Lock()

    def allow(self) -> bool:

        with self._lock:

            now = time.time()

            while (
                self.requests
                and
                now - self.requests[0] > self.period_seconds
            ):
                self.requests.popleft()

            if len(self.requests) >= self.max_requests:
                return False

            self.requests.append(now)

            return True

    def count(self) -> int:

        with self._lock:

            now = time.time()

            while (
                self.requests
                and
                now - self.requests[0] > self.period_seconds
            ):
                self.requests.popleft()

            return len(self.requests)


class RateLimiter:

    def __init__(

        self,

        global_requests: int = 500,

        global_period: int = 60,

        burst_capacity: int = 100,

        burst_refill_rate: float = 20.0

    ):

        self.global_limiter = SlidingWindowLimiter(
            global_requests,
            global_period
        )

        self.global_bucket = TokenBucket(
            burst_capacity,
            burst_refill_rate
        )

        self.host_limiters: Dict[
            str,
            SlidingWindowLimiter
        ] = {}

        self.host_rules: Dict[
            str,
            HostRateRule
        ] = {}

        self.cooldowns: Dict[
            str,
            float
        ] = {}

        self.stats = RateLimitStats()

        self._lock = threading.Lock()

    def register_host(

        self,

        host: str,

        requests: int,

        period: int,

        burst_capacity: int = 0,

        cooldown_seconds: int = 30

    ):

        self.host_rules[host] = HostRateRule(
            requests=requests,
            period=period,
            burst_capacity=burst_capacity,
            cooldown_seconds=cooldown_seconds
        )

        self.host_limiters[host] = SlidingWindowLimiter(
            requests,
            period
        )

    def is_host_cooling_down(
        self,
        host: str
    ) -> bool:

        if host not in self.cooldowns:
            return False

        return time.time() < self.cooldowns[host]

    def trigger_cooldown(
        self,
        host: str,
        seconds: Optional[int] = None
    ):

        rule = self.host_rules.get(host)

        cooldown = (
            seconds
            if seconds is not None
            else (
                rule.cooldown_seconds
                if rule
                else 30
            )
        )

        self.cooldowns[host] = (
            time.time() + cooldown
        )

    def acquire(
        self,
        host: Optional[str] = None
    ) -> bool:

        with self._lock:

            if not self.global_limiter.allow():

                self.stats.blocked_requests += 1

                return False

            if not self.global_bucket.consume():

                self.stats.blocked_requests += 1

                return False

            if host:

                if self.is_host_cooling_down(host):

                    self.stats.cooldown_hits += 1

                    return False

                limiter = self.host_limiters.get(host)

                if limiter:

                    if not limiter.allow():

                        self.stats.blocked_requests += 1

                        return False

            self.stats.allowed_requests += 1

            return True

    async def wait_for_slot(
        self,
        host: Optional[str] = None,
        retry_delay: float = 1.0
    ):

        total_wait = 0.0

        while True:

            if self.acquire(host):
                break

            await asyncio.sleep(retry_delay)

            total_wait += retry_delay

        self.stats.total_sleep_time += total_wait

    def report_response(

        self,

        host: str,

        status_code: int

    ):

        if status_code == 429:

            self.trigger_cooldown(
                host,
                120
            )

        elif status_code == 403:

            self.trigger_cooldown(
                host,
                60
            )

    def get_host_usage(
        self,
        host: str
    ) -> dict:

        limiter = self.host_limiters.get(host)

        if not limiter:

            return {}

        return {
            "requests_in_window":
                limiter.count(),
            "limit":
                limiter.max_requests,
            "period":
                limiter.period_seconds,
            "cooldown":
                self.is_host_cooling_down(host)
        }

    def get_stats(self) -> dict:

        hosts = {}

        for host in self.host_limiters:

            hosts[host] = self.get_host_usage(
                host
            )

        return {
            "allowed_requests":
                self.stats.allowed_requests,

            "blocked_requests":
                self.stats.blocked_requests,

            "cooldown_hits":
                self.stats.cooldown_hits,

            "burst_tokens_remaining":
                self.global_bucket.get_tokens(),

            "total_sleep_time":
                round(
                    self.stats.total_sleep_time,
                    2
                ),

            "active_hosts":
                len(self.host_limiters),

            "hosts":
                hosts
        }

    def reset(self):

        self.stats = RateLimitStats()

        self.cooldowns.clear()

    def __repr__(self):

        return (
            f"RateLimiter("
            f"allowed={self.stats.allowed_requests}, "
            f"blocked={self.stats.blocked_requests}, "
            f"hosts={len(self.host_limiters)})"
        )