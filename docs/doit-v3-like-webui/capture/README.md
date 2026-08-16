# DOIT V3-like hardware and Flash capture

This directory is for **public, text-only characterization results** from the DOIT V3-like Web UI module.

Raw Flash images must stay outside `docs/`, under the ignored `local-backups/` tree. The repository root `.gitignore` already excludes both `local-backups/` and `*.bin`.

## Verified hardware for this specimen

The module has now been identified through the ESP ROM bootloader as:

```text
Chip type: ESP8285N08
Features: Wi-Fi, 160MHz, Embedded Flash
Crystal frequency: 26MHz
MAC: e0:98:06:c3:b3:b2
Chip ID: 0x00c3b3b2
Flash manufacturer: 51
Flash device: 4014
Detected flash size: 1MB
```

The Web UI MAC `E0-98-06-C3-B3-B2` matches the ROM/base MAC exactly.

## Storage layout

```text
docs/doit-v3-like-webui/capture/
    chip-id.txt
    read-mac.txt
    flash-id.txt
    read-flash.txt
    fullflash-metadata.txt
    flash-layout.txt
    at-1.1-reference-layout.txt
    layout-compare.txt

local-backups/doit-v3-like-webui/
    esp8285n08_doit-v3-like_sw-v3.2.1_hd-v1.0_1MiB_chip-00c3b3b2_fullflash.bin
```

Only the `docs/.../capture/*.txt` files should be committed. The `.bin` file remains local.

## Before starting

1. Close MobaXterm, serial terminals, and any program holding the COM port.
2. **Enter ESP ROM programming/download mode before running esptool.** On the tested setup, the correct COM port alone was not enough; normal firmware mode produced `No serial data received`.
3. Run the commands from the repository root in Windows PowerShell.
4. If necessary, install esptool first:

```powershell
py -m pip install esptool
```

## 1. Prepare paths and COM port

For the currently tested unit:

```powershell
$Port = "COM24"
$Capture = "docs\doit-v3-like-webui\capture"
$Backup = "local-backups\doit-v3-like-webui"
$Dump = Join-Path $Backup "esp8285n08_doit-v3-like_sw-v3.2.1_hd-v1.0_1MiB_chip-00c3b3b2_fullflash.bin"

New-Item -ItemType Directory -Force $Capture | Out-Null
New-Item -ItemType Directory -Force $Backup | Out-Null

"Using port: $Port"
"Dump path: $Dump"
```

## 2. Capture chip ID

Because the module is already in ROM bootloader mode, use `--before no-reset`:

```powershell
$Out = py -m esptool --chip esp8266 --port $Port --before no-reset chip-id 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\chip-id.txt"
```

## 3. Capture MAC

```powershell
$Out = py -m esptool --chip esp8266 --port $Port --before no-reset read-mac 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\read-mac.txt"
```

## 4. Capture Flash identification

```powershell
$Out = py -m esptool --chip esp8266 --port $Port --before no-reset flash-id 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\flash-id.txt"
```

## 5. Read the complete Flash image

This is a read-only operation:

```powershell
$Out = py -m esptool --chip esp8266 --port $Port --before no-reset read-flash 0 ALL $Dump 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\read-flash.txt"
```

Do **not** run `erase-flash`, `erase-region`, `write-flash`, or other write/erase commands during characterization.

## 6. Save dump size and SHA-256

```powershell
$Size = (Get-Item $Dump).Length
$Sha256 = (Get-FileHash $Dump -Algorithm SHA256).Hash
$Captured = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

$Metadata = @(
    "Firmware profile: DOIT V3-like Web UI"
    "Observed SW version: v3.2.1"
    "Observed HD version: v1.0"
    "SoC: ESP8285N08"
    "Chip ID: 0x00c3b3b2"
    "MAC: e0:98:06:c3:b3:b2"
    "Detected Flash: 1 MiB"
    "Dump filename: $([System.IO.Path]::GetFileName($Dump))"
    "Size: $Size bytes"
    "SHA256: $Sha256"
    "Captured: $Captured"
)

$Metadata
$Metadata | Set-Content -Encoding UTF8 "$Capture\fullflash-metadata.txt"
```

## 7. Scan the DOIT-like Flash layout

```powershell
$Out = py tools\flash_layout_scan.py $Dump 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\flash-layout.txt"
```

## 8. Generate the same report for the known ESP8285N08 AT 1.1 reference

Reference identity:

```text
ESP8285N08
Chip ID: 0x009f7c3c
MAC: 7c:87:ce:9f:7c:3c
Flash: 1 MiB
SHA256: 8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

If the local reference dump was renamed to the recommended stable name:

```powershell
$AtDump = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"
```

If it still has the original temporary name:

```powershell
$AtDump = "local-backups\COM23-full-flash.bin"
```

Then:

```powershell
$Out = py tools\flash_layout_scan.py $AtDump 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\at-1.1-reference-layout.txt"
```

## 9. Save a first structural comparison

```powershell
$Compare = Compare-Object `
    (Get-Content "$Capture\at-1.1-reference-layout.txt") `
    (Get-Content "$Capture\flash-layout.txt")

$CompareText = $Compare | Format-Table -AutoSize | Out-String -Width 240
$CompareText
$CompareText | Set-Content -Encoding UTF8 "$Capture\layout-compare.txt"
```

`Compare-Object` is only a first text-level comparison of scanner reports. A deeper sector-by-sector comparison should follow before any firmware transplant experiment.

## 10. Verify what Git will publish

```powershell
git status --short
git check-ignore -v $Dump
```

The raw image should be ignored; only text results under `docs/doit-v3-like-webui/capture/` should be candidates for commit.

## 11. Commit the public capture results

```powershell
git add docs\doit-v3-like-webui\capture
git status --short
git commit -m "Capture DOIT V3-like hardware and flash metadata"
git push
```

Do not use `git add -f` on the raw `.bin` image.
