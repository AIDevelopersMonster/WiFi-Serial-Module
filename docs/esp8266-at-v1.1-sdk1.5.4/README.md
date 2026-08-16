# ESP8266 AT v1.1 / NONOS SDK 1.5.4 module profile

This folder documents the `ESP_XXXXXX` Wi-Fi serial modules observed in this project that answer standard Espressif AT commands at 115200 baud.

## Identified firmware

Observed on project hardware (Windows `COM23`):

```text
AT

OK
AT+GMR

AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
OK
```

This identifies the firmware generation as **Espressif ESP8266 AT v1.1 based on ESP8266 NONOS SDK v1.5.4**.

Espressif announced this release on 20 May 2016. The release notes mention optimization of Flash writes and DHCP server behavior, and an update to `AT+SAVETRANSLINK` so that a domain name can be saved.

## Current project fingerprint

| Property | Observed / documented |
|---|---|
| AP SSID pattern | `ESP_XXXXXX` on the tested modules |
| Tested SSID | `ESP_9F7C3C` |
| UART | 115200 baud on the tested module |
| AT startup test | `AT` -> `OK` |
| Version query | `AT+GMR` -> AT 1.1.0.0 / SDK 1.5.4 |
| Wi-Fi mode | SoftAP (`CWMODE=2`) |
| AP IPv4 | `192.168.4.1/24` |
| Station MAC | `7c:87:ce:9f:7c:3c` |
| SoftAP MAC | `7e:87:ce:9f:7c:3c` |
| DOIT-specific `AT+STASTATUS` | `ERROR` |
| DOIT-specific `AT+STAINFO` | `ERROR` |
| DOIT web UI at 192.168.4.1 | Not expected from this firmware family |
| Configuration | AT commands over UART |
| Transparent transport | Supported by the AT firmware, with constraints described in `commands.md` |

The failed DOIT-specific commands are useful negative fingerprints: they distinguish this firmware from DOIT Transparent Transmission Firmware V3.0.

## Files

- [`commands.md`](commands.md) - command inventory from the ESP8266 AT Instruction Set v1.5.4, examples, and safety classification.
- [`com23-observation.md`](com23-observation.md) - the first identification session captured from the project hardware.
- [`com23-at-audit.md`](com23-at-audit.md) - human-readable safe AT command audit from the actual COM23 module.
- [`com23-at-audit.json`](com23-at-audit.json) - machine-readable copy of the same audit.
- [`hardware-capture.md`](hardware-capture.md) - next step: SoC/chip ID, MAC, SPI flash identification and private full-flash backup using Espressif esptool.
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

## Next hardware characterization step

AT commands have identified the firmware family but not the exact SoC/flash implementation. The next read-only stage uses Espressif `esptool` in ROM download mode:

```powershell
py -m esptool --port COM23 chip-id
py -m esptool --port COM23 read-mac
py -m esptool --port COM23 flash-id
```

See [`hardware-capture.md`](hardware-capture.md) before running these commands. A complete flash backup can also be read without erasing the module, but the raw binary should remain private until checked for saved credentials and configuration.

## Important version boundary

Do not use a modern ESP-AT command list as if every command existed in this 2016 firmware. For example, commands introduced in later NONOS/ESP-AT builds may return `ERROR`. The project uses the 2016 **ESP8266 AT Instruction Set v1.5.4** as the primary command reference for this module profile.

## Sources

- Espressif release announcement: `ESP8266_AT_v1.1 Release based on ESP8266_NONOS_SDK_V1.5.4`, 20 May 2016.
- Espressif `ESP8266 AT Instruction Set`, Version 1.5.4, May 2016.
- Current Espressif esptool documentation for ESP8266 ROM bootloader and read-only chip/flash operations.
- Current Espressif AT Command Set Comparison is useful only as a migration cross-check between old NONOS-AT and newer ESP-AT.
