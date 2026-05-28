/**
 * Derive count of risk zones from temperature delta.
 * Models a nonlinear climate-stress curve.
 */
export function riskZoneCount(temp: number): number {
  if (temp < 0.5) return 3;
  if (temp < 1.5) return 5;
  if (temp < 2.5) return 8;
  if (temp < 3.5) return 11;
  return 14;
}

/** Derive connected mesh nodes from mesh activity (0..100). */
export function nodeCount(meshActivity: number): number {
  return Math.round(15000 + (meshActivity / 100) * 12000);
}

/**
 * Target resilience the system should converge toward, given inputs.
 * Temperature penalty is quadratic above +0.3°C; humidity and mesh
 * add linear bonuses; federation burst adds a transient boost.
 */
export function targetResilience(
  temperature: number,
  humidity: number,
  meshActivity: number,
  federationBurst: number = 0
): number {
  const tempPenalty = Math.max(0, temperature - 0.3) ** 2 * 7;
  const humidityBonus = (humidity - 65) * 0.18;
  const meshBonus = (meshActivity - 78) * 0.12;
  return Math.max(
    5,
    Math.min(98, 87 - tempPenalty + humidityBonus + meshBonus + federationBurst)
  );
}
