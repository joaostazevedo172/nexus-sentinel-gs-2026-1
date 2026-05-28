# 🚀 Guia de Deploy — Nexus Sentinel

Deploy completo em produção com **dois serviços gratuitos**: Vercel para o
frontend Next.js, Render para o backend FastAPI + Postgres. Tempo total: ~15 minutos.

---

## Arquitetura de Produção

```
┌──────────────────────────┐         ┌──────────────────────────────┐
│       VERCEL             │         │         RENDER               │
│                          │         │                              │
│  ┌────────────────────┐  │         │  ┌────────────────────────┐  │
│  │  Next.js Frontend  │──┼─HTTPS──▶│  │  FastAPI Backend       │  │
│  │  (Edge Network)    │  │  REST   │  │  (Docker, free tier)   │  │
│  │  Global CDN        │──┼──WSS───▶│  │                        │  │
│  └────────────────────┘  │         │  └─────────┬──────────────┘  │
│                          │         │            │                 │
│  Region: gru1 (SP)       │         │  ┌─────────▼──────────────┐  │
│  Domain: *.vercel.app    │         │  │  Postgres (free 1GB)   │  │
└──────────────────────────┘         │  │  Auto-attached         │  │
                                     │  └────────────────────────┘  │
                                     │  Region: Oregon (US-W)       │
                                     │  Domain: *.onrender.com      │
                                     └──────────────────────────────┘
```

> **Latência esperada:** ~150–250ms São Paulo → Oregon. Aceitável para POC.
> Para latência mais baixa, alternativa: usar **Fly.io** com região `gru` (São Paulo) — config em `fly.toml` já incluída.

---

## 🔧 Passo 1: Subir o código no GitHub

Crie um novo repositório (ou use o template FIAP `TEMPLATE-TIAO-2026` já clonado):

```bash
cd NEXUS-SENTINEL-GS-2026-1
git init
git add .
git commit -m "Initial commit — Nexus Sentinel GS 2026.1"
git branch -M main
git remote add origin git@github.com:seu-usuario/seu-repo.git
git push -u origin main
```

---

## 🐍 Passo 2: Deploy do Backend (Render + Postgres)

### 2.1. Conta Render (gratuita)

1. Acesse https://render.com → **Sign up with GitHub** (autoriza o app a ler seus repositórios)
2. No dashboard → **New** → **Blueprint**
3. Selecione o repositório recém-criado
4. Render detecta automaticamente o `render.yaml` em `src/backend/`

   > **Importante:** Render lê `render.yaml` da **raiz** do repo. Se quiser deploy só do backend, mova o arquivo para a raiz:
   > ```bash
   > cp src/backend/render.yaml ./render.yaml
   > ```
   > E ajuste `dockerfilePath: ./src/backend/Dockerfile` no `render.yaml`.

5. Clique **Apply** — Render:
   - Cria o serviço web `nexus-sentinel-api`
   - Cria o Postgres `nexus-sentinel-db`
   - Conecta os dois (injeta `DATABASE_URL` automaticamente)
   - Faz o primeiro build & deploy (~3–5 min)

### 2.2. Verificar deploy

Quando ficar verde:
```bash
curl https://nexus-sentinel-api.onrender.com/health
# {"status":"ok"}

curl https://nexus-sentinel-api.onrender.com/api/predict/water-scarcity
# {"horizonMonths":6,"points":[...],"metrics":{"r2":0.995,...}}
```

### 2.3. (Opcional) Habilitar AWS Bedrock

No painel Render → seu serviço → **Environment**:

```
AWS_ACCESS_KEY_ID     = AKIAxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION            = us-east-1
```

> No console AWS, habilite o modelo Claude 3.5 Sonnet em **Bedrock → Model access** (us-east-1 ou us-west-2).

Reinicie o serviço. Agora `/api/briefing/generate` retorna `model: "anthropic.claude-3-5-sonnet-v2"` em vez de `template-fallback`.

### 2.4. Sobre o "cold start" do free tier

Render Free dorme depois de 15 min sem requisições. A primeira requisição depois disso leva ~30s pra acordar.

**Mitigação para a banca:** acordar o serviço 1 minuto antes da apresentação:
```bash
curl https://nexus-sentinel-api.onrender.com/health
```

Ou faça upgrade para o plano **Starter ($7/mês)** que mantém o serviço sempre ativo.

---

## ⚡ Passo 3: Deploy do Frontend (Vercel)

### 3.1. Conta Vercel (gratuita)

1. Acesse https://vercel.com → **Sign up with GitHub**
2. **Add New** → **Project** → selecione o repositório
3. **Root Directory:** `src/frontend`  (Vercel detecta Next.js automaticamente)
4. **Environment Variables** (cole estas duas):

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_USE_BACKEND` | `true` |
   | `NEXT_PUBLIC_API_URL` | `https://nexus-sentinel-api.onrender.com` |

5. **Deploy** — Vercel builda em ~2 min.

### 3.2. Verificar

Acesse a URL gerada (ex: `https://nexus-sentinel-xyz.vercel.app`).

- ✅ Dashboard carrega com globo Three.js girando
- ✅ DevTools → Network → WS → `wss://nexus-sentinel-api.onrender.com/ws/yolo` deve estar `101 Switching Protocols`
- ✅ Frames YOLO chegam a cada 3.2s
- ✅ Mover slider de temperatura → globo reage em tempo real
- ✅ Botão "Briefing IA" → drawer abre, gera análise

### 3.3. Configurar CORS de volta no backend

Volte no Render → seu serviço → **Environment**:

```
ALLOWED_ORIGINS = https://nexus-sentinel-xyz.vercel.app,https://*.vercel.app
```

(Substitua pela URL real da Vercel.) Reinicie o serviço Render.

> **Já está configurado por regex:** o backend aceita qualquer `*.vercel.app` que contenha `nexus-sentinel` no host, então previews de PR também funcionam.

---

## 📡 Passo 4: ESP32 Simulator em Produção

O simulador pode rodar localmente ou em qualquer VPS:

```bash
cd src/iot
pip install requests
python esp32_simulator.py \
  --api https://nexus-sentinel-api.onrender.com \
  --interval 10 \
  --sensor-id ESP32-DEMO-001
```

A umidade do solo do dashboard hospedado vai começar a oscilar.

---

## ☁️ Passo 5 (Opcional) — AWS Lambda

Se quiser publicar as Lambdas além do backend Render:

```bash
cd src/aws
pip install aws-sam-cli
aws configure                # acesse https://console.aws.amazon.com/iam/
sam build
sam deploy --guided
```

Anote o `ApiEndpoint` que aparece nos outputs. Para usar essa Lambda em vez do
endpoint do Render, atualize na Vercel:

```
NEXT_PUBLIC_API_URL = https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod
```

---

## 🔍 Troubleshooting

### "Failed to fetch" no browser, mas backend responde no curl

**Causa:** CORS mal configurado. Render usa a regex `*.vercel.app` por padrão, mas se você tem domínio custom, adicione manualmente em `ALLOWED_ORIGINS`.

### WebSocket conecta e fecha imediatamente

**Causa:** Render Free Tier suporta WebSocket, mas alguns proxies intermediários cortam após 60s de inatividade. O frontend tem **auto-reconnect a cada 5s** (em `lib/websocket.ts`), então é transparente. Para reduzir reconnections, faça upgrade para Starter.

### Cold start de 30s no primeiro acesso

Comportamento esperado do Render Free Tier. Acorde antes da banca ou upgrade.

### Postgres "too many connections"

Render Free Tier tem limite de ~97 conexões. O SQLModel está configurado com `pool_pre_ping=True` e gerencia bem, mas se reiniciar o backend muitas vezes em sequência, espere 1 minuto.

### `next/font/google` falha no build

Vercel tem acesso à internet de build, então não acontece em produção. Se rodar `npm run build` localmente sem internet, edite `app/layout.tsx` temporariamente para remover `next/font/google` (use fontes do sistema).

---

## 🎯 Checklist Final Pré-Banca

- [ ] Repositório no GitHub com o código completo
- [ ] Backend deployado no Render, `/health` retorna `{"status":"ok"}`
- [ ] Postgres do Render conectado (verificar em **Logs** do serviço)
- [ ] Frontend deployado na Vercel, URL anotada
- [ ] `NEXT_PUBLIC_API_URL` na Vercel apontando para o Render
- [ ] `ALLOWED_ORIGINS` no Render incluindo a URL Vercel
- [ ] Dashboard ao vivo abre e mostra o globo
- [ ] WebSockets conectando (verificar DevTools)
- [ ] Slider de temperatura faz o globo reagir
- [ ] Drawer "Briefing IA" responde (template-fallback é OK, Bedrock é bônus)
- [ ] PDF da entrega atualizado com a URL pública no campo 5.1 e 5.2
- [ ] Vídeo gravado e linkado

---

## 💰 Custo total

| Serviço | Plano | Custo |
|---------|-------|-------|
| Vercel  | Hobby | $0/mês (limite generoso de bandwidth) |
| Render Web | Free | $0/mês (sleeps após 15min idle) |
| Render Postgres | Free | $0/mês (1GB, 90 dias retenção) |
| **TOTAL** | | **$0/mês** |

Opcional:
- Render Starter (sem cold start): $7/mês
- AWS Bedrock (Claude 3.5 Sonnet): ~$3 por 1.000 briefings
- Domínio custom (.com.br): ~$40/ano

Para a banca, o stack 100% gratuito é mais que suficiente.
