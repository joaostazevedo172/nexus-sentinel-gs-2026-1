"""Blockchain ledger endpoints."""
from fastapi import APIRouter, Query
from models import BlockchainStats, Transaction
from services.blockchain_service import blockchain_service

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])


@router.get("/transactions", response_model=list[Transaction])
def list_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[Transaction]:
    """Newest-first paginated transaction list.

    A side effect of calling this with limit=1 and an empty ledger is
    that the service will auto-generate one transaction (simulating
    continuous IoT-triggered smart-contract execution). Disable this
    behavior by setting ``BLOCKCHAIN_AUTOGEN=0`` in production.
    """
    existing = blockchain_service.list_transactions(limit, offset)
    if not existing and limit > 0:
        # Seed first transaction to bootstrap the stream
        return blockchain_service.auto_generate(1)
    return existing


@router.get("/stats", response_model=BlockchainStats)
def stats() -> BlockchainStats:
    return blockchain_service.stats()
