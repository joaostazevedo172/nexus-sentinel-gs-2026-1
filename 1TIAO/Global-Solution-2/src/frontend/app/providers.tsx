'use client';

import { useEffect, useRef, useState } from 'react';
import { useNexus } from '@/lib/store';
import { targetResilience } from '@/lib/formulas';
import { pingHealthCheck } from '@/lib/api';
import { useWSChannel } from '@/lib/websocket';
import { generateMockDetections, generateMockTransaction } from '@/lib/mock-data';
import type { Transaction, YoloFrame } from '@/lib/types';

const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';

type BlockchainMsg =
  | { type: 'snapshot'; transactions: Transaction[] }
  | { type: 'transaction'; transaction: Transaction };

/**
 * Orchestrates all background loops:
 * - Resilience smoothing (requestAnimationFrame)
 * - YOLO frames via WebSocket /ws/yolo (fallback: client-side rotation)
 * - Blockchain transactions via WebSocket /ws/blockchain (fallback: auto-gen)
 * - Climate state via WebSocket /ws/climate (ESP32 connection)
 * - Federation burst transaction storm (local trigger always)
 *
 * Strategy: if NEXT_PUBLIC_USE_BACKEND=true, try WS. If WS errors out
 * on first attempt, fall back to client-side simulation.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // ── Resilience smoothing loop ──
  useEffect(() => {
    let id: number;
    const tick = () => {
      const s = useNexus.getState();
      const now = performance.now();
      let fedBurst = 0;
      if (s.federationActive) {
        const dt = (now - s.federationStartedAt) / 1000;
        if (dt < 4) fedBurst = 30 * (1 - dt / 4);
        else if (dt > 6) s.deactivateFederation();
        else fedBurst = 0;
      }
      const tgt = targetResilience(s.temperature, s.humidity, s.meshActivity, fedBurst);
      const next = s.resilience + (tgt - s.resilience) * 0.06;
      if (Math.abs(tgt - s.resilience) > 0.05) s.setResilience(next);
      id = requestAnimationFrame(tick);
    };
    id = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(id);
  }, []);

  // ── Track whether WS is working; if it errors, switch to simulation ──
  const [yoloWsFailed, setYoloWsFailed] = useState(false);
  const [blockchainWsFailed, setBlockchainWsFailed] = useState(false);
  const [climateWsFailed, setClimateWsFailed] = useState(false); // 👈 ADICIONADO: Estado do clima

  // ── Climate via WebSocket (ESP32) ──
  // 👈 ADICIONADO: O "ouvinte" que conecta o backend ao slider
  useWSChannel<any>('/ws/climate', {
    reconnectMs: 5000,
    onMessage: (data) => {
      console.log("[Climate WS] Recebido:", data); 
      if (data.type === 'climate_update' && data.state) {
        useNexus.getState().setHumidity(data.state.humidity);
      }
    },
    onError: () => setClimateWsFailed(true)
  });

  // ── YOLO via WebSocket ──
  useWSChannel<YoloFrame>('/ws/yolo', {
    reconnectMs: 5000,
    onMessage: (frame) => useNexus.getState().setYoloDetections(frame.detections),
    onError: () => setYoloWsFailed(true)
  });

  // ── YOLO fallback: client-side simulation ──
  const lastTxYolo = useRef(0);
  useEffect(() => {
    if (USE_BACKEND && !yoloWsFailed) return; // WS is doing the work
    useNexus.getState().setYoloDetections(generateMockDetections(0));
    let i = 0;
    const id = setInterval(() => {
      i = (i + 1) % 3;
      useNexus.getState().setYoloDetections(generateMockDetections(i));
    }, 3200);
    return () => clearInterval(id);
  }, [yoloWsFailed]);

  // ── Blockchain via WebSocket ──
  useWSChannel<BlockchainMsg>('/ws/blockchain', {
    reconnectMs: 5000,
    onMessage: (msg) => {
      if (msg.type === 'snapshot') {
        // Replace current ledger with server snapshot
        const store = useNexus.getState();
        msg.transactions.slice().reverse().forEach((tx) => store.addTransaction(tx));
      } else if (msg.type === 'transaction') {
        useNexus.getState().addTransaction(msg.transaction);
      }
    },
    onError: () => setBlockchainWsFailed(true)
  });

  // ── Blockchain fallback: auto-generate TX from YOLO good detections ──
  useEffect(() => {
    if (USE_BACKEND && !blockchainWsFailed) return; // backend WS handles this
    let cancelled = false;
    const unsub = useNexus.subscribe(async (state, prev) => {
      if (state.yoloDetections === prev.yoloDetections) return;
      const goodCount = state.yoloDetections.filter((d) => d.kind === 'good').length;
      if (goodCount === 0) return;
      const delay = 1800 + Math.random() * 1500;
      setTimeout(() => {
        if (cancelled) return;
        useNexus.getState().addTransaction(generateMockTransaction());
      }, delay);
    });
    return () => { cancelled = true; unsub(); };
  }, [blockchainWsFailed]);

  // ── Federation burst (local visual reinforcement) ──
  // Always runs locally so the UI animation is snappy, regardless of backend.
  // In backend mode, the server ALSO emits 6 burst TX via /api/federation/activate,
  // which arrive via WS — local + server TX appear interleaved.
  useEffect(() => {
    if (USE_BACKEND && !blockchainWsFailed) return; // server emits burst TX
    const unsub = useNexus.subscribe((state, prev) => {
      if (state.federationActive && !prev.federationActive) {
        for (let i = 0; i < 6; i++) {
          setTimeout(() => {
            useNexus.getState().addTransaction(generateMockTransaction({ fed: true }));
          }, 200 + i * 350);
        }
      }
    });
    return () => unsub();
  }, [blockchainWsFailed]);

  // ── Health probe ──
  useEffect(() => {
    if (!USE_BACKEND) return;
    pingHealthCheck().catch(() =>
      console.warn('[Nexus] Backend unreachable, simulation will take over.')
    );
  }, []);

  return <>{children}</>;
}