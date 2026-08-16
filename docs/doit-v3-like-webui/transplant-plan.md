# Reversible DOIT V3-like transplant plan

This document defines a controlled experiment for converting the characterized ESP8285N08 AT 1.1 specimen into the characterized DOIT V3-like SW v3.2.1 firmware family.

The experiment is intentionally reversible. The original target image must remain available for complete restoration.

## Target and donor

### Target (AT reference)

```text
Chip:       ESP8285N08
Crystal:    26 MHz
Flash:      embedded 1 MiB
Flash ID:   manufacturer 51 / device 4014
MAC:        7c:87:ce:9f:7c:3c
Chip ID:    0x009f7c3c
Firmware:   Espressif AT 1.1.0.0 / NONOS SDK 1.5.4
SHA256:     8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

### Donor (DOIT V3-like)

```text
Chip:       ESP8285N08
Crystal:    26 MHz
Flash:      embedded 1 MiB
Flash ID:   manufacturer 51 / device 4014
MAC:        e0:98:06:c3:b3:b2
Chip ID:    0x00c3b3b2
Firmware:   DOIT V3-like SW v3.2.1 / HD v1.0
SDK:        ESP8266 RTOS SDK 1.5.0-dev era
SHA256:     81860AA052ECF5B888C6E128F2C4D15AC5DA1990DD69E45732F963B234EAB541
```

The SoC, crystal, flash capacity and flash ID match. This makes the experiment plausible but does not prove every PCB connection is identical.

## Why a raw 1 MiB clone is rejected

The donor dump contains per-device state:

- donor MAC at `0x01D002` and `0x01D008`;
- donor MAC copies in SDK parameters near `0xFD484` and `0xFE484`;
- donor-derived SSID `Doit_WiFi_C3B3B2` in the SDK parameter area;
- RF calibration in sector `0xFB000`;
- current SDK/Wi-Fi system state in `0xFD000-0xFFFFF`.

Therefore the full donor image is an evidence artifact, not the preferred transplant image.

## Confirmed RTOS SDK tail map

The official ESP8266 RTOS SDK v1.5.0 project template labels the last sectors `ABCCC`:

```text
A = RF calibration
B = RF init data
C = SDK parameters
```

For 1 MiB flash, sector 251 (`256 - 5`) is the RF calibration sector:

```text
0xFB000-0xFBFFF  RF calibration
0xFC000-0xFCFFF  RF init sector
0xFD000-0xFFFFF  three SDK parameter sectors
```

The donor's first 128 bytes at `0xFC000` are byte-for-byte identical to Espressif RTOS SDK v1.5.0 `esp_init_data_default.bin`:

```text
SHA256 0DA80624EFA6159BBF30141B6E978A17BED80D8F5505C4BBFB75D49F496ECB83
```

## Candidate-image policy

The repository tool [`tools/build_doit_transplant_image.py`](../../tools/build_doit_transplant_image.py) creates a local candidate as follows:

| Region | Candidate action | Rationale |
|---|---|---|
| `0x000000-0x00AFFF` | donor | boot/load image and DOIT application support code |
| `0x01D000` | donor with two MAC replacements | keep DOIT identity structure, use target MAC |
| `0x01E000` | donor | retain known-good default DOIT UART/network configuration |
| `0x020000-0x068FFF` | donor | DOIT flash-mapped application and Web UI |
| `0x069000-0x0FAFFF` | erased as in donor | unused space in captured image |
| `0x0FB000-0x0FBFFF` | erase to `0xFF` | never transplant donor RF calibration |
| `0x0FC000-0x0FC07F` | verified donor/generic Espressif init blob | matches official RTOS SDK v1.5.0 data |
| `0x0FC080-0x0FCFFF` | erase to `0xFF` | remove incidental donor state |
| `0x0FD000-0x0FFFFF` | erase to `0xFF` | remove donor SDK/Wi-Fi parameters |

The generator also refuses the donor by default unless its SHA-256 exactly matches the characterized v3.2.1 image.

## Generate candidate for target chip 0x009f7c3c

From repository root in Windows PowerShell:

```powershell
$Donor = "local-backups\doit-v3-like-webui\esp8285n08_doit-v3-like_sw-v3.2.1_hd-v1.0_1MiB_chip-00c3b3b2_fullflash.bin"
$TargetBackup = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"
$Candidate = "local-backups\doit-v3-like-webui\esp8285n08_doit-v3-like_sw-v3.2.1_target-chip-009f7c3c_candidate.bin"

py tools\build_doit_transplant_image.py `
  $Donor `
  --target-backup $TargetBackup `
  --target-mac 7c:87:ce:9f:7c:3c `
  --output $Candidate
```

For the characterized donor and target, the expected candidate SHA-256 is:

```text
C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
```

If the target backup still has the old temporary name, set:

```powershell
$TargetBackup = "local-backups\COM23-full-flash.bin"
```

## Candidate pre-write audit

Run:

```powershell
py tools\flash_layout_scan.py $Candidate
(Get-FileHash $Candidate -Algorithm SHA256).Hash
(Get-Item $Candidate).Length
```

Expected:

```text
Size:   1048576
SHA256: C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
```

The legacy image checksum at `0x00A1FF` must still be valid (`0x0A`).

Do not continue if the candidate hash differs from the expected hash for these exact source images and target MAC.

## Mandatory rollback verification before any write

Before changing the target, verify the original backup again:

```powershell
$TargetBackup = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"
(Get-Item $TargetBackup).Length
(Get-FileHash $TargetBackup -Algorithm SHA256).Hash
```

Required result:

```text
1048576
8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

If this backup is missing or its hash differs, stop the experiment.

## First write experiment

This is a destructive write to the target Flash, but it is reversible because the complete original image has already been captured and hash-verified.

1. Disconnect all equipment except the USB/UART programmer and power required by the module.
2. Enter the ESP ROM programming mode.
3. Confirm the target is still the expected chip:

```powershell
$Port = "COM23"
py -m esptool --chip esp8266 --port $Port --before no-reset chip-id
```

Required identity:

```text
ESP8285N08
MAC 7c:87:ce:9f:7c:3c
Chip ID 0x009f7c3c
```

4. Write the complete sanitized candidate:

```powershell
py -m esptool --chip esp8266 --port $Port --before no-reset write-flash 0x000000 $Candidate
```

Do not use `erase-flash` first. The full 1 MiB candidate already explicitly defines every byte in the device image, including erased regions.

5. After successful write, power-cycle/reset into normal boot mode.

## First-boot acceptance test

Do not connect the module to an important device yet. Bench-test it first.

Expected minimum observations:

- module boots without reset loop;
- a DOIT-like SoftAP appears;
- SSID is expected to derive from the target identity after SDK parameters regenerate; exact first-boot behavior must be observed rather than assumed;
- `192.168.4.1` Web UI becomes reachable;
- `MORE` reports `SW Version v3.2.1 / HD Version v1.0`;
- UART defaults to 9600 8N1 if the retained `0x01E000` configuration is accepted;
- TCP Server port 9000 is available;
- `AT+STASTATUS` / `AT+STAINFO` behavior can be tested separately if the DOIT AT interface is exposed in the expected operating state.

Record the first boot before changing any Web UI settings.

## Post-boot capture

If it boots successfully, immediately take a second full dump from the converted target:

```powershell
$Post = "local-backups\doit-v3-like-webui\esp8285n08_doit-v3-like_postboot_chip-009f7c3c_fullflash.bin"
py -m esptool --chip esp8266 --port $Port --before no-reset read-flash 0 ALL $Post
(Get-FileHash $Post -Algorithm SHA256).Hash
py tools\flash_layout_scan.py $Post
```

Then compare the candidate to the post-boot image. The most interesting expected changes are in:

```text
0xFB000  RF calibration
0xFD000-0xFFFFF  regenerated SDK/Wi-Fi parameters
```

This post-boot dump will tell us whether the firmware correctly generated target-specific state and whether `Doit_WiFi_9F7C3C`-style identity appears naturally.

## Rollback

If the module does not boot or network/UART behavior is unacceptable, return to programming mode and restore the exact original AT image:

```powershell
$Port = "COM23"
$TargetBackup = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"

py -m esptool --chip esp8266 --port $Port --before no-reset write-flash 0x000000 $TargetBackup
```

After reset, verify:

```text
AT
OK

AT+GMR
AT version:1.1.0.0
SDK version:1.5.4(...)
```

If the original backup is restored byte-for-byte, this should return the target to its captured pre-experiment software state.

## Current claim ceiling

At this stage:

```text
SAME_SOC_FLASH_CLASS: CONFIRMED
DOIT_FIRMWARE_IDENTITY: CONFIRMED
GENERIC_RF_INIT_DATA: CONFIRMED
DONOR_STATE_SANITIZATION: IMPLEMENTED
CANDIDATE_IMAGE: REPRODUCIBLY_BUILDABLE
TARGET_BOOT: NOT YET TESTED
TCP/UART_OPERATION_ON_CONVERTED_TARGET: NOT YET TESTED
```

A successful first boot and post-boot dump are required before calling the conversion procedure validated.
