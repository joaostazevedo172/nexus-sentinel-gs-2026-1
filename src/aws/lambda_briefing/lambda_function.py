"""
AWS Lambda — Geração de Briefing Executivo via Amazon Bedrock.

Endpoint: POST /briefing/generate
Body:     ClimateState (current snapshot do Digital Twin)

Usa o modelo Claude 3.5 Sonnet via Bedrock para sintetizar o estado climático
em uma análise executiva curta, em português, adequada para apresentação à
banca ou liderança operacional.

Se o cliente Bedrock falhar (credenciais ausentes, throttling, etc), cai para
um briefing template-based local — graceful degradation.
"""
import json
import os
from typing import Any

# boto3 vem pré-instalado no runtime Lambda Python
import boto3
from botocore.exceptions import ClientError


def _bedrock_briefing(state: dict) -> str | None:
    """Gera briefing via Bedrock. Retorna None se falhar (cai para fallback)."""
    try:
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        prompt = (
            "Você é o analista-chefe de inteligência climática do sistema "
            "Nexus Sentinel. Gere um briefing executivo (máximo 4 parágrafos curtos, "
            "em português brasileiro, tom técnico-operacional) com base no estado "
            f"atual do Gêmeo Digital:\n\n"
            f"- Temperatura global (Δ°C da baseline): {state['temperature']:+.1f}\n"
            f"- Umidade do solo (média global): {state['humidity']:.1f}%\n"
            f"- Atividade da rede mesh federada: {state['meshActivity']:.0f}%\n"
            f"- Índice de resiliência global: {state['resilience']:.1f}%\n\n"
            "Estruture em: (1) Situação, (2) Riscos prioritários, "
            "(3) Recomendação de ação, (4) Outlook 24h. Seja objetivo."
        )

        resp = client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )
        payload = json.loads(resp["body"].read())
        return payload["content"][0]["text"]
    except (ClientError, KeyError, json.JSONDecodeError) as e:
        print(f"[bedrock] fallback (erro: {e})")
        return None


def _template_briefing(state: dict) -> str:
    """Fallback determinístico — gera briefing por templating quando Bedrock não está disponível."""
    temp = state["temperature"]
    hum = state["humidity"]
    mesh = state["meshActivity"]
    res = state["resilience"]

    if res > 80:
        situ = "Sistema operando em regime nominal."
        risco = "Nenhum risco crítico em horizonte de 24h."
        rec = "Manter monitoramento passivo. Sem necessidade de intervenção federada."
    elif res > 60:
        situ = f"Sistema sob estresse moderado (resiliência {res:.0f}%)."
        risco = f"Δ°C de {temp:+.1f} eleva risco em zonas costeiras e regiões semi-áridas."
        rec = "Preparar alertas preventivos para ONGs nas regiões prioritárias (SP-BR, DEL-IN, CPT-ZA)."
    else:
        situ = f"⚠ Sistema em regime crítico (resiliência {res:.0f}%)."
        risco = "Múltiplas zonas de risco ativas. Probabilidade de deslocamento humano nas próximas 8 semanas: ELEVADA."
        rec = "Acionar imediatamente o Aprendizado Federado para distribuir pesos atualizados aos nós críticos."

    outlook = (
        f"Outlook 24h: umidade média do solo {hum:.0f}% (tendência "
        f"{'estável' if 50 <= hum <= 75 else 'preocupante'}). "
        f"Rede mesh com {mesh:.0f}% de atividade."
    )

    return (
        f"**Situação.** {situ}\n\n"
        f"**Riscos prioritários.** {risco}\n\n"
        f"**Recomendação.** {rec}\n\n"
        f"**Outlook 24h.** {outlook}"
    )


def _cors_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": os.getenv("CORS_ORIGIN", "*"),
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def lambda_handler(event: dict, context: Any) -> dict:
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": _cors_headers(), "body": ""}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": _cors_headers(),
                "body": json.dumps({"error": "invalid JSON body"})}

    state = {
        "temperature":  float(body.get("temperature",   0.0)),
        "humidity":     float(body.get("humidity",     65.0)),
        "meshActivity": float(body.get("meshActivity", 78.0)),
        "resilience":   float(body.get("resilience",   87.0)),
    }

    text = _bedrock_briefing(state)
    used_bedrock = text is not None
    if text is None:
        text = _template_briefing(state)

    return {
        "statusCode": 200,
        "headers": _cors_headers(),
        "body": json.dumps({
            "briefing": text,
            "model": "anthropic.claude-3-5-sonnet-v2" if used_bedrock else "template-fallback",
            "snapshot": state,
        }),
    }
