# DOIT DT-06 Transparent Transmission Firmware V3.0

This page documents the stock DOIT firmware family observed on modules whose factory SSID looks like:

```text
Doit_WiFi_xxxxxx
```

## Core behavior

The DT-06 is a transparent UART-to-Wi-Fi module based on the DOIT ESP-M2 / ESP8285 platform.

The DOIT manual states that the board ships with **Transparent Transmission Firmware V3.0** and supports:

- AP, STA, and AP+STA Wi-Fi modes;
- TCP Server;
- TCP Client;
- UDP Server;
- UDP Client;
- UDP local broadcast;
- configurable UART parameters;
- built-in HTTP configuration server;
- automatic STA reconnect;
- automatic TCP Client reconnect;
- limited AT status/control commands;
- UART firmware download and OTA capability.

## Factory defaults

Documented factory settings:

```text
Wi-Fi mode:        AP
SSID:              Doit_WiFi_xxxxxx
AP IP:             192.168.4.1
UART:              9600 8N1
Packet interval:   50 ms
Network mode:      TCP Server
TCP listen port:   9000
```

This means a factory-reset module can normally be tested immediately by:

1. connecting to `Doit_WiFi_xxxxxx`;
2. opening `http://192.168.4.1`;
3. connecting a TCP client to `192.168.4.1:9000`;
4. sending data in both directions between TCP and UART.

## Pinout

The documented six-pin interface is:

| Pin | Signal | Function |
|---|---|---|
| 1 | STATE | GPIO4 / network status |
| 2 | RXD | UART receive |
| 3 | TXD | UART transmit |
| 4 | GND | Ground |
| 5 | VCC | Module supply |
| 6 | EN | Enable |

The manual specifies module supply as **4.5-6.0 V, 5 V recommended**, and describes the TTL side as 3.3 V with 5 V compatibility on the DT-06 board. Unknown clones should still be verified before applying 5 V logic.

## UART configuration

The web interface supports a wide range of baud rates and standard serial framing options. The two endpoints do not have to use the same baud rate unless the application requires it; each module only needs to match the UART device connected locally. For a transparent replacement of an existing serial cable, using the same framing on both ends is usually simplest.

## DOIT-specific AT fingerprints

The V3 manual documents a small status/control command set:

```text
AT+STASTATUS
AT+STAINFO
AT+TCPCLIENT
AT+RST
AT+RESTORE
```

Characteristic responses include:

```text
STA:OK
STA:DOWN
TCP: OK
TCP: OFF
```

This differs from the much larger generic Espressif AT command firmware.

## Direct paired-link candidate

The stock V3 firmware is particularly useful for this project because one module can be configured as a server and the other as a client.

Recommended topology:

```text
Device A UART
     |
DT-06 #1
AP + TCP Server
192.168.4.1:9000
     ^
     | Wi-Fi / TCP
     v
DT-06 #2
STA + TCP Client
remote 192.168.4.1:9000
     |
Device B UART
```

For DT-06 #2, either disable its own SoftAP or move its SoftAP to a different subnet. The DOIT documentation warns that a module's AP and STA interfaces must not use the same IP network.

Example:

```text
DT-06 #1 AP:  192.168.4.1/24
DT-06 #2 STA: DHCP address in 192.168.4.0/24
DT-06 #2 AP:  disabled
```

or:

```text
DT-06 #2 AP:  192.168.5.1/24
```

## Why this firmware is useful

For the wireless-UART use case it can provide a standalone link without:

- a PC;
- an external router;
- a protocol converter;
- custom firmware.

The first module acts as the Wi-Fi AP and TCP server, while the second module joins that AP and initiates the TCP connection.

## Source

DOIT DT-06 manual:
https://github.com/SmartArduino/gitnova.github.io/blob/master/docs/ESPSeries/ESP8285/DT06/DT06.md
