"""
Firmware MicroPython para ESP32 DevKit + sensor capacitivo de umidade do solo.

Hardware:
    ESP32 DevKit v1
    Sensor capacitivo de umidade do solo v1.2
        VCC  → 3V3
        GND  → GND
        AOUT → GPIO 34 (ADC1_CH6)

Deploy:
    1. Flash MicroPython no ESP32 (esptool.py + firmware oficial)
    2. Configure WIFI_SSID/PASS e API_URL abaixo
    3. ampy --port /dev/ttyUSB0 put main.py
    4. reset → o ESP32 conecta no WiFi e começa a publicar
"""
import network
import time
import machine
import urequests
import ujson

# ──────────────────────────────────────────────────────────────
WIFI_SSID = "YOUR_SSID"
WIFI_PASS = "YOUR_PASSWORD"
API_URL   = "http://192.168.0.100:8000"
SENSOR_ID = "ESP32-SP-001"
INTERVAL  = 5

# Calibração do sensor capacitivo (12-bit ADC, 0..65535 após attenuation)
# Medir manualmente: ADC com sensor seco e mergulhado em água
SENSOR_DRY = 60000      # ar / muito seco
SENSOR_WET = 25000      # solo encharcado
# ──────────────────────────────────────────────────────────────

soil_adc = machine.ADC(machine.Pin(34))
soil_adc.atten(machine.ADC.ATTN_11DB)   # full 3.3V range
led = machine.Pin(2, machine.Pin.OUT)   # built-in LED


def connect_wifi() -> bool:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    print("Conectando WiFi…")
    wlan.connect(WIFI_SSID, WIFI_PASS)
    for _ in range(20):
        if wlan.isconnected():
            print("WiFi OK:", wlan.ifconfig())
            return True
        time.sleep(0.5)
    return False


def read_humidity() -> float:
    """Lê ADC e converte para % via calibração linear."""
    raw = soil_adc.read_u16()
    # Inverter: maior ADC = mais seco
    pct = (SENSOR_DRY - raw) / (SENSOR_DRY - SENSOR_WET) * 100
    return max(0.0, min(100.0, pct))


def publish(humidity: float) -> bool:
    try:
        r = urequests.patch(
            API_URL + "/api/climate/state",
            data=ujson.dumps({"humidity": humidity}),
            headers={
                "Content-Type": "application/json",
                "X-Device-Id": SENSOR_ID,
                "X-Device-Type": "esp32-soil",
            },
        )
        ok = r.status_code == 200
        r.close()
        return ok
    except Exception as e:
        print("publish err:", e)
        return False


def main():
    if not connect_wifi():
        print("Falha no WiFi, reiniciando em 10s…")
        time.sleep(10)
        machine.reset()

    print("ESP32 Nexus Sentinel — iniciado")
    while True:
        h = read_humidity()
        ok = publish(h)
        led.value(1 if ok else 0)
        print("h={:.1f}%  {}".format(h, "OK" if ok else "FAIL"))
        time.sleep(INTERVAL)


main()
