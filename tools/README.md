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

`pyserial` is required for UART tools. `tcp_console.py` uses only the Python standard library.

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
