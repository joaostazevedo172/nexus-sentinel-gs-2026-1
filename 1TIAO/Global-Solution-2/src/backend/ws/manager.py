"""WebSocket connection manager.

Keeps track of active connections per channel and exposes ``broadcast``
for fan-out. Designed to be loop-agnostic: synchronous services can call
``schedule_broadcast`` which marshals the coroutine onto the running
asyncio loop via ``run_coroutine_threadsafe``.
"""
from __future__ import annotations

import asyncio
import json
from threading import Lock
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._channels: dict[str, list[WebSocket]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Called once at FastAPI startup, captures the main event loop
        so synchronous code can schedule broadcasts."""
        self._loop = loop

    async def connect(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        with self._lock:
            self._channels.setdefault(channel, []).append(ws)

    def disconnect(self, channel: str, ws: WebSocket) -> None:
        with self._lock:
            if channel in self._channels and ws in self._channels[channel]:
                self._channels[channel].remove(ws)

    async def broadcast(self, channel: str, payload: Any) -> None:
        msg = json.dumps(payload, default=str)
        with self._lock:
            targets = list(self._channels.get(channel, []))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        if dead:
            with self._lock:
                for ws in dead:
                    if ws in self._channels.get(channel, []):
                        self._channels[channel].remove(ws)

    def schedule_broadcast(self, channel: str, payload: Any) -> None:
        """Thread-safe scheduler — works from synchronous code."""
        if self._loop is None or self._loop.is_closed():
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(channel, payload), self._loop)


manager = ConnectionManager()
