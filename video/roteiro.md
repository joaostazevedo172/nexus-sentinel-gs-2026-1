# 🎬 Roteiro do Vídeo Demonstrativo — Nexus Sentinel

**Duração total:** ≤ 5 minutos · **Plataforma:** YouTube (não listado) · **Resolução mínima:** 1080p

> Frase obrigatória nos primeiros 10 segundos: **"QUERO CONCORRER"**

---

## 🎯 Estrutura por blocos

### ⏱️ 00:00–00:15 — Abertura institucional

**Tela:** Logo FIAP + título "Nexus Sentinel — Global Solution 2026.1"

**Narração:**
> "Somos o grupo Nexus. Apresentamos nosso projeto para a Global Solution 2026.1 da FIAP. **QUERO CONCORRER.** A pergunta da GS é: como a IA pode transformar a nova economia espacial e gerar impacto positivo na Terra? Nossa resposta é o Nexus Sentinel — um Gêmeo Digital de resiliência climática planetária."

---

### ⏱️ 00:15–00:45 — Problema e proposta

**Tela:** Diagrama de arquitetura (`assets/arq-macro.png`) preenchendo a tela

**Narração:**
> "Satélites como o Sentinel-2 geram petabytes de dados por dia, mas traduzir isso em decisões locais é o gargalo. Nosso sistema integra quatro camadas: sensores IoT em campo via ESP32, dados orbitais via Copernicus, processamento por YOLOv8 e scikit-learn, e serviços cognitivos via AWS Bedrock — tudo orquestrado por um backend FastAPI com WebSocket e persistência em SQLite."

---

### ⏱️ 00:45–02:30 — Demo do dashboard ao vivo (o coração do vídeo)

**Tela:** browser em fullscreen rodando `http://localhost:3000`

**Sequência operacional:**

1. **00:45** — Mostrar o dashboard em estado nominal. Apontar para o globo Three.js, os 12 nós pulsando, a resiliência em 87%.
2. **01:00** — Apontar para os 4 cards de métrica (Nós Conectados, Zonas de Risco, Resiliência Global, Modelos Federados) e o gráfico de throughput mesh.
3. **01:15** — Arrastar lentamente o slider de **Temperatura** de 0°C para +2.5°C. **Mostrar a reação em tempo real:**
   - Anel atmosférico do globo muda de ciano para magenta
   - Nós SP-BR e DEL-IN pulsam mais rápido
   - Alertas ativos sobem de 3 para 6
   - Resiliência Global cai de 87% para ~52%
   - Cor da barra de resiliência muda
4. **01:45** — Botão **"Ativar Aprendizado Federado"** aparece (resiliência < 65%). Clicar nele.
5. **02:00** — Mostrar o burst federado: globo acelera rotação, 6 transações `Burst Federado +32 NXS` aparecem no canto, resiliência sobe.
6. **02:15** — Abrir o drawer **"Predição IA"** — mostrar YOLOv8 detecções rotacionando + gráfico scikit-learn com R² 0.995. Clicar em "Emitir Alerta Preventivo para ONGs".

**Narração:** descrever cada ação à medida que mostra ("estou arrastando o slider de temperatura… observem o anel do globo mudando de cor… a resiliência caindo em tempo real…").

---

### ⏱️ 02:30–03:00 — Blockchain Ledger e Mesh

**Tela:** alternar entre drawers de Blockchain Ledger e Rede Mesh

**Narração:**
> "Cada detecção do YOLO que identifica regeneração ambiental gera automaticamente um smart contract registrado no nosso ledger SQLite, tokenizando a ação como Nexus Tokens. As transações sobrevivem a restart do servidor — não é mock. Já a Rede Mesh mostra a topologia federada: dados brutos nunca saem dos nós, apenas gradientes agregados — compliance LGPD e GDPR por construção."

---

### ⏱️ 03:00–03:45 — Briefing IA via Bedrock + IoT ao vivo

**Tela 1:** drawer "Briefing IA"

**Narração:**
> "Aqui está nossa integração com serviços cognitivos: o botão 'Gerar Briefing' chama uma função AWS Lambda que invoca o Claude 3.5 Sonnet via Amazon Bedrock para sintetizar o estado climático atual em uma análise executiva em português. Se Bedrock estiver indisponível, o sistema cai automaticamente para um briefing template — graceful degradation em todas as camadas."

**Tela 2:** Terminal mostrando `python esp32_simulator.py` rodando, com o slider de Umidade do dashboard se movendo sozinho em resposta

**Narração:**
> "Aqui o simulador do ESP32 publicando umidade do solo no backend a cada 5 segundos. O slider do dashboard se move sozinho — em hardware real, isso seria um sensor capacitivo no GPIO 34 do ESP32 com MicroPython. O firmware está em iot/firmware/main.py, pronto para deploy."

---

### ⏱️ 03:45–04:20 — Código e arquitetura

**Tela:** alternar entre VSCode mostrando `services/yolo_service.py`, `prediction_service.py`, `lambda_briefing/lambda_function.py`

**Narração:**
> "Vou mostrar rapidamente os pontos críticos do código. Aqui o `yolo_service` faz auto-discovery dos pesos treinados — se acha, faz inferência real; se não, cai para mock. Aqui o `prediction_service` usando scikit-learn com features polinomiais. Aqui a Lambda do Bedrock. Tudo deployável via SAM. O frontend usa Zustand para estado global e Three.js puro para o globo — sem dependência de Spline ou serviços externos."

---

### ⏱️ 04:20–04:45 — Resultados e diferencial

**Tela:** slide com métricas validadas

**Narração:**
> "Resumindo o que entregamos: 8 endpoints REST + 2 WebSocket testados via TestClient, modelo sklearn com R² 0.995 em holdout, pipeline YOLO completo, 2 funções Lambda smoke-testadas, IoT simulador + firmware MicroPython real, integração Bedrock com fallback, e cerca de 3.900 linhas de código entre Python e TypeScript. O sistema integra ML, visão computacional, IoT, cloud, serviços cognitivos, banco de dados e dashboards — todas as disciplinas que vimos no curso."

---

### ⏱️ 04:45–05:00 — Fechamento

**Tela:** slide final com logo Nexus + nomes dos integrantes + link do repo

**Narração:**
> "O Nexus Sentinel mostra como dados de satélite podem virar decisões operacionais sem comprometer privacidade. Obrigado, FIAP. Equipe Nexus."

---

## 🛠️ Dicas técnicas para gravação

- **OBS Studio** ou **ScreenFlow**: gravar em 1920×1080 a 30fps.
- **Áudio**: microfone próximo (USB ou lavalier), gravar em sala silenciosa, usar `noisereduce` ou Audacity Noise Gate em pós.
- **Setup pré-gravação**:
  1. Backend rodando: `uvicorn main:app --reload --port 8000`
  2. Frontend rodando: `npm run dev` em `http://localhost:3000`
  3. ESP32 simulator rodando: `python iot/esp32_simulator.py`
  4. Resetar a database: `rm src/backend/nexus.db` antes da gravação para começar do zero
  5. Limpar abas do browser e fechar tudo desnecessário
  6. Modo escuro do macOS/Windows para evitar bleeding de luz na tela
- **Editor**: DaVinci Resolve (gratuito) ou CapCut. Cortar respiros, acelerar trechos lentos para 1.2x, adicionar lower-thirds nos nomes dos integrantes.
- **Subtítulos**: gerar automaticamente no YouTube e revisar (banca aprecia).
- **Música**: opcional, low-volume (-30dB). Usar trilha royalty-free (YouTube Audio Library: "Cinematic", "Tech").
- **Thumbnail**: print do globo Three.js em estado crítico (anel magenta) + título grande.

## 📤 Upload

1. YouTube → Studio → Upload
2. Visibilidade: **Não listado** (obrigatório pelo enunciado)
3. Título: `Nexus Sentinel — Global Solution 2026.1 FIAP — QUERO CONCORRER`
4. Descrição: copiar a seção "Proposta" do README + links
5. Capítulos: usar os timestamps acima (YouTube renderiza automaticamente)
6. Copiar o link e colar no PDF (`docs/nexus-sentinel-gs-2026-1.pdf`, seção 5.2) antes do submit final.
