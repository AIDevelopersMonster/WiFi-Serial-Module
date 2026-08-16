# First DOIT V3-like transplant flash experiment

This procedure is for the characterized ESP8285N08 AT 1.1 target module after a sanitized DOIT V3-like candidate image has been generated.

## Current gate status

The target backup was verified with `tools/verify_at_reference_backup.py` and produced:

```text
Full SHA256: 18E3783E0906C3A03C8314726456E64347354D66D2D539BBDDC518D059EAE917
Boot 0-0xFFFF: 63C501659D935AE0E9D5B487CC9566DB1D0B344B17DC0966898B3E887E34D60C
Main 0x10000-0x6FFFF: 972BD88D873CDF258D340196C6200BE131327733CBD1E0D30255FCD5B9C21799
Firmware 0-0x6FFFF: F5097F840622D7C735FFF76AC971EF8D3EBEFFCE2FB34FB780F84015EB55C194
RESULT: SAME_AT_FIRMWARE_MUTABLE_STATE_DIFFERS
```

Therefore the immutable AT 1.1 firmware payload matches the characterized reference; only mutable Flash state differs from the earlier full-dump hash.

## Candidate gate

For target MAC `7c:87:ce:9f:7c:3c`, the sanitized candidate is exactly:

```text
Size:   1048576 bytes
SHA256: C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
```

## Verified write result

The complete 1 MiB sanitized candidate was written to the characterized AT target while it remained in ROM programming mode. A complete pre-boot read-back was then captured.

Observed hashes:

```text
Candidate: C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
Read-back: C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
Match: True
```

This establishes that the exact intended candidate image was physically programmed and read back without a detected byte difference before the first normal boot.

## Verified first normal boot

The target was then booted normally and the DOIT-style Web UI became operational.

Observed Status page values:

```text
Mac Address:         7C-87-CE-9F-7C-3C
Station IP Address:  0.0.0.0
Wi-Fi Status:        un known
SoftAP IP address:   192.168.4.1
System Running Time: 0 days 00:01:17   (at screenshot capture)
```

The page also rendered the expected DOIT-branded navigation and footer.

Most importantly, the Web UI reports the **target** identity `7C-87-CE-9F-7C-3C`, not the donor identity `E0-98-06-C3-B3-B2`. This confirms that the transplant did not leave the donor's application-level MAC identity in the running configuration.

The accessible Web UI at `192.168.4.1` also demonstrates that the target successfully reached normal firmware execution and brought up the SoftAP/HTTP path after starting with blanked RF-calibration and SDK-parameter sectors.

## Post-first-boot Flash capture

After the successful normal boot, a new full 1 MiB Flash dump was captured from the converted target:

```text
File: local-backups\doit-v3-like-webui\target-chip-009f7c3c_after-first-boot.bin
Size: 1048576 bytes (0x100000)
SHA256: 19428502A2C164B7B43B1A6664906CBD44EEE07A10673ECC9F8070A261C85C5F
```

`tools/flash_layout_scan.py` reported the same validated initial image structure as the pre-boot candidate:

```text
magic: 0xE9
segments: 3
SPI mode: DOUT
flash size: 1MB
SPI frequency: 40MHz
entry point: 0x40100004
segment 0 length: 0x7508
segment 1 length: 0x085C
segment 2 length: 0x2470
checksum stored/calculated: 0x0A / 0x0A
checksum match: True
```

Post-boot non-erased sector runs:

```text
0x000000-0x00AFFF: 11 sectors, 40316 non-FF bytes
0x01D000-0x01EFFF: 2 sectors, 204 non-FF bytes
0x020000-0x068FFF: 73 sectors, 290305 non-FF bytes
0x0FB000-0x0FFFFF: 5 sectors, 936 non-FF bytes
```

The sector-level shape is therefore exactly where expected after first boot: the firmware/application regions remain structurally unchanged and the RTOS SDK tail `0xFB000-0xFFFFF` is populated with target runtime state.

A separate byte-level comparator `tools/compare_doit_postboot.py` was added to prove whether *all* differences from the sanitized candidate are confined to that SDK tail. Until that comparator is run, the claim remains structural rather than byte-for-byte for the pre-tail regions.

Run:

```powershell
py tools\compare_doit_postboot.py $Candidate $PostBoot
```

The desired result is:

```text
RESULT: ONLY_RF_SDK_TAIL_CHANGED
```

## Target identity

The converted target is:

```text
Chip type: ESP8285N08
MAC:       7c:87:ce:9f:7c:3c
Chip ID:   0x009f7c3c
```

The original DOIT-like donor used for analysis was a different ESP8285N08 specimen with MAC `e0:98:06:c3:b3:b2` and chip ID `0x00c3b3b2`.

## Remaining functional checks

The conversion has booted successfully, but these items should still be checked explicitly before calling the UART-over-Wi-Fi use case complete:

1. Confirm the exact SoftAP SSID generated on the converted target.
2. Confirm the Web UI `MORE` page reports `SW Version v3.2.1 / HD Version v1.0`.
3. Confirm UART settings: 9600 baud, 8 data bits, no parity, 1 stop bit, 50 ms split timeout.
4. Confirm network mode is TCP Server with local port 9000.
5. Connect to TCP port 9000 and verify bidirectional UART data.
6. Reboot/power-cycle several times and confirm configuration persistence and reliable Wi-Fi startup.

## Rollback

A fresh pre-transplant AT backup remains the rollback path. If later functional testing exposes a problem, place the target back into ROM programming mode and restore that image.

## Experiment status

```text
CANDIDATE_REPRODUCIBLE: YES
TARGET_FIRMWARE_GATE: PASSED
TARGET_PAYLOAD_MATCH: YES
ROLLBACK_AVAILABLE: YES
WRITE_TESTED_ON_TARGET: YES
PREBOOT_READBACK_MATCH: YES
FIRST_BOOT_TESTED: YES
SOFTAP_TESTED: YES
WEB_UI_TESTED: YES
TARGET_IDENTITY_PRESERVED: YES
POST_BOOT_CAPTURED: YES
POST_BOOT_LAYOUT_VALID: YES
POST_BOOT_BYTE_DIFF_AUDIT: PENDING
TCP_SERVER_TESTED: PENDING
UART_DATA_PATH_TESTED: PENDING
```

The central transplant hypothesis is experimentally supported: the DOIT V3-like SW v3.2.1 firmware boots and exposes its Web UI on the previously characterized ESP8285N08 AT 1.1 hardware after donor-specific state is sanitized.
