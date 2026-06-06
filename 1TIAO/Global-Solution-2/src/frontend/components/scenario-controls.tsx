'use client';

import { AnimatePresence, motion } from 'framer-motion';
import {
  Brain, CheckCircle2, Droplets, RotateCw, Share2, Sparkles, Thermometer
} from 'lucide-react';
import { useNexus } from '@/lib/store';
import { activateFederation as apiActivate, patchClimateState } from '@/lib/api';

const easeExpo = [0.16, 1, 0.3, 1] as const;
const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';

/**
 * Floating control panel attached to the 3D viewport.
 * Sliders mutate climate state; the globe and KPIs react in real time.
 * Federation button appears when resilience drops below 65%.
 */
export function ScenarioControls() {
  const {
    temperature, humidity, meshActivity, resilience, federationActive,
    setTemperature, setHumidity, setMeshActivity, activateFederation
  } = useNexus();

  const crisis = resilience < 65 && !federationActive;
  const tempColor = temperature > 2 ? 'is-critical' : temperature > 1 ? 'is-warning' : '';
  const humColor = humidity < 45 ? 'is-warning' : '';

  // Push slider changes to the backend (best-effort; ignored on failure)
  const pushClimate = (patch: Partial<{ temperature: number; humidity: number; meshActivity: number }>) => {
    if (!USE_BACKEND) return;
    patchClimateState(patch).catch(() => {});
  };

  const onActivate = async () => {
    activateFederation();
    if (USE_BACKEND) {
      apiActivate().catch(() => {});
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2, duration: 0.7, ease: easeExpo }}
      className="absolute bottom-7 left-7 z-20 w-[280px] nexus-glass rounded-xl p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-[#00F2FF]" strokeWidth={1.5} />
          <span className="font-mono text-[9px] tracking-[0.2em] uppercase text-neutral-400">
            Simulação de Cenários
          </span>
        </div>
        <span className="font-mono text-[9px] text-neutral-600">DIGITAL TWIN</span>
      </div>

      {/* Temperature */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-neutral-300">
            <Thermometer className="w-3 h-3" strokeWidth={1.5} />
            Temperatura Global
          </span>
          <span
            className={`font-mono text-[11px] tabular-nums font-bold ${
              temperature > 2 ? 'text-[#FF007A]' : temperature > 1 ? 'text-[#FFB800]' : 'text-[#00F2FF]'
            }`}
          >
            {temperature >= 0 ? '+' : ''}{temperature.toFixed(1)}°C
          </span>
        </div>
        <input
          type="range" min={-1} max={4} step={0.1}
          className={`nexus-slider ${tempColor}`}
          value={temperature}
          onChange={(e) => { const v = +e.target.value; setTemperature(v); pushClimate({ temperature: v }); }}
        />
      </div>

      {/* Humidity */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-neutral-300">
            <Droplets className="w-3 h-3" strokeWidth={1.5} />
            Umidade do Solo
          </span>
          <span className={`font-mono text-[11px] tabular-nums font-bold ${
            humidity < 45 ? 'text-[#FFB800]' : 'text-[#00F2FF]'
          }`}>{Math.round(humidity)}%</span>
        </div>
        <input
          type="range" min={30} max={90} step={1}
          className={`nexus-slider ${humColor}`}
          value={humidity}
          onChange={(e) => { const v = +e.target.value; setHumidity(v); pushClimate({ humidity: v }); }}
        />
      </div>

      {/* Mesh activity */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-neutral-300">
            <Share2 className="w-3 h-3" strokeWidth={1.5} />
            Atividade da Rede Mesh
          </span>
          <span className="font-mono text-[11px] tabular-nums font-bold text-[#00F2FF]">
            {Math.round(meshActivity)}%
          </span>
        </div>
        <input
          type="range" min={0} max={100} step={1}
          className="nexus-slider"
          value={meshActivity}
          onChange={(e) => { const v = +e.target.value; setMeshActivity(v); pushClimate({ meshActivity: v }); }}
        />
      </div>

      <AnimatePresence mode="wait">
        {federationActive ? (
          <motion.div
            key="active"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4, ease: easeExpo }}
            className="mt-3 px-3 py-2 rounded-lg border border-[#00F2FF]/40 bg-[#00F2FF]/[0.06] flex items-center gap-2"
          >
            <RotateCw className="w-3.5 h-3.5 text-[#00F2FF] animate-spin" strokeWidth={1.5} />
            <span className="font-mono text-[10px] text-[#00F2FF]">Distribuindo pesos federados…</span>
          </motion.div>
        ) : crisis ? (
          <motion.button
            key="trigger"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            transition={{ duration: 0.4, ease: easeExpo }}
            onClick={onActivate}
            className="mt-3 w-full px-3 py-2.5 rounded-lg bg-[#00F2FF] text-black flex items-center justify-center gap-2 font-display font-bold text-[11px] tracking-[0.15em] uppercase hover:bg-[#33F5FF] transition-colors"
            style={{ boxShadow: '0 0 24px rgba(0,242,255,0.4)' }}
          >
            <Brain className="w-3.5 h-3.5" strokeWidth={2} />
            Ativar Aprendizado Federado
          </motion.button>
        ) : (
          <motion.div
            key="stable"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-3 px-3 py-2 rounded-lg border border-white/[0.06] bg-black/30 flex items-center gap-2"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" strokeWidth={1.5} />
            <span className="font-mono text-[10px] text-neutral-400">
              Sistema estável · sem intervenção
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
