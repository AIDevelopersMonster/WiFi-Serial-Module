# DOIT V3-like hardware and Flash capture

This directory is for **public, text-only characterization results** from the DOIT V3-like Web UI module.

Raw Flash images must stay outside `docs/`, under the ignored `local-backups/` tree. The repository root `.gitignore` already excludes both `local-backups/` and `*.bin`.

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
    doit-v3-like_sw-v3.2.1_hd-v1.0_fullflash.bin
```

Only the `docs/.../capture/*.txt` files should be committed. The `.bin` file remains local.

## Before starting

1. Close MobaXterm, serial terminals, and any program holding the COM port.
2. Put the module into the ESP ROM serial bootloader (GPIO0 low during reset).
3. Run the commands from the repository root in Windows PowerShell.
4. If necessary, install esptool first:

```powershell
py -m pip install esptool
```

## 1. Prepare paths and choose the COM port

Paste this block once. It refuses an empty COM-port value so an accidental Enter cannot shift the esptool arguments:

```powershell
do {
    $Port = (Read-Host "COM port (example: COM24)").Trim()
} while ([string]::IsNullOrWhiteSpace($Port))

$Capture = "docs\doit-v3-like-webui\capture"
$Backup = "local-backups\doit-v3-like-webui"
$Dump = Join-Path $Backup "doit-v3-like_sw-v3.2.1_hd-v1.0_fullflash.bin"

New-Item -ItemType Directory -Force $Capture | Out-Null
New-Item -ItemType Directory -Force $Backup | Out-Null

"Using port: $Port"
"Dump path: $Dump"
```

If the port is already known, it is simpler and safer to assign it directly, for example:

```powershell
$Port = "COM24"
```

The dump filename is intentionally based on the observed Web UI firmware/hardware version rather than on a temporary COM-port number. After `chip-id` identifies the actual SoC and chip ID, the local image may be renamed more specifically.

## 2. Capture chip ID

```powershell
$Out = py -m esptool --port $Port chip-id 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\chip-id.txt"
```

Expected information includes the detected chip type, features, crystal frequency, MAC address, and chip ID.

## 3. Capture MAC

```powershell
$Out = py -m esptool --port $Port read-mac 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\read-mac.txt"
```

The ROM-reported MAC can then be compared with the Web UI value currently shown as `E0-98-06-C3-B3-B2`.

## 4. Capture Flash identification

```powershell
$Out = py -m esptool --port $Port flash-id 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\flash-id.txt"
```

Record the reported Flash manufacturer, device ID, and detected capacity before making the full backup.

## 5. Read the complete Flash image

This is a read-only operation:

```powershell
$Out = py -m esptool --port $Port read-flash 0 ALL $Dump 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\read-flash.txt"
```

Do **not** run `erase-flash`, `erase-region`, `write-flash`, or other write/erase commands during characterization.

### Troubleshooting: `No such command '0'`

If esptool prints:

```text
No such command '0'.
```

check the variable first:

```powershell
"Port=[$Port]"
```

An empty value means `--port` consumed the next token (`read-flash`) as its port argument, so `0` was then interpreted as the command name. Set the correct port explicitly, for example:

```powershell
$Port = "COM24"
```

and rerun the command. The failed `read-flash.txt` is harmless and will be overwritten by the successful rerun.

## 6. Save dump size and SHA-256

```powershell
$Size = (Get-Item $Dump).Length
$Sha256 = (Get-FileHash $Dump -Algorithm SHA256).Hash
$Captured = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

$Metadata = @(
    "Firmware profile: DOIT V3-like Web UI"
    "Observed SW version: v3.2.1"
    "Observed HD version: v1.0"
    "Dump filename: $([System.IO.Path]::GetFileName($Dump))"
    "Size: $Size bytes"
    "SHA256: $Sha256"
    "Captured: $Captured"
)

$Metadata
$Metadata | Set-Content -Encoding UTF8 "$Capture\fullflash-metadata.txt"
```

The public metadata deliberately records only the filename, size, hash, and profile information, not a local absolute path or Windows username.

## 7. Scan the DOIT-like Flash layout

The repository already contains the read-only scanner `tools/flash_layout_scan.py`:

```powershell
$Out = py tools\flash_layout_scan.py $Dump 2>&1
$Out
$Out | ForEach-Object { "$_" } | Set-Content -Encoding UTF8 "$Capture\flash-layout.txt"
```

This records the image hash, legacy ESP image header when present, segment/checksum information, non-erased 4 KiB ranges, and selected firmware markers.

## 8. Generate the same report for the known ESP8285N08 AT 1.1 reference

The previously characterized reference image has chip ID `0x009f7c3c` and SHA-256:

```text
8079DFAB4D1933A9B7B43BC6D29CCDE5A993DF2C51F4430A88037621BF0BBDD9
```

If the local file was renamed to the recommended stable name, set:

```powershell
$AtDump = "local-backups\esp8285n08_at-1.1.0.0_sdk-1.5.4_1MiB_chip-009f7c3c_fullflash.bin"
```

If it still has the original temporary name, use instead:

```powershell
$AtDump = "local-backups\COM23-full-flash.bin"
```

Then run:

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

`Compare-Object` is only a first text-level comparison of the scanner reports. Once the new raw dump is available, a deeper sector-by-sector comparison should be performed before considering any firmware transplant.

## 10. Verify what Git will publish

```powershell
git status --short
```

The expected new tracked candidates are text files under:

```text
docs/doit-v3-like-webui/capture/
```

The raw image under `local-backups/` should **not** appear as an untracked file because it is ignored.

To verify explicitly:

```powershell
git check-ignore -v $Dump
```

## 11. Commit the public capture results

After checking the files:

```powershell
git add docs\doit-v3-like-webui\capture
git status --short
git commit -m "Capture DOIT V3-like hardware and flash metadata"
git push
```

Do not use `git add -f` on the raw `.bin` image.

## What to send back for analysis

Once the capture is complete, the most useful files are:

```text
chip-id.txt
read-mac.txt
flash-id.txt
fullflash-metadata.txt
flash-layout.txt
at-1.1-reference-layout.txt
layout-compare.txt
```

With these committed, the module can be compared against the known ESP8285N08 / AT 1.1 / NONOS SDK 1.5.4 reference without publishing either device's raw Flash contents.
