# Nexus Sentinel — Frontend

Next.js 15 (App Router) + TypeScript + Tailwind + Framer Motion + Three.js + Zustand.

## Setup

```bash
npm install
cp .env.example .env.local      # ajuste a URL do backend se necessário
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000).

## Estrutura

```
app/
├── layout.tsx              # Root layout (fonts via next/font/google)
├── page.tsx                # Composição principal do dashboard
├── providers.tsx           # Loops de simulação (resilience, YOLO, blockchain)
└── globals.css             # Design tokens + classes utilitárias custom

lib/
├── types.ts                # Tipos compartilhados
├── store.ts                # Zustand store (estado global)
├── formulas.ts             # riskZoneCount, nodeCount, targetResilience
├── api.ts                  # Cliente HTTP tipado para a API FastAPI
└── mock-data.ts            # Gerador de dados offline (fallback)

components/
├── nexus-dashboard.tsx     # Composer principal
├── top-bar.tsx
├── bottom-dock.tsx
├── scenario-controls.tsx   # Sliders + Aprendizado Federado
├── wireframe-globe.tsx     # Globo Three.js reativo
├── ui/                     # Atoms (DrawerShell, Spotlight, MetricCard, …)
├── viewport/               # Telemetry, Alerts, Atmospherics
├── micro-charts/           # MicroBarChart, SklearnChart
└── modules/                # Drawers: Predição, Blockchain, Mesh
```

## Modo Backend vs Simulação

- `NEXT_PUBLIC_USE_BACKEND=false` (padrão) → tudo é simulado client-side.
- `NEXT_PUBLIC_USE_BACKEND=true` → consome a API em `NEXT_PUBLIC_API_URL`.

Em modo backend, se qualquer chamada falhar, o frontend **automaticamente cai para simulação** —
graceful degradation sem tela quebrada.

## Padrões importantes

- Todo componente que usa hooks tem `'use client'`.
- Three.js lê estado via `useNexus.getState()` no loop de animação,
  evitando re-renders do React em 60 FPS.
- Sliders empurram mudanças de estado para o backend em background;
  o store local é sempre a fonte autoritária para a UI.
- Easing global: `cubic-bezier(0.16, 1, 0.3, 1)` (expo.out).
- Spring: `damping: 20, stiffness: 90`.

## Migração para shadcn/ui

Os componentes em `components/ui/` já seguem a convenção shadcn. Para adicionar
oficialmente o `shadcn/ui`:

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add card button
```

O `Card` e o `Button` do shadcn substituem os wrappers atuais sem mudanças
no consumo (a API é a mesma).
