'use client';

import { useEffect, useRef } from 'react';

const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

type Status = 'connecting' | 'open' | 'closed' | 'disabled';

interface WSOptions<T> {
  /** Called with every parsed message. */
  onMessage: (data: T) => void;
  /** Called on connection failure — frontend can switch to fallback. */
  onError?: () => void;
  /** Called on successful connection. */
  onOpen?: () => void;
  /** Auto-reconnect delay in ms. 0 to disable. */
  reconnectMs?: number;
}

/**
 * Subscribe to a WebSocket channel on the FastAPI backend.
 * Silently noops if `NEXT_PUBLIC_USE_BACKEND !== 'true'`.
 * Auto-reconnects on disconnect; calls `onError` on first failure so
 * the caller can decide to fall back to simulation.
 */
export function useWSChannel<T>(path: string, opts: WSOptions<T>): { status: Status } {
  const statusRef = useRef<Status>(USE_BACKEND ? 'connecting' : 'disabled');
  const optsRef = useRef(opts);
  optsRef.current = opts;

  useEffect(() => {
    if (!USE_BACKEND) return;

    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;
    const wsUrl = API_URL.replace(/^http/, 'ws') + path;

    const connect = () => {
      if (cancelled) return;
      try {
        ws = new WebSocket(wsUrl);
      } catch (e) {
        statusRef.current = 'closed';
        optsRef.current.onError?.();
        return;
      }

      ws.onopen = () => {
        statusRef.current = 'open';
        optsRef.current.onOpen?.();
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as T;
          optsRef.current.onMessage(data);
        } catch (err) {
          console.warn('[ws]', path, 'failed to parse message', err);
        }
      };

      ws.onerror = () => {
        if (statusRef.current === 'connecting') optsRef.current.onError?.();
      };

      ws.onclose = () => {
        statusRef.current = 'closed';
        if (opts.reconnectMs && opts.reconnectMs > 0 && !cancelled) {
          reconnectTimer = setTimeout(connect, opts.reconnectMs);
        }
      };
    };

    connect();
    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [path, opts.reconnectMs]);

  return { status: statusRef.current };
}
