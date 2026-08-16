#!/usr/bin/env python3
"""Shared helpers for WiFi Serial Module CLI tools."""

from __future__ import annotations

import re
from typing import Iterable


def parse_hex_bytes(value: str) -> bytes:
    """Parse hex such as '01 03 00 FF', '010300ff', or '01:03:00:ff'."""
    cleaned = re.sub(r"[^0-9a-fA-F]", "", value)
    if len(cleaned) % 2:
        raise ValueError("hex input must contain an even number of hexadecimal digits")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise ValueError(f"invalid hex input: {value!r}") from exc


def format_hex(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def percentile(values: Iterable[float], percent: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percent / 100.0
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight
