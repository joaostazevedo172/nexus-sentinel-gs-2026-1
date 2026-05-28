'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useNexus } from '@/lib/store';

const easeExpo = [0.16, 1, 0.3, 1] as const;

const BASE_ALERTS = [
  { c: '#FF007A', t: 'SP-BR',  s: 'Calor Extremo' },
  { c: '#FF007A', t: 'DEL-IN', s: 'Inundação' },
  { c: '#FFB800', t: 'CPT-ZA', s: 'Seca' }
];
const HOT_ALERTS = [
  { c: '#FF007A', t: 'SYD-AU', s: 'Anomalia Crit.' },
  { c: '#FF007A', t: 'NYC-US', s: 'Tempestade' },
  { c: '#FFB800', t: 'MEX-MX', s: 'Onda Calor' }
];

export function ReactiveAlerts() {
  const temperature = useNexus((s) => s.temperature);
  const alerts =
    temperature > 1.5
      ? [...BASE_ALERTS, ...HOT_ALERTS.slice(0, Math.min(3, Math.floor(temperature)))]
      : BASE_ALERTS;

  return (
    <div className="space-y-1.5">
      <AnimatePresence initial={false}>
        {alerts.map((a) => (
          <motion.div
            key={a.t}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.35, ease: easeExpo }}
            className="flex items-center justify-between font-mono text-[10px]"
          >
            <div className="flex items-center gap-1.5">
              <span
                className="w-1 h-1 rounded-full"
                style={{ background: a.c, boxShadow: `0 0 6px ${a.c}` }}
              />
              <span className="text-neutral-300">{a.t}</span>
            </div>
            <span className="text-neutral-500">{a.s}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
