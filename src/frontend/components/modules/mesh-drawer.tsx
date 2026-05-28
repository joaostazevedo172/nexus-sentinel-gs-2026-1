'use client';

import { GitBranch, MapPin, Wifi } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNexus } from '@/lib/store';
import { nodeCount } from '@/lib/formulas';
import { fetchMeshNodes } from '@/lib/api';
import type { MeshNode } from '@/lib/types';
import { DrawerShell } from '@/components/ui/drawer-shell';
import { MeshTopology } from './mesh-topology';

const USE_BACKEND = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';

const FALLBACK_CRITICAL: MeshNode[] = [
  { id: 'SP-BR',  description: 'São Paulo · Calor Extremo',   kind: 'risk',    pingMs: 12, weightSize: '4.2 MB', lat: -23, lng: -46 },
  { id: 'DEL-IN', description: 'Nova Delhi · Inundação',      kind: 'risk',    pingMs: 38, weightSize: '3.8 MB', lat:  28, lng:  77 },
  { id: 'CPT-ZA', description: 'Cape Town · Seca',            kind: 'warning', pingMs: 24, weightSize: '2.1 MB', lat: -34, lng:  18 },
  { id: 'SYD-AU', description: 'Sydney · Anomalia Térmica',   kind: 'warning', pingMs: 41, weightSize: '2.6 MB', lat: -33, lng: 151 }
];

export function MeshDrawer() {
  const open = useNexus((s) => s.openModuleId === 'mesh');
  const closeModule = useNexus((s) => s.closeModule);
  const meshActivity = useNexus((s) => s.meshActivity);
  const federationActive = useNexus((s) => s.federationActive);

  const [critical, setCritical] = useState<MeshNode[]>(FALLBACK_CRITICAL);

  useEffect(() => {
    if (!USE_BACKEND || !open) return;
    fetchMeshNodes()
      .then((nodes) =>
        setCritical(nodes.filter((n) => n.kind !== 'normal').slice(0, 4))
      )
      .catch(() => {
        /* keep fallback */
      });
  }, [open]);

  return (
    <DrawerShell
      open={open}
      onClose={closeModule}
      title="Rede Mesh"
      subtitle="Aprendizado Federado · 124 Nós"
      icon={Wifi}
      accent="#FF007A"
    >
      <section className="mb-5 grid grid-cols-3 gap-2">
        <Stat label="Atividade" value={`${Math.round(meshActivity)}%`} color="#00F2FF" />
        <Stat label="Nós"       value={nodeCount(meshActivity).toLocaleString('pt-BR')} color="#FFFFFF" />
        <Stat label="Status"
              value={federationActive ? 'SYNC' : 'IDLE'}
              color={federationActive ? '#00F2FF' : '#10B981'} />
      </section>

      <section className="mb-5">
        <div className="flex items-center gap-1.5 mb-2">
          <GitBranch className="w-3 h-3 text-[#FF007A]" strokeWidth={1.5} />
          <h3 className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-300">
            Topologia Federada · Troca de Pesos
          </h3>
        </div>
        <div className="bg-black/30 border border-white/[0.05] rounded-lg p-4">
          <MeshTopology />
        </div>
        <div className="mt-2 font-mono text-[10px] text-neutral-500 leading-relaxed">
          Cada nó treina o modelo localmente nos dados climáticos da sua região, e apenas os{' '}
          <span className="text-[#00F2FF]">gradientes agregados</span> trafegam pela rede.{' '}
          <span className="text-white">Privacidade preservada por construção</span>: dados brutos
          nunca saem do nó de origem.
        </div>
      </section>

      <section>
        <div className="flex items-center gap-1.5 mb-2">
          <MapPin className="w-3 h-3 text-[#FF007A]" strokeWidth={1.5} />
          <h3 className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-300">Nós Críticos</h3>
        </div>
        <div className="space-y-1.5">
          {critical.map((n) => {
            const c = n.kind === 'risk' ? '#FF007A' : '#FFB800';
            return (
              <div
                key={n.id}
                className="flex items-center justify-between bg-black/30 border border-white/[0.05] rounded-md px-3 py-2"
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className="relative w-1.5 h-1.5 rounded-full pulse-ring"
                    style={{ background: c, color: c }}
                  />
                  <div>
                    <div className="font-mono text-[11px] text-white tabular-nums">{n.id}</div>
                    <div className="font-mono text-[9px] text-neutral-500">{n.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-[10px] text-[#00F2FF] tabular-nums">{n.pingMs}ms</div>
                  <div className="font-mono text-[9px] text-neutral-500 tabular-nums">{n.weightSize}</div>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </DrawerShell>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="bg-black/30 border border-white/[0.05] rounded-md px-3 py-2">
      <div className="font-mono text-[9px] tracking-widest uppercase text-neutral-500">{label}</div>
      <div className="font-display text-lg font-bold tabular-nums" style={{ color }}>{value}</div>
    </div>
  );
}
