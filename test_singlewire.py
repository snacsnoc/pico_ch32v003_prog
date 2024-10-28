## OK, here goes!
import singlewire_pio
from machine import Pin

WCH_DM_CPBR     = const(0x007C)
WCH_DM_CFGR     = const(0x007D)
WCH_DM_SHDWCFGR = const(0x007E)
WCH_DM_PART     = const(0x007F) # not in doc but appears to be part info

gpio61 = Pin(18, mode=Pin.IN, pull=Pin.PULL_UP)

swio_sm = rp2.StateMachine(4, singlewire_pio.singlewire_pio, freq=10_000_000,
            sideset_base=gpio61, out_base=gpio61, set_base=gpio61, in_base=gpio61)

## Some unavoidable bit-twiddling
SIDE_PINDIR = const(29)
PIO0_BASE = const(0x50200000)
PIO1_BASE = const(0x50300000)
SM0_EXECCTRL = const(0x0cc)  # p 375
SM1_EXECCTRL = const(0xe4)
SM2_EXECCTRL = const(0xfc)
SM3_EXECCTRL = const(0x114)
SM4_EXECCTRL = const(0x0cc)  # p 375
SM5_EXECCTRL = const(0xe4)
SM6_EXECCTRL = const(0xfc)
SM7_EXECCTRL = const(0x114)

## Set side-set to control pindirs state machine
machine.mem32[PIO1_BASE + SM4_EXECCTRL] |= (1 << SIDE_PINDIR)

## should be a write
swio_sm.put(WCH_DM_SHDWCFGR)
swio_sm.put(0x5AA50400)

swio_sm.active(1)

## should be a read?
swio_sm.put(WCH_DM_CFGR)
print(bin(swio_sm.get()))

## and then another write?
## if you've waited a long while, you should load all the bytes together
## is there a better way to do this?
swio_sm.active(0)
swio_sm.put(WCH_DM_SHDWCFGR)
swio_sm.put(0x5AA50400)
swio_sm.active(1)

time.sleep_us(50)
swio_sm.active(0)

## idle high
gpio61.value(1)

