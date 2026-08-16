#!/usr/bin/env python3
"""Build a sanitized 1 MiB DOIT V3-like transplant candidate for ESP8285N08.

This tool NEVER communicates with or writes to a device. It only creates a local
candidate .bin file from an already captured donor image. The default safety
checks are intentionally specific to the characterized DOIT V3-like SW v3.2.1
full dump and the ESP8266 RTOS SDK v1.5.0-era ABCCC tail layout.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

FLASH_SIZE = 0x100000
SECTOR = 0x1000
IDENTITY_SECTOR = 0x1D000
RF_CAL_SECTOR = 0xFB000
RF_INIT_SECTOR = 0xFC000
SDK_PARAM_START = 0xFD000
SDK_PARAM_END = 0x100000

KNOWN_DONOR_SHA256 = "81860AA052ECF5B888C6E128F2C4D15AC5DA1990DD69E45732F963B234EAB541"
KNOWN_AT_REFERENCE_SHA256 = "8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9"
ESP_INIT_DATA_V150_SHA256 = "0DA80624EFA6159BBF30141B6E978A17BED80D8F5505C4BBFB75D49F496ECB83"
DONOR_MARKERS = (
    b"Doit_Ser2Sock_3.2.1_20171229",
    b"Doit_WiFi_TTL_V2.0",
    b"OS SDK ver: 1.5.0-dev",
    b"AT+STASTATUS",
    b"AT+STAINFO",
    b"AT+TCPCLIENT",
)
IDENTITY_MAGIC = b"\x65\xBA"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def parse_mac(value: str) -> bytes:
    compact = re.sub(r"[^0-9A-Fa-f]", "", value)
    if len(compact) != 12:
        raise argparse.ArgumentTypeError("MAC must contain exactly 12 hex digits")
    try:
        mac = bytes.fromhex(compact)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if mac == b"\x00" * 6 or mac == b"\xff" * 6:
        raise argparse.ArgumentTypeError("refusing all-zero or all-FF MAC")
    return mac


def fmt_mac(mac: bytes) -> str:
    return ":".join(f"{x:02x}" for x in mac)


def require_size(path: Path, data: bytes) -> None:
    if len(data) != FLASH_SIZE:
        raise SystemExit(f"{path}: expected 1 MiB (0x100000), got 0x{len(data):X}")


def occurrences(data: bytes, pattern: bytes) -> list[int]:
    result: list[int] = []
    start = 0
    while True:
        offset = data.find(pattern, start)
        if offset < 0:
            return result
        result.append(offset)
        start = offset + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("donor", type=Path, help="characterized DOIT V3-like 1 MiB full dump")
    parser.add_argument("--target-mac", required=True, type=parse_mac, help="target ESP8285 base MAC")
    parser.add_argument("--output", required=True, type=Path, help="local candidate output image")
    parser.add_argument(
        "--target-backup",
        type=Path,
        help="optional 1 MiB target backup; validated and reported, never modified",
    )
    parser.add_argument(
        "--allow-unknown-donor",
        action="store_true",
        help="allow a donor SHA-256 different from the characterized SW v3.2.1 dump",
    )
    args = parser.parse_args()

    donor = args.donor.read_bytes()
    require_size(args.donor, donor)
    donor_hash = sha256(donor)
    if donor_hash != KNOWN_DONOR_SHA256 and not args.allow_unknown_donor:
        raise SystemExit(
            "donor SHA-256 does not match the characterized image; "
            "use --allow-unknown-donor only after independent analysis\n"
            f"expected: {KNOWN_DONOR_SHA256}\nactual:   {donor_hash}"
        )

    for marker in DONOR_MARKERS:
        if marker not in donor:
            raise SystemExit(f"required DOIT marker missing: {marker!r}")

    if donor[IDENTITY_SECTOR : IDENTITY_SECTOR + 2] != IDENTITY_MAGIC:
        raise SystemExit("unexpected custom identity-sector magic at 0x1D000")

    donor_mac_a = donor[IDENTITY_SECTOR + 2 : IDENTITY_SECTOR + 8]
    donor_mac_b = donor[IDENTITY_SECTOR + 8 : IDENTITY_SECTOR + 14]
    if donor_mac_a != donor_mac_b:
        raise SystemExit("the two donor MAC copies at 0x1D002/0x1D008 disagree")

    rf_init_data = donor[RF_INIT_SECTOR : RF_INIT_SECTOR + 128]
    rf_init_hash = sha256(rf_init_data)
    if rf_init_hash != ESP_INIT_DATA_V150_SHA256:
        raise SystemExit(
            "0xFC000 does not contain the verified 128-byte ESP8266 RTOS SDK "
            "v1.5.0 esp_init_data_default.bin\n"
            f"expected: {ESP_INIT_DATA_V150_SHA256}\nactual:   {rf_init_hash}"
        )

    target_hash: str | None = None
    if args.target_backup is not None:
        target = args.target_backup.read_bytes()
        require_size(args.target_backup, target)
        target_hash = sha256(target)

    out = bytearray(donor)

    # Replace the two DOIT application-level copies of the donor base MAC.
    out[IDENTITY_SECTOR + 2 : IDENTITY_SECTOR + 8] = args.target_mac
    out[IDENTITY_SECTOR + 8 : IDENTITY_SECTOR + 14] = args.target_mac

    # Do not carry the donor's RF calibration onto a different physical chip.
    # The first boot remains an experiment: the RTOS SDK is expected to create
    # usable target-specific state, but boot/recalibration must be bench-verified.
    out[RF_CAL_SECTOR : RF_CAL_SECTOR + SECTOR] = b"\xff" * SECTOR

    # Preserve only the verified generic 128-byte Espressif RF init data.
    out[RF_INIT_SECTOR : RF_INIT_SECTOR + SECTOR] = b"\xff" * SECTOR
    out[RF_INIT_SECTOR : RF_INIT_SECTOR + 128] = rf_init_data

    # Remove donor Wi-Fi/system parameters. These sectors include donor-derived
    # SSID/MAC state and must not be transplanted verbatim.
    out[SDK_PARAM_START:SDK_PARAM_END] = b"\xff" * (SDK_PARAM_END - SDK_PARAM_START)

    output = bytes(out)

    # Sanitization audit.
    residual_mac = occurrences(output, donor_mac_a)
    if residual_mac:
        raise SystemExit(
            "sanitization failed: donor MAC remains at "
            + ", ".join(f"0x{x:06X}" for x in residual_mac)
        )

    donor_suffix = donor_mac_a[-3:].hex().upper().encode("ascii")
    residual_suffix = occurrences(output, donor_suffix)
    if residual_suffix:
        raise SystemExit(
            "sanitization failed: donor ASCII MAC suffix remains at "
            + ", ".join(f"0x{x:06X}" for x in residual_suffix)
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)

    print(f"Donor: {args.donor}")
    print(f"Donor SHA256: {donor_hash}")
    print(f"Donor app MAC: {fmt_mac(donor_mac_a)}")
    print(f"RTOS SDK v1.5.0 init-data SHA256: {rf_init_hash}")
    if target_hash is not None:
        print(f"Target backup: {args.target_backup}")
        print(f"Target backup SHA256: {target_hash}")
        if target_hash == KNOWN_AT_REFERENCE_SHA256:
            print("Target backup: matches characterized AT 1.1 reference")
        else:
            print("Target backup: does NOT match the characterized AT 1.1 reference")
    print(f"Target MAC: {fmt_mac(args.target_mac)}")
    print(f"Output: {args.output}")
    print(f"Output size: {len(output)} bytes (0x{len(output):X})")
    print(f"Output SHA256: {sha256(output)}")
    print("\nApplied sanitization:")
    print("  0x1D002-0x1D007: donor MAC -> target MAC")
    print("  0x1D008-0x1D00D: donor MAC -> target MAC")
    print("  0xFB000-0xFBFFF: erased (do not transplant donor RF calibration)")
    print("  0xFC000-0xFC07F: verified generic RTOS SDK v1.5.0 RF init data")
    print("  0xFC080-0xFCFFF: erased")
    print("  0xFD000-0xFFFFF: erased (do not transplant donor SDK parameters)")
    print("\nIMPORTANT: this tool does not prove the candidate boots or recalibrates correctly.")
    print("Keep the original target full-flash backup before any write experiment.")
    print("The generated image remains a local/private experimental artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
