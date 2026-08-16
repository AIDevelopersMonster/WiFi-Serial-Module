#!/usr/bin/env python3
"""Compare a sanitized DOIT candidate with a post-first-boot 1 MiB flash dump.

The tool is read-only. It reports exact byte/sector differences and checks
whether all changes are confined to the ESP8266 RTOS SDK tail area
0xFB000-0xFFFFF (RF calibration, RF init, and SDK parameters).
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

FLASH_SIZE = 0x100000
SECTOR_SIZE = 0x1000
SDK_TAIL_START = 0xFB000

REGIONS = (
    ("boot/load image", 0x000000, 0x010000),
    ("DOIT identity/config", 0x01D000, 0x01F000),
    ("flash-mapped application", 0x020000, 0x069000),
    ("RF calibration", 0x0FB000, 0x0FC000),
    ("RF init", 0x0FC000, 0x0FD000),
    ("SDK parameters", 0x0FD000, 0x100000),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def count_diffs(a: bytes, b: bytes, start: int, end: int) -> int:
    return sum(x != y for x, y in zip(a[start:end], b[start:end]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("postboot", type=Path)
    args = parser.parse_args()

    candidate = args.candidate.read_bytes()
    postboot = args.postboot.read_bytes()

    for path, data in ((args.candidate, candidate), (args.postboot, postboot)):
        if len(data) != FLASH_SIZE:
            print(f"FAIL: {path} is {len(data)} bytes, expected {FLASH_SIZE}")
            return 2

    print(f"Candidate: {args.candidate}")
    print(f"Candidate SHA256: {sha256(candidate)}")
    print(f"Post-boot: {args.postboot}")
    print(f"Post-boot SHA256: {sha256(postboot)}")

    differing_offsets = [i for i, (a, b) in enumerate(zip(candidate, postboot)) if a != b]
    print(f"\nTotal differing bytes: {len(differing_offsets)}")

    if not differing_offsets:
        print("RESULT: EXACTLY_IDENTICAL")
        return 0

    print(f"First differing offset: 0x{differing_offsets[0]:06X}")
    print(f"Last differing offset:  0x{differing_offsets[-1]:06X}")

    print("\nNamed regions:")
    for name, start, end in REGIONS:
        count = count_diffs(candidate, postboot, start, end)
        print(f"  {name:24s} 0x{start:06X}-0x{end - 1:06X}: {count} differing bytes")

    print("\nDiffering 4 KiB sectors:")
    changed_sectors: list[tuple[int, int]] = []
    for start in range(0, FLASH_SIZE, SECTOR_SIZE):
        end = start + SECTOR_SIZE
        count = count_diffs(candidate, postboot, start, end)
        if count:
            changed_sectors.append((start, count))
            print(f"  0x{start:06X}-0x{end - 1:06X}: {count} differing bytes")

    pre_tail = [offset for offset in differing_offsets if offset < SDK_TAIL_START]
    if pre_tail:
        print("\nUnexpected changes exist before 0xFB000.")
        print(f"First pre-tail difference: 0x{pre_tail[0]:06X}")
        print(f"Last pre-tail difference:  0x{pre_tail[-1]:06X}")
        print("RESULT: PRE_TAIL_CONTENT_CHANGED")
        return 1

    print("\nAll byte differences are confined to 0xFB000-0xFFFFF.")
    print("RESULT: ONLY_RF_SDK_TAIL_CHANGED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
