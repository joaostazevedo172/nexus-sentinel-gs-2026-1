import type {
  AlertRequest,
  AlertResponse,
  BlockchainStats,
  ClimateState,
  MeshNode,
  PredictionResponse,
  Transaction,
  YoloFrame
} from './types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    // Don't cache during demo
    cache: 'no-store'
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return res.json() as Promise<T>;
}

// ── Health ──
export const pingHealthCheck = () => http<{ status: string }>('/health');

// ── Climate ──
export const fetchClimateState = () => http<ClimateState>('/api/climate/state');
export const patchClimateState = (patch: Partial<ClimateState>) =>
  http<ClimateState>('/api/climate/state', { method: 'PATCH', body: JSON.stringify(patch) });

// ── YOLO ──
export const fetchYoloLatest = () => http<YoloFrame>('/api/yolo/latest');

// ── Prediction (scikit-learn) ──
export const fetchWaterScarcityPrediction = () =>
  http<PredictionResponse>('/api/predict/water-scarcity');

// ── Alerts ──
export const emitNgoAlert = (req: AlertRequest) =>
  http<AlertResponse>('/api/alerts/ngo', { method: 'POST', body: JSON.stringify(req) });

// ── Blockchain ──
export const fetchBlockchainTransactions = (limit = 20, offset = 0) =>
  http<Transaction[]>(`/api/blockchain/transactions?limit=${limit}&offset=${offset}`);
export const fetchBlockchainStats = () => http<BlockchainStats>('/api/blockchain/stats');

// ── Mesh ──
export const fetchMeshNodes = () => http<MeshNode[]>('/api/mesh/nodes');

// ── Federation ──
export const activateFederation = () =>
  http<{ activated: boolean; burstId: string }>('/api/federation/activate', { method: 'POST' });

// ── Cognitive Briefing (Bedrock) ──
export interface BriefingResponse {
  briefing: string;
  model: string;
  snapshot: ClimateState;
}

export const generateBriefing = () =>
  http<BriefingResponse>('/api/briefing/generate', { method: 'POST', body: JSON.stringify({}) });
