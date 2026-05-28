"""Stand-alone inference smoke test.

Usage:
    python predict.py path/to/image.jpg
    python predict.py            # picks a random val image
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path


def predict(image_path: Path | None = None) -> None:
    try:
        from ultralytics import YOLO
    except ImportError:
        raise SystemExit("ultralytics not installed. pip install -r requirements-ml.txt")

    here = Path(__file__).parent
    runs = here / "runs" / "detect"
    weights_candidates = sorted(runs.glob("train*/weights/best.pt"), reverse=True)
    if not weights_candidates:
        raise SystemExit("No trained weights found. Run train.py first.")

    weights = weights_candidates[0]
    model = YOLO(str(weights))
    print(f"Loaded: {weights}")

    if image_path is None:
        val_dir = here / "data" / "images" / "val"
        candidates = list(val_dir.glob("*.jpg"))
        if not candidates:
            raise SystemExit("No val images. Run synthesize_dataset.py.")
        image_path = random.choice(candidates)

    print(f"Inferring on: {image_path}")
    results = model(str(image_path))
    for r in results:
        print(f"  {len(r.boxes)} detections")
        for b in r.boxes:
            cls_id = int(b.cls.item())
            conf = float(b.conf.item())
            print(f"    class={cls_id} conf={conf:.2f} box={b.xyxyn[0].tolist()}")
        out = image_path.with_suffix(".pred.jpg")
        r.save(filename=str(out))
        print(f"  → annotated saved to {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("image", nargs="?", type=Path, default=None)
    args = p.parse_args()
    predict(args.image)
