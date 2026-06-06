'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useNexus } from '@/lib/store';

const easeExpo = [0.16, 1, 0.3, 1] as const;

/** Live mesh-throughput strip whose bar heights respond to meshActivity. */
export function MicroBarChart() {
  const meshActivity = useNexus((s) => s.meshActivity);
  const [bars, setBars] = useState<number[]>(() => Array(32).fill(0.3));

  // Randomize initial pattern after mount to avoid SSR/CSR mismatch
  useEffect(() => {
    setBars(Array.from({ length: 32 }, () => 0.2 + Math.random() * 0.8));
    const id = setInterval(() => {
      setBars((b) => {
        const next = b.slice(1);
        const m = meshActivity / 100;
        next.push(0.15 + m * 0.45 + Math.random() * 0.4);
        return next;
      });
    }, 240);
    return () => clearInterval(id);
  }, [meshActivity]);

  return (
    <div className="flex items-end gap-[2px] h-10">
      {bars.map((v, i) => (
        <motion.div
          key={i}
          className="micro-bar w-1 rounded-sm"
          animate={{ height: `${v * 100}%` }}
          transition={{ duration: 0.25, ease: easeExpo }}
          style={{ opacity: 0.4 + v * 0.6 }}
        />
      ))}
    </div>
  );
}
