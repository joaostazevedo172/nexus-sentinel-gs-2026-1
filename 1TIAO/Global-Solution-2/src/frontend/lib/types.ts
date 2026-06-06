export type DetectionKind = 'good' | 'bad';

export interface YoloDetection {
  /** [x, y, w, h] as percentages of the frame (0..100) */
  box: [number, number, number, number];
  label: string;
  conf: number;
  kind: DetectionKind;
}

export interface YoloFrame {
  detections: YoloDetection[];
  capturedAt: string;
  sensorId: string;
}

export interface Transaction {
  hash: string;
  region: string;
  action: string;
  reward: number;
  time: string;
  fed?: boolean;
}

export interface BlockchainStats {
  totalTransactions: number;
  totalTokens: number;
  federatedBurstCount: number;
  blockHeight: number;
  contractAddress: string;
}

export interface PredictionPoint {
  month: string;
  noIntervention: number;
  withNexus: number;
}

export interface PredictionResponse {
  horizonMonths: number;
  points: PredictionPoint[];
  metrics: {
    r2: number;
    mae: number;
    estimatedDisplacement: { withoutIntervention: number; withNexus: number };
  };
}

export interface ClimateState {
  temperature: number;
  humidity: number;
  meshActivity: number;
  resilience: number;
}

export interface MeshNode {
  id: string;
  description: string;
  kind: 'normal' | 'warning' | 'risk';
  pingMs: number;
  weightSize: string;
  lat: number;
  lng: number;
}

export interface AlertRequest {
  regions: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  message?: string;
}

export interface AlertResponse {
  alertId: string;
  ngosNotified: number;
  deliveredAt: string;
}

export type ModuleId = 'prediction' | 'blockchain' | 'mesh' | 'briefing' | null;
