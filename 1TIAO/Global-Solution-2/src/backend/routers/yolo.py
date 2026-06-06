"""YOLO endpoints — returns the latest detection frame."""
from fastapi import APIRouter
from models import YoloFrame
from services.yolo_service import get_latest_frame

router = APIRouter(prefix="/api/yolo", tags=["yolo"])


@router.get("/latest", response_model=YoloFrame)
def latest() -> YoloFrame:
    """Most recent YOLO inference frame.

    Frontend polls this every ~3s. In production, replace with a
    WebSocket stream or Server-Sent Events.
    """
    return get_latest_frame()
