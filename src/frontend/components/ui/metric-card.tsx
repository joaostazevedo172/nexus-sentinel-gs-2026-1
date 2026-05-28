'use client';

import { motion } from 'framer-motion';
import { ArrowUpRight, LucideIcon } from 'lucide-react';
import { ReactNode } from 'react';

const easeExpo = [0.16, 1, 0.3, 1] as const;

type Accent = 'cyan' | 'amber' | 'magenta';

interface Props {
  icon: LucideIcon;
  label: string;
  value: ReactNode;
  suffix?: string;
  accent?: Accent;
  children?: ReactNode;
  onClick?: () => void;
}

const accentMap: Record<Accent, { stripe: string; text: string; border: string }> = {
  cyan:    { stripe: '#00F2FF', text: 'text-[#00F2FF]', border: 'border-white/[0.06]' },
  amber:   { stripe: '#FFB800', text: 'text-[#FFB800]', border: 'border-white/[0.06]' },
  magenta: { stripe: '#FF007A', text: 'text-[#FF007A]', border: 'border-[#FF007A]/30' }
};

const itemRise = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: easeExpo } }
};

export function MetricCard({ icon: Icon, label, value, suffix, accent = 'cyan', children, onClick }: Props) {
  const a = accentMap[accent];
  return (
    <motion.div
      variants={itemRise}
      whileHover={{ y: -2 }}
      onClick={onClick}
      transition={{ duration: 0.35, ease: easeExpo }}
      className={`relative bg-black/40 ${a.border} border p-4 rounded-xl overflow-hidden group ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div
        className="absolute top-0 left-0 w-[2px] h-full"
        style={{ background: a.stripe, opacity: accent === 'magenta' ? 1 : 0.4 }}
      />
      <div className="flex items-center justify-between mb-3">
        <Icon className={`w-4 h-4 ${a.text}`} strokeWidth={1.5} />
        <ArrowUpRight
          className="w-3.5 h-3.5 text-neutral-600 group-hover:text-neutral-300 transition-colors"
          strokeWidth={1.5}
        />
      </div>
      <div className="font-mono text-[10px] tracking-[0.18em] uppercase text-neutral-500 mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="font-display text-2xl font-bold text-white ticker-flicker">{value}</span>
        {suffix && <span className="font-mono text-xs text-neutral-500">{suffix}</span>}
      </div>
      {children}
    </motion.div>
  );
}
