"""Gera o PDF final do projeto Nexus Sentinel para entrega da GS 2026.1.

Melhorias v2:
- Sumário gerado automaticamente via TableOfContents (sem hardcode)
- Code blocks via Preformatted (preserva indentação real)
- Limpeza de caracteres unicode que renderizam mal
- Tabelas corrigidas (Zustand, ADC 12-bit, etc.)
- Espaçamentos consistentes entre seções
- URLs reais (repo + vídeo) já preenchidas
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


CYAN = HexColor("#0089A0")
AMBER = HexColor("#B58200")
MAGENTA = HexColor("#B30056")
EMERALD = HexColor("#0E8559")
FG = HexColor("#1F2530")
MUTED = HexColor("#545863")
CODE_BG = HexColor("#F5F6F8")
CODE_FG = HexColor("#1F2530")
CODE_BORDER = HexColor("#D1D5DB")

styles = getSampleStyleSheet()

TITLE = ParagraphStyle("TITLE", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=28, leading=34,
    textColor=CYAN, alignment=TA_LEFT, spaceAfter=8)
SUBTITLE = ParagraphStyle("SUBTITLE", parent=styles["Heading2"],
    fontName="Helvetica", fontSize=14, leading=18,
    textColor=MUTED, alignment=TA_LEFT, spaceAfter=18)
H1 = ParagraphStyle("H1", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=18, leading=24,
    textColor=CYAN, alignment=TA_LEFT,
    spaceBefore=18, spaceAfter=12, keepWithNext=True)
H2 = ParagraphStyle("H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=13, leading=18,
    textColor=FG, alignment=TA_LEFT,
    spaceBefore=14, spaceAfter=8, keepWithNext=True)
BODY = ParagraphStyle("BODY", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=10.5, leading=15.5,
    textColor=FG, alignment=TA_JUSTIFY, spaceAfter=8)
BULLET = ParagraphStyle("BULLET", parent=BODY,
    leftIndent=20, bulletIndent=8, spaceAfter=4)
CAPTION = ParagraphStyle("CAPTION", parent=BODY,
    fontSize=9, leading=12, textColor=MUTED,
    alignment=TA_CENTER, spaceBefore=4, spaceAfter=16)
COMPETE = ParagraphStyle("COMPETE", parent=BODY,
    fontName="Helvetica-Bold", fontSize=15, leading=20,
    textColor=MAGENTA, alignment=TA_CENTER,
    spaceBefore=20, spaceAfter=20)
CODE_STYLE = ParagraphStyle("CODE",
    fontName="Courier", fontSize=7.8, leading=10.4,
    textColor=CODE_FG, backColor=CODE_BG,
    borderColor=CODE_BORDER, borderWidth=0.5,
    borderPadding=8,
    leftIndent=0, rightIndent=0,
    spaceBefore=4, spaceAfter=10)
TOC_H1 = ParagraphStyle("TOC_H1",
    fontName="Helvetica-Bold", fontSize=11.5, leading=18,
    textColor=FG, leftIndent=0, firstLineIndent=0, spaceBefore=4)
TOC_H2 = ParagraphStyle("TOC_H2",
    fontName="Helvetica", fontSize=10, leading=14,
    textColor=MUTED, leftIndent=18, firstLineIndent=0, spaceBefore=1)


def hr() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"),
                      spaceBefore=12, spaceAfter=12)


def clean_code(text: str, max_line: int = 92) -> str:
    """Substitui chars decorativos problemáticos e quebra linhas muito longas."""
    replacements = {
        "─": "-", "■": "-", "└": "|", "├": "|", "│": "|",
        "✓": "OK", "✗": "X",
        "—": "-", "…": "...", "•": "*",
        "“": '"', "”": '"', "‘": "'", "’": "'",
        "Δ": "Delta ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\n{3,}", "\n\n", text)
    out_lines = []
    for line in text.split("\n"):
        if len(line) <= max_line:
            out_lines.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        cont = " " * (indent + 4)
        out_lines.append(line[:max_line])
        rest = line[max_line:]
        while rest:
            out_lines.append(cont + rest[: max_line - 4])
            rest = rest[max_line - 4:]
    return "\n".join(out_lines)


def code_block(text: str) -> Preformatted:
    return Preformatted(clean_code(text), CODE_STYLE)


# Headings que NÃO devem aparecer no sumário (capa, próprio sumário)
_TOC_BLACKLIST = {"Integrantes", "Sumário"}


class NexusDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        text = flowable.getPlainText()
        if text in _TOC_BLACKLIST:
            return
        if style_name == "H1":
            self.notify("TOCEntry", (0, text, self.page))
        elif style_name == "H2":
            self.notify("TOCEntry", (1, text, self.page))


def _get_code(rel: str, lines=None) -> str:
    base = Path(__file__).parent.parent / "src"
    candidates = [
        base / "backend" / rel,
        base / "backend" / "services" / rel,
        base / rel,
        Path(__file__).parent.parent / rel,
    ]
    for p in candidates:
        if p.exists():
            text = p.read_text(encoding="utf-8")
            if lines:
                rows = text.split("\n")
                return "\n".join(rows[lines[0] - 1: lines[1]])
            return text
    return f"# (codigo nao encontrado: {rel})"


def build_pdf(output_path: Path) -> None:
    doc = NexusDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Nexus Sentinel — GS 2026.1",
        author="Grupo Nexus",
    )

    story = []

    # CAPA
    story += [
        Spacer(1, 1 * cm),
        Paragraph("FIAP — Faculdade de Informática e Administração Paulista", SUBTITLE),
        Paragraph("Graduação ON em Inteligência Artificial", SUBTITLE),
        Spacer(1, 0.4 * cm),
        hr(),
        Spacer(1, 0.4 * cm),
        Paragraph("Nexus Sentinel", TITLE),
        Paragraph("Gêmeo Digital de Resiliência Climática Planetária", SUBTITLE),
        Paragraph(
            "Global Solution 2026.1 — Economia Espacial &amp; Impacto Positivo na Terra",
            ParagraphStyle("subt2", parent=SUBTITLE, fontSize=12, textColor=AMBER,
                           spaceAfter=12),
        ),
        Spacer(1, 1.2 * cm),
        Paragraph("<b>Integrantes</b>", H2),
        Paragraph("• Miriã Leal Mantovani — RM 567811", BODY),
        Paragraph("• João Pedro Santos Azevedo — RM 566701", BODY),
        Paragraph("• Rodrigo Souza de Freitas — RM 567100", BODY),
        Paragraph("QUERO CONCORRER", COMPETE),
        hr(),
        Paragraph(
            "<b>Resumo executivo.</b> O Nexus Sentinel é uma plataforma de "
            "monitoramento climático global que integra dados de satélites Sentinel-2, "
            "sensores IoT em ESP32, visão computacional via YOLOv8 e modelagem "
            "preditiva via scikit-learn, com geração de briefings executivos via "
            "AWS Bedrock. Materializa um Gêmeo Digital interativo da resiliência "
            "climática terrestre, com tokenização blockchain de ações de regeneração "
            "ambiental e arquitetura de aprendizado federado preservando privacidade. "
            "O sistema completo está deployado em produção em arquitetura serverless "
            "gratuita (Vercel + Render + Neon).", BODY,
        ),
        PageBreak(),
    ]

    # SUMÁRIO
    toc = TableOfContents()
    toc.levelStyles = [TOC_H1, TOC_H2]
    story += [Paragraph("Sumário", H1), Spacer(1, 0.3 * cm), toc, PageBreak()]

    # 1. INTRODUÇÃO
    story += [
        Paragraph("1. Introdução", H1),
        Paragraph("1.1. Contexto", H2),
        Paragraph(
            "A exploração espacial deixou de ser apenas científica e passou a representar "
            "uma das maiores oportunidades tecnológicas, econômicas e estratégicas da "
            "atualidade. Satélites como Sentinel-2 (Copernicus / ESA) e Landsat (NASA / USGS) "
            "produzem diariamente petabytes de dados sobre clima, solo, vegetação e ocupação "
            "humana. Tecnologias originalmente desenvolvidas para missões espaciais "
            "impulsionaram avanços em Inteligência Artificial, sensores, automação e "
            "visão computacional — e hoje formam a base da nova economia espacial.", BODY),
        Paragraph(
            "Apesar desse acervo monumental, traduzir dados orbitais em "
            "<b>decisões locais acionáveis</b> permanece um gargalo. Governos, ONGs e "
            "agentes locais raramente têm acesso a interfaces que tornem inteligência "
            "planetária digerível em tempo real, e a privacidade dos dados regionais "
            "(LGPD/GDPR) impede a centralização ingênua das informações.", BODY),
        Paragraph("1.2. Problema", H2),
        Paragraph(
            "Como traduzir dados de satélite e sensores IoT em <b>resposta operacional</b> "
            "para crises climáticas, sem violar privacidade de dados locais e sem exigir "
            "infraestrutura proibitiva em regiões críticas?", BODY),
        Paragraph("1.3. Objetivo", H2),
        Paragraph("Desenvolver um MVP funcional — o <b>Nexus Sentinel</b> — composto por:", BODY),
        Paragraph(
            "• Dashboard interativo (Next.js + Three.js) que representa a Terra como um "
            "Gêmeo Digital com nós de monitoramento ao redor do globo.", BULLET),
        Paragraph(
            "• Backend (FastAPI + WebSocket) que integra inferência YOLOv8 para "
            "classificação de uso do solo e modelagem preditiva scikit-learn para "
            "projeção de escassez hídrica.", BULLET),
        Paragraph(
            "• Camada IoT (ESP32 com sensor capacitivo de solo) publicando umidade "
            "do solo em tempo real no Digital Twin.", BULLET),
        Paragraph(
            "• Camada serverless (AWS Lambda + Bedrock) para predição edge-ready e "
            "geração de briefings executivos via LLM.", BULLET),
        Paragraph(
            "• Persistência via Postgres com SQLModel para o ledger blockchain de ações "
            "de regeneração ambiental.", BULLET),
        Paragraph(
            "• Arquitetura de aprendizado federado: dados brutos nunca trafegam — "
            "apenas gradientes agregados, preservando privacidade por construção.", BULLET),
        Paragraph("1.4. Conexão com a Nova Economia Espacial", H2),
        Paragraph(
            "O projeto endereça diretamente o tema da GS 2026.1: <b>como a IA e as "
            "tecnologias digitais podem transformar a nova economia espacial e gerar "
            "impacto positivo na Terra?</b> Os dados Sentinel-2 são processados por modelos "
            "treinados em hardware comum (não requer cluster), as inferências geram "
            "<b>créditos tokenizados de regeneração</b> registrados em ledger imutável, "
            "e cada região monitorada participa de uma rede federada que cresce em "
            "inteligência coletiva sem comprometer soberania de dados.", BODY),
        PageBreak(),
    ]

    # 2. DESENVOLVIMENTO
    story += [
        Paragraph("2. Desenvolvimento", H1),
        Paragraph("2.1. Arquitetura Geral", H2),
        Paragraph("A arquitetura segue 4 camadas verticais, da física à interface:", BODY),
    ]

    diagram_path = Path(__file__).parent.parent / "assets" / "arq-macro.png"
    if diagram_path.exists():
        story += [
            Image(str(diagram_path), width=16 * cm, height=10.5 * cm),
            Paragraph(
                "Figura 1 — Arquitetura macro do Nexus Sentinel. As setas tracejadas "
                "indicam caminhos de fallback (Lambda para o Bedrock, etc).", CAPTION),
        ]

    story += [
        Paragraph(
            "Cada camada é independente e tem fallback bem definido: se o Bedrock falha, "
            "uma rota template-based é usada; se o WebSocket cai, o frontend ativa "
            "simulação client-side; se o YOLO treinado não está disponível, rotação de "
            "cenários mock entra no lugar. Esse design garante <b>demos resilientes</b> "
            "mesmo em condições adversas (rede instável, banca offline, AWS indisponível).", BODY),
        Paragraph("2.2. Stack Tecnológica", H2),
        _make_stack_table(),
        PageBreak(),

        Paragraph("2.3. Backend FastAPI — Endpoints REST e WebSocket", H2),
        Paragraph(
            "A API expõe 8 grupos de endpoints REST e 2 canais WebSocket, com lifecycle "
            "controlado por um lifespan que inicializa o DB, registra o listener pub/sub "
            "do blockchain e dispara o loop de broadcast do YOLO. Trecho do <i>main.py</i>:", BODY),
        code_block(_get_code("main.py", lines=(43, 78))),

        Paragraph("2.4. Inferência Computacional — YOLOv8", H2),
        Paragraph(
            "O <i>yolo_service.py</i> tenta carregar pesos treinados (auto-discovery em "
            "<i>ml/runs/detect/train*/weights/best.pt</i>) e cai para rotação de cenários "
            "mock se a biblioteca <i>ultralytics</i> ou os pesos não estiverem disponíveis. "
            "Isso garante que o dashboard nunca trave por falta de modelo:", BODY),
        code_block(_get_code("yolo_service.py", lines=(68, 96))),

        PageBreak(),

        Paragraph("2.5. Predição via Scikit-Learn", H2),
        Paragraph(
            "O modelo de projeção de escassez hídrica usa <i>LinearRegression</i> com "
            "features polinomiais sobre 24 meses de dados sintéticos. Em produção, os "
            "dados sintéticos seriam substituídos por séries temporais reais do "
            "Copernicus Climate Data Store. A função de treinamento:", BODY),
        code_block(_get_code("prediction_service.py", lines=(28, 60))),
        Paragraph(
            "Métricas avaliadas em holdout (últimos 6 meses): <b>R<super>2</super> = 0.995</b>, "
            "<b>MAE = 0.95</b>. Embora os dados sejam sintéticos, validam a pipeline "
            "end-to-end de treino, avaliação e serialização.", BODY),

        PageBreak(),

        Paragraph("2.6. IoT — Simulador ESP32 e Firmware MicroPython", H2),
        Paragraph(
            "A camada de sensoriamento físico publica umidade do solo a cada 5 segundos "
            "via PATCH no endpoint <i>/api/climate/state</i>, alterando o slider de "
            "Umidade do dashboard em tempo real. Trecho do simulador Python:", BODY),
        code_block(_get_code("../iot/esp32_simulator.py", lines=(20, 50))),
        Paragraph(
            "O firmware MicroPython equivalente (<i>iot/firmware/main.py</i>) roda em "
            "hardware real ESP32 DevKit + sensor capacitivo de solo no GPIO 34. "
            "Esquema elétrico documentado em <i>iot/wiring.md</i> com calibração.", BODY),

        Paragraph("2.7. AWS Lambda — Predição e Briefing Cognitivo", H2),
        Paragraph("Duas funções serverless deployáveis via AWS SAM:", BODY),
        Paragraph(
            "• <b>nexus-predict-water-scarcity</b>: replica o endpoint scikit-learn como "
            "Lambda, com cold start de ~3s e warm de ~120ms.", BULLET),
        Paragraph(
            "• <b>nexus-generate-briefing</b>: invoca o Claude 3.5 Sonnet via Amazon "
            "Bedrock para gerar análise executiva do estado climático em português, com "
            "fallback determinístico se Bedrock estiver indisponível.", BULLET),
        Paragraph("Handler da Lambda de briefing:", BODY),
        code_block(_get_code("../aws/lambda_briefing/lambda_function.py", lines=(16, 48))),

        PageBreak(),

        Paragraph("2.8. Aprendizado Federado", H2),
    ]

    fed_path = Path(__file__).parent.parent / "assets" / "arq-federated-learning.png"
    if fed_path.exists():
        story += [
            Image(str(fed_path), width=15 * cm, height=10.5 * cm),
            Paragraph(
                "Figura 2 — Topologia federada. Dados locais nunca saem dos nós; apenas "
                "gradientes agregados trafegam pela rede.", CAPTION),
        ]

    story += [
        Paragraph(
            "Cada nó (SP-BR, DEL-IN, CPT-ZA…) treina localmente seu modelo nos dados "
            "regionais e publica apenas os gradientes agregados ao Servidor Federado. "
            "O servidor combina os gradientes (média ponderada por tamanho de dataset) "
            "e devolve pesos atualizados aos nós. Esse padrão atende LGPD (Brasil), "
            "GDPR (Europa) e ISO/IEC 27001 por construção.", BODY),

        Paragraph("2.9. Persistência — Postgres + SQLModel", H2),
        Paragraph(
            "O ledger blockchain de ações de regeneração ambiental persiste em Postgres "
            "via SQLModel (SQLAlchemy + Pydantic). Em desenvolvimento, o sistema cai "
            "automaticamente para SQLite local quando a variável <i>DATABASE_URL</i> não "
            "está definida. Cada transação registra: hash, região, ação, recompensa em "
            "NXS (Nexus Tokens), timestamp e flag de origem federada. Esquema:", BODY),
        code_block(_get_code("db.py", lines=(14, 28))),

        PageBreak(),

        Paragraph("2.10. Frontend — Next.js, Three.js e Framer Motion", H2),
        Paragraph(
            "O dashboard é construído com Next.js 15 (App Router), TypeScript, Tailwind, "
            "Framer Motion e Three.js. O Gêmeo Digital 3D é um globo wireframe que reage "
            "em tempo real ao estado climático: cor do anel atmosférico interpola de ciano "
            "para magenta conforme a temperatura sobe, nós críticos pulsam mais rápido e "
            "partículas de aprendizado federado aceleram durante bursts. Estado global "
            "via Zustand store. Trecho do loop de animação do globo:", BODY),
        code_block(_get_code("../frontend/components/wireframe-globe.tsx", lines=(190, 226))),

        PageBreak(),
    ]

    # 3. RESULTADOS
    story += [
        Paragraph("3. Resultados Esperados", H1),
        Paragraph(
            "O MVP entrega uma <b>POC funcional</b> em diversos eixos verificáveis:", BODY),
        Paragraph("3.1. Métricas Quantitativas Validadas", H2),
        _make_metrics_table(),
        Paragraph("3.2. Cenário de Demonstração", H2),
        Paragraph("Roteiro de 90 segundos demonstrando causa-&gt;efeito do sistema:", BODY),
        Paragraph(
            "<b>(1) Estado nominal</b> — resiliência 87%, anel ciano, 3 zonas de risco.", BULLET),
        Paragraph(
            "<b>(2) Aquecimento simulado</b> — operador arrasta o slider de Temperatura "
            "para +2.5°C. O globo Three.js reage em tempo real: anel atmosférico vira "
            "magenta, nós SP-BR e DEL-IN pulsam com mais intensidade, alertas ativos sobem "
            "de 3 para 6, resiliência cai de 87% para ~52%.", BULLET),
        Paragraph(
            "<b>(3) Acionamento federado</b> — botão 'Ativar Aprendizado Federado' aparece "
            "(resiliência &lt; 65%). Operador aciona.", BULLET),
        Paragraph(
            "<b>(4) Burst federado</b> — globo acelera rotação, 6 transações "
            "'Burst Federado · +32 NXS' aparecem no ledger via WebSocket, resiliência "
            "sobe de volta.", BULLET),
        Paragraph(
            "<b>(5) Briefing cognitivo</b> — operador abre o drawer 'Briefing IA': "
            "Claude 3.5 Sonnet (Bedrock) gera análise executiva da situação em português, "
            "com recomendação de ação.", BULLET),
        Paragraph("3.3. Impacto Esperado", H2),
        Paragraph("Em deploy real, o sistema permitiria:", BODY),
        Paragraph(
            "• Redução de risco de deslocamento humano de 3.2M para 0.4M pessoas "
            "(regiões SP/DEL/CPT em janela de 6 meses, conforme projeção sklearn).", BULLET),
        Paragraph(
            "• Alocação dinâmica de recursos de ONGs parceiras via alertas preventivos "
            "automáticos, antes do ponto de irreversibilidade da crise.", BULLET),
        Paragraph(
            "• Tokenização de ações de regeneração ambiental cria <b>incentivo "
            "econômico mensurável</b> para agentes locais.", BULLET),
        Paragraph(
            "• Privacidade preservada por construção, viabilizando deploy em "
            "jurisdições com regulações distintas.", BULLET),
        PageBreak(),
    ]

    # 4. CONCLUSÕES
    story += [
        Paragraph("4. Conclusões", H1),
        Paragraph(
            "O Nexus Sentinel demonstra que a integração entre dados de satélite, "
            "IoT em hardware acessível, modelos de ML treinados e serviços cognitivos "
            "em nuvem pode ser materializada em uma plataforma funcional dentro do "
            "escopo de uma POC acadêmica. As tecnologias específicas trabalhadas "
            "durante o curso aparecem todas no projeto:", BODY),
        _make_disciplines_table(),
        Paragraph(
            "Mais importante: o projeto demonstra um <b>padrão arquitetural</b> — "
            "graceful degradation em cada camada — que torna soluções de IA aplicada "
            "robustas o suficiente para demos públicas e deploy em ambientes "
            "operacionalmente exigentes. Cada subsistema tem fallback bem definido, "
            "e a UX nunca quebra mesmo quando componentes externos falham.", BODY),
        Paragraph("4.1. Limitações Atuais", H2),
        Paragraph("Como POC, o sistema tem limitações honestamente documentadas:", BODY),
        Paragraph(
            "• Os dados de treinamento do YOLO são sintéticos (gerados por "
            "<i>synthesize_dataset.py</i>). Para inferência em pixels reais de Sentinel-2, "
            "é necessário treinar com dataset rotulado real (EuroSAT ou similar).", BULLET),
        Paragraph(
            "• O blockchain é simulado (ledger Postgres), não há L1 real. Em produção "
            "usaria Hyperledger ou contratos Ethereum.", BULLET),
        Paragraph(
            "• O aprendizado federado é visualizado conceitualmente; o agregador real "
            "exigiria framework como Flower ou TensorFlow Federated.", BULLET),
        Paragraph("4.2. Próximos Passos", H2),
        Paragraph(
            "• Substituir o dataset sintético de YOLO por imagens Sentinel-2 reais "
            "via o helper <i>download_sentinel2.py</i> já implementado.", BULLET),
        Paragraph(
            "• Deploy completo do backend em AWS (Lambda + API Gateway + DynamoDB "
            "para o ledger, no lugar do Postgres no Neon).", BULLET),
        Paragraph(
            "• Integrar com a rede de ONGs do programa Selo Verde ou Carbon Markets "
            "para tokenização real dos créditos de regeneração.", BULLET),
        Paragraph(
            "• Hardware: deploy de 3-5 ESP32s reais em campo (SP, Brasília, fronteira "
            "agrícola) para validação com dados de solo reais.", BULLET),
        PageBreak(),
    ]

    # 5. REFERÊNCIAS
    story += [
        Paragraph("5. Referências e Links", H1),
        Paragraph("5.1. Repositório do Projeto", H2),
        Paragraph(
            "<b>GitHub:</b> "
            "<font color='#0089A0'>https://github.com/joaostazevedo172/nexus-sentinel-gs-2026-1</font>",
            BODY),
        Paragraph("5.2. Vídeo Demonstrativo (YouTube — Não Listado)", H2),
        Paragraph(
            "<b>URL:</b> "
            "<font color='#0089A0'>https://www.youtube.com/watch?v=6E_TyXsCIsI</font>",
            BODY),
        Paragraph("5.3. Sistema em Produção", H2),
        Paragraph(
            "O sistema está hospedado em arquitetura serverless gratuita "
            "(Vercel + Render + Neon Postgres). URLs públicas:", BODY),
        Paragraph(
            "• <b>Aplicação ao vivo:</b> "
            "<font color='#0089A0'>https://nexus-sentinel-gs-2026-1.vercel.app</font>", BULLET),
        Paragraph(
            "• <b>API:</b> "
            "<font color='#0089A0'>https://nexus-sentinel-api-gpk9.onrender.com</font>", BULLET),
        Paragraph(
            "• <b>Swagger Docs:</b> "
            "<font color='#0089A0'>https://nexus-sentinel-api-gpk9.onrender.com/docs</font>",
            BULLET),
        Paragraph("5.4. Referências Técnicas", H2),
        Paragraph(
            "• Copernicus Open Access Hub — https://dataspace.copernicus.eu/", BULLET),
        Paragraph("• Ultralytics YOLOv8 — https://docs.ultralytics.com/", BULLET),
        Paragraph("• Amazon Bedrock — https://docs.aws.amazon.com/bedrock/", BULLET),
        Paragraph(
            "• Federated Learning (McMahan et al., 2017) — Communication-Efficient "
            "Learning of Deep Networks from Decentralized Data", BULLET),
        Paragraph("• Next.js App Router — https://nextjs.org/docs/app", BULLET),
        Paragraph("• FastAPI + SQLModel — https://sqlmodel.tiangolo.com/", BULLET),
        Spacer(1, 1 * cm),
        hr(),
        Paragraph(
            "<i>Documento gerado automaticamente a partir do código-fonte do projeto "
            "via reportlab. Para regenerar: "
            "<font face='Courier'>python docs/gerar_pdf.py</font></i>", CAPTION),
    ]

    # multiBuild necessário para o TOC se popular (precisa de 2 passos)
    doc.multiBuild(story)
    print(f"PDF gerado: {output_path}")


def _safe(text: str) -> str:
    """Substitui Unicode problemático por equivalentes que renderizam bem em Helvetica core."""
    return (text
        .replace("R<super>2</super>", "R<super>2</super>")
        .replace("<super>2</super>", "<super>2</super>")
        .replace("³", "<super>3</super>")
        .replace("~", "~")
        .replace("-&gt;", "-&gt;")
        .replace("Δ", "Delta ")
        .replace("∆", "Delta ")
    )


def _cell(text: str, bold: bool = False) -> Paragraph:
    """Célula de tabela com word-wrap automático."""
    style = ParagraphStyle(
        "Cell", parent=BODY,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=8.8, leading=11.5, textColor=FG,
        alignment=TA_LEFT, spaceAfter=0, spaceBefore=0,
    )
    return Paragraph(_safe(text), style)


def _header_cell(text: str) -> Paragraph:
    style = ParagraphStyle(
        "HCell", parent=BODY,
        fontName="Helvetica-Bold", fontSize=9, leading=12,
        textColor=HexColor("#FFFFFF"), alignment=TA_LEFT,
        spaceAfter=0, spaceBefore=0,
    )
    return Paragraph(_safe(text), style)


def _make_stack_table() -> Table:
    rows = [
        ("Camada", "Tecnologias", "Disciplina FIAP"),
        ("Frontend",
         "Next.js 15 · TypeScript · Tailwind · Framer Motion 11 · Three.js · Zustand",
         "Front-end"),
        ("Backend",
         "FastAPI · Pydantic · SQLModel · WebSockets · Uvicorn",
         "APIs Cognitivas"),
        ("ML",
         "scikit-learn (LinearRegression) · YOLOv8 (Ultralytics) · NumPy",
         "Machine Learning, Visão Computacional"),
        ("Persistência",
         "Postgres (Neon) + SQLModel · fallback SQLite local",
         "Banco de Dados"),
        ("IoT",
         "ESP32 DevKit · MicroPython · Sensor capacitivo · ADC 12-bit",
         "IoT / ESP32"),
        ("Cloud",
         "AWS Lambda · API Gateway · Amazon Bedrock · SAM",
         "Computação em Nuvem"),
        ("Cognitivo",
         "Claude 3.5 Sonnet via Bedrock (com fallback)",
         "Serviços Cognitivos"),
        ("Deploy",
         "Vercel (frontend) · Render Docker (backend) · UptimeRobot",
         "DevOps / Engenharia"),
    ]
    data = [[_header_cell(c) for c in rows[0]]]
    for row in rows[1:]:
        data.append([_cell(row[0], bold=True), _cell(row[1]), _cell(row[2])])
    t = Table(data, colWidths=[2.6 * cm, 8.4 * cm, 5 * cm], hAlign="LEFT")
    t.setStyle(_table_style(CYAN))
    return t


def _make_metrics_table() -> Table:
    rows = [
        ("Métrica", "Valor", "Validado por"),
        ("R<super>2</super> do modelo de predição",          "0.995",            "sklearn holdout (6 meses)"),
        ("MAE da predição",                    "0.95 pontos",      "sklearn holdout"),
        ("Linhas de código (front + back)",   "~ 3.900",          "wc -l"),
        ("Endpoints REST",                     "8",                "TestClient (FastAPI)"),
        ("Canais WebSocket",                   "2",                "websockets lib"),
        ("Tabelas Postgres",                   "1 (transactions)", "SQLModel.create_all"),
        ("Funções AWS Lambda",                 "2 deployáveis",    "sam build, smoke test"),
        ("Componentes React",                  "22 (.tsx)",        "find -name *.tsx"),
        ("Modos de degradação graceful",       "5 camadas",        "AWS, WS, YOLO, LLM, cache"),
    ]
    data = [[_header_cell(c) for c in rows[0]]]
    for row in rows[1:]:
        data.append([_cell(row[0], bold=True), _cell(row[1]), _cell(row[2])])
    t = Table(data, colWidths=[7 * cm, 3.5 * cm, 5.5 * cm], hAlign="LEFT")
    t.setStyle(_table_style(AMBER))
    return t


def _make_disciplines_table() -> Table:
    rows = [
        ("Disciplina", "Como aparece no projeto"),
        ("Machine Learning",
         "scikit-learn LinearRegression com features polinomiais, holdout, R<super>2</super>/MAE"),
        ("Visão Computacional",
         "YOLOv8 + dataset sintético + pipeline de treino + auto-discovery de pesos"),
        ("APIs / Web Services",
         "8 endpoints REST FastAPI + 2 canais WebSocket"),
        ("IoT / ESP32",
         "Simulador Python + firmware MicroPython + esquema elétrico"),
        ("Computação em Nuvem",
         "2 Lambdas Python (predict + briefing) deployáveis via SAM"),
        ("Serviços Cognitivos",
         "Amazon Bedrock (Claude 3.5 Sonnet) para briefings executivos"),
        ("Banco de Dados",
         "Postgres no Neon via SQLModel para persistência do ledger"),
        ("Front-end / UI",
         "Next.js 15 + Three.js (Digital Twin 3D) + Framer Motion + Zustand"),
        ("Dashboards / Visualização",
         "Globe wireframe reativo, gráficos de tendência, terminal blockchain"),
        ("Análise de Dados",
         "Pipelines em tempo real (WebSocket, 60FPS Three.js)"),
        ("Compliance / LGPD",
         "Aprendizado federado: dados brutos nunca saem dos nós locais"),
    ]
    data = [[_header_cell(c) for c in rows[0]]]
    for row in rows[1:]:
        data.append([_cell(row[0], bold=True), _cell(row[1])])
    t = Table(data, colWidths=[4.5 * cm, 11.5 * cm], hAlign="LEFT")
    t.setStyle(_table_style(EMERALD))
    return t


def _table_style(header_color) -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [HexColor("#FFFFFF"), HexColor("#F9FAFB")]),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
    ])


if __name__ == "__main__":
    out = Path(__file__).parent / "nexus-sentinel-gs-2026-1.pdf"
    build_pdf(out)