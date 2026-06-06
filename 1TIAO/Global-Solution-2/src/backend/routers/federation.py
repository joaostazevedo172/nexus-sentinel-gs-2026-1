"""Federated learning activation endpoint."""
from secrets import token_hex
from fastapi import APIRouter
from models import FederationResponse
from services.state_store import state_store
from services.blockchain_service import blockchain_service

router = APIRouter(prefix="/api/federation", tags=["federation"])


@router.post("/activate", response_model=FederationResponse)
def activate() -> FederationResponse:
    """Trigger a federated-learning burst.

    Side effects:
    - Marks the global state as federation_active for 6 seconds
    - Generates 6 federated-burst transactions on the ledger
    """
    state_store.activate_federation()
    blockchain_service.federation_burst()
    return FederationResponse(activated=True, burstId=f"fed_{token_hex(4)}")
