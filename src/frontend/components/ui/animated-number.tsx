'use client';

import { useEffect, useState } from 'react';
import { useMotionValue, useSpring } from 'framer-motion';

interface Props {
  value: number;
  format?: (v: number) => string;
}

export function AnimatedNumber({
  value,
  format = (v) => Math.round(v).toLocaleString('pt-BR')
}: Props) {
  const motionVal = useMotionValue(0);
  const spring = useSpring(motionVal, { stiffness: 90, damping: 20 });
  const [display, setDisplay] = useState(format(0));

  useEffect(() => {
    motionVal.set(value);
  }, [value, motionVal]);

  useEffect(() => spring.on('change', (v) => setDisplay(format(v))), [spring, format]);

  return <span>{display}</span>;
}
