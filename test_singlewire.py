## OK, here goes!
import singlewire_pio
from machine import Pin

WCH_DM_CPBR     = const(0x7C)
WCH_DM_CFGR     = const(0x7D)
WCH_DM_SHDWCFGR = const(0x7E)
WCH_DM_PART     = const(0x7F) # not in doc but appears to be part info

gpio61 = Pin(18, mode=Pin.IN, pull=Pin.PULL_UP)

swio_sm = rp2.StateMachine(0, singlewire_pio.singlewire_pio, freq=10_000_000,
            sideset_base=gpio61, out_base=gpio61, set_base=gpio61, in_base=gpio61)

## Some unavoidable bit-twiddling
SIDE_PINDIR = const(29)
PIO0_BASE = const(0x50200000)
SM0_EXECCTRL = const(PIO0_BASE + 0x0cc)  # p 375
## Set side-set to control pindire on machine 0
# machine.mem32[SM0_EXECCTRL] = machine.mem32[SM0_EXECCTRL]  | (1 << SIDE_PINDIR)

## remap sideset to pindir
swio_sm.active(1)

swio_sm.put(WCH_DM_SHDWCFGR)
swio_sm.put(0x5AA50400)

# swio_sm.put(WCH_DM_SHDWCFGR, 0x5AA50400)
# swio_sm.put(WCH_DM_CFGR,     0x5AA50400)

