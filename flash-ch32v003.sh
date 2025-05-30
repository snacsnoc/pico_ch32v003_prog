#!/usr/bin/env bash
# flash-ch32v003.sh — upload & flash a .bin via Pico without entering REPL
# Usage: flash-ch32v003.sh [-p PORT] [-g GPIO_PIN] [--map-to-port] <bin-file>

set -euo pipefail

# defaults
PICO_DEV="/dev/tty.usbmodem11301"
PIN=28
MAP_FLAG="False"

usage() {
  echo "Usage: $0 [-p PORT] [-g GPIO_PIN] [--map-to-port] <bin-file>"
  exit 1
}

# parse args
while [[ $# -gt 1 ]]; do
  case "$1" in
    -p) PICO_DEV="$2"; shift 2 ;;
    -g) PIN="$2";   shift 2 ;;
    --map-to-port) MAP_FLAG="True"; shift ;;
    *) usage ;;
  esac
done

BIN="$1"
[ -f "$BIN" ] || { echo "Error: '$BIN' not found"; exit 1; }
BASENAME=$(basename "$BIN")

# copy the binary onto the Pico
mpremote connect "$PICO_DEV" fs cp "$BIN" :

# execute flash command in one shot
mpremote connect "$PICO_DEV" exec \
  "from flash_ch32v003 import CH32_Flash; CH32_Flash($PIN, map_to_port=$MAP_FLAG).flash_binary('$BASENAME')"