'use client';

import { motion } from 'framer-motion';

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1.8, duration: 1 }}
      className="mt-8 flex flex-wrap items-center justify-between gap-3 text-[10px] font-mono tracking-[0.18em] uppercase text-neutral-600"
    >
      <span>Nexus Sentinel © 2026 — Edge-Ready Architecture</span>
      <span className="flex items-center gap-3">
        <span className="flex items-center gap-1.5">
          <span className="w-1 h-1 rounded-full bg-emerald-500" />
          GDPR · LGPD · ISO/IEC 27001
        </span>
        <span>WCAG AA</span>
      </span>
    </motion.footer>
  );
}
