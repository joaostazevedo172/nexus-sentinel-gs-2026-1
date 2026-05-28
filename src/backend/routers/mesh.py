"""Mesh network endpoints."""
from fastapi import APIRouter
from models import MeshNode
from services.mesh_service import list_nodes

router = APIRouter(prefix="/api/mesh", tags=["mesh"])


@router.get("/nodes", response_model=list[MeshNode])
def get_nodes() -> list[MeshNode]:
    """All registered mesh nodes with their current operational status."""
    return list_nodes()
