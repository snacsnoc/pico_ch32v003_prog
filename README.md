# Pico CH32V003 Programmer

A tool for programming CH32V003 microcontrollers using a Raspberry Pi Pico.
It works by implementing the WCH single-wire debug protocol using the Pico's PIO capabilities.

## Requirements

- Raspberry Pi Pico with MicroPython (1.25.0 tested)
- CH32V003 microcontroller (CH32V003F4P6 tested)
- Python 3.x and `mpremote` tool

## Tools

- `flash-pico.sh` - Uploads MicroPython scripts + blink.bin to the Pico
- `flash-ch32v003.sh` - Uploads a .bin file and flashes it to the CH32V003

**Usage:**
```
 flash-ch32v003.sh [-p PORT] [-g GPIO_PIN] [--map-to-port] <bin-file>
```

## Hardware hookups

- **Power** Pico 3V3(OUT) → CH32 **V** pin    (share GND)

- **SWIO** Pico **GP28** → CH32 **PD1 / SWD** header pin

- **Pull-ups**  
  - 10 kΩ (min.) from PD1 (SWIO) → 3V3
    - External pull-up is required to hold SWIO high when running your application.  
    - Without ≥10 kΩ, the pin’s internal pull-up plus on-board LED wiring leak enough current that the debug interface never clocks correctly (`abs_ctrl 0xffffffff` errors).  

## Docs

Single wire spec: https://github.com/openwch/ch32v003/blob/main/RISC-V%20QingKeV2%20Microprocessor%20Debug%20Manual.pdf

## Credits

- Original implementation by hexagon5un: https://github.com/hexagon5un/pico_ch32v003_prog
- Fork fixes and enhancements by psychogenic: https://github.com/psychogenic/pico_ch32v003_prog