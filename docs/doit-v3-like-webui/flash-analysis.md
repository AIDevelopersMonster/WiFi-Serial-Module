# DOIT V3-like SW v3.2.1 full-Flash analysis

This document records a read-only offline analysis of the 1 MiB full-Flash image captured from the DOIT V3-like Web UI module identified as ESP8285N08, chip ID `0x00c3b3b2`.

The raw `.bin` is intentionally not committed because it contains device-specific configuration/state.

## Captured artifact

Recommended local filename:

```text
esp8285n08_doit-v3-like_sw-v3.2.1_hd-v1.0_1MiB_chip-00c3b3b2_fullflash.bin
```

Verified metadata:

```text
Size:   1048576 bytes (0x100000)
SHA256: 81860AA052ECF5B888C6E128F2C4D15AC5DA1990DD69E45732F963B234EAB541
```

## Legacy image at 0x000000

The dump starts with a valid legacy ESP image:

```text
magic:                0xE9
segments:             3
SPI mode:             DOUT
header Flash size:    1 MB
SPI Flash frequency:  40 MHz
entry point:           0x40100004
checksum stored:      0x0A
checksum calculated:  0x0A
checksum match:       true
```

Segments:

| Segment | File offset | Load address | Length |
|---|---:|---:|---:|
| 0 | `0x000010` | `0x40100000` | `0x7508` |
| 1 | `0x007520` | `0x3FFE8000` | `0x085C` |
| 2 | `0x007D84` | `0x3FFE8860` | `0x2470` |

Segment data ends at `0x00A1F4`; the validated checksum is at `0x00A1FF`.

## Non-erased Flash regions

Observed 4 KiB sector runs:

```text
0x000000-0x00AFFF   11 sectors   40316 non-FF bytes
0x01D000-0x01EFFF    2 sectors     204 non-FF bytes
0x020000-0x068FFF   73 sectors  290305 non-FF bytes
0x0FB000-0x0FFFFF    5 sectors    1147 non-FF bytes
```

Exact non-`0xFF` spans inside those runs are:

```text
0x000000-0x00A1FF
0x01D000-0x01E21C
0x020000-0x0685D1
0x0FB000-0x0FF01F
```

The layout is consistent with an ESP8266 **RTOS SDK 1.5.0-era** non-OTA image: a small load image at `0x000000`, a separate flash-mapped application region, custom application configuration sectors, and the SDK's five reserved tail sectors.

## Strong firmware identity markers

The full dump contains direct firmware/product markers:

```text
0x008BCF  Doit_Ser2Sock_3.2.1_20171229
0x008BEC  Doit_WiFi_TTL_V2.0
0x008B1F  vend':'Doit Corp. Inc.'
0x009599  Doit_WiFi
0x045A60  OS SDK ver: 1.5.0-dev(950076a) compiled @ Nov  4 2016 19:29:32
0x047E78  SW Version: v3.2.1 HD Version:v1.0
```

The `Doit_Ser2Sock_3.2.1_20171229` string is treated as an embedded application/build tag; it is not independently interpreted as a guaranteed source-code release date.

## DOIT-specific AT commands are present

The binary contains exactly the command strings previously associated with the DOIT transparent-transmission firmware family:

```text
0x00943D  AT+RST
0x00945C  AT+RESTORE
0x009472  AT+STASTATUS
0x00948F  AT+STAINFO
0x0094BF  AT+TCPCLIENT
0x0094DB  AT+TIME
```

This is an important contrast with the project's ESP8285N08 AT 1.1 reference module, where `AT+STASTATUS` and `AT+STAINFO` return `ERROR`.

## TCP/UDP and Web UI implementation is embedded in the firmware

Application strings show explicit implementations for:

- TCP client;
- TCP server;
- UDP client;
- UDP server;
- HTTP server;
- Wi-Fi configuration;
- serial/UART configuration.

Examples include:

```text
ESP8266 TCP server task > wait client
ESP8266 TCP server task > listen ok
ESP8266 TCP client task > connect ok!
ESP8266 UDP server task > socket OK!
ESP8266 UDP client task > socket OK!
task_http_server
```

The HTML/JavaScript used by the Web UI is stored directly in the Flash image. The network page includes the following socket choices:

```text
TCP Server
TCP Client
UDP Server
UDP Broadcast
UDP Client
```

The image also contains the DOIT Web UI footer and version page content, including `www.doit.am` and the `SW Version: v3.2.1 HD Version:v1.0` text seen in the captured screenshots.

## Device configuration block at 0x01D000-0x01EFFF

The small two-sector region is not executable application code. It contains device/configuration state associated with this specimen.

At `0x01D002` and `0x01D008`, the ROM/base MAC is stored twice:

```text
e0 98 06 c3 b3 b2
```

The following values can be correlated directly with the Web UI configuration in the `0x01E000` sector:

| Offset | Stored value | Interpretation confirmed by Web UI |
|---:|---|---|
| `0x01E004` | little-endian `0x00002580` | `9600` baud |
| `0x01E00E` | `Doit_WiFi` | SoftAP SSID |
| `0x01E070` | `192.168.4.1` | SoftAP IP |
| `0x01E080` | `192.168.4.1` | gateway |
| `0x01E090` | `255.255.255.0` | netmask |
| `0x01E17C` | little-endian `0x00002328` | `9000` TCP server port |
| `0x01E214` | little-endian `0x00000032` | `50 ms` serial split timeout |

This correspondence independently ties the saved Flash state to the visible Web UI settings.

## RTOS SDK tail sectors at 0x0FB000-0x0FFFFF

The DOIT image identifies itself as ESP8266 **RTOS SDK 1.5.0-dev**. The official Espressif RTOS SDK v1.5.0 project template describes the final sectors as `ABCCC`:

```text
A = RF calibration
B = RF init data
C = SDK parameters
```

For a 1 MiB flash (`256` sectors), the template returns `256 - 5 = 251` as the RF-calibration sector. Sector 251 is `0xFB000`, so the complete reserved tail map is:

```text
0xFB000  RF calibration
0xFC000  RF init data
0xFD000  SDK parameters
0xFE000  SDK parameters
0xFF000  SDK parameters
```

The first 128 bytes at `0xFC000` are byte-for-byte identical to Espressif's official `bin/esp_init_data_default.bin` from RTOS SDK v1.5.0. Its SHA-256 is:

```text
0DA80624EFA6159BBF30141B6E978A17BED80D8F5505C4BBFB75D49F496ECB83
```

The same 128-byte initialization blob is also present at `0xFC000` in the project's AT 1.1 reference dump, although that reference application itself uses NONOS SDK 1.5.4.

A specimen-specific string is present in the DOIT SDK parameter area:

```text
0x0FD0B4  Doit_WiFi_C3B3B2
```

The raw donor MAC also appears in the SDK parameter copies around `0xFD484` and `0xFE484`. This proves that a full donor image contains per-device state and should not be cloned blindly onto another physical chip.

## Consequence for firmware transplantation

The new evidence makes a DOIT-style firmware transplant to the ESP8285N08 AT reference hardware substantially more plausible at the SoC/Flash level because both specimens have:

- ESP8285N08;
- 26 MHz crystal;
- embedded 1 MiB Flash;
- the same esptool-reported Flash manufacturer/device IDs (`51` / `4014`).

However, **blindly cloning the complete 1 MiB donor dump is not the preferred first write experiment**. The donor dump demonstrably contains:

- donor MAC copies in the application configuration area;
- donor-derived SSID state;
- target-specific RF calibration;
- donor SDK/Wi-Fi system parameters;
- current Web UI and network configuration.

A safer experimental candidate keeps the DOIT application/code/configuration, replaces the two application-level donor MAC copies with the target MAC, erases `0xFB000` so RF calibration is not transplanted, preserves only the verified generic 128-byte RF init data at `0xFC000`, and erases the three SDK-parameter sectors `0xFD000-0xFFFFF`.

See [`transplant-plan.md`](transplant-plan.md) and [`../../tools/build_doit_transplant_image.py`](../../tools/build_doit_transplant_image.py).

## Comparison with the ESP8285N08 AT 1.1 reference

Reference artifact:

```text
ESP8285N08
AT firmware 1.1.0.0
NONOS SDK 1.5.4
chip ID 0x009f7c3c
SHA256 8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

### Image-header comparison

| Property | AT 1.1 reference | DOIT V3-like |
|---|---:|---:|
| Flash size | 1 MiB | 1 MiB |
| Image magic | `0xE9` | `0xE9` |
| Segments | 3 | 3 |
| SPI mode | DOUT | DOUT |
| Header Flash size | 1 MB | 1 MB |
| SPI Flash freq | 40 MHz | 40 MHz |
| Entry point | `0x40100004` | `0x40100004` |
| Segment 0 length | `0x6C50` | `0x7508` |
| Segment 1 length | `0x084C` | `0x085C` |
| Segment 2 length | `0x243C` | `0x2470` |
| Image data end | `0x0098F8` | `0x00A1F4` |
| Checksum | `0xBA` valid | `0x0A` valid |

The common header architecture is striking, but the actual application binaries are different.

### Flash-region comparison

AT 1.1 reference:

```text
0x000000-0x009FFF
0x010000-0x066FFF
0x07D000-0x07DFFF
0x07F000-0x07FFFF
0x0FC000-0x0FCFFF
```

DOIT V3-like:

```text
0x000000-0x00AFFF
0x01D000-0x01EFFF
0x020000-0x068FFF
0x0FB000-0x0FFFFF
```

The largest architectural difference is the flash-mapped application region: the AT reference starts at `0x010000`, while the DOIT-like firmware starts at `0x020000`.

A same-offset binary comparison is not very informative because the layouts differ: 62.1% of the complete 1 MiB images match byte-for-byte mostly due to erased `0xFF` space. Comparing the AT application at `0x10000` against the DOIT application shifted to `0x20000` yields only about 1.6% identical bytes. Therefore these are genuinely different application builds, not the same firmware relocated by one sector range.

### SDK lineage

The AT reference identifies itself as:

```text
SDK version:1.5.4(baaeaebb)
```

The DOIT-like dump contains:

```text
OS SDK ver: 1.5.0-dev(950076a) compiled @ Nov  4 2016 19:29:32
```

The DOIT strings and FreeRTOS/task-oriented implementation identify it with the ESP8266 **RTOS SDK 1.5.0-era** lineage, while the AT reference is a **NONOS SDK 1.5.4** application. They share low-level ESP8266 SDK/RF/network components but are not the same SDK/application family.

## Current conclusion

Status after full-dump and region analysis:

```text
HARDWARE_CLASS_MATCH: STRONG
FIRMWARE_FAMILY_MATCH: NO - RTOS DOIT app vs NONOS AT app
DOIT_V3_LIKE_IDENTITY: DIRECTLY_CONFIRMED_IN_BINARY
TAIL_SECTOR_MAP: CONFIRMED AS RTOS SDK ABCCC
FULL_DUMP_CLONE_READY: NO
SANITIZED_TRANSPLANT_CANDIDATE: BUILDABLE, NOT YET BOOT-TESTED
```

The next controlled experiment is to generate and inspect a sanitized candidate image, preserve the target's original full-flash backup, and only then perform a reversible write/boot test on the AT reference specimen.
