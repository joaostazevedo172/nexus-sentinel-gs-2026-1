"""Alerts endpoint — preventive notifications to partner NGOs."""
from datetime import datetime, timezone
from secrets import token_hex
from fastapi import APIRouter
from models import AlertRequest, AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/ngo", response_model=AlertResponse)
def emit_ngo_alert(req: AlertRequest) -> AlertResponse:
    """Broadcast a preventive alert to the partner NGO network.

    In production this would dispatch through a notification fan-out
    (SES / SNS / FCM) to subscribers filtered by region.
    """
    return AlertResponse(
        alertId=f"alert_{token_hex(6)}",
        ngosNotified=42,  # mock count
        deliveredAt=datetime.now(timezone.utc),
    )
