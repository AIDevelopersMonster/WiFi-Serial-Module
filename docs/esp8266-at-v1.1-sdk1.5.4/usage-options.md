# Usage options for the ESP8285N08 / AT 1.1 module

This page maps practical ways to use the tested WiFi Serial Module identified as:

- ESP8285N08;
- embedded 1 MiB Flash;
- 26 MHz crystal;
- Espressif AT firmware 1.1.0.0;
- ESP8266 NONOS SDK 1.5.4;
- 115200 baud on the tested COM23 unit.

The options are ordered roughly from least invasive to most invasive.

## Decision table

| Option | Reflash | Autonomous module-to-module link | Reliability model | Configuration | Project status |
|---|---:|---:|---|---|---|
| Current AT firmware, normal UDP/TCP | No | No, normally needs host AT control | TCP or UDP | AT commands | Available now |
| Current AT firmware, transparent TCP client | No | Only toward an existing TCP server | TCP | AT commands / SAVETRANSLINK | Available now |
| Current AT firmware, transparent UDP pair | No | **Yes** | UDP datagrams under UART passthrough | AT commands / SAVETRANSLINK | **First experiment recommended** |
| Mixed DOIT V3 + Espressif AT | No if modules kept as-is | Possibly | TCP/UDP depending topology | Web + AT | Experimental |
| Reflash with DOIT DT-06 V3 firmware | Yes | Yes, if firmware/hardware compatibility is proven | TCP or UDP | DOIT web UI | Research path, not yet validated |
| Reflash with esp-link | Yes | Not the best direct two-module topology | TCP serial bridge | Web UI | Useful for PC/terminal access |
| Upgrade to a later Espressif AT build | Yes | Depends on selected build | TCP/UDP | AT commands | Possible, constrained by 1 MiB Flash |
| Custom purpose-built firmware | Yes | **Yes** | TCP or UDP with project-defined recovery | Project-defined | Best long-term control, most development work |

---

## 1. Keep the current AT firmware in normal command mode

The module can remain a conventional Wi-Fi modem controlled by an attached MCU.

Typical flow:

```text
MCU UART
   |
   +--> AT+CWMODE...
   +--> AT+CWJAP...
   +--> AT+CIPSTART...
   +--> AT+CIPSEND...
   |
ESP8285 <~~~ Wi-Fi ~~~> TCP/UDP peer
```

Advantages:

- zero firmware risk;
- both TCP and UDP are available;
- the MCU can dynamically select peers, reconnect and inspect status;
- useful when the attached device can be modified to speak AT commands.

Disadvantage for this project: the intended legacy devices should see a transparent UART cable, so requiring them to manage AT commands is undesirable.

---

## 2. Transparent TCP client

The current firmware supports UART-Wi-Fi passthrough in TCP **single-connection** mode.

This is useful for:

```text
UART device -> ESP8285 -> Wi-Fi -> existing TCP server
```

For example, a PC, Raspberry Pi, Orange Pi or server can receive the UART stream over TCP.

The link can be stored with `AT+SAVETRANSLINK`, allowing passthrough after power-up.

### Important limitation for two identical modules

Transparent TCP is not a clean symmetric two-module solution with this AT architecture:

- TCP server mode requires multiple connections (`CIPMUX=1`);
- transparent passthrough requires TCP single-connection mode (`CIPMUX=0`).

Therefore one old AT module cannot simply be configured as a transparent TCP server while the other is a transparent TCP client.

This is why UDP is the more interesting no-reflash path for a direct pair.

---

## 3. Transparent UDP pair - recommended first experiment

UDP has no server/client role in the same sense as TCP. Each module can have a fixed remote IP/port and a fixed local UDP port while remaining in transparent UART mode.

Proposed topology:

```text
Device A UART
    |
ESP A / SoftAP
192.168.4.1
UDP local 10001
    |
    |  Wi-Fi / UDP
    |
ESP B / Station
192.168.4.2
UDP local 10002
    |
Device B UART
```

Fixed peer mapping:

```text
ESP A: local 10001 -> 192.168.4.2:10002
ESP B: local 10002 -> 192.168.4.1:10001
```

### Why static addressing matters

UDP passthrough requires a fixed remote endpoint. Module B should therefore use a stable station IP such as `192.168.4.2` rather than an unpredictable DHCP lease.

### Temporary test before saving anything

First configure the Wi-Fi relationship:

- A = SoftAP at `192.168.4.1`;
- B = Station associated with A;
- B = static `192.168.4.2`;
- both UARTs set to the test baud rate.

Then test transport without committing automatic passthrough.

Module A:

```text
AT+CIPMUX=0
AT+CIPMODE=1
AT+CIPSTART="UDP","192.168.4.2",10002,10001,0
AT+CIPSEND
```

Module B:

```text
AT+CIPMUX=0
AT+CIPMODE=1
AT+CIPSTART="UDP","192.168.4.1",10001,10002,0
AT+CIPSEND
```

After `AT+CIPSEND` the UART becomes the raw data path.

To exit transparent mode, send the standalone escape sequence:

```text
+++
```

and wait at least one second before sending another AT command.

### Persist only after the temporary test succeeds

Module A:

```text
AT+SAVETRANSLINK=1,"192.168.4.2",10002,"UDP",10001
```

Module B:

```text
AT+SAVETRANSLINK=1,"192.168.4.1",10001,"UDP",10002
```

The goal is then:

```text
power on
   -> Wi-Fi association
   -> saved UDP passthrough
   -> UART bytes cross the wireless link automatically
```

### UDP limitations

UDP does not guarantee delivery, duplicate suppression or ordering at the network layer. A short dedicated Wi-Fi link may work extremely well in practice, but the project must measure packet loss under interference and power/reconnect events.

Transparent mode also buffers UART data into network packets. Espressif documents a roughly 20 ms packet interval and a maximum 2048-byte packet in passthrough mode. Therefore this is not electrically or temporally identical to a copper UART connection.

Protocols that depend on precise inter-character gaps must be tested explicitly.

---

## 4. Mixed DOIT V3 + Espressif AT

A mixed pair may be possible if both ends are configured for compatible UDP endpoints.

Example concept:

```text
DOIT V3 UDP endpoint <~~~ Wi-Fi ~~~> Espressif AT UDP passthrough
```

This is worth testing only after AT-to-AT UDP is proven, because otherwise too many variables change at once.

TCP is less attractive for a mixed transparent pair because the old Espressif AT side has the TCP server/passthrough limitation described above.

---

## 5. Reflash this hardware with DOIT DT-06 V3 firmware

This is technically plausible but **not yet validated**.

Reasons it is plausible:

- the tested module is ESP8285N08 with embedded 1 MiB Flash;
- DOIT DT-06 documentation describes an ESP-M2/ESP8285 platform;
- both products expose the UART, GPIO0/FLASH and reset path needed for ROM flashing.

However, a matching public DOIT V3 firmware image has not yet been established in this project.

### Preferred investigation path

Use a known-good `Doit_WiFi_xxxxxx` module as a donor/reference:

1. identify its SoC with esptool;
2. identify its Flash size and crystal;
3. capture a complete read-only Flash image;
4. hash the image;
5. compare its layout with the current AT module;
6. identify boot/application/system-parameter regions;
7. determine whether a code-only transplant is possible;
8. only then test flashing on a spare module.

### Do not start with a blind full-Flash clone

A full donor image can also copy saved Wi-Fi configuration, SDK system parameters and RF/calibration-related state stored near the end of Flash.

The current AT firmware backup must be preserved before any write operation.

If a compatible official/factory DOIT binary is found later, that is preferable to treating an arbitrary configured donor dump as the production image.

### Why DOIT V3 is attractive

If proven compatible, DOIT V3 gives the exact user model wanted for this project:

```text
web configuration
AP / STA
TCP Server / TCP Client
UDP Server / UDP Client
transparent UART transport
automatic reconnect behavior
```

A pair could then use the simple topology:

```text
DOIT A: AP + TCP Server
DOIT B: STA + TCP Client
```

without the old Espressif AT TCP-server transparent-mode conflict.

---

## 6. Reflash with esp-link

JeeLabs esp-link is an open-source ESP8266 Wi-Fi/serial bridge with a web UI and a transparent serial bridge on TCP port 23.

It is useful for:

```text
PC / terminal <-> TCP port 23 <-> ESP8266 <-> UART device
```

It is therefore excellent for diagnostics, development consoles and remote access to one UART endpoint.

For the main goal - two autonomous modules behaving like one wireless UART cable - it is less direct than either the current UDP passthrough or a purpose-built firmware.

---

## 7. Upgrade to a later Espressif AT firmware

The current AT 1.1 / NONOS SDK 1.5.4 is from 2016. Later NONOS releases contain fixes and expanded AT functionality.

The important hardware constraint is the integrated **1 MiB Flash**. Not every later full AT image fits that flash map. Espressif later added an `at_nano` configuration intended to support 1 MiB devices.

An upgrade should therefore be treated as a separate compatibility experiment rather than simply flashing the newest available ESP8266 AT package.

Benefits could include bug fixes and improved networking behavior, but it does not automatically remove the architectural constraints of the AT command model.

---

## 8. Purpose-built WiFi Serial Module firmware

This is the strongest long-term engineering option if the project grows beyond a quick retrofit.

The firmware can be designed specifically as a two-ended UART cable:

```text
UART A
  |
ESP8285 A
  |  application-controlled Wi-Fi protocol
ESP8285 B
  |
UART B
```

Possible features:

- AP/STA automatic pairing;
- fixed peer identity;
- TCP client/server with deterministic reconnect;
- UDP mode with sequence numbers and optional ACK/retry;
- configurable UART framing and baud rate;
- watchdog and link-state GPIO;
- local web/CLI setup;
- packet counters and latency statistics;
- optional frame-preserving mode for protocols such as Modbus RTU;
- firmware-version and hardware-profile reporting.

This avoids inheriting limitations of either old Espressif AT or proprietary DOIT firmware, but requires development and testing.

---

## Recommended project order

### Stage 1 - preserve

Already complete for COM23:

- hardware identified;
- current AT firmware identified;
- full 1 MiB Flash backup captured;
- SHA-256 recorded.

### Stage 2 - prove UDP without reflashing

Use two AT modules and test:

1. A -> B byte integrity;
2. B -> A byte integrity;
3. binary data including `00` and `FF`;
4. sustained load;
5. latency and jitter;
6. packet loss;
7. reboot A;
8. reboot B;
9. Wi-Fi interruption/recovery;
10. original legacy protocol traffic.

If this works, the project already has a zero-reflash solution.

### Stage 3 - characterize a real DOIT V3 donor

Run the same esptool hardware and Flash-backup procedure on a known-good `Doit_WiFi_xxxxxx` module.

This will tell us whether the AT and DOIT boards are truly flash-compatible rather than merely visually similar.

### Stage 4 - compare solutions

Compare:

```text
AT 1.1 UDP passthrough
vs
DOIT V3 TCP transparent pair
vs
custom firmware
```

using the same loopback, latency, reconnect and protocol tests.

## Current recommendation

Do **not** erase the AT firmware yet.

The first engineering target should be the symmetric transparent UDP pair on the existing firmware. It is the shortest path from the already-characterized hardware to the intended `UART <-> Wi-Fi <-> UART` link and remains fully reversible because the original Flash image is already backed up.
