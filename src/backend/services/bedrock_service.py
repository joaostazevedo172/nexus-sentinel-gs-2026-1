"""Serviço cognitivo — Briefing Executivo.

Replica a lógica da Lambda `nexus-generate-briefing` para uso direto pelo
backend FastAPI (mais rápido em demos locais, sem custo). Em produção
substitua a chamada local pela invocação da Lambda via boto3.
"""
from __future__ import annotations

import json
import os
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    _BEDROCK_AVAILABLE = True
except ImportError:
    _BEDROCK_AVAILABLE = False


def _bedrock_briefing(state: dict) -> Optional[str]:
    """Chama o Claude 3.5 Sonnet via Amazon Bedrock. Retorna None em falha."""
    if not _BEDROCK_AVAILABLE:
        return None
    if not os.getenv("AWS_ACCESS_KEY_ID") and not os.path.exists(
        os.path.expanduser("~/.aws/credentials")
    ):
        return None

    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
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
    except (ClientError, NoCredentialsError, KeyError, json.JSONDecodeError) as e:
        print(f"[bedrock] fallback (erro: {e})")
        return None


def _template_briefing(state: dict) -> str:
    """Briefing determinístico — fallback quando Bedrock não disponível."""
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


def generate_briefing(state: dict) -> tuple[str, str]:
    """Gera briefing. Retorna (texto, modelo_usado)."""
    text = _bedrock_briefing(state)
    if text is not None:
        return text, "anthropic.claude-3-5-sonnet-v2"
    return _template_briefing(state), "template-fallback"
