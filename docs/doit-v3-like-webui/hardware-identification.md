# DOIT V3-like hardware identification

The Web UI module identified as `SW Version v3.2.1 / HD Version v1.0` has now been identified independently through the ESP ROM serial bootloader using `esptool v5.3.1`.

## Verified hardware

| Property | Value |
|---|---|
| Chip type | `ESP8285N08` |
| Features | Wi-Fi, 160 MHz, Embedded Flash |
| Crystal frequency | 26 MHz |
| ROM/base MAC | `e0:98:06:c3:b3:b2` |
| Chip ID | `0x00c3b3b2` |
| Flash manufacturer | `51` as reported by esptool |
| Flash device | `4014` as reported by esptool |
| Detected Flash size | 1 MB |
| Web UI MAC | `E0-98-06-C3-B3-B2` |
| Web UI SW version | `v3.2.1` |
| Web UI HD version | `v1.0` |

The MAC address reported by the ESP ROM tooling exactly matches the address shown by the Web UI. This strongly ties the captured Web UI configuration to this physical ESP8285 device.

## Chip ID capture

```text
esptool v5.3.1
Serial port COM24:
Connected to ESP8266 on COM24:
Chip type:          ESP8285N08
Features:           Wi-Fi, 160MHz, Embedded Flash
Crystal frequency:  26MHz
MAC:                e0:98:06:c3:b3:b2

Chip ID: 0x00c3b3b2
```

## MAC capture

```text
MAC:                e0:98:06:c3:b3:b2
```

## Flash identification

```text
Flash Memory Information:
=========================
Manufacturer: 51
Device: 4014
Detected flash size: 1MB
```

## Comparison with the AT 1.1 reference module

The previously characterized Espressif AT 1.1 module is also:

- ESP8285N08;
- 26 MHz crystal;
- embedded 1 MiB Flash;
- Flash IDs reported as manufacturer `51`, device `4014`.

The two specimens therefore share the same identified SoC/Flash class. Their unique identities differ:

| Specimen | MAC | Chip ID | Firmware behavior |
|---|---|---|---|
| AT 1.1 reference | `7c:87:ce:9f:7c:3c` | `0x009f7c3c` | Espressif AT 1.1 / NONOS SDK 1.5.4 |
| DOIT V3-like | `e0:98:06:c3:b3:b2` | `0x00c3b3b2` | DOIT-like Web UI, SW v3.2.1, working TCP Server |

This is strong evidence that the major functional difference may be firmware rather than SoC/Flash capability. It does **not** yet prove that the PCB, GPIO strapping, RF layout, power circuitry, or all peripheral connections are identical.

## Programming-mode requirement

The module must be placed into the ESP ROM programming/download mode before esptool can communicate with it. On this setup, using the correct COM port without entering programming mode produced `No serial data received`.

Once programming mode was entered, the following form worked reliably:

```powershell
py -m esptool --chip esp8266 --port COM24 --before no-reset chip-id
```

The same `--before no-reset` form should be used for the remaining read-only characterization and full Flash backup while the module is already in bootloader mode.
