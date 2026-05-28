'use client';

import { RefObject, useEffect } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface Props {
  containerRef: RefObject<HTMLElement>;
}

export function Spotlight({ containerRef }: Props) {
  const x = useMotionValue(-1000);
  const y = useMotionValue(-1000);
  const sx = useSpring(x, { stiffness: 90, damping: 20, mass: 0.5 });
  const sy = useSpring(y, { stiffness: 90, damping: 20, mass: 0.5 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onMove = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      x.set(e.clientX - r.left);
      y.set(e.clientY - r.top);
    };
    const onLeave = () => {
      x.set(-1000);
      y.set(-1000);
    };
    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerleave', onLeave);
    return () => {
      el.removeEventListener('pointermove', onMove);
      el.removeEventListener('pointerleave', onLeave);
    };
  }, [containerRef, x, y]);

  const background = useTransform(
    [sx, sy],
    ([vx, vy]) =>
      `radial-gradient(360px circle at ${vx}px ${vy}px, rgba(0,242,255,0.10), transparent 60%)`
  );

  return (
    <motion.div
      aria-hidden
      className="pointer-events-none absolute inset-0 z-10"
      style={{ background }}
    />
  );
}
