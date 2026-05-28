'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { LucideIcon, X } from 'lucide-react';
import { ReactNode, useEffect } from 'react';

const easeExpo = [0.16, 1, 0.3, 1] as const;

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle: string;
  icon: LucideIcon;
  accent: string;
  children: ReactNode;
}

export function DrawerShell({ open, onClose, title, subtitle, icon: Icon, accent, children }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.55, ease: easeExpo }}
            className="fixed top-0 right-0 bottom-0 w-full md:w-[560px] z-50 nexus-glass border-l flex flex-col overflow-hidden"
            style={{ borderColor: 'rgba(255,255,255,0.08)' }}
          >
            <header className="flex items-start justify-between p-5 border-b border-white/[0.06]">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center border"
                  style={{
                    borderColor: `${accent}33`,
                    background: `${accent}0d`,
                    boxShadow: `0 0 20px ${accent}26`
                  }}
                >
                  <Icon className="w-4 h-4" style={{ color: accent }} strokeWidth={1.5} />
                </div>
                <div>
                  <div className="font-display text-[15px] font-bold tracking-wider text-white">{title}</div>
                  <div className="font-mono text-[10px] tracking-[0.18em] uppercase text-neutral-500">{subtitle}</div>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-md border border-white/[0.08] flex items-center justify-center text-neutral-400 hover:text-white hover:border-white/20 transition-colors"
                aria-label="Fechar"
              >
                <X className="w-3.5 h-3.5" strokeWidth={1.5} />
              </button>
            </header>
            <div className="flex-1 overflow-y-auto p-5">{children}</div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
