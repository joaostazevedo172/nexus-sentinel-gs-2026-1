"""Climate (Digital Twin) state — GET current snapshot, PATCH variables."""
from fastapi import APIRouter
from models import ClimateState, ClimateStatePatch
from services.state_store import state_store
from ws.manager import manager  # 👈 IMPORTANTE: Trazendo o manager do WebSocket

router = APIRouter(prefix="/api/climate", tags=["climate"])


@router.get("/state", response_model=ClimateState)
def get_state() -> ClimateState:
    s = state_store.snapshot()
    return ClimateState(
        temperature=round(s.temperature, 2),
        humidity=round(s.humidity, 2),
        meshActivity=round(s.mesh_activity, 2),
        resilience=round(s.resilience, 2),
    )


@router.patch("/state", response_model=ClimateState)
async def patch_state(patch: ClimateStatePatch) -> ClimateState: # 👈 MUDANÇA CRÍTICA: 'async def'
    # 1. Atualiza o estado na memória/banco (mantido como estava)
    s = state_store.update(
        temperature=patch.temperature,
        humidity=patch.humidity,
        mesh_activity=patch.meshActivity,
    )
    
    # 2. A MÁGICA: Dispara o aviso pelo WebSocket para o Gêmeo Digital (Three.js/Zustand)
    await manager.broadcast(
        channel="climate", # Se o seu frontend ouve tudo junto, pode remover ou manter
        message={
            "type": "climate_update",
            "state": {
                "temperature": round(s.temperature, 2),
                "humidity": round(s.humidity, 2),
                "meshActivity": round(s.mesh_activity, 2),
                "resilience": round(s.resilience, 2),
            }
        }
    )

    # 3. Retorna a resposta HTTP (200 OK) para o ESP32
    return ClimateState(
        temperature=round(s.temperature, 2),
        humidity=round(s.humidity, 2),
        meshActivity=round(s.mesh_activity, 2),
        resilience=round(s.resilience, 2),
    )