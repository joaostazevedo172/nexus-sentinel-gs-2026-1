"""
Simulador ESP32 — sensor de umidade do solo.

Mimetiza o comportamento de um ESP32 com sensor capacitivo de umidade
(Sentinel-Soil v1) publicando leituras a cada 5 segundos no endpoint
PATCH /api/climate/state do backend Nexus Sentinel.

Em produção, o firmware MicroPython equivalente roda em firmware/main.py
sobre o hardware real (ESP32 DevKit + sensor capacitivo no GPIO 34).

Uso:
    python esp32_simulator.py
    python esp32_simulator.py --api https://nexus-sentinel-api-gpk9.onrender.com --interval 5 --sensor-id ESP32-SP-001
"""
from __future__ import annotations

import argparse
import math
import random
import signal
import sys
import time
from datetime import datetime
from typing import Any

try:
    import requests
except ImportError:
    sys.exit("requests não instalado. Rode: pip install requests")


def read_soil_moisture(t: float, baseline: float = 60.0) -> float:
    """Simula leitura do ADC do ESP32 conectado a um sensor capacitivo.

    No hardware real: machine.ADC(machine.Pin(34)).read_u16() retorna
    um valor 0..65535 que é convertido para % de umidade via calibração
    (seco = ~65535, encharcado = ~20000).

    Aqui modelamos com uma onda senoidal lenta (ciclo dia/noite) +
    ruído gaussiano (3 pontos de desvio padrão).
    """
    diurnal = baseline + 12.0 * math.sin(t / 1800.0)        # ciclo de ~3h para demo
    noise = random.gauss(0, 3.0)
    moisture = max(30.0, min(90.0, diurnal + noise))
    return round(moisture, 1)


def publish(api: str, sensor_id: str, humidity: float, timeout: float = 3.0) -> bool:
    try:
        r = requests.patch(
            f"{api}/api/climate/state",
            json={"humidity": humidity},
            headers={"X-Device-Id": sensor_id, "X-Device-Type": "esp32-soil"},
            timeout=timeout,
        )
        
        # --- ADICIONE ESTAS DUAS LINHAS DE DEBUG AQUI ---
        if r.status_code != 200:
            print(f"  [DEBUG] O Render recusou! Status {r.status_code}: {r.text}")
        # ------------------------------------------------
            
        return r.status_code == 200
    except requests.RequestException as e:
        print(f"  ✗ erro de rede: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Nexus ESP32 soil-moisture simulator")
    parser.add_argument("--api", default="http://localhost:8000", help="URL do backend")
    parser.add_argument("--interval", type=float, default=5.0, help="segundos entre leituras")
    parser.add_argument("--sensor-id", default="ESP32-SP-001")
    parser.add_argument("--baseline", type=float, default=60.0, help="umidade média (%)")
    args = parser.parse_args()

    running = True

    def stop(*_: Any) -> None:
        nonlocal running
        running = False
        print("\n[ESP32] shutdown solicitado, desligando…")

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"[ESP32] {args.sensor_id} iniciado")
    print(f"[ESP32] publicando em {args.api}/api/climate/state a cada {args.interval}s")
    print(f"[ESP32] baseline de umidade: {args.baseline}%")
    print()

    start = time.time()
    samples = 0
    while running:
        t = time.time() - start
        moisture = read_soil_moisture(t, baseline=args.baseline)
        ok = publish(args.api, args.sensor_id, moisture)
        ts = datetime.now().strftime("%H:%M:%S")
        status = "✓ enviado" if ok else "✗ falhou"
        print(f"  [{ts}] {args.sensor_id}  humidity={moisture:5.1f}%  {status}")
        samples += 1
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            break

    print(f"\n[ESP32] {samples} amostras publicadas em {time.time() - start:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
