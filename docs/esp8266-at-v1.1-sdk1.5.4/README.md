# ESP8266 AT v1.1 / NONOS SDK 1.5.4 module profile

This folder documents the `ESP_XXXXXX` Wi-Fi serial modules observed in this project that answer standard Espressif AT commands at 115200 baud.

## Identified hardware and firmware

The tested project module (`COM23`, SSID `ESP_9F7C3C`) is now identified as:

- SoC: **ESP8285N08**
- integrated Flash: **1 MB**
- crystal: **26 MHz**
- chip ID: `0x009f7c3c`
- base/station MAC: `7c:87:ce:9f:7c:3c`
- SoftAP MAC: `7e:87:ce:9f:7c:3c`
- AT firmware: **1.1.0.0**
- SDK: **ESP8266 NONOS SDK 1.5.4**
- firmware compile time: **May 20 2016 15:08:19**
- UART: **115200 baud** on the tested module

Observed AT identification:

```text
AT

OK
AT+GMR

AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
OK
```

Espressif announced this AT release on 20 May 2016.

## Current project fingerprint

| Property | Observed / documented |
|---|---|
| Chip type | `ESP8285N08` |
| Features | Wi-Fi, 160 MHz, embedded Flash |
| Crystal | 26 MHz |
| Integrated Flash | 1 MB |
| Chip ID | `0x009f7c3c` |
| AP SSID pattern | `ESP_XXXXXX` on the tested modules |
| Tested SSID | `ESP_9F7C3C` |
| UART | 115200 baud on the tested module |
| AT startup test | `AT` -> `OK` |
| Version query | `AT+GMR` -> AT 1.1.0.0 / SDK 1.5.4 |
| Wi-Fi mode | SoftAP (`CWMODE=2`) |
| AP IPv4 | `192.168.4.1/24` |
| Station/base MAC | `7c:87:ce:9f:7c:3c` |
| SoftAP MAC | `7e:87:ce:9f:7c:3c` |
| DOIT-specific `AT+STASTATUS` | `ERROR` |
| DOIT-specific `AT+STAINFO` | `ERROR` |
| DOIT web UI at 192.168.4.1 | Not expected from this firmware family |
| Configuration | AT commands over UART |
| Transparent transport | Supported by the AT firmware, with constraints described in `commands.md` |

The failed DOIT-specific commands are useful negative fingerprints: they distinguish this firmware from DOIT Transparent Transmission Firmware V3.0.

## Files

- [`commands.md`](commands.md) - command inventory from the ESP8266 AT Instruction Set v1.5.4, examples, and safety classification.
- [`usage-options.md`](usage-options.md) - practical use/reflash options: current AT firmware, transparent TCP/UDP, DOIT V3 investigation, esp-link, later AT and custom firmware.
- [`com23-observation.md`](com23-observation.md) - the first identification session captured from the project hardware.
- [`com23-at-audit.md`](com23-at-audit.md) - human-readable safe AT command audit from the actual COM23 module.
- [`com23-at-audit.json`](com23-at-audit.json) - machine-readable copy of the same audit.
- [`com23-esptool-hardware.md`](com23-esptool-hardware.md) - actual esptool hardware/ROM/Flash identification results and private-backup hash.
- [`hardware-capture.md`](hardware-capture.md) - read-only hardware identification and private Flash-backup procedure.
- [`../../tools/at_command_audit.py`](../../tools/at_command_audit.py) - read-only/state-preserving command capability audit.

## Safe command audit

### Windows

```powershell
py tools\at_command_audit.py COM23 --baud 115200 --markdown com23-at-audit.md --json com23-at-audit.json
```

### Linux

```bash
python3 tools/at_command_audit.py /dev/ttyUSB0 --baud 115200 --markdown at-audit.md --json at-audit.json
```

The audit intentionally does **not** execute reset, restore, sleep, Wi-Fi join/leave, UART reconfiguration, Flash-writing commands, socket creation/closure, data transmission, WPS/SmartConfig, or OTA update commands.

## Private Flash backup

A complete read-only 1 MiB Flash image has been captured locally and fingerprinted by SHA-256. Keep raw images in the ignored `local-backups/` directory; do not publish them until inspected for credentials, saved access-point data, calibration/configuration records, and other device-specific state.

## Practical next step

See [`usage-options.md`](usage-options.md). The recommended first experiment is a **symmetric transparent UDP pair on the existing AT firmware**, before any erase/reflash operation. A known-good DOIT V3 module can then be characterized as a donor/reference for a separate compatibility study.

## Important version boundary

Do not use a modern ESP-AT command list as if every command existed in this 2016 firmware. Commands introduced in later NONOS/ESP-AT builds may return `ERROR`. The project uses the 2016 **ESP8266 AT Instruction Set v1.5.4** as the primary command reference for this module profile.

## Sources

- Espressif release announcement: `ESP8266_AT_v1.1 Release based on ESP8266_NONOS_SDK_V1.5.4`, 20 May 2016.
- Espressif `ESP8266 AT Instruction Set`, Version 1.5.4, May 2016.
- Current Espressif esptool documentation for ESP8266 ROM bootloader and read-only chip/flash operations.
- Current Espressif AT Command Set Comparison is useful only as a migration cross-check between old NONOS-AT and newer ESP-AT.
