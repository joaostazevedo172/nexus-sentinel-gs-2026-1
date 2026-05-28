# Esquema Elétrico — ESP32 Soil Sensor

## Componentes

| Item | Modelo | Quantidade |
|------|--------|-----------|
| Microcontrolador | ESP32 DevKit v1 (38 pinos) | 1 |
| Sensor de umidade do solo | Capacitivo v1.2 (analógico) | 1 |
| Fonte | USB micro-B 5V/2A | 1 |
| Jumpers | Macho-Macho | 3 |

## Pinout

```
   ESP32 DevKit v1                  Sensor Capacitivo v1.2
   ────────────────                 ──────────────────────
        3V3 ────────────────────► VCC
        GND ────────────────────► GND
   GPIO 34 ◄──────────────────── AOUT  (saída analógica 0–3.3V)
```

## Por que GPIO 34?

GPIO 34 é input-only e está no ADC1, que permanece funcional mesmo com WiFi
ativo (ADC2 entra em conflito com o rádio). Resolução: 12 bits (0–4095),
ou 16 bits após `ADC.read_u16()` (0–65535).

## Calibração

Antes de deployar:

1. Ligue o sensor com o ESP32 e abra serial monitor (115200 baud)
2. Mantenha o sensor **no ar** por 30s → anote o valor médio de `raw` em `SENSOR_DRY`
3. Mergulhe em copo d'água por 30s (até a linha máxima, NÃO submerso) → anote `SENSOR_WET`
4. Atualize as constantes em `firmware/main.py` e flash novamente
