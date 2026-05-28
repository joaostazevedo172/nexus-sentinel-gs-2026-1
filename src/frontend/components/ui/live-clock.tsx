'use client';

import { useEffect, useState } from 'react';

/**
 * Live UTC clock — starts with placeholder to avoid SSR/CSR hydration mismatch,
 * then updates every second after mount.
 */
export function LiveClock() {
  const [text, setText] = useState('—— —— —— UTC');

  useEffect(() => {
    const update = () =>
      setText(new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC');
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
