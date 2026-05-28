"""Gera os 3 diagramas de arquitetura em PNG com identidade visual Nexus.

Cores:
  --nexus-bg     #0A0C10
  --nexus-cyan   #00F2FF
  --nexus-amber  #FFB800
  --nexus-magenta#FF007A
  --emerald      #10B981
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch
from matplotlib.lines import Line2D

BG = "#0A0C10"
FG = "#EDEDEF"
FG_DIM = "#8A8F98"
CYAN = "#00F2FF"
AMBER = "#FFB800"
MAGENTA = "#FF007A"
EMERALD = "#10B981"
PANEL = "#0F1218"
BORDER = "#1F2530"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": FG,
    "axes.edgecolor": BORDER,
    "savefig.facecolor": BG,
    "figure.facecolor": BG,
})


def make_axes(figsize=(14, 9)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.set_facecolor(BG)
    ax.axis("off")
    return fig, ax


def card(ax, x, y, w, h, text, color=CYAN, fontsize=10, bold=True):
    """Glassmorphism-style card."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.8",
        linewidth=1.4, edgecolor=color, facecolor=PANEL,
        alpha=0.95, zorder=2,
    )
    ax.add_patch(box)
    ax.text(
        x + w/2, y + h/2, text,
        ha="center", va="center",
        fontsize=fontsize, color=FG,
        fontweight="bold" if bold else "normal",
        zorder=3,
    )


def section(ax, x, y, w, h, title, color=CYAN):
    """Outer section frame with title in upper-left corner."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=1.2",
        linewidth=1.2, edgecolor=color, facecolor="#050608",
        alpha=0.7, linestyle="--", zorder=1,
    )
    ax.add_patch(box)
    ax.text(
        x + 0.8, y + h - 1.2, title,
        ha="left", va="top",
        fontsize=10, color=color,
        fontweight="bold",
        family="monospace",
        zorder=2,
    )


def arrow(ax, p1, p2, color=CYAN, label=None, label_offset=(0, 0.5), dashed=False, label_color=None):
    ls = (0, (4, 3)) if dashed else "-"
    a = FancyArrowPatch(
        p1, p2,
        arrowstyle="->,head_width=0.30,head_length=0.55",
        color=color, linewidth=1.4, linestyle=ls,
        connectionstyle="arc3,rad=0", zorder=4,
        mutation_scale=10,
    )
    ax.add_patch(a)
    if label:
        mid = ((p1[0] + p2[0]) / 2 + label_offset[0],
               (p1[1] + p2[1]) / 2 + label_offset[1])
        ax.text(mid[0], mid[1], label,
                ha="center", va="center",
                fontsize=7.5, color=label_color or FG_DIM,
                family="monospace",
                bbox=dict(facecolor=BG, edgecolor="none", pad=1),
                zorder=5)


# ═══════════════════════════════════════════════════════════════════════
# Diagram 1 — Arquitetura Macro
# ═══════════════════════════════════════════════════════════════════════
fig, ax = make_axes(figsize=(16, 10))

# 4 horizontal sections (top to bottom: field, edge, core, frontend)
section(ax, 2, 56, 96, 11, "● CAMADA FÍSICA (IoT + SATÉLITE)", EMERALD)
section(ax, 2, 41, 96, 12, "● AWS LAMBDA + BEDROCK (SERVERLESS)", AMBER)
section(ax, 2, 20, 96, 18, "● BACKEND FASTAPI (CORE)", CYAN)
section(ax, 2,  2, 96, 14, "● NEXT.JS DASHBOARD (FRONTEND)", MAGENTA)

# Camada Física
card(ax, 10, 58.5, 20, 6,
     "ESP32 + Sensor\nCapacitivo de Solo", EMERALD, fontsize=10)
card(ax, 38, 58.5, 22, 6,
     "Satélite Sentinel-2\n(Copernicus / GEE)", EMERALD, fontsize=10)
card(ax, 68, 58.5, 22, 6,
     "Modelo Federado\n(Pesos dos Nós)", EMERALD, fontsize=10)

# AWS Lambda
card(ax, 16, 44, 26, 6,
     "Lambda · Predict\nScikit-Learn LinReg",
     AMBER, fontsize=10)
card(ax, 58, 44, 26, 6,
     "Lambda · Briefing\nAWS Bedrock · Claude 3.5",
     AMBER, fontsize=10)

# Core Backend
card(ax, 6,  29, 16, 7, "REST API\n/api/*", CYAN, fontsize=9.5)
card(ax, 25, 29, 16, 7, "WebSocket Hub\n/ws/*", CYAN, fontsize=9.5)
card(ax, 44, 29, 16, 7, "YOLOv8\nInference",  CYAN, fontsize=9.5)
card(ax, 63, 29, 16, 7, "Scikit-Learn\nPredictor", CYAN, fontsize=9.5)
card(ax, 82, 29, 14, 7, "State Store\nDigital Twin", CYAN, fontsize=9.5)
card(ax, 35, 21,  30, 5.5, "SQLite — Blockchain Ledger\n(SQLModel · ACID · persistente)",
     CYAN, fontsize=9.5)

# Frontend
card(ax, 6,   5, 18, 8.5,
     "React + Three.js\nDigital Twin 3D\n(globo wireframe)",
     MAGENTA, fontsize=9.5)
card(ax, 28,  5, 18, 8.5,
     "Zustand Store\nReactive State", MAGENTA, fontsize=9.5)
card(ax, 50,  5, 22, 8.5,
     "4 Drawer Modules\nPredição · Blockchain\nMesh · Briefing", MAGENTA, fontsize=9.5)
card(ax, 76,  5, 20, 8.5,
     "Framer Motion\nSpotlight · HUD\nGlassmorphism", MAGENTA, fontsize=9.5)

# Arrows: field → core
arrow(ax, (20, 58.5), (14, 36.5), EMERALD, "PATCH /climate/state", label_offset=(-3, 2))
arrow(ax, (49, 58.5), (52, 36.5), EMERALD, "RGB tiles\n/ml/data/", label_offset=(5, 2))
arrow(ax, (79, 58.5), (88, 36.5), EMERALD, "weights", label_offset=(2.5, 2))

# Arrows: lambdas ↔ core
arrow(ax, (29, 44), (14, 36.5), AMBER, "fallback", dashed=True)
arrow(ax, (71, 44), (52, 36.5), AMBER, "Bedrock\nfallback", dashed=True)

# Arrows: core → frontend
arrow(ax, (33, 29), (37, 13.5), CYAN, "ws://yolo · ws://blockchain", label_offset=(0, 2))
arrow(ax, (14, 29), (15, 13.5), CYAN, "HTTPS REST", label_offset=(-3, 2))

# Legend (bottom right corner)
ax.text(83, 67, "NEXUS SENTINEL — ARQUITETURA MACRO",
        ha="left", va="top",
        fontsize=11, color=CYAN, family="monospace", fontweight="bold")
ax.text(83, 65.7, "v1.2 · GS 2026.1 · FIAP",
        ha="left", va="top",
        fontsize=8, color=FG_DIM, family="monospace")

plt.tight_layout()
plt.savefig("arq-macro.png", dpi=140, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print("✓ arq-macro.png")
plt.close()


# ═══════════════════════════════════════════════════════════════════════
# Diagram 2 — Fluxo Real-Time (sequence)
# ═══════════════════════════════════════════════════════════════════════
fig, ax = make_axes(figsize=(16, 11))
ax.set_ylim(0, 80)

actors = [
    ("ESP32",       12, EMERALD),
    ("FastAPI",     30, CYAN),
    ("State Store", 48, CYAN),
    ("SQLite",      63, CYAN),
    ("WS Hub",      78, CYAN),
    ("Next.js UI",  92, MAGENTA),
]
top_y = 72
bot_y = 6

# Actor heads
for name, x, color in actors:
    card(ax, x - 6, top_y, 12, 4, name, color, fontsize=10)
    # Lifeline
    ax.plot([x, x], [top_y, bot_y], color=BORDER, linewidth=0.8, linestyle=":", zorder=1)

def msg(ax, src, dst, y, label, color=CYAN, dashed=False):
    arrow(ax, (src, y), (dst, y), color=color, dashed=dashed)
    mid_x = (src + dst) / 2
    ax.text(mid_x, y + 0.7, label,
            ha="center", va="bottom",
            fontsize=8, color=FG,
            family="monospace",
            bbox=dict(facecolor=PANEL, edgecolor=BORDER, pad=2.5),
            zorder=5)

def note(ax, x, y, w, text, color=AMBER):
    box = FancyBboxPatch((x, y - 1.5), w, 3, boxstyle="round,pad=0.03",
                          linewidth=1, edgecolor=color, facecolor=PANEL, alpha=0.95)
    ax.add_patch(box)
    ax.text(x + w/2, y, text, ha="center", va="center",
            fontsize=8, color=color, family="monospace")

# Sequence
msg(ax, 12, 30, 65, "PATCH /climate/state {humidity:67.3}", EMERALD)
msg(ax, 30, 48, 60, "update humidity", CYAN)
note(ax, 40, 55, 18, "recompute resilience target", AMBER)
msg(ax, 30, 12, 50, "200 OK + snapshot", EMERALD, dashed=True)

note(ax, 22, 44, 60, "every 3.2s: YOLO broadcast loop", AMBER)
msg(ax, 30, 78, 39, "broadcast YOLO frame", CYAN)
msg(ax, 78, 92, 34, "ws://yolo {detections:[...]}", CYAN)
note(ax, 70, 29, 25, "UI re-renders YOLO feed", AMBER)

msg(ax, 92, 30, 23, "implicit blockchain TX", MAGENTA)
msg(ax, 30, 63, 18, "INSERT INTO transactions", CYAN)
msg(ax, 63, 30, 14, "TX persisted ✓", CYAN, dashed=True)
msg(ax, 30, 78, 11, "notify(new_tx)", CYAN)
msg(ax, 78, 92,  8, "ws://blockchain {type:transaction}", CYAN)

# Title
ax.text(50, 77, "FLUXO DE DADOS EM TEMPO REAL",
        ha="center", va="top",
        fontsize=12, color=CYAN, family="monospace", fontweight="bold")
ax.text(50, 75, "IoT → State → SQLite → WebSocket → UI",
        ha="center", va="top",
        fontsize=9, color=FG_DIM, family="monospace")

plt.tight_layout()
plt.savefig("arq-fluxo-realtime.png", dpi=140, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print("✓ arq-fluxo-realtime.png")
plt.close()


# ═══════════════════════════════════════════════════════════════════════
# Diagram 3 — Federated Learning
# ═══════════════════════════════════════════════════════════════════════
fig, ax = make_axes(figsize=(14, 10))
ax.set_ylim(0, 70)

# 3 client nodes around a central aggregator
positions = [
    ("Nó SP-BR\n(RISCO)",   18, 55, MAGENTA),
    ("Nó DEL-IN\n(RISCO)",   18, 35, MAGENTA),
    ("Nó CPT-ZA\n(WARNING)", 18, 15, AMBER),
]
data_cards = []
for label, x, y, color in positions:
    card(ax, x, y, 16, 7.5, label, color, fontsize=10)
    # Local data card next to it
    card(ax, x - 14, y, 12, 7.5,
         "Dados locais\nNUNCA SAEM", EMERALD, fontsize=8)
    # Arrow data→model (local training)
    arrow(ax, (x - 2, y + 3.75), (x, y + 3.75), EMERALD, dashed=True)

# Central aggregator
card(ax, 60, 33, 22, 12,
     "AGREGADOR FEDERADO\n\nNexus Core\n(servidor de pesos)",
     CYAN, fontsize=10)
card(ax, 85, 35, 11, 8, "Modelo\nGlobal", AMBER, fontsize=9)

# Gradient flows up
for label, x, y, color in positions:
    # Up arrow: gradients
    arrow(ax, (x + 16, y + 3.75), (60, 39), CYAN,
          label="gradientes\n(LGPD ✓)" if y == 35 else None,
          label_offset=(5, 0), label_color=CYAN)
    # Down arrow: updated weights
    arrow(ax, (60, 38), (x + 16, y + 5), AMBER,
          dashed=True,
          label="pesos\natualizados" if y == 35 else None,
          label_offset=(-7, 0), label_color=AMBER)

# Aggregator → Global model
arrow(ax, (82, 39), (85, 39), CYAN)

# Title + privacy callout
ax.text(50, 67, "APRENDIZADO FEDERADO — PRIVACIDADE POR CONSTRUÇÃO",
        ha="center", va="top",
        fontsize=12, color=CYAN, family="monospace", fontweight="bold")

ax.text(50, 4, "● Dados brutos nunca trafegam pela rede.   ● Apenas gradientes agregados são compartilhados.   ● Compliance: LGPD · GDPR · ISO 27001",
        ha="center", va="bottom",
        fontsize=9, color=EMERALD, family="monospace",
        bbox=dict(facecolor=PANEL, edgecolor=EMERALD, pad=8))

plt.tight_layout()
plt.savefig("arq-federated-learning.png", dpi=140, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print("✓ arq-federated-learning.png")
plt.close()
