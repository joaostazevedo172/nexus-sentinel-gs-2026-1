# Nexus Sentinel — ML (YOLOv8)

Pipeline completo de visão computacional para detecção de áreas de
regeneração/degradação do solo via imagens "satelitais".

## Workflow

```bash
# 1. Instale dependências ML (uma vez)
pip install -r requirements-ml.txt

# 2. Gere dataset sintético (~5s, 240 imagens 640×640)
python synthesize_dataset.py
#   → ml/data/images/{train,val}/ + ml/data/labels/{train,val}/

# 3. Treine YOLOv8n (CPU: ~10min para 10 épocas, ~50min para 50)
python train.py --quick     # 10 épocas, sanity check
python train.py             # 50 épocas, produção

# 4. Teste a inferência standalone
python predict.py
#   → ml/data/images/val/nexus_val_00000.pred.jpg (com bboxes)
```

Quando `ml/runs/detect/train*/weights/best.pt` existir, o backend principal
**carrega automaticamente** os pesos no startup (via
`services/yolo_service.py`) e passa a fazer **inferência real** em
substituição aos cenários mock.

## Classes

| ID | Label técnico       | Display              | Kind  |
|----|---------------------|----------------------|-------|
| 0  | `plantio_cobertura` | Plantio de Cobertura | good  |
| 1  | `area_degradada`    | Área Degradada       | bad   |
| 2  | `solo_regenerado`   | Solo Regenerado      | good  |
| 3  | `erosao_avancada`   | Erosão Avançada      | bad   |

## Próximos passos para produção

Para usar dados reais em vez do dataset sintético:

1. **Google Earth Engine** → exporte tiles Sentinel-2 RGB (10m/pixel)
   das regiões SP/DEL/CPT em janelas mensais (~6 meses de histórico).
2. **Labeling** via Roboflow ou CVAT — exporte em formato YOLO.
3. Substitua o conteúdo de `ml/data/` pelo dataset real, mantendo
   a estrutura `images/{train,val}` + `labels/{train,val}`.
4. Re-treine: `python train.py` (use GPU se possível: `--device 0`).

A interface (`yolo_service.py`) já está pronta — não precisa mexer.

## Sobre o dataset sintético

Os "satellite-like images" são gerados via composição de:
- 4-6 radial gradients em tons de terra (base do terreno)
- 1-4 elipses coloridas representando as 4 classes
- Ruído gaussiano + blur leve para realismo

É **suficiente para validar end-to-end** que: o dataset carrega, o YOLO
treina, os pesos são salvos, e o backend faz inferência real. Não é
adequado para predições reais em produção.

## Imagens reais de Sentinel-2 (Copernicus)

Para substituir o dataset sintético por imagens orbitais reais:

```bash
# 1. Crie conta gratuita em https://dataspace.copernicus.eu/
export COPERNICUS_USER='seu_email'
export COPERNICUS_PASS='sua_senha'

# 2. Instale dependências adicionais
pip install sentinelhub pillow

# 3. Baixe tiles das regiões críticas (5 por região)
python download_sentinel2.py --region SP  --max-tiles 5
python download_sentinel2.py --region DEL --max-tiles 5
python download_sentinel2.py --region CPT --max-tiles 5
```

Tiles vão para `data/images/val/` automaticamente. O `yolo_service.py` os
descobre no startup e passa a fazer inferência em **pixels reais de satélite**
em vez de imagens sintéticas.

> ⚠ Se o YOLO foi treinado **somente** no dataset sintético, ele provavelmente
> não vai detectar nada útil em imagens Sentinel-2 reais — domínio diferente.
> Para inferência real, treine o YOLO com um dataset real de uso do solo
> (ex: [EuroSAT](https://github.com/phelber/eurosat) com labels customizados).
