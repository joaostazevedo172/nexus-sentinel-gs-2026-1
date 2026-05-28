"""Nexus Sentinel — FastAPI entrypoint.

Run with:
    uvicorn main:app --reload --port 8000

Docs at http://localhost:8000/docs · WebSocket at /ws/yolo and /ws/blockchain
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import init_db
from routers import alerts, blockchain, briefing, climate, federation, mesh, prediction, yolo
from services.blockchain_service import blockchain_service
from services.prediction_service import _train_models
from ws.manager import manager
from ws.router import router as ws_router, yolo_broadcast_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    init_db()
    _train_models()  # warm-up sklearn

    loop = asyncio.get_running_loop()
    manager.bind_loop(loop)

    # Fan-out new transactions to WS subscribers as they land
    unsubscribe = blockchain_service.subscribe(
        lambda tx: manager.schedule_broadcast(
            "blockchain", {"type": "transaction", "transaction": tx.model_dump()}
        )
    )

    # Periodic YOLO broadcast
    yolo_task = asyncio.create_task(yolo_broadcast_loop())

    try:
        yield
    finally:
        # ── Shutdown ──────────────────────────────────────────────
        yolo_task.cancel()
        unsubscribe()
        try:
            await yolo_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Nexus Sentinel API",
    version="1.1.0",
    description="Backend para o Gêmeo Digital de Resiliência Climática.",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    # Accept any Vercel preview deployment as well (PRs → unique URL)
    allow_origin_regex=r"https://.*-?nexus-?sentinel.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Detailed health check — used by Render/Vercel/uptime monitors.

    Returns subsystem status for quick diagnosis. Always returns 200 if the
    process is alive; subsystems report 'ok'/'degraded'/'down' individually.
    """
    from services.yolo_service import is_real_mode
    from services.blockchain_service import blockchain_service
    from services.bedrock_service import _BEDROCK_AVAILABLE
    import os

    try:
        stats = blockchain_service.stats()
        db_status = "ok"
        tx_count = stats.totalTransactions
    except Exception as e:  # noqa: BLE001
        db_status, tx_count = f"degraded ({type(e).__name__})", -1

    return {
        "status": "ok",
        "version": app.version,
        "subsystems": {
            "database":   {"status": db_status, "transactions": tx_count},
            "yolo":       {"mode": "real" if is_real_mode() else "mock"},
            "bedrock":    {
                "available": _BEDROCK_AVAILABLE and bool(os.getenv("AWS_ACCESS_KEY_ID")),
                "fallback":  "template",
            },
        },
    }


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"service": "Nexus Sentinel API", "version": app.version, "docs": "/docs"}


# REST routers
app.include_router(climate.router)
app.include_router(yolo.router)
app.include_router(prediction.router)
app.include_router(alerts.router)
app.include_router(blockchain.router)
app.include_router(mesh.router)
app.include_router(federation.router)
app.include_router(briefing.router)

# WebSocket routers
app.include_router(ws_router)
