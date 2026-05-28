# 🛰️ Nexus Sentinel — Gêmeo Digital de Resiliência Climática

> **Global Solution 2026.1 — FIAP**
> Como a IA e as tecnologias digitais podem transformar a nova economia espacial e gerar impacto positivo na Terra?

![Stack](https://img.shields.io/badge/Stack-Next.js%2015%20%2B%20FastAPI%20%2B%20YOLOv8%20%2B%20Bedrock-00F2FF?style=flat-square)
![Status](https://img.shields.io/badge/Status-POC%20Funcional-10B981?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-FFB800?style=flat-square)

---

## 👥 Integrantes

| Nome | RM | GitHub |
|------|----|----|
| [Nome completo 1] | [00000] | [@usuario1](https://github.com/usuario1) |
| [Nome completo 2] | [00000] | [@usuario2](https://github.com/usuario2) |
| [Nome completo 3] | [00000] | [@usuario3](https://github.com/usuario3) |
| [Nome completo 4] | [00000] | [@usuario4](https://github.com/usuario4) |
| [Nome completo 5] | [00000] | [@usuario5](https://github.com/usuario5) |

> ⚠ **Substituir pelos nomes reais e RMs antes do commit final.**

---

## 🎯 Proposta

O **Nexus Sentinel** é uma plataforma de monitoramento climático global que integra:

- **🛰️ Dados orbitais** — imagens RGB de Sentinel-2 (Copernicus/ESA) processadas via YOLOv8 para classificação de uso do solo (plantios, áreas degradadas, regeneração)
- **📡 IoT em campo** — ESP32 com sensor capacitivo de umidade do solo publicando leituras em tempo real
- **🧠 ML preditivo** — scikit-learn LinearRegression projetando escassez hídrica em 6 meses (R² 0.995)
- **☁️ Cloud serverless** — AWS Lambda + Amazon Bedrock (Claude 3.5 Sonnet) para briefings executivos automáticos
- **🌐 Aprendizado federado** — dados brutos nunca saem dos nós; apenas gradientes trafegam (LGPD/GDPR compliant)
- **⛓️ Blockchain ledger** — tokenização de ações de regeneração ambiental em SQLite/SQLModel
- **🎨 Digital Twin 3D** — globo wireframe Three.js reativo, com WebSocket streaming a 60 FPS

---

## 🚀 Quick Start

### 1. Backend (FastAPI)

```bash
cd src/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- WebSockets: `ws://localhost:8000/ws/yolo` e `ws://localhost:8000/ws/blockchain`

### 2. Frontend (Next.js 15)

```bash
cd src/frontend
npm install
cp .env.example .env.local       # configurar NEXT_PUBLIC_USE_BACKEND=true
npm run dev
```

Acesse http://localhost:3000.

### 3. IoT (Simulador ESP32, opcional)

```bash
cd src/iot
pip install requests
python esp32_simulator.py
```

A umidade do solo do dashboard começa a oscilar sozinha (ciclo dia/noite + ruído).

### 4. ML — Treino YOLOv8 (opcional)

```bash
cd src/backend/ml
pip install -r requirements-ml.txt
python synthesize_dataset.py        # gera 240 imagens 640x640
python train.py --quick             # 10 épocas (~5min em CPU)
```

Reinicie o backend — o `yolo_service.py` auto-descobre os pesos e passa a fazer inferência real.

### 5. AWS Lambda (opcional)

```bash
cd src/aws
sam build && sam deploy --guided
```

---

## 📁 Estrutura do Projeto

```
NEXUS-SENTINEL-GS-2026-1/
├── README.md                          ← este arquivo
├── docs/
│   ├── nexus-sentinel-gs-2026-1.pdf  ← PDF de entrega
│   └── gerar_pdf.py                  ← gerador do PDF (reportlab)
├── assets/
│   ├── arq-macro.png                 ← arquitetura geral
│   ├── arq-fluxo-realtime.png        ← sequence diagram
│   ├── arq-federated-learning.png    ← padrão federado
│   ├── arquitetura.md                ← versão Mermaid dos diagramas
│   └── render_diagrams.py            ← gerador dos diagramas
├── video/
│   └── roteiro.md                    ← roteiro do vídeo de 5 min
└── src/
    ├── frontend/                     # Next.js 15 + TS + Tailwind + Framer Motion + Three.js + Zustand
    ├── backend/                      # FastAPI + SQLModel + WebSockets + scikit-learn + boto3
    │   ├── routers/                  # 8 endpoints REST
    │   ├── services/                 # yolo · prediction · blockchain · mesh · bedrock · state
    │   ├── ws/                       # WebSocket hub
    │   └── ml/                       # YOLOv8 training pipeline
    ├── iot/                          # ESP32 simulator + firmware MicroPython
    │   ├── esp32_simulator.py
    │   ├── firmware/main.py
    │   └── wiring.md
    └── aws/                          # AWS Lambda + SAM
        ├── lambda_predict/           # scikit-learn como Lambda
        ├── lambda_briefing/          # Bedrock + Claude 3.5
        └── template.yaml             # SAM template
```

---

## 🧪 Tecnologias por Disciplina

| Disciplina FIAP | Como aparece no projeto |
|-----------------|-------------------------|
| Machine Learning | scikit-learn LinearRegression com features polinomiais, R² 0.995 |
| Visão Computacional | YOLOv8 + dataset sintético + pipeline real de treino |
| APIs / Web Services | 8 endpoints REST FastAPI + 2 canais WebSocket |
| IoT / ESP32 | Simulador Python + firmware MicroPython + esquema elétrico |
| Computação em Nuvem | 2 Lambdas Python deployáveis via AWS SAM |
| Serviços Cognitivos | Amazon Bedrock (Claude 3.5 Sonnet) para briefings |
| Banco de Dados | SQLite via SQLModel para o ledger blockchain |
| Front-end / UI | Next.js 15 + Three.js + Framer Motion + Zustand |
| Dashboards | Globo wireframe reativo · gráficos · terminal blockchain |
| Análise de Dados Real-Time | WebSocket streaming · 60 FPS Three.js |
| Compliance / LGPD | Aprendizado federado: dados brutos nunca saem dos nós |

---

## 🎬 Vídeo Demonstrativo

🔗 **YouTube (Não Listado):** https://youtu.be/[ID-DO-VIDEO]

> Substituir pelo ID real após upload.

Roteiro completo em [`video/roteiro.md`](./video/roteiro.md).

---

## 📄 PDF de Entrega

O PDF da entrega está em [`docs/nexus-sentinel-gs-2026-1.pdf`](./docs/nexus-sentinel-gs-2026-1.pdf) (15 páginas, gerado automaticamente via reportlab).

Para regenerar:
```bash
pip install reportlab pypdf
python docs/gerar_pdf.py
```

---


---

## 🚀 Deploy Público

Para hospedar o sistema em produção (Vercel + Render, **gratuito**), siga o guia completo em [`DEPLOY.md`](./DEPLOY.md).

**Stack de produção:**
- 🌐 **Frontend** → Vercel (região São Paulo)
- 🐍 **Backend** → Render (Docker + Postgres free)
- ☁️ **Lambdas (opcional)** → AWS SAM
- ⏱️ **Tempo total de deploy:** ~15 minutos

URLs públicas (preencher após deploy):
- App: `https://nexus-sentinel.vercel.app` (substituir)
- API: `https://nexus-sentinel-api.onrender.com` (substituir)
- API Health: `https://nexus-sentinel-api.onrender.com/health`
- API Docs: `https://nexus-sentinel-api.onrender.com/docs`

## ⚖️ Licença

Este projeto está licenciado sob a Creative Commons Attribution 4.0 International ([CC BY 4.0](http://creativecommons.org/licenses/by/4.0/)), seguindo o modelo FIAP.

---

<p align="center">
<i>Desenvolvido por equipe Nexus para a GS 2026.1 — FIAP Graduação ON em Inteligência Artificial</i>
</p>
