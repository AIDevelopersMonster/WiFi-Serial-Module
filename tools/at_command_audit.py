#!/usr/bin/env python3
"""Safe capability audit for ESP8266 NONOS AT firmware around v1.1 / SDK 1.5.4.

The default probe intentionally avoids commands that reset the module, write
configuration to flash, change UART settings, join/leave networks, enter sleep,
start WPS/SmartConfig, open/close sockets, send data, or perform OTA updates.

Windows example:
    py tools/at_command_audit.py COM23 --baud 115200 --markdown report.md --json report.json

Linux example:
    python3 tools/at_command_audit.py /dev/ttyUSB0 --baud 115200 --markdown report.md --json report.json
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import serial
except ImportError as exc:
    raise SystemExit("pyserial is required: py -m pip install pyserial") from exc


@dataclass(frozen=True)
class Probe:
    name: str
    command: str
    group: str
    note: str


SAFE_PROBES = [
    Probe("AT", "AT", "basic", "startup test"),
    Probe("GMR", "AT+GMR", "basic", "firmware/SDK version"),
    Probe("UART_CUR", "AT+UART_CUR?", "basic", "current UART configuration"),
    Probe("UART_DEF", "AT+UART_DEF?", "basic", "default UART configuration"),
    Probe("SLEEP", "AT+SLEEP?", "basic", "current sleep mode"),
    Probe("RFPOWER", "AT+RFPOWER?", "basic", "RF power query if supported by build"),
    Probe("CWMODE_CUR", "AT+CWMODE_CUR?", "wifi", "current Wi-Fi mode"),
    Probe("CWMODE_DEF", "AT+CWMODE_DEF?", "wifi", "default Wi-Fi mode"),
    Probe("CWJAP_CUR", "AT+CWJAP_CUR?", "wifi", "current associated AP"),
    Probe("CWJAP_DEF", "AT+CWJAP_DEF?", "wifi", "saved associated AP"),
    Probe("CWLAPOPT", "AT+CWLAPOPT?", "wifi", "scan output configuration; may be unsupported as query"),
    Probe("CWLIF", "AT+CWLIF", "wifi", "stations connected to softAP; mode-dependent"),
    Probe("CWSAP_CUR", "AT+CWSAP_CUR?", "wifi", "current softAP configuration"),
    Probe("CWSAP_DEF", "AT+CWSAP_DEF?", "wifi", "default softAP configuration"),
    Probe("CWDHCP_CUR", "AT+CWDHCP_CUR?", "wifi", "current DHCP configuration"),
    Probe("CWDHCP_DEF", "AT+CWDHCP_DEF?", "wifi", "default DHCP configuration"),
    Probe("CWDHCPS_CUR", "AT+CWDHCPS_CUR?", "wifi", "current softAP DHCP range"),
    Probe("CWDHCPS_DEF", "AT+CWDHCPS_DEF?", "wifi", "saved softAP DHCP range"),
    Probe("CIPSTAMAC_CUR", "AT+CIPSTAMAC_CUR?", "wifi", "current station MAC"),
    Probe("CIPSTAMAC_DEF", "AT+CIPSTAMAC_DEF?", "wifi", "default station MAC"),
    Probe("CIPAPMAC_CUR", "AT+CIPAPMAC_CUR?", "wifi", "current softAP MAC"),
    Probe("CIPAPMAC_DEF", "AT+CIPAPMAC_DEF?", "wifi", "default softAP MAC"),
    Probe("CIPSTA_CUR", "AT+CIPSTA_CUR?", "wifi", "current station IP/gateway/netmask"),
    Probe("CIPSTA_DEF", "AT+CIPSTA_DEF?", "wifi", "saved station IP/gateway/netmask"),
    Probe("CIPAP_CUR", "AT+CIPAP_CUR?", "wifi", "current softAP IP/gateway/netmask"),
    Probe("CIPAP_DEF", "AT+CIPAP_DEF?", "wifi", "saved softAP IP/gateway/netmask"),
    Probe("CIPSTATUS", "AT+CIPSTATUS", "tcpip", "network connection status"),
    Probe("CIFSR", "AT+CIFSR", "tcpip", "local IP and MAC information"),
    Probe("CIPMUX", "AT+CIPMUX?", "tcpip", "single/multiple connection mode"),
    Probe("CIPMODE", "AT+CIPMODE?", "tcpip", "normal/transparent transmission mode"),
    Probe("CIPSTO", "AT+CIPSTO?", "tcpip", "TCP server timeout; state-dependent"),
    Probe("CIPDINFO", "AT+CIPDINFO?", "tcpip", "whether +IPD includes remote IP/port"),
]

NOT_AUTO_EXECUTED = [
    "AT+RST", "AT+GSLP", "ATE0/ATE1", "AT+RESTORE", "AT+UART", "AT+UART_DEF(set)",
    "AT+SLEEP(set)", "AT+RFPOWER(set)", "AT+RFVDD", "AT+CWMODE", "AT+CWMODE_CUR(set)",
    "AT+CWMODE_DEF(set)", "AT+CWJAP", "AT+CWJAP_CUR(set)", "AT+CWJAP_DEF(set)",
    "AT+CWLAPOPT(set)", "AT+CWLAP", "AT+CWQAP", "AT+CWSAP", "AT+CWSAP_CUR(set)",
    "AT+CWSAP_DEF(set)", "AT+CWDHCP", "AT+CWDHCP_CUR(set)", "AT+CWDHCP_DEF(set)",
    "AT+CWDHCPS_CUR(set)", "AT+CWDHCPS_DEF(set)", "AT+CWAUTOCONN(set)",
    "AT+CIPSTAMAC", "AT+CIPSTAMAC_CUR(set)", "AT+CIPSTAMAC_DEF(set)", "AT+CIPAPMAC",
    "AT+CIPAPMAC_CUR(set)", "AT+CIPAPMAC_DEF(set)", "AT+CIPSTA", "AT+CIPSTA_CUR(set)",
    "AT+CIPSTA_DEF(set)", "AT+CIPAP", "AT+CIPAP_CUR(set)", "AT+CIPAP_DEF(set)",
    "AT+CWSTARTSMART", "AT+CWSTOPSMART", "AT+CWSTARTDISCOVER", "AT+CWSTOPDISCOVER",
    "AT+WPS", "AT+MDNS", "AT+CIPDOMAIN", "AT+CIPSTART", "AT+CIPSSLSIZE", "AT+CIPSEND",
    "AT+CIPSENDEX", "AT+CIPSENDBUF", "AT+CIPBUFSTATUS", "AT+CIPCHECKSEQ", "AT+CIPBUFRESET",
    "AT+CIPCLOSE", "AT+CIPMUX(set)", "AT+CIPSERVER", "AT+CIPMODE(set)",
    "AT+SAVETRANSLINK", "AT+CIPSTO(set)", "AT+PING", "AT+CIUPDATE", "AT+CIPDINFO(set)",
]


@dataclass
class Result:
    name: str
    command: str
    group: str
    status: str
    response: str
    note: str


def read_until_quiet(ser: serial.Serial, first_wait: float, quiet: float, max_wait: float) -> bytes:
    start = time.monotonic()
    last_rx = start
    data = bytearray()
    time.sleep(first_wait)
    while time.monotonic() - start < max_wait:
        waiting = ser.in_waiting
        if waiting:
            data.extend(ser.read(waiting))
            last_rx = time.monotonic()
        elif data and time.monotonic() - last_rx >= quiet:
            break
        time.sleep(0.01)
    return bytes(data)


def clean_response(raw: bytes, command: str) -> str:
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines and lines[0] == command:
        lines = lines[1:]
    return "\n".join(lines)


def classify(response: str) -> str:
    upper = response.upper()
    if not response:
        return "NO_RESPONSE"
    if "ERROR" in upper or "FAIL" in upper:
        return "ERROR_OR_STATE_DEPENDENT"
    if "OK" in upper or response.startswith("+") or response.startswith("STATUS:"):
        return "SUPPORTED"
    return "RESPONSE_RECEIVED"


def run_probe(ser: serial.Serial, probe: Probe, first_wait: float, quiet: float, max_wait: float) -> Result:
    ser.reset_input_buffer()
    ser.write((probe.command + "\r\n").encode("ascii"))
    ser.flush()
    raw = read_until_quiet(ser, first_wait, quiet, max_wait)
    response = clean_response(raw, probe.command)
    return Result(probe.name, probe.command, probe.group, classify(response), response, probe.note)


def render_markdown(port: str, baud: int, results: list[Result]) -> str:
    lines = [
        "# ESP8266 AT safe command audit",
        "",
        f"- Port: `{port}`",
        f"- Baud: `{baud}`",
        "- Probe policy: read-only/state-preserving commands only",
        "",
        "`ERROR_OR_STATE_DEPENDENT` does not necessarily mean that a command is absent. Some commands require a particular Wi-Fi mode/state or do not implement a safe query form.",
        "",
        "| Group | Command | Result | Response |",
        "|---|---|---|---|",
    ]
    for item in results:
        response = item.response.replace("|", "\\|").replace("\n", "<br>") or "-"
        lines.append(f"| {item.group} | `{item.command}` | {item.status} | {response} |")
    lines.extend(["", "## Documented commands intentionally not auto-executed", ""])
    lines.extend(f"- `{name}`" for name in NOT_AUTO_EXECUTED)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely audit ESP8266 NONOS AT v1.5.4-era command capabilities.")
    parser.add_argument("port", help="Serial port, e.g. COM23 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=0.5, help="serial read/write timeout")
    parser.add_argument("--first-wait", type=float, default=0.15)
    parser.add_argument("--quiet", type=float, default=0.10)
    parser.add_argument("--max-wait", type=float, default=1.2)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", dest="markdown_path", type=Path)
    args = parser.parse_args()

    results: list[Result] = []
    try:
        with serial.Serial(args.port, args.baud, timeout=args.timeout, write_timeout=args.timeout) as ser:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            for probe in SAFE_PROBES:
                result = run_probe(ser, probe, args.first_wait, args.quiet, args.max_wait)
                results.append(result)
                compact = result.response.replace("\n", " | ") or "<no response>"
                print(f"{probe.command:<22} {result.status:<24} {compact}")
    except (serial.SerialException, OSError) as exc:
        raise SystemExit(f"serial error: {exc}") from exc

    supported = sum(item.status == "SUPPORTED" for item in results)
    print(f"\nSupported/readable: {supported}/{len(results)} safe probes")
    print("Note: ERROR can be mode/state-dependent and is not automatically classified as 'command absent'.")

    payload = {
        "port": args.port,
        "baud": args.baud,
        "probe_policy": "read-only/state-preserving",
        "results": [asdict(item) for item in results],
        "not_auto_executed": NOT_AUTO_EXECUTED,
    }
    if args.json_path:
        args.json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"JSON: {args.json_path}")
    if args.markdown_path:
        args.markdown_path.write_text(render_markdown(args.port, args.baud, results), encoding="utf-8")
        print(f"Markdown: {args.markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
