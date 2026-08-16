# Command-line tools

The tools are cross-platform. Examples are explicitly marked for **Windows** and **Linux**.

## Install dependency

### Windows

```powershell
py -m pip install -r requirements.txt
```

### Linux

```bash
python3 -m pip install -r requirements.txt
```

`pyserial` is required for UART tools. `tcp_console.py`, `flash_layout_scan.py`, and `build_doit_transplant_image.py` use only the Python standard library.

## detect_module.py

Read-only firmware fingerprinting using UART identification/status commands and optional TCP-port probing.

### Windows

```powershell
py tools/detect_module.py COM3
py tools/detect_module.py COM3 --host 192.168.4.1
```

### Linux

```bash
python3 tools/detect_module.py /dev/ttyUSB0
python3 tools/detect_module.py /dev/ttyUSB0 --host 192.168.4.1
```

The default UART probe tries 115200 and 9600 baud. It recognizes the observed Espressif AT firmware from `AT+GMR` and DOIT V3-like firmware from `AT+STASTATUS` / `AT+STAINFO` responses. Network probing checks TCP ports 23, 80, and 9000.

## at_command_audit.py

Safe capability audit for the project's ESP8266 AT v1.1 / NONOS SDK 1.5.4 modules. It queries read-only/state-preserving command forms and can write both Markdown and JSON reports.

It deliberately does **not** execute factory reset, reboot, sleep, UART reconfiguration, Wi-Fi join/leave, Flash-writing commands, socket creation/closure, payload transmission, WPS/SmartConfig, or OTA update commands.

### Windows

```powershell
py tools/at_command_audit.py COM23 --baud 115200
py tools/at_command_audit.py COM23 --baud 115200 --markdown com23-at-audit.md --json com23-at-audit.json
```

### Linux

```bash
python3 tools/at_command_audit.py /dev/ttyUSB0 --baud 115200
python3 tools/at_command_audit.py /dev/ttyUSB0 --baud 115200 --markdown at-audit.md --json at-audit.json
```

An `ERROR_OR_STATE_DEPENDENT` result is intentionally not treated as proof that a command is absent: some commands only work in a particular Wi-Fi mode/state or do not provide a safe query form.

See [`../docs/esp8266-at-v1.1-sdk1.5.4/`](../docs/esp8266-at-v1.1-sdk1.5.4/) for the firmware-specific command inventory.

## flash_layout_scan.py

Offline, read-only structure scanner for raw ESP8266/ESP8285 Flash images. It does not require pyserial or esptool and does not modify the file.

It reports file size and SHA-256, a legacy `0xE9` image header when present, SPI mode/declared Flash size/frequency, load segments, checksum validation, non-erased 4 KiB sector runs, and selected AT/SDK marker offsets.

### Windows

```powershell
py tools\flash_layout_scan.py local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin
```

### Linux

```bash
python3 tools/flash_layout_scan.py local-backups/esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin
```

Use the same scanner on the DOIT V3-like donor and generated candidate images so their layouts can be compared using the same measurements.

## build_doit_transplant_image.py

Offline candidate-image builder for the characterized DOIT V3-like SW v3.2.1 firmware. It **never communicates with or writes to a device**.

The tool is intentionally conservative and specific to the captured donor SHA-256. It:

- validates donor size, hash and DOIT firmware markers;
- verifies the donor's RTOS SDK v1.5.0 RF init data;
- replaces the donor MAC copies in the DOIT application identity sector with the target MAC;
- erases donor RF calibration at `0xFB000`;
- preserves only the verified 128-byte generic Espressif RF init data at `0xFC000`;
- erases donor SDK parameter sectors `0xFD000-0xFFFFF`;
- verifies that donor MAC/suffix data no longer remains in the generated candidate.

Generated `.bin` files remain local/private and are covered by the repository's `*.bin` / `local-backups/` ignore policy.

### Windows — characterized donor to AT reference target

```powershell
$Donor = "local-backups\doit-v3-like-webui\esp8285n08_doit-v3-like_sw-v3.2.1_hd-v1.0_1MiB_chip-00c3b3b2_fullflash.bin"
$TargetBackup = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"
$Candidate = "local-backups\doit-v3-like-webui\esp8285n08_doit-v3-like_sw-v3.2.1_target-chip-009f7c3c_candidate.bin"

py tools\build_doit_transplant_image.py `
  $Donor `
  --target-backup $TargetBackup `
  --target-mac 7c:87:ce:9f:7c:3c `
  --output $Candidate
```

For the exact donor and target characterized in this repository, the expected candidate hash is:

```text
C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
```

See [`../docs/doit-v3-like-webui/transplant-plan.md`](../docs/doit-v3-like-webui/transplant-plan.md) before any device write experiment.

## serial_console.py

Interactive serial terminal. Text mode appends CRLF by default; hexadecimal input/output is available for binary protocols.

### Windows

```powershell
py tools/serial_console.py COM3 --baud 115200
py tools/serial_console.py COM3 --baud 9600 --hex-input --hex-output --eol none
```

### Linux

```bash
python3 tools/serial_console.py /dev/ttyUSB0 --baud 115200
python3 tools/serial_console.py /dev/ttyUSB0 --baud 9600 --hex-input --hex-output --eol none
```

## tcp_console.py

Interactive TCP client for a module configured as a transparent TCP server.

### Windows

```powershell
py tools/tcp_console.py 192.168.4.1 9000
```

### Linux

```bash
python3 tools/tcp_console.py 192.168.4.1 9000
```

Use `--hex-input --hex-output --eol none` for binary protocols.

## uart_loopback_test.py

Byte-integrity test. For a local test, connect TX to RX. For a complete wireless-link test, place the TX/RX loopback jumper at the remote UART endpoint.

### Windows

```powershell
py tools/uart_loopback_test.py COM3 --baud 115200 --count 1000 --size 64
```

### Linux

```bash
python3 tools/uart_loopback_test.py /dev/ttyUSB0 --baud 115200 --count 1000 --size 64
```

A non-zero exit status indicates at least one timeout or data mismatch.

## latency_test.py

Measures round-trip time through an echo path and reports min/average/p50/p95/max plus jitter.

### Serial — Windows

```powershell
py tools/latency_test.py --serial COM3 --baud 115200 --count 100
```

### Serial — Linux

```bash
python3 tools/latency_test.py --serial /dev/ttyUSB0 --baud 115200 --count 100
```

### TCP — Windows

```powershell
py tools/latency_test.py --tcp 192.168.4.1:9000 --count 100
```

### TCP — Linux

```bash
python3 tools/latency_test.py --tcp 192.168.4.1:9000 --count 100
```

The far endpoint must echo the exact bytes. For end-to-end UART-over-Wi-Fi measurement, the simplest fixture is a TX-to-RX jumper on the far UART module.
