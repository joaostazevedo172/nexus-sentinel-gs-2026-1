# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="https://tse2.mm.bing.net/th/id/OIP.3xs_MSeNC0T1UOrJaCEqWAHaEK?cb=12&rs=1&pid=ImgDetMain&o=7&rm=3" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# 🛰️ Nexus Sentinel — Gêmeo Digital de Resiliência Climática

> **Global Solution 2026.1 — FIAP**
> Como a IA e as tecnologias digitais podem transformar a nova economia espacial e gerar impacto positivo na Terra?

![Stack](https://img.shields.io/badge/Stack-Next.js%2015%20%2B%20FastAPI%20%2B%20YOLOv8%20%2B%20Bedrock-00F2FF?style=flat-square)
![Status](https://img.shields.io/badge/Status-POC%20Funcional-10B981?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-FFB800?style=flat-square)

---

## 👥 Integrantes — Grupo Nexus

| Nome | RM |
|------|----|
| Miriã Leal Mantovani | RM567811 |
| João Pedro Santos Azevedo | RM566701 |
| Rodrigo de Souza Freitas | RM567100 |

---

## 🎯 Proposta

O **Nexus Sentinel** é uma plataforma de monitoramento climático global que integra:

- **🛰️ Dados orbitais** — imagens RGB de Sentinel-2 (Copernicus/ESA) processadas via YOLOv8 para classificação de uso do solo (plantios, áreas degradadas, regeneração)
- **📡 IoT em campo** — ESP32 com sensor capacitivo de umidade do solo publicando leituras em tempo real
- **🧠 ML preditivo** — scikit-learn LinearRegression projetando escassez hídrica em 6 meses (R² 0.995)
- **☁️ Cloud serverless** — AWS Lambda + Amazon Bedrock (Claude 3.5 Sonnet) para briefings executivos automáticos
- **🌐 Aprendizado federado** — dados brutos nunca saem dos nós; apenas gradientes trafegam (LGPD/GDPR compliant)
- **⛓️ Blockchain ledger** — tokenização de ações de regeneração ambiental em Postgres/SQLModel
- **🎨 Digital Twin 3D** — globo wireframe Three.js reativo, com WebSocket streaming a 60 FPS

---

## 📍 Onde está o projeto neste repositório

Este repositório segue a estrutura do portfólio **TIAO 2026** da FIAP. O projeto da Global Solution 2026.1 está dentro de:

```
1TIAO/Global-Solution-2/
```

Todos os comandos abaixo assumem que você está na **raiz deste repositório** após o clone.

---

## 🚀 Quick Start

### 1. Backend (FastAPI)

```bash
cd 1TIAO/Global-Solution-2/src/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- WebSockets: `ws://localhost:8000/ws/yolo` e `ws://localhost:8000/ws/blockchain`

### 2. Frontend (Next.js 15)

```bash
cd 1TIAO/Global-Solution-2/src/frontend
npm install
cp .env.example .env.local       # configurar NEXT_PUBLIC_USE_BACKEND=true
npm run dev
```

Acesse http://localhost:3000.

### 3. IoT (Simulador ESP32, opcional)

```bash
cd 1TIAO/Global-Solution-2/src/iot
pip install requests
python esp32_simulator.py --api https://nexus-sentinel-api-gpk9.onrender.com
```

A umidade do solo do dashboard começa a oscilar sozinha (ciclo dia/noite + ruído).

### 4. ML — Treino YOLOv8 (opcional)

```bash
cd 1TIAO/Global-Solution-2/src/backend/ml
pip install -r requirements-ml.txt
python synthesize_dataset.py        # gera 240 imagens 640x640
python train.py --quick             # 10 épocas (~5min em CPU)
```

Reinicie o backend — o `yolo_service.py` auto-descobre os pesos e passa a fazer inferência real.

### 5. AWS Lambda (opcional)

```bash
cd 1TIAO/Global-Solution-2/src/aws
sam build && sam deploy --guided
```

---

## 📁 Estrutura do Projeto

```
nexus-sentinel-gs-2026-1/                      ← raiz do repositório (portfólio TIAO)
├── README.md                                  ← este arquivo
├── 1TIAO/
│   └── Global-Solution-2/                     ← projeto da GS 2026.1
│       ├── README.md                          ← README detalhado da Global Solution
│       ├── DEPLOY.md                          ← guia de deploy Vercel + Render + Neon
│       ├── render.yaml                        ← Infrastructure as Code
│       ├── docs/
│       │   ├── nexus-sentinel-gs-26-1.pdf     ← PDF de entrega
│       │   └── gerar_pdf.py                   ← gerador do PDF (reportlab)
│       ├── assets/
│       │   ├── arq-macro.png                  ← arquitetura geral
│       │   ├── arq-fluxo-realtime.png         ← sequence diagram
│       │   └── arq-federated-learning.png     ← padrão federado
│       ├── data/
│       │   ├── README.md                      ← documentação dos dados
│       │   ├── samples/                       ← imagens de exemplo YOLO
│       │   ├── transactions_seed.json         ← seed do ledger
│       │   └── climate_baseline.json          ← estado climático nominal
│       └── src/
│           ├── frontend/                      ← Next.js 15 + TS + Tailwind + Framer + Three.js + Zustand
│           ├── backend/                       ← FastAPI + SQLModel + WebSockets + scikit-learn + boto3
│           │   ├── routers/                   ← 8 endpoints REST
│           │   ├── services/                  ← yolo · prediction · blockchain · mesh · bedrock · state
│           │   ├── ws/                        ← WebSocket hub
│           │   └── ml/                        ← YOLOv8 training pipeline
│           ├── iot/                           ← ESP32 simulator + firmware MicroPython
│           │   ├── esp32_simulator.py
│           │   ├── firmware/main.py
│           │   └── wiring.md
│           └── aws/                           ← AWS Lambda + SAM
│               ├── lambda_predict/            ← scikit-learn como Lambda
│               ├── lambda_briefing/           ← Bedrock + Claude 3.5
│               └── template.yaml              ← SAM template
└── 2TIAO/                                     ← placeholder para futuras atividades
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
| Banco de Dados | Postgres (Neon) via SQLModel para o ledger blockchain |
| Front-end / UI | Next.js 15 + Three.js + Framer Motion + Zustand |
| Dashboards | Globo wireframe reativo · gráficos · terminal blockchain |
| Análise de Dados Real-Time | WebSocket streaming · 60 FPS Three.js |
| Compliance / LGPD | Aprendizado federado: dados brutos nunca saem dos nós |

---

## 🎬 Vídeo Demonstrativo

🔗 **YouTube (Não Listado):** https://youtu.be/8eqUow8rGTI

---

## 📄 PDF de Entrega

O PDF da entrega está em [`1TIAO/Global-Solution-2/docs/nexus-sentinel-gs-26-1.pdf`](./1TIAO/Global-Solution-2/docs/nexus-sentinel-gs-26-1.pdf) (18 páginas, gerado automaticamente via reportlab).

Para regenerar:
```bash
pip install reportlab pypdf
python 1TIAO/Global-Solution-2/docs/gerar_pdf.py
```

---

## 🚀 Deploy Público

Para hospedar o sistema em produção (Vercel + Render + Neon, **gratuito**), siga o guia completo em [`1TIAO/Global-Solution-2/DEPLOY.md`](./1TIAO/Global-Solution-2/DEPLOY.md).

**Stack de produção:**
- 🌐 **Frontend** → Vercel (região São Paulo)
- 🐍 **Backend** → Render (Docker, free tier)
- 🗄️ **Postgres** → Neon (free perpétuo, sem expiração)
- ⏱️ **Uptime** → UptimeRobot (ping a cada 5min, elimina cold start)
- ☁️ **Lambdas (opcional)** → AWS SAM

**URLs públicas:**
- 🌍 **App ao vivo:** https://nexus-sentinel-gs-2026-1.vercel.app
- 🔌 **API:** https://nexus-sentinel-api-gpk9.onrender.com
- ❤️ **API Health:** https://nexus-sentinel-api-gpk9.onrender.com/health
- 📖 **API Docs (Swagger):** https://nexus-sentinel-api-gpk9.onrender.com/docs

---

## 📜 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sob <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

---

## 🙏 Agradecimentos

Às tutoras **Sabrina Otoni** e **Ana Cristina dos Santos** pelo acompanhamento durante o desenvolvimento das fases. Os feedbacks construtivos foram essenciais para a evolução técnica do projeto.

---

<p align="center">
<i>Desenvolvido pelo <b>Grupo Nexus</b> para a GS 2026.1 — FIAP Graduação ON em Inteligência Artificial</i>
</p>