'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { Hash, Layers } from 'lucide-react';
import { useNexus } from '@/lib/store';
import { DrawerShell } from '@/components/ui/drawer-shell';

const easeExpo = [0.16, 1, 0.3, 1] as const;

export function BlockchainDrawer() {
  const open = useNexus((s) => s.openModuleId === 'blockchain');
  const closeModule = useNexus((s) => s.closeModule);
  const transactions = useNexus((s) => s.transactions);

  const totalTokens = transactions.reduce((a, t) => a + t.reward, 0);
  const fedCount = transactions.filter((t) => t.fed).length;

  return (
    <DrawerShell
      open={open}
      onClose={closeModule}
      title="Blockchain Ledger"
      subtitle="Smart Contracts · Nexus Tokens"
      icon={Layers}
      accent="#FFB800"
    >
      <section className="grid grid-cols-3 gap-2 mb-5">
        <Stat label="Transações"     value={transactions.length}              color="#FFFFFF" />
        <Stat label="Tokens Nexus"   value={totalTokens}                       color="#FFB800" />
        <Stat label="Burst Federado" value={fedCount}                          color="#00F2FF" />
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5">
            <Hash className="w-3 h-3 text-[#FFB800]" strokeWidth={1.5} />
            <h3 className="font-mono text-[10px] tracking-[0.2em] uppercase text-neutral-300">
              Stream do Ledger
            </h3>
          </div>
          <span className="flex items-center gap-1.5 font-mono text-[9px] text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>
        </div>
        <div className="bg-black/50 border border-white/[0.06] rounded-lg p-3 terminal max-h-[440px] overflow-y-auto">
          <div className="text-neutral-600 mb-1">
            {'>'} Conectado ao Nexus Chain · Block #4,829,177 · {transactions.length} TX
          </div>
          <div className="text-neutral-600 mb-3">
            {'>'} Smart Contract: 0x9f4...ab12 · Verificado ✓
          </div>
          <AnimatePresence initial={false}>
            {transactions.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-neutral-600 italic"
              >
                Aguardando detecções do módulo YOLO…
              </motion.div>
            )}
            {transactions.map((tx) => (
              <motion.div
                key={tx.hash + tx.time}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, ease: easeExpo }}
                className={`mb-1 ${tx.fed ? 'border-l-2 border-[#00F2FF] pl-2' : ''}`}
              >
                <span className="tx-time">[{tx.time}]</span>{' '}
                <span className="tx-hash">{tx.hash}</span>{' '}
                <span className="text-neutral-500">·</span>{' '}
                <span className="tx-region">{tx.region}</span>{' '}
                <span className="text-neutral-500">·</span>{' '}
                <span>{tx.action}</span>{' '}
                <span className="text-neutral-500">·</span>{' '}
                <span className="tx-reward">+{tx.reward} NXS</span>
                {tx.fed && <span className="text-[#00F2FF] ml-1">[FED]</span>}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        <div className="mt-3 font-mono text-[9px] text-neutral-500 leading-relaxed">
          Cada transação <span className="text-[#FFB800]">tokeniza</span> uma ação de regeneração detectada
          por visão computacional. Os Nexus Tokens são liberados via smart contract para os agentes locais
          responsáveis pela ação — materializando o <span className="text-white">altruísmo algorítmico</span>{' '}
          em economia circular.
        </div>
      </section>
    </DrawerShell>
  );
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-black/30 border border-white/[0.05] rounded-md px-3 py-2">
      <div className="font-mono text-[9px] tracking-widest uppercase text-neutral-500">{label}</div>
      <div className="font-display text-lg font-bold tabular-nums" style={{ color }}>
        {value.toLocaleString('pt-BR')}
      </div>
    </div>
  );
}
