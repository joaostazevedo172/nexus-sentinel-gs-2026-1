"""Generate a synthetic soil-monitoring dataset for YOLOv8 training.

Each image is a 640×640 "satellite-like" terrain with 1-4 colored patches
representing the 4 classes. Labels are written in YOLO format
(class_id cx cy w h, all normalized to 0..1).

Usage:
    python synthesize_dataset.py --train 200 --val 40
    python synthesize_dataset.py --train 50 --val 10  # quick

This is a proof-of-pipeline. Real production would use Google Earth Engine
exports (Sentinel-2 RGB) labeled via Roboflow or CVAT.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CLASSES = [
    # (name, base_color_rgb, color_jitter)
    ("plantio_cobertura", (60, 130, 50),  20),  # green
    ("area_degradada",    (140, 80, 50),  25),  # red-brown
    ("solo_regenerado",   (40, 170, 180), 20),  # cyan-teal
    ("erosao_avancada",   (110, 35, 30),  20),  # dark red
]

IMG_SIZE = 640


def _terrain_background(rng: random.Random) -> Image.Image:
    """Generate a noisy terrain-ish background using overlapping radial blobs."""
    # Start with mid-luminance earth tone (satellite imagery is rarely pitch black)
    arr = np.full((IMG_SIZE, IMG_SIZE, 3), [70, 75, 55], dtype=np.float32)
    # 6-9 base blobs in earth tones, brighter and more varied
    base_tones = [
        (95, 110, 70), (130, 100, 65), (80, 105, 80),
        (115, 95, 60),  (100, 120, 80), (140, 130, 90),
        (90, 95, 65),   (110, 115, 75),
    ]
    n_blobs = rng.randint(6, 9)
    for _ in range(n_blobs):
        cx, cy = rng.randint(0, IMG_SIZE), rng.randint(0, IMG_SIZE)
        radius = rng.randint(150, 350)
        tone = np.array(rng.choice(base_tones), dtype=np.float32)
        yy, xx = np.ogrid[:IMG_SIZE, :IMG_SIZE]
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        falloff = np.clip(1.0 - d2 / (radius * radius), 0, 1) ** 2
        arr += tone[None, None, :] * falloff[:, :, None]
    # Normalize + add fine noise
    arr = np.clip(arr, 0, 255)
    noise = np.random.normal(0, 8, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(radius=2))
    return img


def _jitter_color(base: tuple[int, int, int], jitter: int, rng: random.Random) -> tuple[int, int, int]:
    return tuple(
        max(0, min(255, c + rng.randint(-jitter, jitter))) for c in base
    )


def _place_patch(
    img: Image.Image,
    rng: random.Random,
) -> tuple[int, float, float, float, float]:
    """Place a random colored patch and return (class_id, cx, cy, w, h) normalized."""
    class_id = rng.randint(0, len(CLASSES) - 1)
    name, color, jitter = CLASSES[class_id]
    pcolor = _jitter_color(color, jitter, rng)

    w_px = rng.randint(80, 200)
    h_px = rng.randint(70, 180)
    x = rng.randint(0, IMG_SIZE - w_px)
    y = rng.randint(0, IMG_SIZE - h_px)

    # Draw ellipse for organic shape, with semi-transparent overlay
    overlay = Image.new("RGBA", (w_px, h_px), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    alpha = rng.randint(180, 230)
    od.ellipse([0, 0, w_px - 1, h_px - 1], fill=(*pcolor, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(overlay, (x, y), overlay)

    cx = (x + w_px / 2) / IMG_SIZE
    cy = (y + h_px / 2) / IMG_SIZE
    w = w_px / IMG_SIZE
    h = h_px / IMG_SIZE
    return class_id, cx, cy, w, h


def generate(out_root: Path, n_train: int, n_val: int, seed: int = 42) -> None:
    rng = random.Random(seed)
    splits = [("train", n_train), ("val", n_val)]
    for split, n in splits:
        img_dir = out_root / "images" / split
        lbl_dir = out_root / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            img = _terrain_background(rng)
            n_patches = rng.randint(1, 4)
            lines: list[str] = []
            for _ in range(n_patches):
                class_id, cx, cy, w, h = _place_patch(img, rng)
                lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            stem = f"nexus_{split}_{i:05d}"
            img.save(img_dir / f"{stem}.jpg", quality=88)
            (lbl_dir / f"{stem}.txt").write_text("\n".join(lines) + "\n")
        print(f"  · {split}: {n} images → {img_dir}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--train", type=int, default=200, help="train images to generate")
    p.add_argument("--val",   type=int, default=40,  help="val images to generate")
    p.add_argument("--out",   type=Path, default=Path(__file__).parent / "data")
    p.add_argument("--seed",  type=int, default=42)
    args = p.parse_args()
    print(f"Generating synthetic Nexus dataset → {args.out}")
    generate(args.out, args.train, args.val, args.seed)
    print("✓ Dataset ready. Next: python train.py")
