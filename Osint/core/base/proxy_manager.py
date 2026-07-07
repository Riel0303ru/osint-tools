# core/base/proxy_manager.py

from __future__ import annotations

import random
import threading
import time

from dataclasses import dataclass, field
from typing import Dict
from typing import List
from typing import Optional


@dataclass(slots=True)
class ProxyInfo:

    proxy_id: str

    proxy_url: str

    proxy_type: str = "http"

    country: Optional[str] = None

    city: Optional[str] = None

    provider: Optional[str] = None

    username: Optional[str] = None

    password: Optional[str] = None

    enabled: bool = True

    healthy: bool = True

    anonymous: bool = False

    last_used: float = 0.0

    last_checked: float = 0.0

    response_time: float = 0.0

    success_count: int = 0

    failure_count: int = 0

    cooldown_until: float = 0.0

    tags: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)

    @property
    def total_requests(self) -> int:

        return (
            self.success_count +
            self.failure_count
        )

    @property
    def success_rate(self) -> float:

        total = self.total_requests

        if total == 0:
            return 1.0

        return self.success_count / total

    @property
    def is_available(self) -> bool:

        if not self.enabled:
            return False

        if not self.healthy:
            return False

        if time.time() < self.cooldown_until:
            return False

        return True


class ProxyManager:

    def __init__(self):

        self._lock = threading.RLock()

        self.proxies: Dict[
            str,
            ProxyInfo
        ] = {}

        self.rotation_index = 0

    def add_proxy(

        self,

        proxy_id: str,

        proxy_url: str,

        proxy_type: str = "http",

        country: Optional[str] = None,

        city: Optional[str] = None,

        provider: Optional[str] = None,

        tags: Optional[List[str]] = None

    ) -> ProxyInfo:

        proxy = ProxyInfo(

            proxy_id=proxy_id,

            proxy_url=proxy_url,

            proxy_type=proxy_type,

            country=country,

            city=city,

            provider=provider,

            tags=tags or []
        )

        with self._lock:

            self.proxies[
                proxy_id
            ] = proxy

        return proxy

    def remove_proxy(
        self,
        proxy_id: str
    ) -> bool:

        with self._lock:

            if proxy_id not in self.proxies:
                return False

            del self.proxies[proxy_id]

            return True

    def get_proxy(
        self,
        proxy_id: str
    ) -> Optional[ProxyInfo]:

        return self.proxies.get(proxy_id)

    def list_proxies(
        self
    ) -> List[ProxyInfo]:

        return list(
            self.proxies.values()
        )

    def get_available_proxies(
        self
    ) -> List[ProxyInfo]:

        return [

            proxy

            for proxy in self.proxies.values()

            if proxy.is_available
        ]

    def get_random_proxy(
        self
    ) -> Optional[ProxyInfo]:

        proxies = self.get_available_proxies()

        if not proxies:
            return None

        return random.choice(proxies)

    def get_round_robin_proxy(
        self
    ) -> Optional[ProxyInfo]:

        proxies = self.get_available_proxies()

        if not proxies:
            return None

        proxy = proxies[
            self.rotation_index % len(proxies)
        ]

        self.rotation_index += 1

        return proxy

    def get_best_proxy(
        self
    ) -> Optional[ProxyInfo]:

        proxies = self.get_available_proxies()

        if not proxies:
            return None

        proxies.sort(
            key=lambda p: (
                p.success_rate,
                -p.response_time
            ),
            reverse=True
        )

        return proxies[0]

    def get_proxy_by_country(
        self,
        country: str
    ) -> Optional[ProxyInfo]:

        candidates = [

            proxy

            for proxy in self.get_available_proxies()

            if (
                proxy.country and
                proxy.country.lower() ==
                country.lower()
            )
        ]

        if not candidates:
            return None

        return random.choice(
            candidates
        )

    def get_proxy_by_tag(
        self,
        tag: str
    ) -> Optional[ProxyInfo]:

        candidates = []

        for proxy in self.get_available_proxies():

            if tag.lower() in [

                t.lower()

                for t in proxy.tags

            ]:

                candidates.append(proxy)

        if not candidates:
            return None

        return random.choice(
            candidates
        )

    def mark_success(

        self,

        proxy_id: str,

        response_time: float

    ):

        proxy = self.proxies.get(
            proxy_id
        )

        if not proxy:
            return

        proxy.success_count += 1

        proxy.response_time = response_time

        proxy.last_used = time.time()

        proxy.healthy = True

    def mark_failure(

        self,

        proxy_id: str,

        cooldown_seconds: int = 60

    ):

        proxy = self.proxies.get(
            proxy_id
        )

        if not proxy:
            return

        proxy.failure_count += 1

        proxy.last_used = time.time()

        proxy.cooldown_until = (
            time.time() +
            cooldown_seconds
        )

        if proxy.failure_count >= 5:

            proxy.healthy = False

    def recover_proxy(
        self,
        proxy_id: str
    ):

        proxy = self.proxies.get(
            proxy_id
        )

        if not proxy:
            return

        proxy.healthy = True

        proxy.cooldown_until = 0

    def disable_proxy(
        self,
        proxy_id: str
    ):

        proxy = self.proxies.get(
            proxy_id
        )

        if proxy:

            proxy.enabled = False

    def enable_proxy(
        self,
        proxy_id: str
    ):

        proxy = self.proxies.get(
            proxy_id
        )

        if proxy:

            proxy.enabled = True

    def build_httpx_proxy_dict(
        self,
        proxy: ProxyInfo
    ) -> Dict:

        return {

            "http://":
                proxy.proxy_url,

            "https://":
                proxy.proxy_url
        }

    def export_statistics(
        self
    ) -> Dict:

        total = len(
            self.proxies
        )

        active = len(
            self.get_available_proxies()
        )

        healthy = len([

            p

            for p in self.proxies.values()

            if p.healthy

        ])

        unhealthy = total - healthy

        return {

            "total_proxies":
                total,

            "active_proxies":
                active,

            "healthy_proxies":
                healthy,

            "unhealthy_proxies":
                unhealthy,

            "rotation_index":
                self.rotation_index
        }

    def reset_statistics(
        self
    ):

        for proxy in self.proxies.values():

            proxy.success_count = 0

            proxy.failure_count = 0

            proxy.response_time = 0.0

            proxy.cooldown_until = 0

            proxy.healthy = True

    def __len__(
        self
    ):

        return len(
            self.proxies
        )

    def __repr__(
        self
    ):

        return (
            f"ProxyManager("
            f"proxies={len(self.proxies)})"
        )