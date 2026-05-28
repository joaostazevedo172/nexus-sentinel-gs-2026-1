'use client';

import { motion } from 'framer-motion';
import { Brain, RotateCw, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { useNexus } from '@/lib/store';
import { generateBriefing, BriefingResponse } from '@/lib/api';
import { DrawerShell } from '@/components/ui/drawer-shell';

const easeExpo = [0.16, 1, 0.3, 1] as const;

export function BriefingDrawer() {
  const open = useNexus((s) => s.openModuleId === 'briefing');
  const closeModule = useNexus((s) => s.closeModule);
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<BriefingResponse | null>(null);

  const run = async () => {
    setLoading(true);
    try {
      const data = await generateBriefing();
      setResp(data);
    } catch (e) {
      console.error('[briefing] failed:', e);
      setResp({
        briefing: '_Erro ao gerar briefing — verifique se o backend está rodando._',
        model: 'error',
        snapshot: { temperature: 0, humidity: 0, meshActivity: 0, resilience: 0 },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DrawerShell
      open={open}
      onClose={closeModule}
      title="Briefing Executivo"
      subtitle="Amazon Bedrock · Claude 3.5 Sonnet"
      icon={Brain}
      accent="#00F2FF"
    >
      <section className="mb-5">
        <p className="font-mono text-[11px] text-neutral-400 leading-relaxed mb-4">
          Sintetiza o estado atual do Gêmeo Digital em uma análise executiva
          em português, gerada por um modelo de linguagem hospedado no{' '}
          <span className="text-[#FFB800]">Amazon Bedrock</span>. Se as
          credenciais AWS não estiverem configuradas, o sistema cai
          automaticamente para um template determinístico.
        </p>

        <motion.button
          onClick={run}
          disabled={loading}
          whileHover={!loading ? { scale: 1.01 } : {}}
          whileTap={!loading ? { scale: 0.98 } : {}}
          transition={{ duration: 0.3, ease: easeExpo }}
          className="w-full px-4 py-3 rounded-lg border border-[#00F2FF]/40 bg-[#00F2FF]/[0.06] text-[#00F2FF] flex items-center justify-center gap-2 font-display font-bold text-[12px] tracking-[0.15em] uppercase hover:bg-[#00F2FF]/[0.12] disabled:opacity-60"
        >
          {loading ? (
            <>
              <RotateCw className="w-3.5 h-3.5 animate-spin" strokeWidth={2} />
              Consultando Bedrock…
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5" strokeWidth={2} />
              Gerar Briefing
            </>
          )}
        </motion.button>
      </section>

      {resp && (
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: easeExpo }}
        >
          <div className="bg-black/40 border border-white/[0.06] rounded-lg p-4 font-mono text-[12px] leading-relaxed text-neutral-200 whitespace-pre-wrap">
            {resp.briefing}
          </div>
          <div className="mt-2 flex items-center justify-between font-mono text-[9px] text-neutral-500">
            <span>Modelo</span>
            <span className={resp.model.includes('claude') ? 'text-[#FFB800]' : 'text-neutral-500'}>
              {resp.model}
            </span>
          </div>
          <div className="mt-1 flex items-center justify-between font-mono text-[9px] text-neutral-500">
            <span>Snapshot</span>
            <span className="text-[#00F2FF]">
              T {resp.snapshot.temperature.toFixed(1)}°C ·{' '}
              H {resp.snapshot.humidity.toFixed(0)}% ·{' '}
              M {resp.snapshot.meshActivity.toFixed(0)}% ·{' '}
              R {resp.snapshot.resilience.toFixed(0)}%
            </span>
          </div>
        </motion.section>
      )}
    </DrawerShell>
  );
}
