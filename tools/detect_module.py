#!/usr/bin/env python3
"""Identify common ESP8285/ESP8266 Wi-Fi serial module firmware families.

Works on Windows (for example COM3) and Linux (for example /dev/ttyUSB0).
The UART probe is read-only: it sends identification/status commands only.
"""

from __future__ import annotations

import argparse
import socket
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import serial
except ImportError as exc:
    raise SystemExit("pyserial is required: python -m pip install pyserial") from exc


@dataclass
class ProbeResult:
    baud: int
    responses: dict[str, str] = field(default_factory=dict)


def read_until_quiet(ser: serial.Serial, first_wait: float = 0.25, quiet: float = 0.12) -> bytes:
    time.sleep(first_wait)
    data = bytearray()
    last_rx = time.monotonic()
    while True:
        waiting = ser.in_waiting
        if waiting:
            data.extend(ser.read(waiting))
            last_rx = time.monotonic()
        elif time.monotonic() - last_rx >= quiet:
            break
        time.sleep(0.01)
    return bytes(data)


def uart_probe(port: str, baud: int, timeout: float) -> ProbeResult:
    result = ProbeResult(baud=baud)
    commands = ["AT", "AT+GMR", "AT+STASTATUS", "AT+STAINFO"]
    with serial.Serial(port=port, baudrate=baud, timeout=timeout, write_timeout=timeout) as ser:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        for command in commands:
            ser.reset_input_buffer()
            ser.write((command + "\r\n").encode("ascii"))
            ser.flush()
            raw = read_until_quiet(ser)
            result.responses[command] = raw.decode("utf-8", errors="replace").strip()
    return result


def classify_uart(results: list[ProbeResult]) -> tuple[str, Optional[ProbeResult]]:
    for result in results:
        gmr = result.responses.get("AT+GMR", "")
        if "AT version:" in gmr or "SDK version:" in gmr:
            return "Espressif AT firmware", result
    for result in results:
        status = result.responses.get("AT+STASTATUS", "")
        info = result.responses.get("AT+STAINFO", "")
        if "STA:OK" in status or "STA:DOWN" in status or ("|" in info and "AT+STAINFO" not in info):
            return "DOIT DT-06 Transparent Transmission firmware (V3-like)", result
    return "Unknown from UART probe", None


def port_open(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def http_probe(host: str, timeout: float) -> str:
    try:
        with socket.create_connection((host, 80), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(b"GET / HTTP/1.0\r\n" + f"Host: {host}\r\n".encode("ascii") + b"Connection: close\r\n\r\n")
            chunks = []
            while True:
                try:
                    chunk = sock.recv(4096)
                except socket.timeout:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
                if sum(map(len, chunks)) >= 16384:
                    break
            return b"".join(chunks).decode("utf-8", errors="replace")
    except OSError:
        return ""


def classify_network(host: str, timeout: float) -> tuple[str, dict[int, bool], str]:
    ports = {port: port_open(host, port, timeout) for port in (23, 80, 9000)}
    page = http_probe(host, timeout) if ports[80] else ""
    lower = page.lower()
    if "esp-link" in lower or "jeelabs" in lower:
        name = "JeeLabs esp-link"
    elif ports[80] and ports[9000]:
        name = "DOIT-style web firmware (network fingerprint only)"
    elif ports[23] and ports[80]:
        name = "Possible esp-link (network fingerprint only)"
    elif any(ports.values()):
        name = "Unknown network firmware"
    else:
        name = "No tested TCP services responded"
    return name, ports, page


def main() -> int:
    parser = argparse.ArgumentParser(description="Identify DOIT V3, Espressif AT, or esp-link-like Wi-Fi serial module firmware.")
    parser.add_argument("port", nargs="?", help="Serial port: Windows COM3, Linux /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, action="append", dest="bauds", help="Baud to probe; repeatable")
    parser.add_argument("--host", help="Optional module IP for network fingerprinting, e.g. 192.168.4.1")
    parser.add_argument("--timeout", type=float, default=0.6, help="I/O timeout in seconds (default: 0.6)")
    args = parser.parse_args()
    if not args.port and not args.host:
        parser.error("provide a serial port, --host, or both")
    if args.port:
        bauds = args.bauds or [115200, 9600]
        results: list[ProbeResult] = []
        print(f"Serial probe: {args.port}")
        for baud in bauds:
            try:
                result = uart_probe(args.port, baud, args.timeout)
            except (serial.SerialException, OSError) as exc:
                print(f"  {baud}: ERROR: {exc}")
                continue
            results.append(result)
            print(f"  {baud} baud:")
            for command, response in result.responses.items():
                compact = response.replace("\r", "\\r").replace("\n", " | ")
                print(f"    {command:<14} -> {compact or '<no response>'}")
        name, matched = classify_uart(results)
        print(f"UART classification: {name}")
        if matched:
            print(f"Matched at: {matched.baud} baud")
    if args.host:
        name, ports, _ = classify_network(args.host, args.timeout)
        print(f"Network probe: {args.host}")
        for port, opened in ports.items():
            print(f"  TCP/{port}: {'open' if opened else 'closed/no response'}")
        print(f"Network classification: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
