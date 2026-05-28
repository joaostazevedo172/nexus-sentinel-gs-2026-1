'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useMemo, useState } from 'react';
import { useNexus } from '@/lib/store';

const easeExpo = [0.16, 1, 0.3, 1] as const;

interface TopoNode {
  id: number;
  x: number;
  y: number;
  label: string;
  kind: 'normal' | 'warning' | 'risk';
}

interface Pulse {
  id: string;
  a: number;
  b: number;
}

const LABELS = ['SP', 'NYC', 'LDN', 'TYO', 'SYD', 'SGP', 'MSK', 'CPT', 'DEL', 'BSB', 'MEX', 'STO'];
const KINDS: TopoNode['kind'][] = [
  'risk',    'normal',  'normal', 'normal',
  'warning', 'normal',  'normal', 'warning',
  'risk',    'normal',  'normal', 'normal'
];

export function MeshTopology() {
  const meshActivity = useNexus((s) => s.meshActivity);

  const nodes: TopoNode[] = useMemo(() => {
    const n = 12;
    return Array.from({ length: n }, (_, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      return {
        id: i,
        x: 50 + Math.cos(a) * 36,
        y: 50 + Math.sin(a) * 36,
        label: LABELS[i],
        kind: KINDS[i]
      };
    });
  }, []);

  const [pulses, setPulses] = useState<Pulse[]>([]);

  useEffect(() => {
    const interval = Math.max(150, 600 - (meshActivity / 100) * 350);
    const id = setInterval(() => {
      const a = Math.floor(Math.random() * nodes.length);
      let b = Math.floor(Math.random() * nodes.length);
      while (b === a) b = Math.floor(Math.random() * nodes.length);
      const pulse: Pulse = { id: Math.random().toString(36).slice(2), a, b };
      setPulses((p) => [...p, pulse]);
      setTimeout(() => setPulses((p) => p.filter((x) => x.id !== pulse.id)), 1400);
    }, interval);
    return () => clearInterval(id);
  }, [nodes, meshActivity]);

  const colorOf = (kind: TopoNode['kind']) =>
    kind === 'risk' ? '#FF007A' : kind === 'warning' ? '#FFB800' : '#00F2FF';

  return (
    <svg viewBox="0 0 100 100" className="w-full h-auto">
      {[36, 24, 12].map((r, i) => (
        <circle key={r} cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.05)"
                strokeDasharray={i === 1 ? '0.5 1.5' : ''} />
      ))}
      {nodes.flatMap((n1, i) =>
        nodes.slice(i + 1).map((n2) => (
          <line key={`l-${n1.id}-${n2.id}`}
                x1={n1.x} y1={n1.y} x2={n2.x} y2={n2.y}
                stroke="rgba(0,242,255,0.06)" strokeWidth="0.15" />
        ))
      )}
      <AnimatePresence>
        {pulses.map((p) => {
          const a = nodes[p.a], b = nodes[p.b];
          return (
            <motion.line key={p.id}
              x1={a.x} y1={a.y} x2={b.x} y2={b.y}
              stroke="#00F2FF" strokeWidth="0.3"
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 0.9, 0] }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.4, ease: easeExpo }}
            />
          );
        })}
      </AnimatePresence>
      {nodes.map((n) => {
        const c = colorOf(n.kind);
        return (
          <g key={n.id}>
            <circle cx={n.x} cy={n.y} r="2.6" fill={c} fillOpacity="0.18" />
            <circle cx={n.x} cy={n.y} r="1.2" fill={c} />
            <text x={n.x} y={n.y - 4} textAnchor="middle" fontSize="2.2"
                  fill="#EDEDEF" fontFamily="JetBrains Mono">{n.label}</text>
          </g>
        );
      })}
      <circle cx="50" cy="50" r="3" fill="#00F2FF" fillOpacity="0.1"
              stroke="#00F2FF" strokeOpacity="0.5" strokeWidth="0.2" />
      <text x="50" y="51" textAnchor="middle" fontSize="2"
            fill="#00F2FF" fontFamily="Orbitron" fontWeight="700">NEXUS</text>
    </svg>
  );
}
