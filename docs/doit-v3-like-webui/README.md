# DOIT V3-like Web UI module profile

This folder is for a second WiFi Serial Module variant that behaves much more like the documented DOIT transparent-transmission firmware than the previously characterized Espressif AT 1.1 module.

**Authenticity is not yet established.** The module presents a DOIT-branded web interface and a working TCP Server mode, but it should be treated as **DOIT V3-like / compatible behavior** until its SoC, flash, firmware image and hardware identity are captured independently.

## Observed web interface

The current screenshots show a three-tab interface:

- `STATUS`
- `MODULE`
- `MORE`

The footer identifies:

```text
Doctors of Intelligence&Technology
www.doit.am
© 2014-2018 All right reversed.
```

The `MORE` page reports:

```text
SW Version: v3.2.1
HD Version: v1.0
```

## Current observed status

| Property | Observed value |
|---|---|
| MAC address shown by web UI | `E0-98-06-C3-B3-B2` |
| Station IP | `0.0.0.0` |
| Wi-Fi Status | `un known` |
| SoftAP IP | `192.168.4.1` |
| SoftAP | enabled in captured configuration |
| SoftAP SSID | `Doit_WiFi` |
| SoftAP netmask | `255.255.255.0` |
| SoftAP gateway | `192.168.4.1` |
| Station | disabled in captured configuration |

## UART configuration shown

| Setting | Value |
|---|---|
| Baud rate | `9600` |
| Data bits | `8` |
| Parity | `NONE` |
| Stop bits | `1` |
| Serial split timeout | `50 ms` |

This matches the practical configuration expected for a transparent UART/Wi-Fi bridge.

## Network modes exposed by the UI

The `Networks` page exposes at least these socket roles:

- TCP Server
- TCP Client
- UDP Server
- UDP Broadcast
- UDP Client

The captured configuration shows:

```text
Socket Type: TCP Server
TCP Server Local Port: 9000
```

This is especially important for the project because the server mode is actually working on this unit, unlike the architectural limitation encountered with the legacy Espressif AT 1.1 transparent TCP path.

## Project significance

This module is currently the strongest candidate for the intended direct replacement topology:

```text
Device A UART
    |
DOIT-like module A
AP + TCP Server
    |
    | Wi-Fi
    |
DOIT-like module B
STA + TCP Client
    |
Device B UART
```

The same hardware can also be evaluated in UDP modes for lower-overhead transparent transport.

## Images

Screenshots of the web interface belong in [`img/`](img/).

The image directory intentionally uses short stable names instead of Windows screenshot timestamps. See [`img/README.md`](img/README.md) for the naming scheme.

## Next characterization steps

Before calling this an original DOIT module or using its firmware as a donor image, capture the same hardware evidence used for the ESP8285N08 AT module:

```powershell
py -m esptool --port COMxx chip-id
py -m esptool --port COMxx read-mac
py -m esptool --port COMxx flash-id
```

Then make a private full-flash backup and record only its size and SHA-256 in Git until the dump has been inspected for credentials and device-specific configuration.

Once that is done, compare the resulting image with the existing AT 1.1 dump using `tools/flash_layout_scan.py`.
