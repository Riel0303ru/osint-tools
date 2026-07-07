from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List

import httpx


@dataclass
class SessionInfo:
    session_id: str
    created_at: float
    last_used: float
    request_count: int = 0
    error_count: int = 0
    active: bool = True


class SessionManager:

    def __init__(
        self,
        timeout: int = 30,
        verify_ssl: bool = True,
        http2: bool = True,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: int = 60
    ):

        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.http2 = http2

        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry

        self._sync_sessions: Dict[str, httpx.Client] = {}
        self._async_sessions: Dict[str, httpx.AsyncClient] = {}

        self._metadata: Dict[str, SessionInfo] = {}

    def _build_limits(self) -> httpx.Limits:

        return httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry=self.keepalive_expiry
        )

    def create_session(
        self,
        session_id: str,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        proxy: Optional[str] = None
    ) -> httpx.Client:

        if session_id in self._sync_sessions:
            return self._sync_sessions[session_id]

        client = httpx.Client(
            timeout=self.timeout,
            verify=self.verify_ssl,
            http2=self.http2,
            headers=headers,
            cookies=cookies,
            proxy=proxy,
            limits=self._build_limits(),
            follow_redirects=True
        )

        self._sync_sessions[session_id] = client

        self._metadata[session_id] = SessionInfo(
            session_id=session_id,
            created_at=time.time(),
            last_used=time.time()
        )

        return client

    async def create_async_session(
        self,
        session_id: str,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        proxy: Optional[str] = None
    ) -> httpx.AsyncClient:

        if session_id in self._async_sessions:
            return self._async_sessions[session_id]

        client = httpx.AsyncClient(
            timeout=self.timeout,
            verify=self.verify_ssl,
            http2=self.http2,
            headers=headers,
            cookies=cookies,
            proxy=proxy,
            limits=self._build_limits(),
            follow_redirects=True
        )

        self._async_sessions[session_id] = client

        self._metadata[session_id] = SessionInfo(
            session_id=session_id,
            created_at=time.time(),
            last_used=time.time()
        )

        return client

    def get_session(
        self,
        session_id: str
    ) -> Optional[httpx.Client]:

        session = self._sync_sessions.get(session_id)

        if session:
            self.touch(session_id)

        return session

    def get_async_session(
        self,
        session_id: str
    ) -> Optional[httpx.AsyncClient]:

        session = self._async_sessions.get(session_id)

        if session:
            self.touch(session_id)

        return session

    def touch(self, session_id: str):

        if session_id not in self._metadata:
            return

        self._metadata[session_id].last_used = time.time()
        self._metadata[session_id].request_count += 1

    def register_error(
        self,
        session_id: str
    ):

        if session_id not in self._metadata:
            return

        self._metadata[session_id].error_count += 1

    def get_cookies(
        self,
        session_id: str
    ) -> Dict:

        session = self._sync_sessions.get(session_id)

        if not session:
            return {}

        return dict(session.cookies)

    def update_headers(
        self,
        session_id: str,
        headers: Dict
    ):

        session = self._sync_sessions.get(session_id)

        if not session:
            return

        session.headers.update(headers)

    async def update_async_headers(
        self,
        session_id: str,
        headers: Dict
    ):

        session = self._async_sessions.get(session_id)

        if not session:
            return

        session.headers.update(headers)

    def get_session_stats(
        self,
        session_id: str
    ) -> Optional[Dict]:

        meta = self._metadata.get(session_id)

        if not meta:
            return None

        age = time.time() - meta.created_at

        return {
            "session_id": meta.session_id,
            "age_seconds": round(age, 2),
            "request_count": meta.request_count,
            "error_count": meta.error_count,
            "active": meta.active
        }

    def list_sessions(self) -> List[Dict]:

        return [
            self.get_session_stats(session_id)
            for session_id in self._metadata.keys()
        ]

    def close_session(
        self,
        session_id: str
    ):

        session = self._sync_sessions.pop(
            session_id,
            None
        )

        if session:
            session.close()

        if session_id in self._metadata:
            self._metadata[session_id].active = False

    async def close_async_session(
        self,
        session_id: str
    ):

        session = self._async_sessions.pop(
            session_id,
            None
        )

        if session:
            await session.aclose()

        if session_id in self._metadata:
            self._metadata[session_id].active = False

    def close_all(self):

        for session in self._sync_sessions.values():
            session.close()

        self._sync_sessions.clear()

        for meta in self._metadata.values():
            meta.active = False

    async def close_all_async(self):

        await asyncio.gather(
            *[
                session.aclose()
                for session in self._async_sessions.values()
            ],
            return_exceptions=True
        )

        self._async_sessions.clear()

        for meta in self._metadata.values():
            meta.active = False

    def cleanup_idle_sessions(
        self,
        idle_seconds: int = 600
    ):

        now = time.time()

        to_remove = []

        for session_id, meta in self._metadata.items():

            idle_time = now - meta.last_used

            if idle_time > idle_seconds:
                to_remove.append(session_id)

        for session_id in to_remove:
            self.close_session(session_id)

    async def cleanup_idle_async_sessions(
        self,
        idle_seconds: int = 600
    ):

        now = time.time()

        to_remove = []

        for session_id, meta in self._metadata.items():

            idle_time = now - meta.last_used

            if idle_time > idle_seconds:
                to_remove.append(session_id)

        for session_id in to_remove:
            await self.close_async_session(session_id)

    def __len__(self):

        return (
            len(self._sync_sessions)
            + len(self._async_sessions)
        )

    def __repr__(self):

        return (
            f"SessionManager("
            f"sync={len(self._sync_sessions)}, "
            f"async={len(self._async_sessions)})"
        )