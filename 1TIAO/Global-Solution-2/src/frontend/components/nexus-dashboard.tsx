'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';
import { Activity, Cpu, Eye, Globe, Layers, Lock, Satellite, ShieldAlert } from 'lucide-react';

import { useNexus } from '@/lib/store';
import { nodeCount, riskZoneCount } from '@/lib/formulas';
import { AnimatedNumber } from './ui/animated-number';
import { Spotlight } from './ui/spotlight';
import { MetricCard } from './ui/metric-card';
import { Telemetry } from './viewport/telemetry';
import { ReactiveAlerts } from './viewport/reactive-alerts';
import { MicroBarChart } from './micro-charts/micro-bar-chart';
import { WireframeGlobe } from './wireframe-globe';
import { ScenarioControls } from './scenario-controls';

const easeExpo = [0.16, 1, 0.3, 1] as const;
const containerStagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.15 } }
};
const itemRise = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: easeExpo } }
};

export function NexusDashboard() {
  const cardRef = useRef<HTMLDivElement>(null);
  const state = useNexus();
  const risks = riskZoneCount(state.temperature);
  const nodes = nodeCount(state.meshActivity);
  const fedTxCount = state.transactions.filter((t) => t.fed).length;

  const resilienceAccent =
    state.resilience < 55 ? 'magenta' : state.resilience < 75 ? 'amber' : 'cyan';

  const resilienceBar =
    state.resilience < 55
      ? 'linear-gradient(90deg, #FF007A, #FFB800)'
      : state.resilience < 75
        ? 'linear-gradient(90deg, #FFB800, #00F2FF)'
        : 'linear-gradient(90deg, #00F2FF, #FFB800)';

  return (
    <motion.div
      ref={cardRef}
      variants={containerStagger}
      initial="hidden"
      animate="visible"
      className="nexus-card hud-brackets relative w-full overflow-hidden"
      style={{ minHeight: 660 }}
    >
      <span className="br-tl" />
      <span className="br-bl" />
      <Spotlight containerRef={cardRef} />
      <div className="absolute inset-0 nexus-grid opacity-40 pointer-events-none" />

      <div className="relative z-20 flex flex-col lg:flex-row min-h-[660px]">

        {/* ── LEFT PANEL ── */}
        <div className="flex-1 p-8 lg:p-12 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-white/[0.06]">
          <div>
            <motion.div variants={itemRise} className="flex items-center gap-2 mb-8">
              <Globe className="text-[#00F2FF] w-4 h-4 animate-pulse" strokeWidth={1.5} />
              <span className="font-mono text-[10px] tracking-[0.24em] uppercase text-[#00F2FF] glow-cyan">
                Rede Mesh Ativa · {Math.round(state.meshActivity)}%
              </span>
            </motion.div>

            <motion.h1
              variants={itemRise}
              className="font-display text-[2.4rem] lg:text-[2.9rem] leading-[1.05] font-bold tracking-tight"
            >
              <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-neutral-500">
                Gêmeo Digital de
              </span>
              <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00F2FF] via-white to-[#00F2FF]">
                Resiliência Climática
              </span>
            </motion.h1>

            <motion.p
              variants={itemRise}
              className="mt-6 font-mono text-[12px] leading-[1.7] text-neutral-400 max-w-md"
            >
              Monitoramento global via IoT e predição de anomalias climáticas. Aprendizado federado
              processando padrões locais para gerar inteligência planetária em tempo real.
            </motion.p>

            <motion.div variants={itemRise} className="mt-8 grid grid-cols-2 gap-3">
              <MetricCard
                icon={Activity} label="Nós Conectados" accent="amber"
                value={<AnimatedNumber value={nodes} />}
                onClick={() => state.openModule('mesh')}
              />
              <MetricCard
                icon={ShieldAlert} label="Zonas de Risco" accent="magenta"
                value={<AnimatedNumber value={risks} format={(v) => String(Math.round(v)).padStart(2, '0')} />}
              />
              <MetricCard
                icon={Cpu} label="Resiliência Global"
                accent={resilienceAccent}
                value={<AnimatedNumber value={state.resilience} format={(v) => String(Math.round(v))} />}
                suffix="%"
              >
                <div className="mt-2 h-1 bg-white/[0.04] rounded-full overflow-hidden">
                  <motion.div
                    className="h-full"
                    style={{ background: resilienceBar }}
                    animate={{ width: `${state.resilience}%` }}
                    transition={{ duration: 0.4, ease: easeExpo }}
                  />
                </div>
              </MetricCard>
              <MetricCard
                icon={Layers} label="Modelos Federados" accent="cyan"
                value={<AnimatedNumber value={1284 + fedTxCount * 3} />}
                onClick={() => state.openModule('blockchain')}
              />
            </motion.div>
          </div>

          <motion.div variants={itemRise} className="mt-8 pt-5 border-t border-white/[0.05]">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-500">
                Throughput Mesh · MB/s
              </span>
              <span className="font-mono text-[10px] text-[#00F2FF] tabular-nums">
                ↑ {(state.meshActivity * 6.18).toFixed(1)}
              </span>
            </div>
            <MicroBarChart />
          </motion.div>
        </div>

        {/* ── RIGHT PANEL: 3D VIEWPORT ── */}
        <motion.div
          variants={itemRise}
          className="flex-1 relative min-h-[520px] lg:min-h-full cursor-crosshair overflow-hidden"
        >
          <div className="absolute inset-4 z-10 pointer-events-none rounded-[28px] border border-[#00F2FF]/12" />
          <WireframeGlobe />
          <div className="scan-line" />

          {/* Top-left telemetry */}
          <motion.div
            initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.4, duration: 0.6, ease: easeExpo }}
            className="absolute top-7 left-7 z-20 p-3 bg-black/40 backdrop-blur-md border border-white/[0.06] rounded-lg min-w-[140px]"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <Satellite className="w-3 h-3 text-[#00F2FF]" strokeWidth={1.5} />
              <span className="font-mono text-[9px] tracking-[0.2em] uppercase text-neutral-500">
                Telemetria
              </span>
            </div>
            <Telemetry />
          </motion.div>

          {/* Top-right reactive alerts */}
          <motion.div
            initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.5, duration: 0.6, ease: easeExpo }}
            className="absolute top-7 right-7 z-20 p-3 bg-black/40 backdrop-blur-md border border-white/[0.06] rounded-lg max-w-[180px]"
          >
            <div className="flex items-center gap-1.5 mb-2">
              <Eye className="w-3 h-3 text-[#FFB800]" strokeWidth={1.5} />
              <span className="font-mono text-[9px] tracking-[0.2em] uppercase text-neutral-500">
                Alertas Ativos
              </span>
            </div>
            <ReactiveAlerts />
          </motion.div>

          {/* Bottom-left: scenario controls (sliders + federation) */}
          <ScenarioControls />

          {/* Bottom-right status pills */}
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6, duration: 0.6, ease: easeExpo }}
            className="absolute bottom-7 right-7 z-20 flex flex-col gap-2 items-end"
          >
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 border border-white/[0.06] backdrop-blur-md">
              <Lock className="w-3 h-3 text-emerald-400" strokeWidth={1.8} />
              <span className="font-mono text-[10px] text-neutral-300">Privacidade Preservada</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 border border-[#00F2FF]/20 backdrop-blur-md">
              <span className="relative w-1.5 h-1.5 rounded-full bg-[#00F2FF] pulse-ring text-[#00F2FF]" />
              <span className="font-mono text-[10px] text-[#00F2FF]">
                {state.federationActive ? 'Aprendizado Federado · Ativo' : 'Modelo Federado · Sincronizado'}
              </span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
}
