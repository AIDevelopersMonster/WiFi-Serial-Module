# ESP8266 AT safe command audit

- Port: `COM23`
- Baud: `115200`
- Probe policy: read-only/state-preserving commands only

`ERROR_OR_STATE_DEPENDENT` does not necessarily mean that a command is absent. Some commands require a particular Wi-Fi mode/state or do not implement a safe query form.

| Group | Command | Result | Response |
|---|---|---|---|
| basic | `AT` | SUPPORTED | OK |
| basic | `AT+GMR` | SUPPORTED | AT version:1.1.0.0(May 11 2016 18:09:56)<br>SDK version:1.5.4(baaeaebb)<br>compile time:May 20 2016 15:08:19<br>OK |
| basic | `AT+UART_CUR?` | ERROR_OR_STATE_DEPENDENT | ERROR |
| basic | `AT+UART_DEF?` | ERROR_OR_STATE_DEPENDENT | ERROR |
| basic | `AT+SLEEP?` | SUPPORTED | +SLEEP:2<br>OK |
| basic | `AT+RFPOWER?` | ERROR_OR_STATE_DEPENDENT | ERROR |
| wifi | `AT+CWMODE_CUR?` | SUPPORTED | +CWMODE_CUR:2<br>OK |
| wifi | `AT+CWMODE_DEF?` | SUPPORTED | +CWMODE_DEF:2<br>OK |
| wifi | `AT+CWJAP_CUR?` | SUPPORTED | No AP<br>OK |
| wifi | `AT+CWJAP_DEF?` | SUPPORTED | No AP<br>OK |
| wifi | `AT+CWLAPOPT?` | ERROR_OR_STATE_DEPENDENT | ERROR |
| wifi | `AT+CWLIF` | SUPPORTED | OK |
| wifi | `AT+CWSAP_CUR?` | SUPPORTED | +CWSAP_CUR:"ESP_9F7C3C","",1,0,4,0<br>OK |
| wifi | `AT+CWSAP_DEF?` | SUPPORTED | +CWSAP_DEF:"ESP_9F7C3C","",1,0,8,0<br>OK |
| wifi | `AT+CWDHCP_CUR?` | SUPPORTED | +CWDHCP_CUR:3<br>OK |
| wifi | `AT+CWDHCP_DEF?` | SUPPORTED | +CWDHCP_DEF:3<br>OK |
| wifi | `AT+CWDHCPS_CUR?` | SUPPORTED | +CWDHCPS_CUR:120,192.168.4.2,192.168.4.101<br>OK |
| wifi | `AT+CWDHCPS_DEF?` | SUPPORTED | +CWDHCPS_DEF:0,0.0.0.0,0.0.0.0<br>OK |
| wifi | `AT+CIPSTAMAC_CUR?` | SUPPORTED | +CIPSTAMAC_CUR:"7c:87:ce:9f:7c:3c"<br>OK |
| wifi | `AT+CIPSTAMAC_DEF?` | SUPPORTED | +CIPSTAMAC_DEF:"ff:ff:ff:ff:ff:ff"<br>OK |
| wifi | `AT+CIPAPMAC_CUR?` | SUPPORTED | +CIPAPMAC_CUR:"7e:87:ce:9f:7c:3c"<br>OK |
| wifi | `AT+CIPAPMAC_DEF?` | SUPPORTED | +CIPAPMAC_DEF:"ff:ff:ff:ff:ff:ff"<br>OK |
| wifi | `AT+CIPSTA_CUR?` | SUPPORTED | +CIPSTA_CUR:ip:"0.0.0.0"<br>+CIPSTA_CUR:gateway:"0.0.0.0"<br>+CIPSTA_CUR:netmask:"0.0.0.0"<br>OK |
| wifi | `AT+CIPSTA_DEF?` | SUPPORTED | +CIPSTA_DEF:ip:"0.0.0.0"<br>+CIPSTA_DEF:gateway:"0.0.0.0"<br>+CIPSTA_DEF:netmask:"0.0.0.0"<br>OK |
| wifi | `AT+CIPAP_CUR?` | SUPPORTED | +CIPAP_CUR:ip:"192.168.4.1"<br>+CIPAP_CUR:gateway:"192.168.4.1"<br>+CIPAP_CUR:netmask:"255.255.255.0"<br>OK |
| wifi | `AT+CIPAP_DEF?` | SUPPORTED | +CIPAP_DEF:ip:"0.0.0.0"<br>+CIPAP_DEF:gateway:"0.0.0.0"<br>+CIPAP_DEF:netmask:"0.0.0.0"<br>OK |
| tcpip | `AT+CIPSTATUS` | SUPPORTED | STATUS:5<br>OK |
| tcpip | `AT+CIFSR` | SUPPORTED | +CIFSR:APIP,"192.168.4.1"<br>+CIFSR:APMAC,"7e:87:ce:9f:7c:3c"<br>OK |
| tcpip | `AT+CIPMUX?` | SUPPORTED | +CIPMUX:0<br>OK |
| tcpip | `AT+CIPMODE?` | SUPPORTED | +CIPMODE:0<br>OK |
| tcpip | `AT+CIPSTO?` | SUPPORTED | +CIPSTO:180<br>OK |
| tcpip | `AT+CIPDINFO?` | SUPPORTED | +CIPDINFO:FALSE<br>OK |

## Documented commands intentionally not auto-executed

- `AT+RST`
- `AT+GSLP`
- `ATE0/ATE1`
- `AT+RESTORE`
- `AT+UART`
- `AT+UART_DEF(set)`
- `AT+SLEEP(set)`
- `AT+RFPOWER(set)`
- `AT+RFVDD`
- `AT+CWMODE`
- `AT+CWMODE_CUR(set)`
- `AT+CWMODE_DEF(set)`
- `AT+CWJAP`
- `AT+CWJAP_CUR(set)`
- `AT+CWJAP_DEF(set)`
- `AT+CWLAPOPT(set)`
- `AT+CWLAP`
- `AT+CWQAP`
- `AT+CWSAP`
- `AT+CWSAP_CUR(set)`
- `AT+CWSAP_DEF(set)`
- `AT+CWDHCP`
- `AT+CWDHCP_CUR(set)`
- `AT+CWDHCP_DEF(set)`
- `AT+CWDHCPS_CUR(set)`
- `AT+CWDHCPS_DEF(set)`
- `AT+CWAUTOCONN(set)`
- `AT+CIPSTAMAC`
- `AT+CIPSTAMAC_CUR(set)`
- `AT+CIPSTAMAC_DEF(set)`
- `AT+CIPAPMAC`
- `AT+CIPAPMAC_CUR(set)`
- `AT+CIPAPMAC_DEF(set)`
- `AT+CIPSTA`
- `AT+CIPSTA_CUR(set)`
- `AT+CIPSTA_DEF(set)`
- `AT+CIPAP`
- `AT+CIPAP_CUR(set)`
- `AT+CIPAP_DEF(set)`
- `AT+CWSTARTSMART`
- `AT+CWSTOPSMART`
- `AT+CWSTARTDISCOVER`
- `AT+CWSTOPDISCOVER`
- `AT+WPS`
- `AT+MDNS`
- `AT+CIPDOMAIN`
- `AT+CIPSTART`
- `AT+CIPSSLSIZE`
- `AT+CIPSEND`
- `AT+CIPSENDEX`
- `AT+CIPSENDBUF`
- `AT+CIPBUFSTATUS`
- `AT+CIPCHECKSEQ`
- `AT+CIPBUFRESET`
- `AT+CIPCLOSE`
- `AT+CIPMUX(set)`
- `AT+CIPSERVER`
- `AT+CIPMODE(set)`
- `AT+SAVETRANSLINK`
- `AT+CIPSTO(set)`
- `AT+PING`
- `AT+CIUPDATE`
- `AT+CIPDINFO(set)`
