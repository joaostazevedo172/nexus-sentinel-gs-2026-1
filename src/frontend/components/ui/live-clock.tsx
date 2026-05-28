'use client';

import { useEffect, useState } from 'react';

/**
 * Live clock — horário de Brasília (BRT/BRST).
 * Começa com placeholder pra evitar SSR/CSR hydration mismatch.
 */
export function LiveClock() {
  const [text, setText] = useState('—— ——:——:—— BRT');

  useEffect(() => {
    const update = () => {
      const now = new Date().toLocaleString('sv-SE', {
        timeZone: 'America/Sao_Paulo',
        hour12: false,
      });
      // "sv-SE" garante formato "YYYY-MM-DD HH:MM:SS"
      setText(now + ' BRT');
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <span className="font-mono text-[11px] tracking-wider text-neutral-400" suppressHydrationWarning>
      {text}
    </span>
  );
}