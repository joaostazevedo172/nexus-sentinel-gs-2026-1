'use client';

import { motion } from 'framer-motion';
import { Radio } from 'lucide-react';
import { LiveClock } from './ui/live-clock';
import { StatusPill } from './ui/status-pill';
import { useNexus } from '@/lib/store';
import { riskZoneCount } from '@/lib/formulas';

const easeExpo = [0.16, 1, 0.3, 1] as const;

export function TopBar() {
  const temperature = useNexus((s) => s.temperature);
  const federationActive = useNexus((s) => s.federationActive);
  const risks = riskZoneCount(temperature);
  const warnings = Math.max(0, Math.floor(risks * 1.3) + Math.floor(temperature * 2));

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: easeExpo }}
      className="flex flex-wrap items-center justify-between gap-4 mb-6"
    >
      <div className="flex items-center gap-3">
        <div className="relative w-9 h-9 rounded-lg border border-[#00F2FF]/30 bg-[#00F2FF]/5 flex items-center justify-center">
          <div className="absolute inset-0 rounded-lg shadow-[0_0_20px_rgba(0,242,255,0.25)]" />
          <Radio className="w-4 h-4 text-[#00F2FF]" strokeWidth={1.5} />
        </div>
        <div>
          <div className="font-display text-sm font-bold tracking-[0.15em]">NEXUS SENTINEL</div>
          <div className="font-mono text-[10px] tracking-[0.18em] uppercase text-neutral-500">
            Global Climate Intelligence
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3 flex-wrap">
        <LiveClock />
        <span className="h-3 w-px bg-white/10" />
        <StatusPill color="cyan"    label="OPS"       value={federationActive ? 'SYNC' : 'NOMINAL'} />
        <StatusPill color="amber"   label="Anomalias" value={String(warnings)} />
        <StatusPill color="magenta" label="Críticas"  value={String(risks).padStart(2, '0')} />
      </div>
    </motion.header>
  );
}
