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

Status at this point:

```text
WRITE_COMPLETED: YES
FULL_PREBOOT_READBACK: YES
PREBOOT_BINARY_MATCH: YES
FIRST_NORMAL_BOOT: PENDING
```

## CRITICAL: use the target port, not the donor port

The DOIT-like donor was captured on `COM24`. The characterized AT target was previously on `COM23`. Do **not** reuse a donor-port variable for recovery or post-boot work.

The target identity is:

```text
Chip type: ESP8285N08
MAC:       7c:87:ce:9f:7c:3c
Chip ID:   0x009f7c3c
```

## First normal boot

After the verified matching read-back:

1. remove the GPIO0/programming-mode condition;
2. reset or power-cycle normally;
3. allow the first boot to initialize RF calibration and SDK parameter state.

The full 1 MiB SHA-256 is expected to change after normal boot because `0xFB000-0xFFFFF` is mutable SDK state.

Initial checks:

1. Look for a Wi-Fi AP.
2. Record the exact AP SSID that appears; do not assume whether the firmware uses the plain `Doit_WiFi` name or regenerates a MAC-derived suffix.
3. Connect to the AP and check `192.168.4.1`.
4. Open the Web UI and confirm `SW Version v3.2.1 / HD Version v1.0`.
5. Record the MAC displayed by the Web UI. For this target, the expected application identity is `7C-87-CE-9F-7C-3C`, not donor `E0-98-06-C3-B3-B2`.
6. Confirm the visible UART configuration: 9600, 8 data bits, no parity, 1 stop bit, 50 ms serial split timeout.
7. Confirm TCP Server mode and local port 9000.
8. Test TCP Server port 9000 only after the Web UI is responsive.

## Post-boot capture

After successful first boot, return the target to programming mode and capture its newly generated state:

```powershell
$PostBoot = "local-backups\doit-v3-like-webui\target-chip-009f7c3c_after-first-boot.bin"

py -m esptool --chip esp8266 --port $TargetPort --before no-reset read-flash 0 ALL $PostBoot
py tools\flash_layout_scan.py $PostBoot
```

Also record its hash:

```powershell
(Get-Item $PostBoot).Length
(Get-FileHash $PostBoot -Algorithm SHA256).Hash
```

The post-boot image should differ from the candidate in mutable RF/SDK state. It should be analyzed before the conversion is declared fully characterized.

## Rollback

If the candidate does not boot correctly, put the target back into ROM programming mode and verify the target MAC/chip ID again. Then restore the fresh rollback image:

```powershell
py -m esptool `
  --chip esp8266 `
  --port $TargetPort `
  --before no-reset `
  --after no-reset `
  write-flash 0x000000 $Rollback
```

Read it back before normal boot:

```powershell
$RollbackVerify = "local-backups\rollback_verify.bin"

py -m esptool --chip esp8266 --port $TargetPort --before no-reset --after no-reset read-flash 0 ALL $RollbackVerify

$RollbackHash = (Get-FileHash $Rollback -Algorithm SHA256).Hash
$RollbackVerifyHash = (Get-FileHash $RollbackVerify -Algorithm SHA256).Hash

"Rollback: $RollbackHash"
"Read-back: $RollbackVerifyHash"
"Match: $($RollbackHash -eq $RollbackVerifyHash)"
```

Require `Match: True`, then remove programming mode and normal-boot the restored AT firmware.

## Experiment status

```text
CANDIDATE_REPRODUCIBLE: YES
TARGET_FIRMWARE_GATE: PASSED
TARGET_PAYLOAD_MATCH: YES
ROLLBACK_AVAILABLE: YES
WRITE_TESTED_ON_TARGET: YES
PREBOOT_READBACK_MATCH: YES
FIRST_BOOT_TESTED: NO
WEB_UI_TESTED: NO
TCP_SERVER_TESTED: NO
```

The write stage is now verified. Functional compatibility is established only after normal boot, RF/Wi-Fi initialization, Web UI operation, target identity validation, and UART/TCP behavior tests.
