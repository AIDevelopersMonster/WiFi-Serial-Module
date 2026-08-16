#!/usr/bin/env python3
"""Interactive TCP console for a transparent Wi-Fi serial endpoint."""

from __future__ import annotations

import argparse
import socket
import sys
import threading

from common import format_hex, parse_hex_bytes


def reader(sock: socket.socket, stop: threading.Event, hex_output: bool) -> None:
    while not stop.is_set():
        try:
            data = sock.recv(4096)
        except socket.timeout:
            continue
        except OSError:
            stop.set()
            return
        if not data:
            print("\n[remote closed connection]", file=sys.stderr)
            stop.set()
            return
        if hex_output:
            print(f"RX: {format_hex(data)}", flush=True)
        else:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive TCP console for Wi-Fi serial modules.")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--connect-timeout", type=float, default=5.0)
    parser.add_argument("--eol", choices=["none", "cr", "lf", "crlf"], default="crlf")
    parser.add_argument("--hex-input", action="store_true")
    parser.add_argument("--hex-output", action="store_true")
    args = parser.parse_args()
    eol = {"none": b"", "cr": b"\r", "lf": b"\n", "crlf": b"\r\n"}[args.eol]
    try:
        sock = socket.create_connection((args.host, args.port), timeout=args.connect_timeout)
    except OSError as exc:
        print(f"Connection failed: {exc}", file=sys.stderr)
        return 2
    sock.settimeout(0.25)
    stop = threading.Event()
    threading.Thread(target=reader, args=(sock, stop, args.hex_output), daemon=True).start()
    print(f"Connected to {args.host}:{args.port}. Ctrl+C or Ctrl+Z/Ctrl+D to exit.")
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
            try:
                sock.sendall(payload)
            except OSError as exc:
                print(f"Send failed: {exc}", file=sys.stderr)
                break
            if args.hex_input:
                print(f"TX: {format_hex(payload)}")
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
