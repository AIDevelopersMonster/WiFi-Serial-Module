# ESP8266 AT Instruction Set v1.5.4 - command inventory

This page tracks the commands documented by Espressif for the May 2016 ESP8266 NONOS AT generation used by the project's `AT version:1.1.0.0` / `SDK version:1.5.4` modules.

AT commands are uppercase and terminate with CRLF. The documented default baud rate is 115200.

Safety labels used below:

- **READ** - safe to query without intentionally changing configuration.
- **TEST** - capability/range query such as `=?`; normally does not change configuration.
- **VOLATILE** - changes runtime state but is not primarily a persistent Flash setting.
- **FLASH** - can store configuration in Flash or alter persistent defaults.
- **DISRUPTIVE** - resets, sleeps, disconnects, performs OTA, or otherwise interrupts operation.
- **DATA** - opens/closes sockets or transmits network data.

Not every command supports all four AT forms (test/query/set/execute). An `ERROR` from a query form therefore does not always mean that the command is absent.

## Basic commands (12)

| Command | Purpose | Example | Safety |
|---|---|---|---|
| `AT` | Startup test | `AT` | READ |
| `AT+RST` | Restart module | `AT+RST` | DISRUPTIVE |
| `AT+GMR` | Firmware/SDK version | `AT+GMR` | READ |
| `AT+GSLP` | Deep sleep | `AT+GSLP=1000` | DISRUPTIVE |
| `ATE` | Command echo | `ATE0`, `ATE1` | VOLATILE |
| `AT+RESTORE` | Factory reset | `AT+RESTORE` | DISRUPTIVE / FLASH |
| `AT+UART` | Legacy UART configuration (deprecated) | `AT+UART=115200,8,1,0,0` | VOLATILE / legacy |
| `AT+UART_CUR` | Current UART configuration | `AT+UART_CUR?` | READ; set form VOLATILE |
| `AT+UART_DEF` | Default UART configuration | `AT+UART_DEF?` | READ; set form FLASH |
| `AT+SLEEP` | Sleep mode | `AT+SLEEP?` | READ; set form VOLATILE |
| `AT+RFPOWER` | Maximum RF TX power | `AT+RFPOWER?` | READ if query supported; set form VOLATILE |
| `AT+RFVDD` | RF TX power according to VDD33 | use only with hardware understanding | VOLATILE |

## Wi-Fi commands (37)

| Command | Purpose | Typical safe/example form | Safety |
|---|---|---|---|
| `AT+CWMODE` | Legacy Wi-Fi mode | `AT+CWMODE?` | READ; set may persist (deprecated) |
| `AT+CWMODE_CUR` | Current Wi-Fi mode | `AT+CWMODE_CUR?` | READ; set VOLATILE |
| `AT+CWMODE_DEF` | Default Wi-Fi mode | `AT+CWMODE_DEF?` | READ; set FLASH |
| `AT+CWJAP` | Legacy connect/query AP | `AT+CWJAP?` | READ/query; connect DISRUPTIVE |
| `AT+CWJAP_CUR` | Current AP configuration | `AT+CWJAP_CUR?` | READ; set VOLATILE |
| `AT+CWJAP_DEF` | Saved AP configuration | `AT+CWJAP_DEF?` | READ; set FLASH |
| `AT+CWLAPOPT` | Configure AP scan output | `AT+CWLAPOPT=?` | TEST; set VOLATILE |
| `AT+CWLAP` | Scan/list APs | `AT+CWLAP` | READ/active scan |
| `AT+CWQAP` | Disconnect station from AP | `AT+CWQAP` | DISRUPTIVE |
| `AT+CWSAP` | Legacy softAP config | `AT+CWSAP?` | READ; set legacy/persistent behavior |
| `AT+CWSAP_CUR` | Current softAP config | `AT+CWSAP_CUR?` | READ; set VOLATILE |
| `AT+CWSAP_DEF` | Default softAP config | `AT+CWSAP_DEF?` | READ; set FLASH |
| `AT+CWLIF` | List stations on softAP | `AT+CWLIF` | READ, mode-dependent |
| `AT+CWDHCP` | Legacy DHCP setting | `AT+CWDHCP?` where supported | query/read; set changes DHCP |
| `AT+CWDHCP_CUR` | Current DHCP config | `AT+CWDHCP_CUR?` | READ; set VOLATILE |
| `AT+CWDHCP_DEF` | Default DHCP config | `AT+CWDHCP_DEF?` | READ; set FLASH |
| `AT+CWDHCPS_CUR` | Current softAP DHCP range | `AT+CWDHCPS_CUR?` | READ; set VOLATILE |
| `AT+CWDHCPS_DEF` | Saved softAP DHCP range | `AT+CWDHCPS_DEF?` | READ; set FLASH |
| `AT+CWAUTOCONN` | Auto-connect after power-up | `AT+CWAUTOCONN=1` | FLASH/state change |
| `AT+CIPSTAMAC` | Legacy station MAC | `AT+CIPSTAMAC?` | READ; set deprecated |
| `AT+CIPSTAMAC_CUR` | Current station MAC | `AT+CIPSTAMAC_CUR?` | READ; set VOLATILE |
| `AT+CIPSTAMAC_DEF` | Default station MAC | `AT+CIPSTAMAC_DEF?` | READ; set FLASH |
| `AT+CIPAPMAC` | Legacy softAP MAC | `AT+CIPAPMAC?` | READ; set deprecated |
| `AT+CIPAPMAC_CUR` | Current softAP MAC | `AT+CIPAPMAC_CUR?` | READ; set VOLATILE |
| `AT+CIPAPMAC_DEF` | Default softAP MAC | `AT+CIPAPMAC_DEF?` | READ; set FLASH |
| `AT+CIPSTA` | Legacy station IP | `AT+CIPSTA?` | READ; set deprecated |
| `AT+CIPSTA_CUR` | Current station IP/gateway/netmask | `AT+CIPSTA_CUR?` | READ; set VOLATILE |
| `AT+CIPSTA_DEF` | Default station IP/gateway/netmask | `AT+CIPSTA_DEF?` | READ; set FLASH |
| `AT+CIPAP` | Legacy softAP IP | `AT+CIPAP?` | READ; set deprecated |
| `AT+CIPAP_CUR` | Current softAP IP/gateway/netmask | `AT+CIPAP_CUR?` | READ; set VOLATILE |
| `AT+CIPAP_DEF` | Default softAP IP/gateway/netmask | `AT+CIPAP_DEF?` | READ; set FLASH |
| `AT+CWSTARTSMART` | Start SmartConfig | `AT+CWSTARTSMART` | DISRUPTIVE/state change |
| `AT+CWSTOPSMART` | Stop SmartConfig | `AT+CWSTOPSMART` | state change |
| `AT+CWSTARTDISCOVER` | WeChat discovery mode | command requires parameters/state | state/network activity |
| `AT+CWSTOPDISCOVER` | Stop WeChat discovery | `AT+CWSTOPDISCOVER` | state change |
| `AT+WPS` | WPS | `AT+WPS=1` | DISRUPTIVE/state change |
| `AT+MDNS` | mDNS service | `AT+MDNS=1,"espressif","iot",8080` | state/network change |

## TCP/IP commands (20 commands + `+IPD` indication)

| Command | Purpose | Example | Safety |
|---|---|---|---|
| `AT+CIPSTATUS` | Connection status | `AT+CIPSTATUS` | READ |
| `AT+CIPDOMAIN` | DNS lookup | `AT+CIPDOMAIN="example.com"` | network activity |
| `AT+CIPSTART` | Open TCP/UDP/SSL connection | `AT+CIPSTART="TCP","192.168.1.10",9000` | DATA |
| `AT+CIPSSLSIZE` | SSL buffer size | `AT+CIPSSLSIZE=4096` | VOLATILE |
| `AT+CIPSEND` | Send data | `AT+CIPSEND=<length>` | DATA |
| `AT+CIPSENDEX` | Send data with terminator behavior | `AT+CIPSENDEX=<length>` | DATA |
| `AT+CIPSENDBUF` | Write TCP send buffer | state-dependent | DATA |
| `AT+CIPBUFSTATUS` | TCP send-buffer status | state-dependent | READ but connection-dependent |
| `AT+CIPCHECKSEQ` | Check buffered segment sequence | state-dependent | READ but connection-dependent |
| `AT+CIPBUFRESET` | Reset segment ID count | state-dependent | DATA/state change |
| `AT+CIPCLOSE` | Close TCP/UDP/SSL connection | `AT+CIPCLOSE` | DATA / DISRUPTIVE |
| `AT+CIFSR` | Local IP/MAC | `AT+CIFSR` | READ |
| `AT+CIPMUX` | Single/multiple connections | `AT+CIPMUX?` | READ; set VOLATILE |
| `AT+CIPSERVER` | TCP server | `AT+CIPSERVER=1,9000` | DATA/state change |
| `AT+CIPMODE` | Normal/transparent mode | `AT+CIPMODE?` | READ; set VOLATILE |
| `AT+SAVETRANSLINK` | Save auto transparent link | e.g. `AT+SAVETRANSLINK=1,"192.168.1.10",9000,"TCP"` | FLASH |
| `AT+CIPSTO` | TCP server timeout | `AT+CIPSTO?` | READ; set VOLATILE |
| `AT+PING` | Ping host | `AT+PING="192.168.1.1"` | network activity |
| `AT+CIUPDATE` | Firmware update through network | `AT+CIUPDATE` | **OTA / DISRUPTIVE** |
| `AT+CIPDINFO` | Include remote IP/port in `+IPD` | `AT+CIPDINFO?` | READ; set VOLATILE |
| `+IPD` | Unsolicited received-data indication | `+IPD,...` is output, not a command | READ/output |

## Transparent UART-over-Wi-Fi relevance

For this project the most important commands are:

```text
AT+CWMODE_CUR / AT+CWMODE_DEF
AT+CWJAP_CUR / AT+CWJAP_DEF
AT+CIFSR
AT+CIPMUX
AT+CIPSTART
AT+CIPMODE
AT+SAVETRANSLINK
AT+CIPSTATUS
AT+CIPCLOSE
```

A typical single transparent client flow is conceptually:

```text
AT+CWMODE_CUR=1
AT+CWJAP_CUR="SSID","password"
AT+CIPMUX=0
AT+CIPMODE=1
AT+CIPSTART="TCP","192.168.1.10",9000
AT+CIPSEND
```

After `AT+CIPSEND` enters transparent transmission, UART bytes are carried over the network until the transparent session is escaped/terminated according to the firmware rules. Do not run this sequence on a module whose current configuration you need to preserve without first recording its settings.

`AT+SAVETRANSLINK` is particularly relevant to a cable-replacement design because it can save an automatic transparent link in Flash. It must be treated as a persistent configuration write.

## Commands deliberately not attributed to v1.5.4

Do not infer support from newer documentation. For example, newer NONOS/ESP-AT families contain commands not present in the May 2016 v1.5.4 manual. A later forum report using the same `AT version:1.1.0.0` / `SDK version:1.5.4` strings specifically reports `AT+CIPSNTPTIME?` returning `ERROR`.

## Automated verification

Use:

### Windows

```powershell
py tools\at_command_audit.py COM23 --baud 115200 --markdown com23-at-audit.md --json com23-at-audit.json
```

### Linux

```bash
python3 tools/at_command_audit.py /dev/ttyUSB0 --baud 115200 --markdown at-audit.md --json at-audit.json
```

The tool tests only read-only/state-preserving forms. Commands whose only meaningful test would modify the module are listed but not executed.
