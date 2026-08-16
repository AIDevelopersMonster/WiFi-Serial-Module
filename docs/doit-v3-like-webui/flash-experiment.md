# First DOIT V3-like transplant flash experiment

This procedure is for the characterized ESP8285N08 AT 1.1 target module after a sanitized DOIT V3-like candidate image has been generated.

## Stop gate: verify the target backup first

The full 1 MiB SHA-256 of an ESP8266/ESP8285 backup may change after the device has run because configuration/system sectors are mutable. Therefore do **not** require an exact full-image SHA match before flashing.

Instead, verify that the immutable firmware payload still matches the characterized AT 1.1 reference:

```powershell
py tools\verify_at_reference_backup.py $TargetBackup
```

Proceed only if the result is one of:

```text
RESULT: EXACT_REFERENCE
RESULT: SAME_AT_FIRMWARE_MUTABLE_STATE_DIFFERS
```

Stop if the result is:

```text
RESULT: NOT_VERIFIED_AT_REFERENCE
```

## Candidate gate

For the current target MAC `7c:87:ce:9f:7c:3c`, the validated sanitized candidate must be exactly:

```text
Size:   1048576 bytes
SHA256: C1090E484F2EF71630E67B269868320D50095236D8892540A53B17847326FE56
```

Verify locally:

```powershell
(Get-Item $Candidate).Length
(Get-FileHash $Candidate -Algorithm SHA256).Hash
```

## Preserve rollback image

Before any write, make sure `$TargetBackup` exists and is 1 MiB:

```powershell
Get-Item $TargetBackup | Select-Object FullName,Length
Get-FileHash $TargetBackup -Algorithm SHA256
```

Do not overwrite or rename it during the experiment.

## Put target into programming mode

The target ESP8285 must be in ROM download/programming mode. Close MobaXterm and other serial programs first.

Verify bootloader communication:

```powershell
py -m esptool --chip esp8266 --port $Port --before no-reset chip-id
```

Expected target identity:

```text
Chip type: ESP8285N08
MAC:       7c:87:ce:9f:7c:3c
Chip ID:   0x009f7c3c
```

## First write

The first experiment writes the complete sanitized 1 MiB candidate so old AT configuration sectors cannot interfere with the RTOS SDK layout.

```powershell
py -m esptool --chip esp8266 --port $Port --before no-reset write-flash 0x000000 $Candidate
```

Do not use `erase-flash` separately unless debugging a failed experiment. `write-flash` erases the required sectors before programming.

## Read-back verification before normal boot

After the write, re-enter programming mode if necessary and read the complete Flash back to a different local filename:

```powershell
$Verify = "local-backups\doit-v3-like-webui\target-chip-009f7c3c_postwrite_verify.bin"
py -m esptool --chip esp8266 --port $Port --before no-reset read-flash 0 ALL $Verify
```

Compare the read-back image with the candidate before the first normal boot:

```powershell
(Get-FileHash $Candidate -Algorithm SHA256).Hash
(Get-FileHash $Verify -Algorithm SHA256).Hash
```

At this stage the two hashes should be identical. If they differ, stop and do not normal-boot the module.

## First normal boot

Remove the programming-mode condition and reset/power-cycle the module normally.

The first boot is expected to initialize/rewrite the blank RF calibration and SDK parameter sectors. Therefore the full 1 MiB SHA-256 is expected to change after first normal boot.

Initial checks:

1. Look for a Wi-Fi AP.
2. Expected default/application-level settings inherited from the sanitized DOIT configuration include `Doit_WiFi`, `192.168.4.1`, UART 9600 8N1, TCP Server port 9000, and 50 ms serial split timeout.
3. Open `http://192.168.4.1` if the AP appears.
4. Confirm the Web UI identifies `SW Version v3.2.1 / HD Version v1.0`.
5. Confirm the module-specific MAC/SSID state is regenerated for the target rather than retaining donor suffix `C3B3B2`.
6. Test TCP Server port 9000 only after the Web UI is responsive.

## Post-boot capture

After successful first boot, return to programming mode and capture a second 1 MiB image:

```powershell
$PostBoot = "local-backups\doit-v3-like-webui\target-chip-009f7c3c_after-first-boot.bin"
py -m esptool --chip esp8266 --port $Port --before no-reset read-flash 0 ALL $PostBoot
py tools\flash_layout_scan.py $PostBoot
```

This image is expected to differ from the candidate in the mutable `0xFB000-0xFFFFF` SDK state area. It should be analyzed before the conversion is declared successful.

## Rollback

If the candidate does not boot correctly, return the target to programming mode and restore the saved AT image:

```powershell
py -m esptool --chip esp8266 --port $Port --before no-reset write-flash 0x000000 $TargetBackup
```

Then read it back before normal boot:

```powershell
$RollbackVerify = "local-backups\rollback_verify.bin"
py -m esptool --chip esp8266 --port $Port --before no-reset read-flash 0 ALL $RollbackVerify
(Get-FileHash $TargetBackup -Algorithm SHA256).Hash
(Get-FileHash $RollbackVerify -Algorithm SHA256).Hash
```

The hashes should match before normal boot. After normal boot, mutable configuration sectors may change again.

## Experiment status

```text
CANDIDATE_REPRODUCIBLE: YES
TARGET_FIRMWARE_GATE: REQUIRED
WRITE_TESTED_ON_TARGET: NO
FIRST_BOOT_TESTED: NO
ROLLBACK_IMAGE_AVAILABLE: REQUIRED
```

Do not interpret successful flashing alone as proof of functional compatibility. The decisive evidence is successful first boot, RF/Wi-Fi initialization, Web UI operation, regenerated target identity, and UART/TCP behavior.
