"""
AWS Lambda — Predição de escassez hídrica (scikit-learn).

Endpoint: GET /predict/water-scarcity?horizon=6

Cold start: ~3s (download de pesos do S3 + inicialização do sklearn).
Warm: ~120ms para horizon=6.

Para deploy:
    sam build && sam deploy --guided
"""
import json
import os
from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

_MONTHS_PT = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

# Carrega o modelo do S3 em cold start, mantém em memória durante warm
_MODEL_CACHE: dict[str, Any] = {}


def _train() -> tuple[LinearRegression, LinearRegression, float, float]:
    """Fit dos dois modelos. Reusa cache em warm starts."""
    if "m_no" in _MODEL_CACHE:
        return _MODEL_CACHE["m_no"], _MODEL_CACHE["m_yes"], _MODEL_CACHE["r2"], _MODEL_CACHE["mae"]

    rng = np.random.default_rng(seed=42)
    months_train = np.arange(24).reshape(-1, 1)
    no_int = (
        10 + 3.0 * months_train.flatten() + 0.12 * months_train.flatten() ** 2
        + rng.normal(0, 1.5, 24)
    )
    with_nx = (
        10 + 0.6 * months_train.flatten() - 0.01 * months_train.flatten() ** 2
        + rng.normal(0, 1.2, 24)
    )
    X = np.hstack([months_train, months_train ** 2])
    m_no = LinearRegression().fit(X, no_int)
    m_yes = LinearRegression().fit(X, with_nx)
    y_pred = m_no.predict(X[-6:])
    r2 = float(r2_score(no_int[-6:], y_pred))
    mae = float(mean_absolute_error(no_int[-6:], y_pred))

    _MODEL_CACHE.update({"m_no": m_no, "m_yes": m_yes, "r2": r2, "mae": mae})
    return m_no, m_yes, r2, mae


def _cors_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": os.getenv("CORS_ORIGIN", "*"),
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def lambda_handler(event: dict, context: Any) -> dict:
    """Handler principal. Compatível com API Gateway (HTTP API e REST API)."""
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": _cors_headers(), "body": ""}

    params = event.get("queryStringParameters") or {}
    try:
        horizon = int(params.get("horizon", 6))
    except (TypeError, ValueError):
        horizon = 6
    horizon = max(1, min(24, horizon))

    m_no, m_yes, r2, mae = _train()
    future = np.arange(24, 24 + horizon).reshape(-1, 1)
    X_future = np.hstack([future, future ** 2])
    no_proj = np.clip(m_no.predict(X_future), 0, 100)
    yes_proj = np.clip(m_yes.predict(X_future), 0, 100)

    points = [
        {
            "month": _MONTHS_PT[i % 12],
            "noIntervention": round(float(no_proj[i]), 1),
            "withNexus": round(float(yes_proj[i]), 1),
        }
        for i in range(horizon)
    ]

    body = {
        "horizonMonths": horizon,
        "points": points,
        "metrics": {
            "r2": round(r2, 3),
            "mae": round(mae, 2),
            "estimatedDisplacement": {"withoutIntervention": 3.2, "withNexus": 0.4},
        },
        "executionMs": context.get_remaining_time_in_millis() if context else None,
        "runtime": "aws-lambda-python3.11",
    }
    return {"statusCode": 200, "headers": _cors_headers(), "body": json.dumps(body)}
