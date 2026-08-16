# COM23 esptool hardware identification

Hardware identification captured from the tested `ESP_9F7C3C` module on Windows using `esptool v5.3.1`.

## Summary

| Property | Measured value |
|---|---|
| Chip type | `ESP8285N08` |
| Features | Wi-Fi, 160 MHz, embedded Flash |
| Crystal | 26 MHz |
| Base MAC | `7c:87:ce:9f:7c:3c` |
| Chip ID | `0x009f7c3c` |
| Flash manufacturer | `51` (as reported by esptool) |
| Flash device | `4014` (as reported by esptool) |
| Detected Flash size | 1 MB |
| Tool | esptool v5.3.1 |
| Windows port | `COM23` |

The AT-level station MAC previously observed matches the base MAC returned by the ROM bootloader tooling.

## `chip-id`

```text
PS> py -m esptool --port COM23 chip-id
esptool v5.3.1
Connected to ESP8266 on COM23:
Chip type:          ESP8285N08
Features:           Wi-Fi, 160MHz, Embedded Flash
Crystal frequency:  26MHz
MAC:                7c:87:ce:9f:7c:3c

Stub flasher running.

Chip ID: 0x009f7c3c

Hard resetting via RTS pin...
```

## `read-mac`

```text
PS> py -m esptool --port COM23 read-mac
esptool v5.3.1
Connected to ESP8266 on COM23:
Chip type:          ESP8285N08
Features:           Wi-Fi, 160MHz, Embedded Flash
Crystal frequency:  26MHz
MAC:                7c:87:ce:9f:7c:3c

Stub flasher is already running. No upload is necessary.

MAC:                7c:87:ce:9f:7c:3c

Hard resetting via RTS pin...
```

## `flash-id`

```text
PS> py -m esptool --port COM23 flash-id
esptool v5.3.1
Connected to ESP8266 on COM23:
Chip type:          ESP8285N08
Features:           Wi-Fi, 160MHz, Embedded Flash
Crystal frequency:  26MHz
MAC:                7c:87:ce:9f:7c:3c

Stub flasher is already running. No upload is necessary.

Flash Memory Information:
=========================
Manufacturer: 51
Device: 4014
Detected flash size: 1MB

Hard resetting via RTS pin...
```

## Current identification status

The tested module is now characterized at three layers:

1. Hardware: ESP8285N08 with embedded 1 MB Flash and 26 MHz crystal.
2. ROM/identity: chip ID `0x009f7c3c`, base MAC `7c:87:ce:9f:7c:3c`.
3. Application firmware: Espressif AT 1.1.0.0 on NONOS SDK 1.5.4, compiled May 20 2016.

The remaining useful capture is a private, read-only full Flash image plus its size and cryptographic hash. The raw image must not be committed to the public repository until inspected for saved credentials and configuration.
