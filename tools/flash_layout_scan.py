#!/usr/bin/env python3
"""Inspect a raw ESP8266/ESP8285 flash dump without modifying it.

The scanner uses only Python's standard library. It reports file integrity,
a legacy 0xE9 image header at offset 0 when present, segment/checksum details,
4 KiB non-erased sector runs, and selected firmware marker strings.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

FLASH_MODES = {0: "QIO", 1: "QOUT", 2: "DIO", 3: "DOUT"}
FLASH_SIZES = {
    0: "512KB",
    1: "256KB",
    2: "1MB",
    3: "2MB",
    4: "4MB",
    5: "2MB-c1",
    6: "4MB-c1",
    8: "8MB",
    9: "16MB",
}
FLASH_FREQS = {0: "40MHz", 1: "26MHz", 2: "20MHz", 0xF: "80MHz"}
DEFAULT_MARKERS = [
    b"AT version:",
    b"SDK version:",
    b"compile time:",
    b"+CIPSTART",
    b"+SAVETRANSLINK",
    b"+CWMODE_CUR",
    b"Espressif",
    b"ESP_%02X%02X%02X",
    b"ESPTOUCH",
    b"SCAN SSID",
    b"sniffer",
    b"VER2",
]


def non_ff_sector_runs(data: bytes, sector_size: int) -> list[tuple[int, int, int]]:
    runs: list[tuple[int, int, int]] = []
    start: int | None = None
    end = 0
    non_ff = 0
    for offset in range(0, len(data), sector_size):
        block = data[offset : offset + sector_size]
        count = sum(byte != 0xFF for byte in block)
        if count:
            if start is None:
                start = offset
                non_ff = 0
            end = min(offset + sector_size, len(data))
            non_ff += count
        elif start is not None:
            runs.append((start, end, non_ff))
            start = None
    if start is not None:
        runs.append((start, end, non_ff))
    return runs


def marker_offsets(data: bytes, marker: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(marker, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def parse_legacy_image(data: bytes) -> dict[str, object] | None:
    if len(data) < 8 or data[0] != 0xE9:
        return None

    segment_count = data[1]
    flash_mode = data[2]
    size_freq = data[3]
    entry = struct.unpack_from("<I", data, 4)[0]
    position = 8
    checksum = 0xEF
    segments: list[dict[str, int]] = []

    for index in range(segment_count):
        if position + 8 > len(data):
            raise ValueError("truncated segment header")
        address, length = struct.unpack_from("<II", data, position)
        position += 8
        if position + length > len(data):
            raise ValueError("truncated segment data")
        payload = data[position : position + length]
        for byte in payload:
            checksum ^= byte
        segments.append(
            {
                "index": index,
                "load_address": address,
                "length": length,
                "file_offset": position,
            }
        )
        position += length

    checksum_offset = ((position + 16) & ~0xF) - 1
    if checksum_offset >= len(data):
        raise ValueError("image footer lies outside file")
    stored_checksum = data[checksum_offset]

    return {
        "segment_count": segment_count,
        "flash_mode": flash_mode,
        "flash_mode_name": FLASH_MODES.get(flash_mode, "unknown"),
        "flash_size_code": size_freq >> 4,
        "flash_size_name": FLASH_SIZES.get(size_freq >> 4, "unknown"),
        "flash_freq_code": size_freq & 0xF,
        "flash_freq_name": FLASH_FREQS.get(size_freq & 0xF, "unknown"),
        "entry": entry,
        "segments": segments,
        "data_end": position,
        "checksum_offset": checksum_offset,
        "checksum_calculated": checksum,
        "checksum_stored": stored_checksum,
        "checksum_ok": checksum == stored_checksum,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="raw flash dump or ESP8266 image")
    parser.add_argument("--sector-size", type=lambda x: int(x, 0), default=0x1000)
    args = parser.parse_args()

    data = args.image.read_bytes()
    print(f"File: {args.image}")
    print(f"Size: {len(data)} bytes (0x{len(data):X})")
    print(f"SHA256: {hashlib.sha256(data).hexdigest().upper()}")

    image = parse_legacy_image(data)
    if image is None:
        print("\nLegacy image @ 0x000000: not detected")
    else:
        print("\nLegacy image @ 0x000000:")
        print("  magic: 0xE9")
        print(f"  segments: {image['segment_count']}")
        print(f"  SPI mode: {image['flash_mode_name']} ({image['flash_mode']})")
        print(f"  declared flash size: {image['flash_size_name']}")
        print(f"  SPI flash frequency: {image['flash_freq_name']}")
        print(f"  entry point: 0x{image['entry']:08X}")
        for segment in image["segments"]:  # type: ignore[index]
            print(
                f"  segment {segment['index']}: file=0x{segment['file_offset']:06X} "
                f"load=0x{segment['load_address']:08X} length=0x{segment['length']:X}"
            )
        print(f"  segment data end: 0x{image['data_end']:06X}")
        print(
            f"  checksum @ 0x{image['checksum_offset']:06X}: "
            f"stored=0x{image['checksum_stored']:02X} "
            f"calculated=0x{image['checksum_calculated']:02X} "
            f"match={image['checksum_ok']}"
        )

    print(f"\nNon-erased {args.sector_size}-byte sector runs:")
    for start, end, count in non_ff_sector_runs(data, args.sector_size):
        print(
            f"  0x{start:06X}-0x{end - 1:06X}: "
            f"{(end - start) // args.sector_size} sectors, {count} non-FF bytes"
        )

    print("\nSelected markers:")
    for marker in DEFAULT_MARKERS:
        offsets = marker_offsets(data, marker)
        if offsets:
            joined = ", ".join(f"0x{x:06X}" for x in offsets)
            print(f"  {marker.decode('ascii', errors='replace')!r}: {joined}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
