"""Briefing Executivo — endpoint cognitivo."""
from fastapi import APIRouter
from pydantic import BaseModel

from services.bedrock_service import generate_briefing
from services.state_store import state_store

router = APIRouter(prefix="/api/briefing", tags=["briefing"])


class BriefingResponse(BaseModel):
    briefing: str
    model: str
    snapshot: dict


@router.post("/generate", response_model=BriefingResponse)
def generate() -> BriefingResponse:
    """Gera um briefing executivo do estado atual do Digital Twin.

    Usa Amazon Bedrock (Claude 3.5 Sonnet) se disponível, com fallback
    determinístico via templating caso credenciais AWS não estejam
    configuradas no ambiente.
    """
    s = state_store.snapshot()
    snap = {
        "temperature":  round(s.temperature, 2),
        "humidity":     round(s.humidity, 2),
        "meshActivity": round(s.mesh_activity, 2),
        "resilience":   round(s.resilience, 2),
    }
    text, model = generate_briefing(snap)
    return BriefingResponse(briefing=text, model=model, snapshot=snap)
