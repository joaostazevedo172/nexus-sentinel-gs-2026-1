'use client';

import { motion } from 'framer-motion';

/** Animated ambient blobs that breathe behind the dashboard. */
export function Atmospherics() {
  return (
    <>
      <motion.div
        aria-hidden
        className="absolute -top-32 -left-32 w-[520px] h-[520px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(0,242,255,0.13), transparent 65%)',
          filter: 'blur(40px)'
        }}
        animate={{ x: [0, 60, 0], y: [0, 40, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden
        className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(255,0,122,0.10), transparent 65%)',
          filter: 'blur(50px)'
        }}
        animate={{ x: [0, -50, 0], y: [0, -30, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden
        className="absolute top-1/3 left-1/2 w-[400px] h-[400px] rounded-full -translate-x-1/2"
        style={{
          background: 'radial-gradient(circle, rgba(255,184,0,0.06), transparent 65%)',
          filter: 'blur(40px)'
        }}
        animate={{ x: [-30, 30, -30] }}
        transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
      />
    </>
  );
}
