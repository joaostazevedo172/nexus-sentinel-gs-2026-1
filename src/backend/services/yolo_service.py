"""YOLO inference service.

Two operation modes, decided at import time:

1. **Real inference** — if ``ultralytics`` is installed AND a trained
   weights file is found (``NEXUS_YOLO_WEIGHTS`` env var, or auto-discovery
   under ``ml/runs/detect/train*/weights/best.pt``), every call to
   ``get_latest_frame()`` runs YOLOv8 on a fresh val image.

2. **Mock rotation** — fallback that rotates through hand-crafted
   scenarios (the v1 behavior). Triggered when ultralytics is absent
   or no weights are found. This keeps the demo runnable on any machine.

The model is loaded once at module import and cached.
"""
from __future__ import annotations

import os
import random
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Any

from config import get_settings
from models import YoloDetection, YoloFrame

# ── Class mapping: YOLO class_id → (display label, "good" | "bad") ──
_CLASS_MAP: dict[int, tuple[str, str]] = {
    0: ("Plantio de Cobertura", "good"),
    1: ("Área Degradada",        "bad"),
    2: ("Solo Regenerado",       "good"),
    3: ("Erosão Avançada",       "bad"),
}

# ── Mock scenarios (fallback) ──
_SCENARIOS: list[list[YoloDetection]] = [
    [
        YoloDetection(box=(12, 22, 28, 24), label="Plantio de Cobertura", conf=0.94, kind="good"),
        YoloDetection(box=(55, 18, 22, 30), label="Área Degradada",       conf=0.87, kind="bad"),
        YoloDetection(box=(42, 60, 30, 24), label="Solo Regenerado",      conf=0.91, kind="good"),
    ],
    [
        YoloDetection(box=(18, 14, 34, 28), label="Plantio de Cobertura", conf=0.96, kind="good"),
        YoloDetection(box=(60, 50, 26, 22), label="Erosão Avançada",       conf=0.82, kind="bad"),
    ],
    [
        YoloDetection(box=(22, 28, 24, 20), label="Solo Regenerado",      conf=0.93, kind="good"),
        YoloDetection(box=(50, 18, 30, 26), label="Plantio de Cobertura", conf=0.95, kind="good"),
        YoloDetection(box=(14, 62, 22, 22), label="Área Degradada",       conf=0.79, kind="bad"),
        YoloDetection(box=(62, 65, 26, 20), label="Solo Regenerado",      conf=0.88, kind="good"),
    ],
]


def _find_weights() -> Path | None:
    """Auto-discover the most recent trained weights."""
    override = os.getenv("NEXUS_YOLO_WEIGHTS")
    if override and Path(override).is_file():
        return Path(override)
    ml_runs = Path(__file__).resolve().parent.parent / "ml" / "runs" / "detect"
    candidates = sorted(ml_runs.glob("train*/weights/best.pt"), reverse=True)
    return candidates[0] if candidates else None


def _try_load_model() -> tuple[Any, list[Path]] | None:
    """Returns (model, val_images) on success, None on fallback."""
    weights = _find_weights()
    if weights is None:
        return None
    try:
        from ultralytics import YOLO  # type: ignore
    except ImportError:
        print("[yolo_service] ultralytics not installed → mock mode")
        return None
    val_dir = Path(__file__).resolve().parent.parent / "ml" / "data" / "images" / "val"
    val_images = list(val_dir.glob("*.jpg"))
    if not val_images:
        print(f"[yolo_service] no val images at {val_dir} → mock mode")
        return None
    try:
        model = YOLO(str(weights))
        print(f"[yolo_service] ✓ real inference: {weights} ({len(val_images)} val images)")
        return model, val_images
    except Exception as e:  # noqa: BLE001
        print(f"[yolo_service] failed to load YOLO weights ({e}) → mock mode")
        return None


_loaded = _try_load_model()
_REAL_MODE = _loaded is not None
_model = _loaded[0] if _loaded else None
_val_images: list[Path] = _loaded[1] if _loaded else []
_rng = random.Random()


def _detections_from_results(results: Any) -> list[YoloDetection]:
    out: list[YoloDetection] = []
    for r in results:
        for b in r.boxes:
            cls_id = int(b.cls.item())
            conf = float(b.conf.item())
            x1, y1, x2, y2 = b.xyxyn[0].tolist()  # normalized 0..1
            label, kind = _CLASS_MAP.get(cls_id, (f"class_{cls_id}", "bad"))
            out.append(
                YoloDetection(
                    box=(x1 * 100, y1 * 100, (x2 - x1) * 100, (y2 - y1) * 100),
                    label=label, conf=conf, kind=kind,
                )
            )
    return out


def get_latest_frame() -> YoloFrame:
    """Latest YOLO frame — real inference if model is loaded, else mock rotation."""
    if _REAL_MODE and _model is not None and _val_images:
        img_path = _rng.choice(_val_images)
        try:
            results = _model(str(img_path), verbose=False)
            return YoloFrame(
                detections=_detections_from_results(results),
                capturedAt=datetime.now(timezone.utc),
                sensorId=f"SENT-3B/{img_path.name}",
            )
        except Exception as e:  # noqa: BLE001
            print(f"[yolo_service] inference error ({e}) → mock fallback for this frame")

    # Mock rotation
    settings = get_settings()
    idx = int(time() // settings.yolo_rotation_seconds) % len(_SCENARIOS)
    return YoloFrame(
        detections=_SCENARIOS[idx],
        capturedAt=datetime.now(timezone.utc),
        sensorId="SENT-3B-MOCK",
    )


def is_real_mode() -> bool:
    """Used by /health-ml endpoint and tests."""
    return _REAL_MODE
