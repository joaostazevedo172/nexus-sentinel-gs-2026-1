"""Blockchain ledger service — SQLite-backed via SQLModel.

The public API is identical to the previous in-memory version, so all
routers and tests continue to work. Each call opens a session, performs
the query, and closes it (short-lived transactions).

A pluggable ``subscribe`` callback is exposed so the WebSocket hub can
react to new-transaction events without coupling the service to FastAPI.
"""
from __future__ import annotations

import random
import secrets
from datetime import datetime
from threading import Lock
from typing import Callable

from sqlmodel import Session, desc, func, select

from db import TransactionDB, engine
from models import BlockchainStats, Transaction


_REGIONS = ["SP-BR", "BSB-BR", "DEL-IN", "CPT-ZA", "MEX-MX", "NYC-US", "SYD-AU", "LDN-UK"]
_ACTIONS: list[tuple[str, int]] = [
    ("Regeneração 5ha", 12),
    ("Cobertura 3.2ha", 8),
    ("Reflorest. 8ha", 21),
    ("Recup. solo 2ha", 6),
]
_CONTRACT_ADDRESS = "0x9f4ab12c7d3a9b8e0f5c2d1a3b4c5d6e7f8a9b0c"


def _row_to_model(row: TransactionDB) -> Transaction:
    return Transaction(
        hash=row.hash, region=row.region, action=row.action,
        reward=row.reward, time=row.time, fed=row.fed,
    )


def _model_to_row(tx: Transaction) -> TransactionDB:
    return TransactionDB(
        hash=tx.hash, region=tx.region, action=tx.action,
        reward=tx.reward, time=tx.time, fed=bool(tx.fed),
    )


class BlockchainService:
    """Thread-safe ledger backed by SQLite."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._listeners: list[Callable[[Transaction], None]] = []

    # ── Pub/Sub for WebSocket fan-out ───────────────────────────────
    def subscribe(self, fn: Callable[[Transaction], None]) -> Callable[[], None]:
        with self._lock:
            self._listeners.append(fn)

        def unsubscribe() -> None:
            with self._lock:
                if fn in self._listeners:
                    self._listeners.remove(fn)

        return unsubscribe

    def _notify(self, tx: Transaction) -> None:
        for fn in list(self._listeners):
            try:
                fn(tx)
            except Exception as e:  # noqa: BLE001
                print(f"[blockchain_service] listener error: {e}")

    # ── Queries ─────────────────────────────────────────────────────
    def list_transactions(self, limit: int = 20, offset: int = 0) -> list[Transaction]:
        with Session(engine) as session:
            stmt = (
                select(TransactionDB)
                .order_by(desc(TransactionDB.created_at))
                .offset(offset)
                .limit(limit)
            )
            rows = session.exec(stmt).all()
            return [_row_to_model(r) for r in rows]

    def stats(self) -> BlockchainStats:
        with Session(engine) as session:
            total = session.exec(select(func.count(TransactionDB.id))).one() or 0
            tokens = session.exec(select(func.sum(TransactionDB.reward))).one() or 0
            fed_count = session.exec(
                select(func.count(TransactionDB.id)).where(TransactionDB.fed == True)  # noqa: E712
            ).one() or 0
        return BlockchainStats(
            totalTransactions=int(total),
            totalTokens=int(tokens or 0),
            federatedBurstCount=int(fed_count),
            blockHeight=4_829_177 + int(total),
            contractAddress=_CONTRACT_ADDRESS,
        )

    # ── Writes ──────────────────────────────────────────────────────
    @staticmethod
    def _make_hash() -> str:
        return f"0x{secrets.token_hex(4)}…{secrets.token_hex(2)}"

    def push(self, tx: Transaction) -> Transaction:
        row = _model_to_row(tx)
        with Session(engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
        result = _row_to_model(row)
        self._notify(result)
        return result

    def _generate(self, fed: bool = False) -> Transaction:
        if fed:
            action, reward = ("Burst Federado · 12ha", 32)
        else:
            action, reward = random.choice(_ACTIONS)
        return Transaction(
            hash=self._make_hash(),
            region=random.choice(_REGIONS),
            action=action,
            reward=reward,
            time=datetime.now().strftime("%H:%M:%S"),
            fed=fed,
        )

    def auto_generate(self, count: int = 1) -> list[Transaction]:
        return [self.push(self._generate()) for _ in range(count)]

    def federation_burst(self) -> list[Transaction]:
        return [self.push(self._generate(fed=True)) for _ in range(6)]


# Singleton
blockchain_service = BlockchainService()
