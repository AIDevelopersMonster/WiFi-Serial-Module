#!/usr/bin/env python3
"""Verify byte-perfect UART or transparent-link loopback operation.

For a local test, connect TX to RX. For an end-to-end Wi-Fi test, loop TX to RX
at the remote UART endpoint and run this tool at the local serial endpoint.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

try:
    import serial
except ImportError as exc:
    raise SystemExit("pyserial is required: python -m pip install pyserial") from exc

from common import format_hex


def read_exact(ser: serial.Serial, size: int, deadline: float) -> bytes:
    data = bytearray()
    while len(data) < size and time.monotonic() < deadline:
        chunk = ser.read(size - len(data))
        if chunk:
            data.extend(chunk)
    return bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="UART loopback integrity test for Windows and Linux.")
    parser.add_argument("port", help="Windows COM3 or Linux /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--size", type=int, default=32, help="Bytes per test packet")
    parser.add_argument("--timeout", type=float, default=1.0, help="Echo timeout per packet")
    parser.add_argument("--interval", type=float, default=0.01)
    args = parser.parse_args()
    if args.count <= 0 or args.size <= 0:
        parser.error("--count and --size must be positive")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.05, write_timeout=args.timeout)
    except serial.SerialException as exc:
        print(f"Unable to open {args.port}: {exc}", file=sys.stderr)
        return 2
    passed = failed = total_bytes = 0
    started = time.monotonic()
    try:
        ser.reset_input_buffer()
        for index in range(1, args.count + 1):
            payload = (index.to_bytes(4, "big") + os.urandom(max(0, args.size - 4)))[: args.size]
            ser.reset_input_buffer()
            ser.write(payload)
            ser.flush()
            received = read_exact(ser, len(payload), time.monotonic() + args.timeout)
            total_bytes += len(payload)
            if received == payload:
                passed += 1
            else:
                failed += 1
                print(f"FAIL #{index}: expected {format_hex(payload)}", file=sys.stderr)
                print(f"          got {format_hex(received)}", file=sys.stderr)
            if args.interval:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        ser.close()
    elapsed = max(time.monotonic() - started, 1e-9)
    print(f"Packets: {passed + failed}; passed: {passed}; failed: {failed}")
    print(f"Payload bytes sent: {total_bytes}; elapsed: {elapsed:.3f} s")
    print(f"Application payload rate: {total_bytes / elapsed:.1f} B/s")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
