'use client';

import { motion } from 'framer-motion';
import { Brain, ChevronRight, Cpu, Layers, Wifi, LucideIcon } from 'lucide-react';
import { useNexus } from '@/lib/store';
import type { ModuleId } from '@/lib/types';

const easeExpo = [0.16, 1, 0.3, 1] as const;
const containerStagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.15 } }
};
const itemRise = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: easeExpo } }
};

interface DockItem {
  id: NonNullable<ModuleId>;
  icon: LucideIcon;
  title: string;
  sub: string;
  color: string;
}

export function BottomDock() {
  const openModule = useNexus((s) => s.openModule);
  const txCount = useNexus((s) => s.transactions.length);

  const items: DockItem[] = [
    { id: 'prediction', icon: Cpu,    title: 'Predição IA',       sub: 'Scikit · YOLO',                color: '#00F2FF' },
    { id: 'blockchain', icon: Layers, title: 'Blockchain Ledger', sub: `${txCount} TX · Nexus Token`,  color: '#FFB800' },
    { id: 'mesh',       icon: Wifi,   title: 'Rede Mesh',         sub: 'Aprendizado Federado',         color: '#FF007A' },
    { id: 'briefing',   icon: Brain,  title: 'Briefing IA',       sub: 'AWS Bedrock · Claude',         color: '#10B981' }
  ];

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerStagger}
      className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-3"
    >
      {items.map((it) => (
        <motion.button
          key={it.id}
          variants={itemRise}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.3, ease: easeExpo }}
          onClick={() => openModule(it.id)}
          className="group nexus-card p-4 flex items-center justify-between text-left"
          style={{ borderColor: 'rgba(255,255,255,0.06)' }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center border"
              style={{ borderColor: `${it.color}33`, background: `${it.color}0d` }}
            >
              <it.icon className="w-4 h-4" style={{ color: it.color }} strokeWidth={1.5} />
            </div>
            <div>
              <div className="font-display text-[13px] font-bold tracking-wider text-white">{it.title}</div>
              <div className="font-mono text-[10px] tracking-[0.16em] uppercase text-neutral-500">{it.sub}</div>
            </div>
          </div>
          <ChevronRight
            className="w-4 h-4 text-neutral-600 group-hover:text-neutral-300 group-hover:translate-x-0.5 transition-all"
            strokeWidth={1.5}
          />
        </motion.button>
      ))}
    </motion.div>
  );
}
