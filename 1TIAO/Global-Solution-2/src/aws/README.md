# AWS — Camada Serverless

Funções AWS Lambda complementares ao backend FastAPI, deployáveis via SAM
(Serverless Application Model). Demonstram a arquitetura **Edge-Ready** que
o sistema foi desenhado para suportar.

## Funções

### 1. `nexus-predict-water-scarcity` (Lambda + API Gateway)

Replica o endpoint `/api/predict/water-scarcity` do backend, mas roda como
função serverless. Usa `scikit-learn` para regressão polinomial sobre dados
sintéticos de 24 meses.

- **Cold start**: ~3s
- **Warm**: ~120ms
- **Endpoint**: `GET /predict/water-scarcity?horizon=6`

### 2. `nexus-generate-briefing` (Lambda + Amazon Bedrock)

Recebe um snapshot do Digital Twin e gera um **Briefing Executivo** em
português via Claude 3.5 Sonnet (Amazon Bedrock). Se Bedrock falhar
(credenciais ausentes, throttling, modelo indisponível na região), cai
automaticamente para um briefing template-based — graceful degradation.

- **Endpoint**: `POST /briefing/generate`
- **Modelo**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Permissão IAM**: `bedrock:InvokeModel`

## Deploy

Pré-requisitos:
- AWS CLI configurado (`aws configure`)
- SAM CLI instalado (`brew install aws-sam-cli`)
- Para Bedrock: habilitar acesso ao modelo Claude 3.5 Sonnet no console
  ([instruções AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html))

```bash
sam build
sam deploy --guided
```

Outputs ao final mostram a URL do API Gateway:

```
ApiEndpoint = https://abc123.execute-api.us-east-1.amazonaws.com/Prod
```

Testes:

```bash
curl "https://abc123.execute-api.us-east-1.amazonaws.com/Prod/predict/water-scarcity?horizon=6"

curl -X POST "https://abc123.execute-api.us-east-1.amazonaws.com/Prod/briefing/generate" \
  -H "Content-Type: application/json" \
  -d '{"temperature": 2.5, "humidity": 45, "meshActivity": 80, "resilience": 52}'
```

## Integração com o frontend

Para usar os endpoints Lambda em vez dos endpoints FastAPI locais, configure
no `.env.local` do frontend:

```bash
NEXT_PUBLIC_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com/Prod
```

Os endpoints são compatíveis com o cliente HTTP em `lib/api.ts` sem nenhuma
mudança de código.

## Custo estimado (free tier)

| Função | Invocações grátis/mês | Após free tier |
|--------|----------------------|----------------|
| Predict | 1M | $0.20 / 1M invocações |
| Briefing | 1M Lambda + Bedrock cobrado por token | ~$3 / 1K briefings |

Para banca da FIAP, o uso fica completamente dentro do free tier.
