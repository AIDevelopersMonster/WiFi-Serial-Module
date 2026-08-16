# COM23 observed module

Date recorded in project: 2026-08-16.

Host environment: Windows PowerShell.

Command:

```powershell
py tools/detect_module.py COM23
```

Observed result:

```text
Serial probe: COM23
  115200 baud:
    AT             -> AT\r\r | \r | OK
    AT+GMR         -> AT+GMR\r\r | AT version:1.1.0.0(May 11 2016 18:09:56)\r | SDK version:1.5.4(baaeaebb)\r | compile time:May 20 2016 15:08:19\r | OK
    AT+STASTATUS   -> AT+STASTATUS\r\r | \r | ERROR
    AT+STAINFO     -> AT+STAINFO\r\r | \r | ERROR
  9600 baud:
    AT             -> <no response>
    AT+GMR         -> <no response>
    AT+STASTATUS   -> <no response>
    AT+STAINFO     -> <no response>
UART classification: Espressif AT firmware
Matched at: 115200 baud
```

## Interpretation

1. The active UART rate is 115200 baud.
2. `AT` and `AT+GMR` behave as standard Espressif AT commands.
3. The version strings match ESP8266 AT v1.1 / NONOS SDK 1.5.4.
4. DOIT V3 status commands are not implemented by this firmware (`ERROR`).
5. No valid response is present at 9600 baud.

This observation is a hardware result for this project, not merely a documentation assumption.
