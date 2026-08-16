#!/usr/bin/env python3
"""Simple cross-platform interactive serial console.

Windows example: py tools/serial_console.py COM3 --baud 115200
Linux example:   python3 tools/serial_console.py /dev/ttyUSB0 --baud 115200
"""

from __future__ import annotations

import argparse
import sys
import threading

try:
    import serial
except ImportError as exc:
    raise SystemExit("pyserial is required: python -m pip install pyserial") from exc

from common import format_hex, parse_hex_bytes


def reader(ser: serial.Serial, stop: threading.Event, hex_output: bool) -> None:
    while not stop.is_set():
        try:
            data = ser.read(ser.in_waiting or 1)
        except serial.SerialException:
            stop.set()
            return
        if not data:
            continue
        if hex_output:
            print(f"RX: {format_hex(data)}", flush=True)
        else:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive UART console for Windows and Linux.")
    parser.add_argument("port", help="Windows COM3 or Linux /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=0.1)
    parser.add_argument("--eol", choices=["none", "cr", "lf", "crlf"], default="crlf")
    parser.add_argument("--hex-input", action="store_true", help="Interpret each entered line as hexadecimal bytes")
    parser.add_argument("--hex-output", action="store_true", help="Print received bytes as hexadecimal")
    args = parser.parse_args()
    eol = {"none": b"", "cr": b"\r", "lf": b"\n", "crlf": b"\r\n"}[args.eol]
    try:
        ser = serial.Serial(args.port, args.baud, timeout=args.timeout, write_timeout=1.0)
    except serial.SerialException as exc:
        print(f"Unable to open {args.port}: {exc}", file=sys.stderr)
        return 2
    stop = threading.Event()
    threading.Thread(target=reader, args=(ser, stop, args.hex_output), daemon=True).start()
    print(f"Connected to {args.port} at {args.baud} baud. Ctrl+C or Ctrl+Z/Ctrl+D to exit.")
    try:
        while not stop.is_set():
            try:
                line = input()
            except EOFError:
                break
            try:
                payload = parse_hex_bytes(line) if args.hex_input else line.encode("utf-8") + eol
            except ValueError as exc:
                print(f"Input error: {exc}", file=sys.stderr)
                continue
            ser.write(payload)
            ser.flush()
            if args.hex_input:
                print(f"TX: {format_hex(payload)}")
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        ser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
