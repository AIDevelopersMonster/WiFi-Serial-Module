#!/usr/bin/env python3
"""Verify that a 1 MiB backup still contains the characterized AT 1.1 firmware payload.

The full Flash SHA may change when ESP8266/ESP8285 mutable configuration/system
sectors change. This verifier therefore checks both the complete image hash and
a stronger invariant firmware fingerprint over 0x000000-0x06FFFF.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

FLASH_SIZE = 0x100000
FIRMWARE_END = 0x70000
BOOT_END = 0x10000

KNOWN_FULL_SHA256 = "8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9"
KNOWN_FIRMWARE_SHA256 = "F5097F840622D7C735FFF76AC971EF8D3EBEFFCE2FB34FB780F84015EB55C194"
KNOWN_BOOT64K_SHA256 = "63C501659D935AE0E9D5B487CC9566DB1D0B344B17DC0966898B3E887E34D60C"
KNOWN_MAIN_SHA256 = "972BD88D873CDF258D340196C6200BE131327733CBD1E0D30255FCD5B9C21799"
REQUIRED_MARKERS = (
    b"AT version:",
    b"SDK version:",
    b"+CIPSTART",
    b"+SAVETRANSLINK",
    b"+CWMODE_CUR",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()

    data = args.image.read_bytes()
    if len(data) != FLASH_SIZE:
        print(f"FAIL: expected 1048576 bytes, got {len(data)}")
        return 2

    full = sha256(data)
    boot = sha256(data[:BOOT_END])
    main = sha256(data[BOOT_END:FIRMWARE_END])
    firmware = sha256(data[:FIRMWARE_END])
    missing = [m.decode("ascii") for m in REQUIRED_MARKERS if m not in data[:FIRMWARE_END]]

    print(f"File: {args.image}")
    print(f"Full SHA256:     {full}")
    print(f"Boot 0-0xFFFF:   {boot}")
    print(f"Main 0x10000-0x6FFFF: {main}")
    print(f"Firmware 0-0x6FFFF:  {firmware}")
    print(f"Full reference match:     {full == KNOWN_FULL_SHA256}")
    print(f"Firmware payload match:   {firmware == KNOWN_FIRMWARE_SHA256}")
    print(f"Boot region match:        {boot == KNOWN_BOOT64K_SHA256}")
    print(f"Main region match:        {main == KNOWN_MAIN_SHA256}")
    print(f"Required markers present: {not missing}")
    if missing:
        print("Missing markers: " + ", ".join(missing))

    if firmware == KNOWN_FIRMWARE_SHA256 and not missing:
        if full == KNOWN_FULL_SHA256:
            print("RESULT: EXACT_REFERENCE")
        else:
            print("RESULT: SAME_AT_FIRMWARE_MUTABLE_STATE_DIFFERS")
        return 0

    print("RESULT: NOT_VERIFIED_AT_REFERENCE")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
