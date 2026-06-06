'use client';

type Accent = 'cyan' | 'amber' | 'magenta';

interface Props {
  color?: Accent;
  label: string;
  value?: string;
}

const accentMap: Record<Accent, { text: string; dot: string }> = {
  cyan:    { text: 'text-[#00F2FF]', dot: 'bg-[#00F2FF]' },
  amber:   { text: 'text-[#FFB800]', dot: 'bg-[#FFB800]' },
  magenta: { text: 'text-[#FF007A]', dot: 'bg-[#FF007A]' }
};

export function StatusPill({ color = 'cyan', label, value }: Props) {
  const c = accentMap[color];
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/40 border border-white/[0.06]">
      <span className={`relative inline-flex w-1.5 h-1.5 rounded-full ${c.dot} pulse-ring ${c.text}`} />
      <span className="font-mono text-[10px] tracking-[0.18em] uppercase text-neutral-400">{label}</span>
      {value && <span className={`font-mono text-[10px] ${c.text}`}>{value}</span>}
    </div>
  );
}
