# Nexus Sentinel — Backend (FastAPI v1.1)

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- WebSockets: `ws://localhost:8000/ws/yolo` e `ws://localhost:8000/ws/blockchain`

## Endpoints

### REST
| Método | Rota | Descrição |
|--------|------|-----------|
| GET    | `/api/climate/state` | Snapshot atual do Digital Twin |
| PATCH  | `/api/climate/state` | Atualiza temperature/humidity/meshActivity |
| GET    | `/api/yolo/latest`   | Último frame YOLO (real ou mock) |
| GET    | `/api/predict/water-scarcity?horizon=6` | Predição scikit-learn |
| POST   | `/api/alerts/ngo`    | Emite alerta preventivo |
| GET    | `/api/blockchain/transactions?limit=20` | Ledger paginado (SQLite) |
| GET    | `/api/blockchain/stats` | Agregados do ledger |
| GET    | `/api/mesh/nodes`    | Lista de nós da rede federada |
| POST   | `/api/federation/activate` | Trigger burst federado |

### WebSocket
| Rota | Mensagens |
|------|-----------|
| `/ws/yolo` | `YoloFrame` a cada `YOLO_ROTATION_S` (3.2s default), + 1 frame imediato ao conectar |
| `/ws/blockchain` | `{type:"snapshot", transactions:[…]}` ao conectar, `{type:"transaction", transaction:{…}}` por TX nova |

## Persistência

- **SQLite** em `nexus.db` (gitignored). Schema gerado via `SQLModel.metadata.create_all()` em startup.
- Para resetar: `rm nexus.db`

## YOLOv8 real

Quando `ml/runs/detect/train*/weights/best.pt` existe e `ultralytics` está instalado,
o servidor carrega o modelo no startup e passa a fazer inferência real em imagens
de validação aleatórias. Caso contrário, usa rotação de cenários mock.

Para sobrescrever o caminho dos pesos: `export NEXUS_YOLO_WEIGHTS=/path/to/best.pt`.

Workflow completo em `ml/README.md`.

## Estrutura

```
backend/
├── main.py                 # FastAPI app + lifespan (DB init, WS loop, sklearn warm-up)
├── db.py                   # SQLModel engine + TransactionDB
├── config.py               # Settings via env vars
├── models.py               # Pydantic models compartilhados
├── routers/
│   ├── climate.py          # /api/climate/state
│   ├── yolo.py             # /api/yolo/latest
│   ├── prediction.py       # /api/predict/water-scarcity
│   ├── alerts.py           # /api/alerts/ngo
│   ├── blockchain.py       # /api/blockchain/{transactions,stats}
│   ├── mesh.py             # /api/mesh/nodes
│   └── federation.py       # /api/federation/activate
├── services/
│   ├── state_store.py      # Thread-safe Digital Twin state
│   ├── yolo_service.py     # Real YOLO if available, else mock rotation
│   ├── prediction_service.py  # scikit-learn LinearRegression (polynomial features)
│   ├── blockchain_service.py  # SQLite-backed ledger + pub/sub
│   └── mesh_service.py     # Node registry
├── ws/
│   ├── manager.py          # Connection manager + thread-safe broadcaster
│   └── router.py           # /ws/yolo and /ws/blockchain endpoints
└── ml/                     # YOLOv8 training pipeline (see ml/README.md)
```

## Variáveis de ambiente

| Var | Default | Descrição |
|-----|---------|-----------|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CSV de origens CORS |
| `YOLO_ROTATION_S` | `3.2` | Intervalo de broadcast WS de YOLO |
| `BLOCKCHAIN_MAX_HISTORY` | `500` | Limite de buffer (não afeta SQLite) |
| `NEXUS_YOLO_WEIGHTS` | (auto-discover) | Path explícito para pesos `.pt` |
