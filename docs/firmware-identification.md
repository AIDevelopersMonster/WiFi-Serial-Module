# Firmware identification

Physically similar ESP8285/ESP8266 Wi-Fi serial modules may ship with very different firmware. Identify the firmware **before** changing flash contents.

## Quick decision table

| Test | DOIT Transparent V3 | Espressif AT 1.1.x | JeeLabs esp-link |
|---|---|---|---|
| Typical SSID | `Doit_WiFi_xxxxxx` | Often `ESP_xxxxxx` or configured value | `ESP_xxxxxx` after initial setup/reset |
| `192.168.4.1` web UI | Yes | Normally no DOIT-style UI | Yes |
| Factory UART | 9600 8N1 | Commonly 115200 8N1 | Commonly 115200 8N1 |
| `AT` -> `OK` | Not a reliable identifier | **Yes** | No |
| `AT+GMR` -> AT/SDK version | No | **Yes** | No |
| `AT+STASTATUS` | **Yes** | No | No |
| TCP port 23 serial bridge | No by factory default | Only if configured | **Characteristic esp-link service** |
| Factory TCP port 9000 | **Yes** | Only if configured | No |
| Main configuration | Browser | UART AT commands | Browser |

## Identification procedure

### Step 1 — record the SSID

Power the module without changing anything and record the access-point name.

Examples:

```text
Doit_WiFi_A1B2C3
ESP_A1B2C3
```

SSID is only a clue, not proof.

### Step 2 — inspect the network parameters

Connect a phone or computer to the module AP and record:

- assigned client IP;
- gateway address;
- subnet mask;
- whether HTTP responds at the gateway address.

For genuine DOIT V3 factory configuration, the AP address is documented as:

```text
192.168.4.1
```

and a configuration page should open there.

### Step 3 — test UART at 115200 8N1

Use a 3.3 V-compatible USB-UART adapter and send commands terminated with CR+LF:

```text
AT
AT+GMR
```

If the result is similar to:

```text
AT
OK

AT+GMR
AT version:1.1.0.0(...)
SDK version:1.5.4(...)
compile time:...
OK
```

the module is running the Espressif AT firmware family.

### Step 4 — test DOIT-specific status commands

At the configured UART rate, try:

```text
AT+STASTATUS
AT+STAINFO
AT+TCPCLIENT
```

The DOIT V3 manual documents responses such as:

```text
STA:OK
STA:DOWN
TCP: OK
TCP: OFF
```

These commands are useful fingerprints for DOIT firmware.

### Step 5 — check for esp-link only if relevant

If the module creates `ESP_xxxxxx`, has a web UI at `192.168.4.1`, and exposes the esp-link configuration interface / TCP serial service (typically port 23), it may be JeeLabs esp-link.

Do not identify a module as esp-link from SSID alone.

## Observed module in this project

One `ESP_XXXXX` unit has been positively identified by UART:

```text
AT

OK
AT+GMR

AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
OK
```

Classification:

```text
ESP8266/ESP8285 Espressif AT firmware family
AT version 1.1.0.0
NONOS SDK 1.5.4
May 2016 build
```

Therefore this tested `ESP_XXXXX` module is **not** DOIT Transparent V3 and **not** esp-link.

## Recommended inventory record

For each physical module, record:

| Field | Example |
|---|---|
| Module ID | M01 |
| PCB marking | DT-06 / unknown |
| ESP module marking | ESP-M2 / unknown |
| SSID | `ESP_A1B2C3` |
| AP IP / gateway | `192.168.4.1` |
| Web UI | no |
| UART baud | 115200 |
| `AT` response | `OK` |
| `AT+GMR` | AT 1.1.0.0 / SDK 1.5.4 |
| Firmware classification | Espressif AT |
| Flash backup made | yes/no |
| Notes | ... |

## Sources

- DOIT DT-06 manual: https://github.com/SmartArduino/gitnova.github.io/blob/master/docs/ESPSeries/ESP8285/DT06/DT06.md
- Espressif technical documentation: https://www.espressif.com/en/support/documents/technical-documents
- JeeLabs esp-link: https://github.com/jeelabs/esp-link
