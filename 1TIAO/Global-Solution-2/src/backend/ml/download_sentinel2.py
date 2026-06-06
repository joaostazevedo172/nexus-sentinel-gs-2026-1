"""
Download de tiles Sentinel-2 RGB para uso real do YOLO Nexus Sentinel.

Usa a API pública do Copernicus Data Space (sucessor do Open Access Hub).
Requer conta gratuita em https://dataspace.copernicus.eu/

Uso:
    export COPERNICUS_USER='seu_email'
    export COPERNICUS_PASS='sua_senha'
    python download_sentinel2.py --region SP --max-tiles 5
    python download_sentinel2.py --region DEL --max-tiles 5
    python download_sentinel2.py --region CPT --max-tiles 5

Os tiles são salvos como JPG 640x640 em data/images/val/, prontos para
o `services/yolo_service.py` consumir em inferência real.

Para a banca FIAP: se você não quiser criar conta no Copernicus, o dataset
sintético gerado por `synthesize_dataset.py` já produz inferência válida
end-to-end (apenas em pixels sintéticos em vez de pixels reais).
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Regiões de interesse do Nexus Sentinel (lat, lon, raio em km)
REGIONS = {
    "SP":  (-23.55,  -46.63, 50, "São Paulo, Brasil"),
    "DEL": ( 28.61,   77.21, 50, "Nova Delhi, Índia"),
    "CPT": (-33.92,   18.42, 50, "Cape Town, África do Sul"),
    "BSB": (-15.79,  -47.88, 50, "Brasília, Brasil"),
    "SYD": (-33.87,  151.21, 50, "Sydney, Austrália"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Sentinel-2 RGB tiles")
    parser.add_argument("--region", required=True, choices=list(REGIONS.keys()))
    parser.add_argument("--max-tiles", type=int, default=5)
    parser.add_argument("--cloud-pct", type=float, default=20, help="máximo de cobertura de nuvens")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "data" / "images" / "val")
    args = parser.parse_args()

    user = os.getenv("COPERNICUS_USER")
    password = os.getenv("COPERNICUS_PASS")
    if not user or not password:
        sys.exit(
            "Defina COPERNICUS_USER e COPERNICUS_PASS no ambiente.\n"
            "Conta gratuita: https://dataspace.copernicus.eu/"
        )

    try:
        from sentinelhub import SHConfig, SentinelHubRequest, MimeType, CRS, BBox, DataCollection
    except ImportError:
        sys.exit(
            "Instale sentinelhub-py:\n"
            "    pip install sentinelhub"
        )

    lat, lon, radius_km, desc = REGIONS[args.region]
    print(f"Baixando até {args.max_tiles} tiles de {desc}")
    print(f"  Centro: ({lat}, {lon}) · raio {radius_km}km · cloud<{args.cloud_pct}%")

    # Janela temporal: últimos 90 dias
    today = datetime.utcnow().date()
    start = (today - timedelta(days=90)).isoformat()
    end = today.isoformat()

    # Configurar SH
    config = SHConfig()
    config.sh_client_id = user
    config.sh_client_secret = password

    # Aproximação simples de bbox: 1° ≈ 111km
    delta_deg = radius_km / 111.0
    bbox = BBox(
        bbox=[lon - delta_deg, lat - delta_deg, lon + delta_deg, lat + delta_deg],
        crs=CRS.WGS84,
    )

    evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04"],
    output: { bands: 3 }
  };
}
function evaluatePixel(s) {
  return [2.5 * s.B04, 2.5 * s.B03, 2.5 * s.B02];
}
"""

    args.out.mkdir(parents=True, exist_ok=True)

    for i in range(args.max_tiles):
        try:
            req = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(start, end),
                        maxcc=args.cloud_pct / 100,
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.JPG)],
                bbox=bbox,
                size=(640, 640),
                config=config,
            )
            images = req.get_data()
            if not images:
                print(f"  [{i+1}] sem imagem disponível, pulando")
                continue
            out_path = args.out / f"sentinel2_{args.region.lower()}_{i:03d}.jpg"
            from PIL import Image
            Image.fromarray(images[0]).save(out_path, quality=88)
            print(f"  [{i+1}] {out_path.name}  ({out_path.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"  [{i+1}] erro: {e}")

    print("\n✓ Download concluído.")
    print("  Para usar no YOLO: estes arquivos já estão em ml/data/images/val/")
    print("  e o yolo_service.py escolherá um aleatório a cada frame WS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
