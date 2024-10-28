## OK, here goes!
import singlewire_write_pio
from machine import Pin

WCH_DM_CPBR     = const(0x007C)
WCH_DM_CFGR     = const(0x007D)
WCH_DM_SHDWCFGR = const(0x007E)
WCH_DM_PART     = const(0x007F) # not in doc but appears to be part info

gpio61 = Pin(18, mode=Pin.IN, pull=Pin.PULL_UP)

swio_sm = rp2.StateMachine(0, singlewire_write_pio.singlewire_write_pio, freq=10_000_000,
            sideset_base=gpio61, out_base=gpio61, set_base=gpio61, in_base=gpio61)

## Some unavoidable bit-twiddling

## GPIO CTRL reg p 247
IO_BANK0_BASE = const(0x40014000)
GPIO_CTRL_REGs = [IO_BANK0_BASE + x + 4 for x in range(0, 8*30, 8)]
OEOVER = const(12)
OUTOVER = const(8)
# GPIO_CTRL_REGs[18] |= (1 << OEOVER)
# GPIO_CTRL_REGs[18] |= (1 << OUTOVER)


SIDE_PINDIR = const(29)
PIO0_BASE = const(0x50200000)
SM0_EXECCTRL = const(PIO0_BASE + 0x0cc)  # p 375
## Set side-set to control pindirs on machine 0
## doesn't work because direction not inverted -- have pullup on input and high value on output
## need to invert this sense like in the i2c example
#machine.mem32[SM0_EXECCTRL] = machine.mem32[SM0_EXECCTRL]  | (1 << SIDE_PINDIR)

swio_sm.put(WCH_DM_SHDWCFGR)
swio_sm.put(0x5AA50400)
swio_sm.active(1)
time.sleep_ms(10)
swio_sm.active(0)

## then need to figure out the calling convention.
gpio61.value(0)
# swio_sm.put(WCH_DM_SHDWCFGR, 0x5AA50400)
# swio_sm.put(WCH_DM_CFGR,     0x5AA50400)


### works, but is write only b/c not using pullup

