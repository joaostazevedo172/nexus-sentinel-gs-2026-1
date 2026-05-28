'use client';

import { create } from 'zustand';
import type { ModuleId, Transaction, YoloDetection } from './types';

interface NexusState {
  // Digital Twin inputs
  temperature: number;        // Δ°C, range -1 → +4
  humidity: number;           // % range 30 → 90
  meshActivity: number;       // % range 0 → 100
  // Derived/animated
  resilience: number;         // %
  // Federation
  federationActive: boolean;
  federationStartedAt: number;
  // UI
  openModuleId: ModuleId;
  // Server-derived data
  transactions: Transaction[];
  yoloDetections: YoloDetection[];
  alertsSent: number;
}

interface NexusActions {
  setTemperature: (v: number) => void;
  setHumidity: (v: number) => void;
  setMeshActivity: (v: number) => void;
  setResilience: (v: number) => void;
  activateFederation: () => void;
  deactivateFederation: () => void;
  openModule: (id: ModuleId) => void;
  closeModule: () => void;
  addTransaction: (tx: Transaction) => void;
  setYoloDetections: (d: YoloDetection[]) => void;
  incrementAlerts: () => void;
}

type NexusStore = NexusState & NexusActions;

export const useNexus = create<NexusStore>((set) => ({
  temperature: 0,
  humidity: 65,
  meshActivity: 78,
  resilience: 87,
  federationActive: false,
  federationStartedAt: 0,
  openModuleId: null,
  transactions: [],
  yoloDetections: [],
  alertsSent: 0,

  setTemperature: (v) => set({ temperature: v }),
  setHumidity: (v) => set({ humidity: v }),
  setMeshActivity: (v) => set({ meshActivity: v }),
  setResilience: (v) => set({ resilience: v }),
  activateFederation: () =>
    set({ federationActive: true, federationStartedAt: performance.now() }),
  deactivateFederation: () => set({ federationActive: false }),
  openModule: (id) => set({ openModuleId: id }),
  closeModule: () => set({ openModuleId: null }),
  addTransaction: (tx) =>
    set((s) => ({ transactions: [tx, ...s.transactions].slice(0, 80) })),
  setYoloDetections: (d) => set({ yoloDetections: d }),
  incrementAlerts: () => set((s) => ({ alertsSent: s.alertsSent + 1 }))
}));
