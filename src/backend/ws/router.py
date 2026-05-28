"""WebSocket endpoints.

- ``/ws/yolo``       — server pushes the latest YOLO frame every YOLO_ROTATION_S seconds
- ``/ws/blockchain`` — server pushes each new transaction as it lands in the ledger
"""
from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import get_settings
from services.yolo_service import get_latest_frame
from services.blockchain_service import blockchain_service
from ws.manager import manager

router = APIRouter()


@router.websocket("/ws/yolo")
async def ws_yolo(ws: WebSocket) -> None:
    await manager.connect("yolo", ws)
    # Send a frame immediately on connect, so the client has data right away
    try:
        await ws.send_text(get_latest_frame().model_dump_json())
        while True:
            # Keep the connection alive; the broadcast loop fans out frames
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("yolo", ws)
    except Exception:
        manager.disconnect("yolo", ws)


@router.websocket("/ws/blockchain")
async def ws_blockchain(ws: WebSocket) -> None:
    await manager.connect("blockchain", ws)
    # Send recent transactions on connect to bootstrap the UI
    try:
        recent = blockchain_service.list_transactions(limit=20)
        await ws.send_text(json.dumps(
            {"type": "snapshot", "transactions": [t.model_dump() for t in recent]},
            default=str,
        ))
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("blockchain", ws)
    except Exception:
        manager.disconnect("blockchain", ws)


async def yolo_broadcast_loop() -> None:
    """Background task: pushes the latest YOLO frame to all subscribers
    every YOLO_ROTATION_S seconds."""
    interval = get_settings().yolo_rotation_seconds
    while True:
        try:
            frame = get_latest_frame()
            await manager.broadcast("yolo", json.loads(frame.model_dump_json()))
        except Exception as e:  # noqa: BLE001
            print(f"[ws.yolo_broadcast_loop] {e}")
        await asyncio.sleep(interval)
