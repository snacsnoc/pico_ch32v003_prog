#!/bin/bash
PICO_DEV=/dev/tty.usbmodem11301

# Upload files
mpremote connect $PICO_DEV fs cp constants.py :
mpremote connect $PICO_DEV fs cp singlewire_pio.py :
mpremote connect $PICO_DEV fs cp flash_ch32v003.py :
mpremote connect $PICO_DEV fs cp blink.bin :
mpremote connect $PICO_DEV fs cp boot.py :

#
##
# from flash_ch32v003 import CH32_Flash; CH32_Flash(28, map_to_port=False).flash_binary("blink.bin")
#