from __future__ import annotations

import threading
import statistics

from time import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RequestMetric:

    timestamp: float

    module: str

    provider: str

    method: str

    url: str

    success: bool

    status_code: Optional[int]

    response_time_ms: float

    retry_count: int = 0

    cache_hit: bool = False

    proxy_used: bool = False

    error_message: Optional[str] = None

    response_size_bytes: int = 0

    def to_dict(self) -> dict:

        return {
            "timestamp": self.timestamp,
            "module": self.module,
            "provider": self.provider,
            "method": self.method,
            "url": self.url,
            "success": self.success,
            "status_code": self.status_code,
            "response_time_ms": round(
                self.response_time_ms,
                2
            ),
            "retry_count": self.retry_count,
            "cache_hit": self.cache_hit,
            "proxy_used": self.proxy_used,
            "error_message": self.error_message,
            "response_size_bytes": self.response_size_bytes,
        }


@dataclass
class ProviderStatistics:

    provider: str

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    cache_hits: int = 0

    retries: int = 0

    average_response_time_ms: float = 0.0

    fastest_response_ms: float = 0.0

    slowest_response_ms: float = 0.0

    success_rate: float = 0.0

    def to_dict(self) -> dict:

        return {
            "provider": self.provider,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "cache_hits": self.cache_hits,
            "retries": self.retries,
            "average_response_time_ms": round(
                self.average_response_time_ms,
                2
            ),
            "fastest_response_ms": round(
                self.fastest_response_ms,
                2
            ),
            "slowest_response_ms": round(
                self.slowest_response_ms,
                2
            ),
            "success_rate": round(
                self.success_rate,
                2
            ),
        }


class RequestMetrics:

    def __init__(self):

        self._metrics: List[RequestMetric] = []

        self._lock = threading.Lock()

        self.started_at = time()

    def record(
        self,
        module: str,
        provider: str,
        method: str,
        url: str,
        success: bool,
        status_code: Optional[int],
        response_time_ms: float,
        retry_count: int = 0,
        cache_hit: bool = False,
        proxy_used: bool = False,
        error_message: Optional[str] = None,
        response_size_bytes: int = 0,
    ) -> None:

        metric = RequestMetric(
            timestamp=time(),
            module=module,
            provider=provider,
            method=method,
            url=url,
            success=success,
            status_code=status_code,
            response_time_ms=response_time_ms,
            retry_count=retry_count,
            cache_hit=cache_hit,
            proxy_used=proxy_used,
            error_message=error_message,
            response_size_bytes=response_size_bytes,
        )

        with self._lock:
            self._metrics.append(metric)

    def clear(self) -> None:

        with self._lock:
            self._metrics.clear()

    def count(self) -> int:

        return len(self._metrics)

    def get_all(self) -> List[RequestMetric]:

        return list(self._metrics)

    def get_successful(self) -> List[RequestMetric]:

        return [
            metric
            for metric in self._metrics
            if metric.success
        ]

    def get_failed(self) -> List[RequestMetric]:

        return [
            metric
            for metric in self._metrics
            if not metric.success
        ]

    def get_cache_hits(self) -> List[RequestMetric]:

        return [
            metric
            for metric in self._metrics
            if metric.cache_hit
        ]

    def get_provider_statistics(
        self,
        provider: str
    ) -> ProviderStatistics:

        provider_metrics = [
            metric
            for metric in self._metrics
            if metric.provider == provider
        ]

        if not provider_metrics:

            return ProviderStatistics(
                provider=provider
            )

        total = len(provider_metrics)

        successful = sum(
            1
            for metric in provider_metrics
            if metric.success
        )

        failed = total - successful

        cache_hits = sum(
            1
            for metric in provider_metrics
            if metric.cache_hit
        )

        retries = sum(
            metric.retry_count
            for metric in provider_metrics
        )

        response_times = [
            metric.response_time_ms
            for metric in provider_metrics
        ]

        success_rate = (
            successful / total * 100
        )

        return ProviderStatistics(
            provider=provider,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            cache_hits=cache_hits,
            retries=retries,
            average_response_time_ms=statistics.mean(
                response_times
            ),
            fastest_response_ms=min(
                response_times
            ),
            slowest_response_ms=max(
                response_times
            ),
            success_rate=success_rate,
        )

    def get_all_provider_statistics(
        self
    ) -> Dict[str, dict]:

        providers = {
            metric.provider
            for metric in self._metrics
        }

        return {
            provider: self.get_provider_statistics(
                provider
            ).to_dict()
            for provider in providers
        }

    def get_global_statistics(
        self
    ) -> dict:

        total_requests = len(
            self._metrics
        )

        successful_requests = len(
            self.get_successful()
        )

        failed_requests = len(
            self.get_failed()
        )

        cache_hits = len(
            self.get_cache_hits()
        )

        total_retries = sum(
            metric.retry_count
            for metric in self._metrics
        )

        response_times = [
            metric.response_time_ms
            for metric in self._metrics
        ]

        average_response_time = (
            statistics.mean(response_times)
            if response_times
            else 0
        )

        uptime_seconds = (
            time() - self.started_at
        )

        return {
            "uptime_seconds": round(
                uptime_seconds,
                2
            ),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "cache_hits": cache_hits,
            "total_retries": total_retries,
            "success_rate": round(
                (
                    successful_requests /
                    total_requests * 100
                )
                if total_requests
                else 0,
                2
            ),
            "average_response_time_ms": round(
                average_response_time,
                2
            ),
        }

    def get_top_fastest_providers(
        self,
        limit: int = 10
    ) -> List[dict]:

        providers = []

        for provider in {
            metric.provider
            for metric in self._metrics
        }:

            stats = self.get_provider_statistics(
                provider
            )

            providers.append(
                stats.to_dict()
            )

        providers.sort(
            key=lambda x: x[
                "average_response_time_ms"
            ]
        )

        return providers[:limit]

    def get_top_slowest_providers(
        self,
        limit: int = 10
    ) -> List[dict]:

        providers = []

        for provider in {
            metric.provider
            for metric in self._metrics
        }:

            stats = self.get_provider_statistics(
                provider
            )

            providers.append(
                stats.to_dict()
            )

        providers.sort(
            key=lambda x: x[
                "average_response_time_ms"
            ],
            reverse=True
        )

        return providers[:limit]

    def export_json(self) -> List[dict]:

        return [
            metric.to_dict()
            for metric in self._metrics
        ]