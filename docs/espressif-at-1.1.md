# Espressif AT firmware 1.1.0.0 / NONOS SDK 1.5.4

This page documents the firmware positively observed on one module advertising an SSID of the form:

```text
ESP_XXXXXX
```

## Positive identification

UART test result:

```text
AT

OK
AT+GMR

AT version:1.1.0.0(May 11 2016 18:09:56)
SDK version:1.5.4(baaeaebb)
compile time:May 20 2016 15:08:19
OK
```

This is the Espressif ESP8266/ESP8285 AT firmware family, not DOIT Transparent V3 and not JeeLabs esp-link.

## Main characteristics

Configuration is performed through UART AT commands rather than a DOIT-style web page.

Typical command families include:

```text
AT
AT+GMR
AT+CWMODE...
AT+CWJAP...
AT+CIPSTATUS
AT+CIPSTART...
AT+CIPSEND...
AT+CIPMODE...
AT+SAVETRANSLINK...
```

Exact syntax and availability depend on the firmware release, so commands should be checked against the matching Espressif AT instruction set before writing permanent configuration.

## Why `ESP_XXXXXX` did not open a browser

That behavior is expected for this firmware family. The module may expose a Wi-Fi AP, but its primary management interface is the serial AT command set. The presence of an AP does not imply that an HTTP configuration server exists.

## Transparent transmission

Espressif AT firmware supports transparent UART/network operation, but this firmware family has mode restrictions that differ from DOIT V3.

A key point for this project is that classic ESP8266 AT transparent TCP mode is associated with a single connection, while TCP Server operation is tied to multi-connection mode in older AT command sets. Therefore a symmetric two-module transparent TCP pair is not as straightforward as with DOIT V3.

UDP is worth testing as a peer-to-peer transparent transport because the old AT firmware supports UDP endpoints and persistent transparent-link configuration through `AT+SAVETRANSLINK` in relevant releases.

Do not write `SAVETRANSLINK` until a temporary/manual link has been tested successfully.

## Suggested characterization commands

Before changing anything, record the following:

```text
AT
AT+GMR
AT+CWMODE?
AT+CIPSTATUS
AT+CIFSR
```

Also record the current UART rate and whether the module is in AP, STA, or AP+STA mode.

## Backup before reflashing

These modules are old enough that preserving the original firmware is valuable. Before replacing the firmware, make a complete flash dump and record:

- physical module ID;
- MAC address;
- flash size;
- `AT+GMR` output;
- current baud rate;
- current AP SSID;
- flash backup checksum.

## Possible use in this project

Three paths are available:

1. **Keep the original AT firmware** and configure network links through AT commands.
2. **Use it as a test platform** for transparent UDP or TCP client links.
3. **Reflash later** with DOIT-compatible/custom/esp-link firmware only after backing up the original image.

At the current stage, option 1 is preferred because the installed firmware is known and functional.

## References

- Espressif ESP8266 technical documents: https://www.espressif.com/en/support/documents/technical-documents
- Historical ESP8266 AT instruction sets are available through Espressif documentation archives.
