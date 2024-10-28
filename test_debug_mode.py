
import singlewire_pio
import gc
from machine import Pin

WCH_DM_CPBR     = const(0x007C)
WCH_DM_CFGR     = const(0x007D)
WCH_DM_SHDWCFGR = const(0x007E)
WCH_DM_PART     = const(0x007F) # not in doc but appears to be part info
SECRET          = const(0x5AA5000)
DM_CTRL         = const(0x0010)  ## in debug mode
DM_STATUS       = const(0x0011)  # debug mode, read/write

def read_address(register):
    return(register << 1)
def write_address(register):
    return((register << 1) + 1)

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

OUTSTA = const(SECRET | (1 << 10)) ## OUTSTA: 0: The debug slave has output function. 

## Set side-set to control pindirs state machine
machine.mem32[PIO1_BASE + SM4_EXECCTRL] |= (1 << SIDE_PINDIR)

gc.disable()
gc.collect()

def b32(num):
    aa = (num & 0xFF000000) >> 24 
    bb= (num & 0x00FF0000) >> 16
    cc= (num & 0x0000FF00) >> 8
    dd= num & 0x000000FF
    print(f'{aa:#010b} {bb:#010b} {cc:#010b} {dd:#010b}')

b32(write_address(WCH_DM_SHDWCFGR))
b32(OUTSTA)


### start writing, careful to load first, run second
swio_sm.put(write_address(WCH_DM_SHDWCFGR))
swio_sm.put(OUTSTA)

swio_sm.active(1)
time.sleep_us(50)
swio_sm.active(0)

swio_sm.put(write_address(WCH_DM_SHDWCFGR))
swio_sm.put(OUTSTA)

swio_sm.active(1)
time.sleep_us(50)
swio_sm.active(0)

swio_sm.put(write_address(WCH_DM_CFGR))
swio_sm.put(OUTSTA) 

swio_sm.active(1)
time.sleep_us(60)
swio_sm.active(0)

swio_sm.put(write_address(DM_CTRL))
swio_sm.put(0x80000001) ## 1: Debug module works properly 

swio_sm.active(1)
time.sleep_us(60)
swio_sm.active(0)

swio_sm.put(write_address(DM_CTRL))
swio_sm.put(0x80000003) ## Reboot

swio_sm.active(1)
time.sleep_us(60)
swio_sm.active(0)

swio_sm.put(write_address(DM_CTRL))
swio_sm.put(0x80000001) ## 1: Debug module works properly 

swio_sm.active(1)
time.sleep_us(60)
swio_sm.active(0)

swio_sm.put(read_address(DM_STATUS))
swio_sm.active(1)
status = swio_sm.get()

b32(write_address(DM_STATUS))
b32(status)
