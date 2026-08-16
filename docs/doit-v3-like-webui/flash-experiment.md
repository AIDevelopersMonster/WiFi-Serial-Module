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

Verify immediately before writing:

```powershell
(Get-Item $Candidate).Length
(Get-FileHash $Candidate -Algorithm SHA256).Hash
```

## CRITICAL: use the target port, not the donor port

The DOIT-like donor was captured on `COM24`. The characterized AT target was previously on `COM23`. Do **not** reuse a `$Port` variable that still points to `COM24`.

Set a separate target variable. If Windows still assigns the AT target to COM23:

```powershell
$TargetPort = "COM23"
```

If the port changed, substitute the actual AT-target port.

Put the **AT target** into ROM programming/download mode and verify identity:

```powershell
py -m esptool --chip esp8266 --port $TargetPort --before no-reset chip-id
```

Proceed only if the connected device is exactly:

```text
Chip type: ESP8285N08
MAC:       7c:87:ce:9f:7c:3c
Chip ID:   0x009f7c3c
```

If the MAC/chip ID differs, STOP. Do not write anything.

## Make a fresh rollback dump immediately before writing

A fresh backup is preferred even though an older valid target backup already exists:

```powershell
$Rollback = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_pre-transplant_2026-08-16_fullflash.bin"

py -m esptool --chip esp8266 --port $TargetPort --before no-reset --after no-reset read-flash 0 ALL $Rollback

(Get-Item $Rollback).Length
(Get-FileHash $Rollback -Algorithm SHA256).Hash
py tools\verify_at_reference_backup.py $Rollback
```

Proceed only if the rollback file is 1048576 bytes and the verifier reports either:

```text
RESULT: EXACT_REFERENCE
```

or:

```text
RESULT: SAME_AT_FIRMWARE_MUTABLE_STATE_DIFFERS
```

Keep this rollback image private under `local-backups/`.

## First write

The first experiment writes the complete sanitized 1 MiB candidate so old AT configuration sectors cannot interfere with the RTOS SDK layout.

Use `--after no-reset` so esptool does not intentionally start the newly written firmware before the explicit read-back check:

```powershell
py -m esptool `
  --chip esp8266 `
  --port $TargetPort `
  --before no-reset `
  --after no-reset `
  write-flash 0x000000 $Candidate
```

Do not run a separate `erase-flash`; `write-flash` erases affected 4 KiB sectors as required.

With esptool v5, successful `write-flash` automatically verifies written data when technically feasible, so a legacy `--verify` option is not required.

## Read-back verification before normal boot

Keep the module in programming mode. Read all 1 MiB back before the first intentional normal boot:

```powershell
$Verify = "local-backups\doit-v3-like-webui\target-chip-009f7c3c_postwrite_verify.bin"

py -m esptool `
  --chip esp8266 `
  --port $TargetPort `
  --before no-reset `
  --after no-reset `
  read-flash 0 ALL $Verify
```

Compare hashes:

```powershell
$CandidateHash = (Get-FileHash $Candidate -Algorithm SHA256).Hash
$VerifyHash = (Get-FileHash $Verify -Algorithm SHA256).Hash

"Candidate: $CandidateHash"
"Read-back: $VerifyHash"
"Match: $($CandidateHash -eq $VerifyHash)"
```

Required result before first normal boot:

```text
Match: True
```

If it is false, STOP and restore `$Rollback`.

## First normal boot

After a matching read-back:

1. remove the GPIO0/programming-mode condition;
2. reset or power-cycle normally;
3. allow the first boot to initialize RF calibration and SDK parameter state.

The full 1 MiB SHA-256 is expected to change after normal boot because `0xFB000-0xFFFFF` is mutable SDK state.

Initial checks:

1. Look for a Wi-Fi AP.
2. Expected application-level configuration includes `Doit_WiFi`, `192.168.4.1`, UART 9600 8N1, TCP Server port 9000, and 50 ms serial split timeout.
3. Open `http://192.168.4.1` if the AP appears.
4. Confirm `SW Version v3.2.1 / HD Version v1.0`.
5. Confirm the target identity was regenerated/retained correctly and the donor suffix `C3B3B2` was not inherited.
6. Test TCP Server port 9000 only after the Web UI is responsive.

## Post-boot capture

After successful first boot, return the target to programming mode and capture its newly generated state:

```powershell
$PostBoot = "local-backups\doit-v3-like-webui\target-chip-009f7c3c_after-first-boot.bin"

py -m esptool --chip esp8266 --port $TargetPort --before no-reset read-flash 0 ALL $PostBoot
py tools\flash_layout_scan.py $PostBoot
```

The post-boot image should differ from the candidate primarily in mutable SDK/state areas. Analyze it before declaring the conversion complete.

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
FRESH_ROLLBACK_CAPTURE: REQUIRED BEFORE WRITE
WRITE_TESTED_ON_TARGET: NO
FIRST_BOOT_TESTED: NO
```

Successful flashing alone is not proof of functional compatibility. The decisive evidence is successful first boot, RF/Wi-Fi initialization, Web UI operation, target identity, and UART/TCP behavior.
