# Pairing two WiFi Serial Modules

The project target is a transparent wireless replacement for a direct serial transport path.

## Concept

Before:

```text
MCU A UART -> RS-485 transceiver -> A/B cable -> RS-485 transceiver -> MCU B UART
```

After removing the RS-485 physical layer:

```text
MCU A UART -> WiFi Serial Module A <~~~ Wi-Fi ~~~> WiFi Serial Module B -> MCU B UART
```

No RS-485 A/B wiring, DE/RE control, termination resistors, or remote common ground is required between the endpoints.

## Local UART wiring

At endpoint A:

```text
Device A TX  ---> Module A RXD
Device A RX  <--- Module A TXD
Device A GND ---- Module A GND
```

At endpoint B:

```text
Device B TX  ---> Module B RXD
Device B RX  <--- Module B TXD
Device B GND ---- Module B GND
```

## DOIT V3 to DOIT V3

This is currently the simplest no-reflash topology.

### Module A

Configure:

```text
Wi-Fi mode: AP
AP IP:      192.168.4.1
Network:    TCP Server
Port:       9000
```

Factory-reset DOIT V3 firmware already closely matches this configuration.

### Module B

Configure:

```text
Wi-Fi mode: STA
SSID:       Module A SSID
Network:    TCP Client
Remote IP:  192.168.4.1
Remote port:9000
```

Disable Module B's SoftAP if possible, or put it on another subnet such as `192.168.5.1/24`.

### Result

After power-up:

1. Module A creates the Wi-Fi AP and starts TCP Server.
2. Module B joins Module A's AP.
3. Module B opens the TCP Client connection to `192.168.4.1:9000`.
4. UART bytes arriving at one endpoint are transported through the TCP connection and emitted by the UART at the opposite endpoint.

## UART framing

Each local module must match its attached device.

Example:

```text
Device A UART: 9600 8N1
Module A UART: 9600 8N1

Device B UART: 9600 8N1
Module B UART: 9600 8N1
```

If the original protocol used request/response half-duplex behavior over RS-485, the application protocol can continue to behave that way even though the physical UART interface now has separate TX and RX signals.

## Espressif AT to Espressif AT

The observed `ESP_XXXXXX` modules use Espressif AT 1.1.0.0 / NONOS SDK 1.5.4.

They are not configured through the DOIT browser interface. Pairing must be created through AT commands.

Older Espressif AT firmware has restrictions around TCP transparent mode and TCP Server / multiple-connection mode, so do not assume the DOIT TCP Server + TCP Client recipe applies directly.

A bidirectional UDP transparent link is a promising candidate for these modules and should be tested experimentally before storing automatic startup configuration.

## Mixed pair: DOIT V3 + Espressif AT

A mixed pair is theoretically possible if both sides are configured for compatible TCP/UDP endpoint behavior, but it is not yet validated in this project.

Treat it as an experiment, not a supported configuration.

## Validation checklist

Before connecting production equipment, test with two USB-UART adapters or loopback generators:

- transmission A -> B;
- transmission B -> A;
- binary bytes including `00`, `FF`, CR/LF and random payloads;
- sustained traffic;
- reconnect after powering off Module A;
- reconnect after powering off Module B;
- reconnect after Wi-Fi interruption;
- latency and jitter;
- maximum usable baud rate;
- behavior with back-to-back protocol frames.

## Important protocol caveat

Wi-Fi/TCP is not electrically or temporally identical to RS-485. It adds buffering, variable latency, packetization, and reconnect behavior. Protocols that depend strongly on inter-character timing must be tested on real hardware before declaring the replacement transparent.
