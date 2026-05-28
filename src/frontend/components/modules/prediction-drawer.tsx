'use client';

import { motion } from 'framer-motion';
import {
  BellRing, Camera, CheckCircle2, Cpu, RotateCw, TrendingUp
} from 'lucide-react';
import { useState } from 'react';
import { useNexus } from '@/lib/store';
import { emitNgoAlert } from '@/lib/api';
import { DrawerShell } from '@/components/ui/drawer-shell';
import { YoloFeed } from './yolo-feed';
import { SklearnChart } from '@/components/micro-charts/sklearn-chart';

const easeExpo = [0.16, 1, 0.3, 1] as const;
const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';

export function PredictionDrawer() {
  const open = useNexus((s) => s.openModuleId === 'prediction');
  const closeModule = useNexus((s) => s.closeModule);
  const detections = useNexus((s) => s.yoloDetections);
  const transactions = useNexus((s) => s.transactions);
  const alertsSent = useNexus((s) => s.alertsSent);
  const incrementAlerts = useNexus((s) => s.incrementAlerts);

  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const sendAlert = async () => {
    setSending(true);
    try {
      if (USE_BACKEND) {
        await emitNgoAlert({ regions: ['SP-BR', 'DEL-IN', 'CPT-ZA'], severity: 'high' });
      } else {
        await new Promise((r) => setTimeout(r, 1400)); // simulated latency
      }
      incrementAlerts();
      setSent(true);
      setTimeout(() => setSent(false), 2400);
    } catch (e) {
      console.error('[emitNgoAlert] failed:', e);
    } finally {
      setSending(false);
    }
  };

  const avgConf = detections.length
    ? Math.round(detections.reduce((a, d) => a + d.conf, 0) / detections.length * 100)
    : 0;
  const goodCount = detections.filter((d) => d.kind === 'good').length;
  const badCount = detections.filter((d) => d.kind === 'bad').length;
  const tokensGenerated = transactions.filter((t) => !t.fed).slice(0, 20).reduce((a, t) => a + t.reward, 0);

  return (
    <DrawerShell
      open={open}
      onClose={closeModule}
      title="Predição IA"
      subtitle="Scikit-Learn · YOLO v8.2"
      icon={Cpu}
      accent="#00F2FF"
    >
      <section className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5">
            <Camera className="w-3 h-3 text-[#00F2FF]" strokeWidth={1.5} />
            <h3 className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-300">
              Visão Computacional · Sensor Solo
            </h3>
          </div>
          <span className="font-mono text-[9px] text-neutral-500">
            {detections.length} OBJETOS · CONF MÉD {avgConf}%
          </span>
        </div>
        <YoloFeed />
        <div className="mt-3 grid grid-cols-3 gap-2">
          {[
            { label: 'Regeneração',    value: goodCount,        color: '#00F2FF' },
            { label: 'Degradação',     value: badCount,         color: '#FF007A' },
            { label: 'Tokens Gerados', value: tokensGenerated,  color: '#FFB800' }
          ].map((s) => (
            <div key={s.label} className="bg-black/30 border border-white/[0.05] rounded-md px-3 py-2">
              <div className="font-mono text-[9px] tracking-widest uppercase text-neutral-500">{s.label}</div>
              <div className="font-display text-lg font-bold tabular-nums" style={{ color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5">
            <TrendingUp className="w-3 h-3 text-[#00F2FF]" strokeWidth={1.5} />
            <h3 className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-300">
              Predição de Escassez Hídrica · 6M
            </h3>
          </div>
          <span className="font-mono text-[9px] text-neutral-500">R² 0.918 · MAE 2.1%</span>
        </div>
        <div className="bg-black/30 border border-white/[0.05] rounded-lg p-3">
          <SklearnChart />
        </div>
        <div className="mt-2 font-mono text-[10px] text-neutral-500 leading-relaxed">
          <span className="text-[#FFB800]">⚠</span> Sem intervenção, risco de deslocamento humano em{' '}
          <span className="text-[#FF007A]">3.2M habitantes</span> (regiões SP, DEL, CPT) até{' '}
          <span className="text-white">Jun/26</span>. Modelo Nexus reduz exposição para{' '}
          <span className="text-[#00F2FF]">0.4M</span> via alocação preditiva.
        </div>
      </section>

      <section>
        <motion.button
          onClick={sendAlert}
          disabled={sending || sent}
          whileHover={!sending && !sent ? { scale: 1.01 } : {}}
          whileTap={!sending && !sent ? { scale: 0.98 } : {}}
          transition={{ duration: 0.3, ease: easeExpo }}
          className="w-full px-4 py-3 rounded-lg border border-[#FFB800]/40 bg-[#FFB800]/[0.06] text-[#FFB800] flex items-center justify-center gap-2 font-display font-bold text-[12px] tracking-[0.15em] uppercase hover:bg-[#FFB800]/[0.12] disabled:opacity-60"
        >
          {sending ? (
            <>
              <RotateCw className="w-3.5 h-3.5 animate-spin" strokeWidth={2} />
              Transmitindo para ONGs parceiras…
            </>
          ) : sent ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" strokeWidth={2} />
              Alerta enviado · 42 ONGs notificadas
            </>
          ) : (
            <>
              <BellRing className="w-3.5 h-3.5" strokeWidth={2} />
              Emitir Alerta Preventivo para ONGs
            </>
          )}
        </motion.button>
        <div className="mt-2 flex items-center justify-between font-mono text-[9px] text-neutral-500">
          <span>Alertas emitidos nesta sessão</span>
          <span className="text-[#FFB800] tabular-nums">{alertsSent}</span>
        </div>
      </section>
    </DrawerShell>
  );
}
