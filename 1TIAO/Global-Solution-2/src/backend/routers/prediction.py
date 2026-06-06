"""Prediction endpoints — scikit-learn-backed projections."""
from fastapi import APIRouter, Query
from models import PredictionResponse
from services.prediction_service import predict_water_scarcity

router = APIRouter(prefix="/api/predict", tags=["prediction"])


@router.get("/water-scarcity", response_model=PredictionResponse)
def water_scarcity(horizon: int = Query(6, ge=1, le=24)) -> PredictionResponse:
    """6-month (default) projection of water-scarcity risk percentage,
    with and without Nexus intervention. Backed by scikit-learn's
    LinearRegression fit on historical climate telemetry."""
    return predict_water_scarcity(horizon)
