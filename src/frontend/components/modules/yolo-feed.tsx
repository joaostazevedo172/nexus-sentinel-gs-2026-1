'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useNexus } from '@/lib/store';
import type { YoloDetection } from '@/lib/types';

const easeExpo = [0.16, 1, 0.3, 1] as const;

export function YoloFeed() {
  const detections = useNexus((s) => s.yoloDetections);

  return (
    <div
      className="relative aspect-[16/10] rounded-lg overflow-hidden border border-white/[0.08]"
      style={{
        background: `
          radial-gradient(ellipse 40% 35% at 25% 30%, #3a5a2a, transparent 60%),
          radial-gradient(ellipse 30% 30% at 70% 25%, #5a3a1a, transparent 65%),
          radial-gradient(ellipse 35% 30% at 55% 70%, #2a4a3a, transparent 60%),
          radial-gradient(ellipse 30% 25% at 80% 75%, #6a4a2a, transparent 60%),
          linear-gradient(180deg, #1a1d12, #0e1108)
        `
      }}
    >
      <svg viewBox="0 0 100 62.5" className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
        <AnimatePresence>
          {detections.map((d, i) => <BoundingBox key={`${d.label}-${i}-${d.box.join('-')}`} d={d} />)}
        </AnimatePresence>
      </svg>

      {detections.map((d, i) => {
        const color = d.kind === 'good' ? '#00F2FF' : '#FF007A';
        return (
          <div
            key={`label-${i}-${d.box.join('-')}`}
            className="absolute font-mono text-[9px] px-1.5 py-0.5 rounded"
            style={{
              left: `${d.box[0]}%`,
              top: `${d.box[1]}%`,
              transform: 'translateY(-100%)',
              background: `${color}26`,
              color,
              border: `1px solid ${color}66`,
              whiteSpace: 'nowrap'
            }}
          >
            {d.label} · {(d.conf * 100).toFixed(0)}%
          </div>
        );
      })}

      <div className="absolute top-2 left-2 font-mono text-[9px] tracking-[0.18em] uppercase text-[#00F2FF] flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-[#FF007A] animate-pulse" />
        REC · YOLO v8.2 · SENT-3B
      </div>
      <div className="absolute top-2 right-2 font-mono text-[9px] tracking-widest text-neutral-300">
        512×320 · 24fps
      </div>
      <div className="absolute bottom-2 left-2 font-mono text-[9px] text-neutral-400">
        -23.5505°, -46.6333°
      </div>
      <div className="scan-line" style={{ animationDuration: '4s' }} />
    </div>
  );
}

function BoundingBox({ d }: { d: YoloDetection }) {
  const color = d.kind === 'good' ? '#00F2FF' : '#FF007A';
  const [x, y, w, h] = d.box;
  return (
    <motion.g
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35, ease: easeExpo }}
    >
      <path d="M0 3 L0 0 L3 0" transform={`translate(${x} ${y})`}        stroke={color} strokeWidth="0.4" fill="none" />
      <path d="M-3 0 L0 0 L0 3" transform={`translate(${x + w} ${y})`}    stroke={color} strokeWidth="0.4" fill="none" />
      <path d="M0 -3 L0 0 L3 0" transform={`translate(${x} ${y + h})`}    stroke={color} strokeWidth="0.4" fill="none" />
      <path d="M-3 0 L0 0 L0 -3" transform={`translate(${x + w} ${y + h})`} stroke={color} strokeWidth="0.4" fill="none" />
      <rect x={x} y={y} width={w} height={h}
        fill={color} fillOpacity="0.06" stroke={color} strokeOpacity="0.5" strokeWidth="0.25" />
    </motion.g>
  );
}
