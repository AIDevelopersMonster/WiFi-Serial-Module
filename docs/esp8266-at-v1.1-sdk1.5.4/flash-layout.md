# Flash layout of the preserved ESP8285N08 AT image

This page records an offline inspection of the complete 1 MiB Flash image captured from the tested module (`chip ID 0x009f7c3c`). The raw binary remains private/ignored; only derived metadata and structural observations are committed.

Recommended stable local filename:

```text
esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin
```

## Image identity

```text
Size:   1048576 bytes (0x100000)
SHA256: 8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

## Legacy ESP image header at 0x000000

The dump begins with a valid legacy ESP8266 image header (`0xE9`). Parsing the image gives:

| Field | Value |
|---|---|
| Magic | `0xE9` |
| Segment count | 3 |
| SPI flash mode | DOUT (`3`) |
| Declared Flash size | 1 MB |
| SPI flash frequency | 40 MHz |
| Entry point | `0x40100004` |
| Segment data end | `0x0098F8` |
| Stored checksum | `0xBA` |
| Calculated checksum | `0xBA` |
| Checksum status | **MATCH** |

Segments:

| # | File offset | Load address | Length |
|---:|---:|---:|---:|
| 0 | `0x000010` | `0x40100000` | `0x6C50` |
| 1 | `0x006C68` | `0x3FFE8000` | `0x084C` |
| 2 | `0x0074BC` | `0x3FFE8850` | `0x243C` |

This is direct evidence that the preserved image starts with a structurally valid executable image rather than arbitrary data.

## Non-erased 4 KiB sector map

A sector is listed here when at least one byte differs from erased Flash value `0xFF`.

```text
0x000000-0x009FFF  10 sectors   38,037 non-FF bytes
0x010000-0x066FFF  87 sectors  344,378 non-FF bytes
0x07D000-0x07DFFF   1 sector       104 non-FF bytes
0x07F000-0x07FFFF   1 sector        17 non-FF bytes
0x0FC000-0x0FCFFF   1 sector       544 non-FF bytes
```

All other 4 KiB sectors in this particular dump are fully erased (`0xFF`).

## Structural map

The following map deliberately separates **observed facts** from **interpretation**.

```text
0x000000 +----------------------------------+
         | Valid legacy ESP image (0xE9)  |
         | 3 RAM-load segments             |
         | entry 0x40100004                |
         | checksum valid                  |
0x009900 | image segment payload ends      |
0x00A000 +----------------------------------+
         | erased                          |
0x010000 +----------------------------------+
         | large populated code/data area  |
         |                                |
         | AT/Wi-Fi/TCP-IP/SmartConfig     |
         | marker strings observed here    |
0x067000 +----------------------------------+
         | erased                          |
         |                                |
0x07D000 +----------------------------------+
         | small data record; starts VER2  |
0x07E000 +----------------------------------+
         | erased                          |
0x07F000 +----------------------------------+
         | small record with AA55AA55      |
0x080000 +----------------------------------+
         | erased                          |
         |                                |
0x0FC000 +----------------------------------+
         | small populated tail sector     |
0x0FD000 +----------------------------------+
         | erased through end              |
0x100000 +----------------------------------+
```

### Confidence notes

- `0x000000` executable image: **high confidence**, parsed header and checksum.
- `0x010000-0x066FFF` application/SDK flash-mapped code/data: **high confidence** as a populated firmware region; exact linker-section boundaries are not yet reconstructed.
- `0x07D000`, `0x07F000`, `0x0FC000`: **observed service/data sectors**, but their exact SDK semantic role is intentionally not asserted yet. They should be compared against Espressif NONOS SDK flash-map documentation and, later, a known-good DOIT V3 image before assigning stronger labels.

## Firmware markers found in the image

Selected strings and offsets:

```text
0x008040  compile time:
0x008078  AT version:
0x0080B0  SDK version:
0x008178  +CIPSTART
0x00827C  +SAVETRANSLINK
0x0082FC  +CWMODE_CUR
0x009144  Espressif
0x009151  Espressif
0x0627E0  ESP_%02X%02X%02X
0x065CE8  ESPTOUCH
0x065F42  SCAN SSID
0x0654A3  sniffer
0x07D000  VER2
```

Additional `ESPTOUCH`, `SCAN SSID`, and `sniffer` strings occur in the `0x065000-0x066000` area. This confirms that the preserved binary contains the expected Espressif AT/SDK functionality beyond what has been exercised in the current bench tests.

## What is *not* present as a populated second half-image

The 1 MiB dump does not show another large contiguous populated firmware region after the main `0x010000-0x066FFF` block. Instead, most of the upper Flash is erased apart from the small sectors listed above.

This is useful evidence when comparing the image with a later DOIT V3 donor, but it is not by itself proof about the complete OTA/update architecture of this AT build.

## Reproducible scanner

The repository includes:

```text
tools/flash_layout_scan.py
```

Run on Windows:

```powershell
py tools\flash_layout_scan.py local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin
```

Run on Linux:

```bash
python3 tools/flash_layout_scan.py local-backups/esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin
```

The scanner uses only the Python standard library and does not modify the image. It reports:

- size and SHA-256;
- legacy `0xE9` header fields;
- RAM-load segments;
- ESP image checksum validation;
- non-erased 4 KiB sector runs;
- selected firmware marker offsets.

## Why this matters for the DOIT V3 experiment

When a known-good `Doit_WiFi_xxxxxx` module is dumped, run the **same scanner** on its full Flash image. We can then compare, without guessing:

1. SoC/Flash geometry;
2. image header and SPI mode/frequency;
3. executable/flash-mapped region boundaries;
4. upper-Flash service sectors;
5. erased-space pattern;
6. firmware strings and feature markers;
7. whether a full-image transplant would overwrite device-specific state.

Only after this comparison should a DT-06 firmware transplant be considered on a spare module.

## Privacy / preservation rule

Do not commit the raw full-Flash image. It may contain saved network settings or other device-specific state. The repository records only the hash, layout and derived analysis needed to reproduce and compare the experiment.
