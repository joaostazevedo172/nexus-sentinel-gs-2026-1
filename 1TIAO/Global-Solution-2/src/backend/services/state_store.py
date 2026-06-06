"""In-memory climate state for the Digital Twin.

Single source of truth that all routers/services read from.
In production this would be backed by Redis / PostgreSQL.
"""
from threading import RLock
from time import time
from dataclasses import dataclass


@dataclass
class ClimateSnapshot:
    temperature: float  # Δ°C from baseline
    humidity: float     # %
    mesh_activity: float  # %
    resilience: float  # %
    federation_active: bool
    federation_started_at: float


def _target_resilience(temp: float, humidity: float, mesh: float, fed_burst: float) -> float:
    temp_penalty = max(0.0, temp - 0.3) ** 2 * 7.0
    humidity_bonus = (humidity - 65.0) * 0.18
    mesh_bonus = (mesh - 78.0) * 0.12
    return max(5.0, min(98.0, 87.0 - temp_penalty + humidity_bonus + mesh_bonus + fed_burst))


class StateStore:
    """Thread-safe singleton holding the live Digital Twin state."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._s = ClimateSnapshot(
            temperature=0.0,
            humidity=65.0,
            mesh_activity=78.0,
            resilience=87.0,
            federation_active=False,
            federation_started_at=0.0,
        )

    def _recompute_resilience(self) -> None:
        fed_burst = 0.0
        if self._s.federation_active:
            dt = time() - self._s.federation_started_at
            if dt < 4.0:
                fed_burst = 30.0 * (1 - dt / 4.0)
            elif dt > 6.0:
                self._s.federation_active = False
        tgt = _target_resilience(
            self._s.temperature, self._s.humidity, self._s.mesh_activity, fed_burst
        )
        # Smooth toward target (server-side equivalent of the frontend's RAF loop)
        self._s.resilience += (tgt - self._s.resilience) * 0.25

    def snapshot(self) -> ClimateSnapshot:
        with self._lock:
            self._recompute_resilience()
            return ClimateSnapshot(**self._s.__dict__)

    def update(
        self,
        temperature: float | None = None,
        humidity: float | None = None,
        mesh_activity: float | None = None,
    ) -> ClimateSnapshot:
        with self._lock:
            if temperature is not None:
                self._s.temperature = max(-1.0, min(4.0, float(temperature)))
            if humidity is not None:
                self._s.humidity = max(30.0, min(90.0, float(humidity)))
            if mesh_activity is not None:
                self._s.mesh_activity = max(0.0, min(100.0, float(mesh_activity)))
            return self.snapshot()

    def activate_federation(self) -> None:
        with self._lock:
            self._s.federation_active = True
            self._s.federation_started_at = time()


# Singleton instance
state_store = StateStore()
