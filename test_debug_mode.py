
import singlewire_pio
import gc
from machine import Pin

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

gc.disable()
gc.collect()

def b32(num):
    aa = (num & 0xFF000000) >> 24 
    bb= (num & 0x00FF0000) >> 16
    cc= (num & 0x0000FF00) >> 8
    dd= num & 0x000000FF
    print(f'{aa:#010b} {bb:#010b} {cc:#010b} {dd:#010b}')


def read_address(register):
    return(register << 1)
def write_address(register):
    return((register << 1) + 1)

inter_packet_delay = 60 

def send_write(address, data, delay=inter_packet_delay):
    swio_sm.put(write_address(address))
    swio_sm.put(data)
    swio_sm.active(1)
    time.sleep_us(delay)
    swio_sm.active(0)

def send_read(address, delay=inter_packet_delay):
    swio_sm.put(read_address(address))
    swio_sm.active(1)
    time.sleep_us(delay)
    swio_sm.active(0)
    return(swio_sm.get())

WCH_DM_CPBR     = const(0x007C)
WCH_DM_CFGR     = const(0x007D)
WCH_DM_SHDWCFGR = const(0x007E)
WCH_DM_PART     = const(0x007F) # not in doc but appears to be part info
SECRET          = const(0x5AA50000)
OUTSTA          = const(SECRET | (1 << 10)) ## OUTSTA: 0: The debug slave has output function.
DM_CTRL         = const(0x0010)  ## in debug mode
DM_STATUS       = const(0x0011)  # debug mode, read/write

# MCF.WriteReg32( dev, DMSHDWCFGR, 0x5aa50000 | (1<<10) ); // Shadow Config Reg
# MCF.WriteReg32( dev, DMCFGR, 0x5aa50000 | (1<<10) ); // CFGR (1<<10 == Allow output from slave)
# MCF.WriteReg32( dev, DMCONTROL, 0x80000001 ); // Make the debug module work properly.
# if( mode == HALT_MODE_HALT_AND_RESET ) MCF.WriteReg32( dev, DMCONTROL, 0x80000003 ); // Reboot.
# MCF.WriteReg32( dev, DMCONTROL, 0x80000001 ); // Re-initiate a halt request.

## blip?

send_write(WCH_DM_SHDWCFGR, OUTSTA)
send_write(WCH_DM_CFGR, OUTSTA)
send_write(DM_CTRL, 0x80000001) ## 1: Debug module works properly 
send_write(DM_CTRL, 0x80000003) ## reboot
send_write(DM_CTRL, 0x80000001) ## 1: Debug module works properly 
status = send_read(DM_STATUS)
b32(status)

