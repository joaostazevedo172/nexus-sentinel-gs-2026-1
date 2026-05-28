'use client';

import { useEffect, useState } from 'react';

export function Telemetry() {
  const [lat, setLat] = useState(-23.5505);
  const [lng, setLng] = useState(-46.6333);
  const [alt, setAlt] = useState(412);

  useEffect(() => {
    const id = setInterval(() => {
      setLat((v) => +(v + (Math.random() - 0.5) * 0.4).toFixed(4));
      setLng((v) => +(v + (Math.random() - 0.5) * 0.4).toFixed(4));
      setAlt((v) => Math.max(380, Math.min(440, v + Math.round((Math.random() - 0.5) * 6))));
    }, 1500);
    return () => clearInterval(id);
  }, []);

  const rows: [string, string][] = [
    ['LAT', lat.toFixed(4) + '°'],
    ['LNG', lng.toFixed(4) + '°'],
    ['ALT', alt + ' KM'],
    ['SAT', 'SENT-3B'],
    ['SIG', '◼◼◼◼◻']
  ];

  return (
    <div className="space-y-1">
      {rows.map(([k, v]) => (
        <div key={k} className="flex items-center justify-between gap-3 font-mono text-[10px]">
          <span className="text-neutral-500 tracking-widest">{k}</span>
          <span className="text-[#00F2FF] tabular-nums">{v}</span>
        </div>
      ))}
    </div>
  );
}
