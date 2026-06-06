'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { fetchWaterScarcityPrediction } from '@/lib/api';
import type { PredictionPoint } from '@/lib/types';

const easeExpo = [0.16, 1, 0.3, 1] as const;
const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';

// Fallback static prediction (matches what the Scikit-Learn endpoint returns)
const FALLBACK: PredictionPoint[] = [
  { month: 'JAN', noIntervention: 22, withNexus: 22 },
  { month: 'FEV', noIntervention: 31, withNexus: 24 },
  { month: 'MAR', noIntervention: 43, withNexus: 23 },
  { month: 'ABR', noIntervention: 58, withNexus: 21 },
  { month: 'MAI', noIntervention: 71, withNexus: 19 },
  { month: 'JUN', noIntervention: 84, withNexus: 16 }
];

export function SklearnChart() {
  const [points, setPoints] = useState<PredictionPoint[]>(FALLBACK);

  useEffect(() => {
    if (!USE_BACKEND) return;
    fetchWaterScarcityPrediction()
      .then((d) => setPoints(d.points))
      .catch(() => {
        /* keep fallback */
      });
  }, []);

  const W = 480, H = 180, P = 28;
  const yMax = 100;
  const xStep = (W - P * 2) / (points.length - 1);
  const ptsA = points.map((p, i) => [P + i * xStep, H - P - (p.noIntervention / yMax) * (H - P * 2)] as const);
  const ptsB = points.map((p, i) => [P + i * xStep, H - P - (p.withNexus / yMax) * (H - P * 2)] as const);
  const path = (pts: readonly (readonly [number, number])[]) =>
    pts.map((p, i) => (i ? `L ${p[0]} ${p[1]}` : `M ${p[0]} ${p[1]}`)).join(' ');
  const area = (pts: readonly (readonly [number, number])[]) =>
    path(pts) + ` L ${pts[pts.length - 1][0]} ${H - P} L ${pts[0][0]} ${H - P} Z`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
      <defs>
        <linearGradient id="dangerGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FF007A" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#FF007A" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#00F2FF" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#00F2FF" stopOpacity="0" />
        </linearGradient>
      </defs>

      {[0, 25, 50, 75, 100].map((v) => (
        <g key={v}>
          <line
            x1={P} x2={W - P}
            y1={H - P - (v / yMax) * (H - P * 2)}
            y2={H - P - (v / yMax) * (H - P * 2)}
            stroke="rgba(255,255,255,0.04)" strokeDasharray="2 4"
          />
          <text
            x={P - 6} y={H - P - (v / yMax) * (H - P * 2) + 3}
            textAnchor="end" fontSize="8" fill="#545863" fontFamily="JetBrains Mono"
          >{v}</text>
        </g>
      ))}
      {points.map((p, i) => (
        <text
          key={p.month}
          x={P + i * xStep} y={H - 8}
          textAnchor="middle" fontSize="8" fill="#8A8F98" fontFamily="JetBrains Mono"
        >{p.month}</text>
      ))}

      <motion.path d={area(ptsA)} fill="url(#dangerGrad)"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6, delay: 0.4 }} />
      <motion.path d={path(ptsA)} stroke="#FF007A" strokeWidth="1.5" fill="none" strokeLinecap="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ duration: 1.6, ease: easeExpo, delay: 0.2 }} />
      {ptsA.map((p, i) => (
        <motion.circle key={`a${i}`} cx={p[0]} cy={p[1]} r="2.5" fill="#FF007A"
          initial={{ scale: 0 }} animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.4 + i * 0.12, ease: easeExpo }} />
      ))}

      <motion.path d={area(ptsB)} fill="url(#safeGrad)"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6, delay: 0.9 }} />
      <motion.path d={path(ptsB)} stroke="#00F2FF" strokeWidth="1.5" fill="none" strokeLinecap="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ duration: 1.6, ease: easeExpo, delay: 0.7 }} />
      {ptsB.map((p, i) => (
        <motion.circle key={`b${i}`} cx={p[0]} cy={p[1]} r="2.5" fill="#00F2FF"
          initial={{ scale: 0 }} animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.9 + i * 0.12, ease: easeExpo }} />
      ))}

      <text x={W - P} y={H - P - (points[5].noIntervention / yMax) * (H - P * 2) - 8}
        textAnchor="end" fontSize="8" fill="#FF007A" fontFamily="JetBrains Mono">
        SEM INTERVENÇÃO · {points[5].noIntervention}%
      </text>
      <text x={W - P} y={H - P - (points[5].withNexus / yMax) * (H - P * 2) - 8}
        textAnchor="end" fontSize="8" fill="#00F2FF" fontFamily="JetBrains Mono">
        COM NEXUS · {points[5].withNexus}%
      </text>
    </svg>
  );
}
