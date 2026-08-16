#!/usr/bin/env python3
"""Measure round-trip latency through a serial or TCP transparent link.

The far endpoint must echo every byte unchanged. This can be a TX/RX jumper at
remote UART or an echo service at the remote TCP endpoint.
"""

from __future__ import annotations

import argparse
import os
import socket
import statistics
import sys
import time
from typing import Protocol

try:
    import serial
except ImportError as exc:
    raise SystemExit("pyserial is required: python -m pip install pyserial") from exc

from common import percentile


class EchoTransport(Protocol):
    def flush_input(self) -> None: ...
    def exchange(self, payload: bytes, timeout: float) -> bytes: ...
    def close(self) -> None: ...


class SerialEcho:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=0.02, write_timeout=1.0)
    def flush_input(self) -> None:
        self.ser.reset_input_buffer()
    def exchange(self, payload: bytes, timeout: float) -> bytes:
        self.ser.write(payload)
        self.ser.flush()
        deadline = time.monotonic() + timeout
        data = bytearray()
        while len(data) < len(payload) and time.monotonic() < deadline:
            chunk = self.ser.read(len(payload) - len(data))
            if chunk:
                data.extend(chunk)
        return bytes(data)
    def close(self) -> None:
        self.ser.close()


class TcpEcho:
    def __init__(self, host: str, port: int, timeout: float):
        self.sock = socket.create_connection((host, port), timeout=timeout)
    def flush_input(self) -> None:
        self.sock.setblocking(False)
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
        except BlockingIOError:
            pass
        finally:
            self.sock.setblocking(True)
    def exchange(self, payload: bytes, timeout: float) -> bytes:
        self.sock.settimeout(timeout)
        self.sock.sendall(payload)
        data = bytearray()
        while len(data) < len(payload):
            try:
                chunk = self.sock.recv(len(payload) - len(data))
            except socket.timeout:
                break
            if not chunk:
                break
            data.extend(chunk)
        return bytes(data)
    def close(self) -> None:
        self.sock.close()


def parse_target(value: str) -> tuple[str, int]:
    host, sep, port_text = value.rpartition(":")
    if not sep or not host:
        raise argparse.ArgumentTypeError("TCP target must be HOST:PORT")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("TCP port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("TCP port must be 1..65535")
    return host, port


def main() -> int:
    parser = argparse.ArgumentParser(description="Round-trip latency test for transparent serial links.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--serial", dest="serial_port", help="Windows COM3 or Linux /dev/ttyUSB0")
    target.add_argument("--tcp", type=parse_target, metavar="HOST:PORT")
    parser.add_argument("--baud", type=int, default=115200, help="Used with --serial")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--size", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--interval", type=float, default=0.05)
    args = parser.parse_args()
    if args.count <= 0 or args.size <= 0:
        parser.error("--count and --size must be positive")
    try:
        if args.serial_port:
            transport: EchoTransport = SerialEcho(args.serial_port, args.baud)
            label = f"serial {args.serial_port} @ {args.baud}"
        else:
            host, port = args.tcp
            transport = TcpEcho(host, port, args.timeout)
            label = f"tcp {host}:{port}"
    except (serial.SerialException, OSError) as exc:
        print(f"Unable to open transport: {exc}", file=sys.stderr)
        return 2
    samples_ms: list[float] = []
    lost = 0
    print(f"Testing {label}; {args.count} probes, {args.size} bytes each")
    try:
        for index in range(1, args.count + 1):
            payload = (index.to_bytes(4, "big") + os.urandom(max(0, args.size - 4)))[: args.size]
            transport.flush_input()
            started = time.perf_counter()
            received = transport.exchange(payload, args.timeout)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            if received == payload:
                samples_ms.append(elapsed_ms)
                print(f"#{index:04d} {elapsed_ms:8.3f} ms")
            else:
                lost += 1
                print(f"#{index:04d} timeout/mismatch", file=sys.stderr)
            if args.interval:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        transport.close()
    total = len(samples_ms) + lost
    print()
    print(f"Received: {len(samples_ms)}/{total}; lost/mismatched: {lost}")
    if not samples_ms:
        return 1
    mean = statistics.fmean(samples_ms)
    stdev = statistics.pstdev(samples_ms) if len(samples_ms) > 1 else 0.0
    print(f"RTT min/avg/p50/p95/max: {min(samples_ms):.3f} / {mean:.3f} / {percentile(samples_ms, 50):.3f} / {percentile(samples_ms, 95):.3f} / {max(samples_ms):.3f} ms")
    print(f"RTT jitter (population stdev): {stdev:.3f} ms")
    return 0 if lost == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
