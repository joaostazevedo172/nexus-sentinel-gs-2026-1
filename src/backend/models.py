"""Pydantic models shared across routers."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


DetectionKind = Literal["good", "bad"]
NodeKind = Literal["normal", "warning", "risk"]
Severity = Literal["low", "medium", "high", "critical"]


class YoloDetection(BaseModel):
    box: tuple[float, float, float, float] = Field(
        ..., description="[x, y, w, h] as percentages of the frame (0..100)"
    )
    label: str
    conf: float = Field(..., ge=0, le=1)
    kind: DetectionKind


class YoloFrame(BaseModel):
    detections: list[YoloDetection]
    capturedAt: datetime
    sensorId: str


class Transaction(BaseModel):
    hash: str
    region: str
    action: str
    reward: int
    time: str
    fed: Optional[bool] = None


class BlockchainStats(BaseModel):
    totalTransactions: int
    totalTokens: int
    federatedBurstCount: int
    blockHeight: int
    contractAddress: str


class PredictionPoint(BaseModel):
    month: str
    noIntervention: float
    withNexus: float


class PredictionMetrics(BaseModel):
    r2: float
    mae: float
    estimatedDisplacement: dict[str, float]


class PredictionResponse(BaseModel):
    horizonMonths: int
    points: list[PredictionPoint]
    metrics: PredictionMetrics


class ClimateState(BaseModel):
    temperature: float
    humidity: float
    meshActivity: float
    resilience: float


class ClimateStatePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    meshActivity: Optional[float] = None


class MeshNode(BaseModel):
    id: str
    description: str
    kind: NodeKind
    pingMs: int
    weightSize: str
    lat: float
    lng: float


class AlertRequest(BaseModel):
    regions: list[str]
    severity: Severity
    message: Optional[str] = None


class AlertResponse(BaseModel):
    alertId: str
    ngosNotified: int
    deliveredAt: datetime


class FederationResponse(BaseModel):
    activated: bool
    burstId: str
