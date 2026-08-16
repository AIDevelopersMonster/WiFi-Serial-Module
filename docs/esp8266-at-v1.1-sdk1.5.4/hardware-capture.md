# Hardware identification and firmware backup

This page describes the remaining non-destructive hardware characterization for the tested `ESP_XXXXXX` module on Windows.

## What is already known from AT commands

The tested module reports:

```text
AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
```

It runs at 115200 baud and currently operates as a SoftAP (`CWMODE=2`) with AP address `192.168.4.1`.

The AT audit also captured:

- station MAC: `7c:87:ce:9f:7c:3c`;
- SoftAP MAC: `7e:87:ce:9f:7c:3c`;
- SoftAP SSID: `ESP_9F7C3C`;
- DHCP range: `192.168.4.2` through `192.168.4.101`;
- `CIPMUX=0`;
- `CIPMODE=0`;
- `CIPSTO=180`;
- `CIPDINFO=FALSE`.

## Why esptool is needed

AT firmware identifies the software stack but does not reliably expose the exact silicon/flash identity. Espressif `esptool` communicates with the ROM serial bootloader and can identify the SoC, read the chip ID/MAC, identify the SPI flash and read the complete flash contents without erasing it.

## Install esptool - Windows

From PowerShell in the repository directory:

```powershell
py -m pip install esptool
py -m esptool version
```

## Enter ESP8266 ROM download mode

For DT-06-style hardware the two buttons are normally:

- `SW1 / FLASH` -> GPIO0;
- `SW2 / RST` -> reset.

To enter the ROM serial bootloader:

1. Hold `FLASH` / SW1 (GPIO0 low).
2. Press and release `RST` / SW2.
3. Release `FLASH`.

GPIO0 low during reset selects the ESP8266 ROM serial bootloader. Normal reset with GPIO0 high boots the AT firmware again.

## Read-only hardware identification

With the module in ROM download mode and connected as `COM23`, run:

```powershell
py -m esptool --port COM23 chip-id
py -m esptool --port COM23 read-mac
py -m esptool --port COM23 flash-id
```

Record the complete console output. These commands should establish:

- detected chip family;
- ESP8266 chip ID;
- base MAC address;
- SPI flash manufacturer/device ID;
- detected flash capacity, where supported by the installed esptool version.

Do **not** use `erase-flash`, `erase-region`, `write-flash`, `write-mem`, or any other write/erase command during characterization.

## Full firmware / flash backup

After hardware identification succeeds, a complete read-only backup can be made with automatic flash-size detection:

```powershell
mkdir local-backups -ErrorAction SilentlyContinue
py -m esptool --port COM23 read-flash 0 ALL local-backups\COM23-full-flash.bin
```

Espressif documents `read-flash 0 ALL` as the way to read from address zero through the automatically detected flash size.

Immediately calculate hashes:

```powershell
Get-FileHash local-backups\COM23-full-flash.bin -Algorithm SHA256
Get-FileHash local-backups\COM23-full-flash.bin -Algorithm MD5
```

Record the file size and hashes in a text file, for example:

```powershell
(Get-Item local-backups\COM23-full-flash.bin).Length
```

## Do not publish the raw dump yet

A complete ESP8266 flash image may contain saved Wi-Fi SSIDs/passwords, configuration, calibration/system parameters, or other device-specific information. Keep `COM23-full-flash.bin` local until it has been inspected and sanitized.

Only the following should initially be committed to the public repository:

- esptool identification output;
- flash size and IDs;
- hashes of the private backup;
- parsed firmware layout information that does not expose credentials or secrets.

## Return to normal firmware

After the read operations finish:

1. release FLASH/GPIO0 if it is still held;
2. press and release RST;
3. reconnect at 115200 baud;
4. verify:

```text
AT
OK
```

No Flash erase or write is required to return to normal operation.

## Next capture requested

Save or paste the output of:

```powershell
py -m esptool --port COM23 chip-id
py -m esptool --port COM23 read-mac
py -m esptool --port COM23 flash-id
```

Then, if those succeed, create the local `read-flash 0 ALL` backup and record its size and SHA-256. With those values we can determine the module/SoC/flash profile much more precisely and inspect the firmware layout without modifying the module.

## Primary reference

Espressif esptool documentation for ESP8266 covers ROM bootloader selection, `chip-id`, `read-mac`, `flash-id`, and `read-flash` operations.
