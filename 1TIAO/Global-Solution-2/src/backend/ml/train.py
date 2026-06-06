"""Fine-tune YOLOv8n on the synthetic Nexus dataset.

Usage:
    pip install -r requirements-ml.txt
    python synthesize_dataset.py
    python train.py             # full: 50 epochs
    python train.py --quick     # quick: 10 epochs (sanity check)

Output: ml/runs/detect/train*/weights/best.pt
This file is auto-loaded by services/yolo_service.py at startup.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def train(quick: bool = False) -> None:
    try:
        from ultralytics import YOLO
    except ImportError:
        raise SystemExit(
            "ultralytics not installed. Run:\n"
            "    pip install -r requirements-ml.txt"
        )

    here = Path(__file__).parent
    data_yaml = here / "data.yaml"
    if not (here / "data" / "images" / "train").exists():
        raise SystemExit(
            "Dataset not found. Run synthesize_dataset.py first."
        )

    model = YOLO("yolov8n.pt")  # auto-downloads on first run

    results = model.train(
        data=str(data_yaml),
        epochs=10 if quick else 50,
        imgsz=640,
        batch=16,
        patience=15,
        project=str(here / "runs" / "detect"),
        name="train",
        exist_ok=True,
        verbose=True,
    )
    best = Path(results.save_dir) / "weights" / "best.pt"
    print(f"\n✓ Training complete. Best weights: {best}")
    print(f"  Set NEXUS_YOLO_WEIGHTS={best} or it will be auto-loaded.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true", help="10 epochs (sanity check)")
    args = p.parse_args()
    train(args.quick)
