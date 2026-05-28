# IoT — ESP32 Soil Moisture Sensor

Camada de sensoriamento físico do Nexus Sentinel. Cada nó da rede mesh
publica leituras de umidade do solo em tempo real para o backend FastAPI,
alimentando o Digital Twin com dados reais de campo.

## Dois modos de operação

### 1. Simulador (Python, sem hardware)

Para desenvolvimento e demo. Mimetiza o comportamento de um ESP32 real:

```bash
pip install requests
python esp32_simulator.py
```

A umidade publicada segue um ciclo senoidal (dia/noite simulado) + ruído
gaussiano. A barra de "Umidade do Solo" do dashboard se move sozinha em
tempo real conforme o "ESP32" envia leituras.

### 2. Hardware real (ESP32 + MicroPython)

Para deploy em campo:

1. Veja o esquema elétrico em [`wiring.md`](./wiring.md)
2. Flash o MicroPython oficial no ESP32 (`esptool.py write_flash …`)
3. Configure `WIFI_SSID`, `WIFI_PASS` e `API_URL` no topo de `firmware/main.py`
4. Faça upload: `ampy --port /dev/ttyUSB0 put firmware/main.py`
5. Reset o ESP32 → o LED interno acende a cada publicação bem-sucedida

## Endpoint consumido

```http
PATCH /api/climate/state
Content-Type: application/json
X-Device-Id: ESP32-SP-001
X-Device-Type: esp32-soil

{"humidity": 67.3}
```

A resposta do backend devolve o estado completo do Digital Twin recalculado:

```json
{"temperature": 0.0, "humidity": 67.3, "meshActivity": 78.0, "resilience": 87.0}
```

## Arquitetura de Privacidade

O ESP32 envia **apenas a leitura agregada de umidade** — nunca dados brutos
de localização, identificação pessoal ou imagens. Em deploy multi-nó, cada
ESP32 treina localmente um modelo simples de anomalia (Z-score sobre janela
de 100 amostras) e só publica leituras + flag de anomalia, mantendo o
princípio de **federated learning** que sustenta o projeto.
