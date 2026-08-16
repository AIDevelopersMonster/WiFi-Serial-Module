# WiFi Serial Module

A practical research and integration project for small ESP8285/ESP8266-based TTL-to-Wi-Fi serial modules, with emphasis on transparent UART links and paired wireless UART replacement.

## Project goal

The primary target is a transparent serial link:

```text
Device A UART <-> WiFi Serial Module A <~~~ Wi-Fi ~~~> WiFi Serial Module B <-> Device B UART
```

This is intended to replace a wired serial transport layer where possible. For example, if two legacy devices previously used RS-485 transceivers only as the physical transport for an underlying UART protocol, the RS-485 transceivers can be removed and the original UART TX/RX signals can be connected directly to the Wi-Fi modules.

The project does **not** assume that every physically similar module has the same firmware. We have already observed at least two firmware families on apparently similar ESP8285-based modules.

## Observed module families

| Observable behavior | Likely firmware | Configuration method | Default / typical UART | Web UI | Transparent network modes | Notes |
|---|---|---|---|---|---|---|
| SSID `Doit_WiFi_xxxxxx`, browser at `192.168.4.1` works | DOIT DT-06 Transparent Transmission Firmware V3.0 | Built-in web interface, limited AT status commands | Factory: 9600 8N1 | Yes | TCP Server, TCP Client, UDP Server, UDP Client, UDP broadcast | Best candidate for a direct server/client pair without reflashing |
| SSID `ESP_xxxxxx`, `AT` -> `OK`, `AT+GMR` reports `AT version:1.1.0.0` and SDK 1.5.4 | Espressif ESP8266 AT firmware 1.1.0.0 / NONOS SDK 1.5.4 | UART AT commands | Commonly 115200 8N1 | No built-in DOIT-style UI | TCP/UDP through AT command set; transparent mode supported with restrictions | One tested module reports build dates May 2016 |
| SSID `ESP_xxxxxx`, browser at `192.168.4.1` shows esp-link UI, TCP port 23 provides serial bridge | JeeLabs esp-link | Web interface | Commonly 115200 8N1 | Yes | Transparent TCP serial bridge | Not yet observed in our hardware; listed for identification only |

**Important:** SSID alone is not sufficient to identify the firmware. `ESP_xxxxxx` may be used by more than one firmware family. Confirm with UART commands and/or the web interface.

## Repository map

- [`docs/firmware-identification.md`](docs/firmware-identification.md) — decision table and tests for identifying unknown modules.
- [`docs/doit-v3.md`](docs/doit-v3.md) — DOIT transparent V3 firmware properties and factory defaults.
- [`docs/espressif-at-1.1.md`](docs/espressif-at-1.1.md) — initial notes on observed Espressif AT 1.1.0.0 modules.
- [`docs/esp8266-at-v1.1-sdk1.5.4/`](docs/esp8266-at-v1.1-sdk1.5.4/) — detailed profile for the tested `ESP_XXXXXX` firmware, full v1.5.4 command inventory, examples, safety classification, and COM23 observation.
- [`docs/pairing.md`](docs/pairing.md) — how to build a module-to-module transparent UART link.
- [`tools/README.md`](tools/README.md) — command-line utilities and separately marked **Windows** / **Linux** examples.

## Command-line tools

The repository includes:

```text
tools/
  detect_module.py
  at_command_audit.py
  serial_console.py
  tcp_console.py
  uart_loopback_test.py
  latency_test.py
```

`detect_module.py` is the quick firmware fingerprint. `at_command_audit.py` is the deeper, state-preserving command audit for the 2016 Espressif AT family.

Install the UART dependency with `py -m pip install -r requirements.txt` on Windows or `python3 -m pip install -r requirements.txt` on Linux. See [`tools/README.md`](tools/README.md) for usage.

## UART wiring

For each endpoint:

```text
Device TX  ---> Module RXD
Device RX  <--- Module TXD
Device GND ---- Module GND
```

TX and RX are crossed. The two remote devices do **not** need a common ground because the transport between the modules is wireless; each device shares ground only with its local Wi-Fi module.

### Voltage caution

The DT-06 documentation describes 4.5-6.0 V module supply and 3.3 V TTL logic, with the board documented as compatible with 5 V TTL through its input circuitry. Treat the ESP8266/ESP8285 silicon itself as a 3.3 V device. For unknown clones or revisions, verify the actual board before applying 5 V logic directly.

## Current hardware observations

### Module type A

Observed SSID:

```text
Doit_WiFi_XXXXXX
```

Observed behavior:

- connects as an access point;
- configuration page opens at `192.168.4.1`;
- behavior matches DOIT DT-06 Transparent Transmission Firmware V3.0.

### Module type B

Observed SSID:

```text
ESP_XXXXXX
```

Observed UART response:

```text
AT

OK
AT+GMR

AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
OK
```

This identifies the tested module as running an old Espressif AT firmware family rather than DOIT V3 or esp-link.

## Sources

Primary references used for the initial documentation:

- DOIT DT-06 manual: https://github.com/SmartArduino/gitnova.github.io/blob/master/docs/ESPSeries/ESP8285/DT06/DT06.md
- Espressif ESP8266 AT documentation archive / AT command set: https://www.espressif.com/en/support/documents/technical-documents?keys=ESP8266%20AT
- JeeLabs esp-link: https://github.com/jeelabs/esp-link

## Status

Early hardware characterization. Do not assume identical firmware, flash layout, UART defaults, or voltage tolerance across visually similar modules until each module/revision is identified.
