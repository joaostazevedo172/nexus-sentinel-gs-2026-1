import type { Transaction, YoloDetection } from './types';

const SCENARIOS: YoloDetection[][] = [
  [
    { box: [12, 22, 28, 24], label: 'Plantio de Cobertura', conf: 0.94, kind: 'good' },
    { box: [55, 18, 22, 30], label: 'Área Degradada', conf: 0.87, kind: 'bad' },
    { box: [42, 60, 30, 24], label: 'Solo Regenerado', conf: 0.91, kind: 'good' }
  ],
  [
    { box: [18, 14, 34, 28], label: 'Plantio de Cobertura', conf: 0.96, kind: 'good' },
    { box: [60, 50, 26, 22], label: 'Erosão Avançada', conf: 0.82, kind: 'bad' }
  ],
  [
    { box: [22, 28, 24, 20], label: 'Solo Regenerado', conf: 0.93, kind: 'good' },
    { box: [50, 18, 30, 26], label: 'Plantio de Cobertura', conf: 0.95, kind: 'good' },
    { box: [14, 62, 22, 22], label: 'Área Degradada', conf: 0.79, kind: 'bad' },
    { box: [62, 65, 26, 20], label: 'Solo Regenerado', conf: 0.88, kind: 'good' }
  ]
];

export function generateMockDetections(index: number): YoloDetection[] {
  return SCENARIOS[index % SCENARIOS.length];
}

const REGIONS = ['SP-BR', 'BSB-BR', 'DEL-IN', 'CPT-ZA', 'MEX-MX', 'NYC-US', 'SYD-AU', 'LDN-UK'];
const ACTIONS = [
  { txt: 'Regeneração 5ha', reward: 12 },
  { txt: 'Cobertura 3.2ha', reward: 8 },
  { txt: 'Reflorest. 8ha', reward: 21 },
  { txt: 'Recup. solo 2ha', reward: 6 }
];

function randomHex(n: number): string {
  return Array.from({ length: n }, () => Math.floor(Math.random() * 16).toString(16)).join('');
}

export function generateMockTransaction(opts?: { fed?: boolean }): Transaction {
  const a = ACTIONS[Math.floor(Math.random() * ACTIONS.length)];
  return {
    hash: '0x' + randomHex(8) + '…' + randomHex(4),
    region: REGIONS[Math.floor(Math.random() * REGIONS.length)],
    action: opts?.fed ? 'Burst Federado · 12ha' : a.txt,
    reward: opts?.fed ? 32 : a.reward,
    time: new Date().toLocaleTimeString('pt-BR', { hour12: false }),
    fed: opts?.fed
  };
}
