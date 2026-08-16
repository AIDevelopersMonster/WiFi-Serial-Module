# Web UI screenshots

Place screenshots for the DOIT V3-like web interface in this directory.

Recommended stable filenames:

```text
status.png
uart-settings.png
wifi-settings.png
network-settings.png
about.png
```

Suggested mapping for the current capture set:

- `status.png` — STATUS page with MAC, Station IP, Wi-Fi Status, SoftAP IP and uptime.
- `uart-settings.png` — MODULE UART page with baud rate, data bits, parity, stop bits and serial split timeout.
- `wifi-settings.png` — MODULE Wi-Fi page with SoftAP and Station settings.
- `network-settings.png` — MODULE Networks page with TCP Server/Client and UDP Server/Broadcast/Client settings.
- `about.png` — MORE / Thanks page with software and hardware version strings.

Avoid timestamp-based filenames such as `Screenshot 2026-08-16 ...` because they describe the capture event rather than the interface content.

When images are uploaded, reference them from the parent `README.md` using relative paths such as:

```markdown
![Status page](img/status.png)
```
