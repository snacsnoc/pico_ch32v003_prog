
import singlewire_pio
import gc
from machine import Pin
from constants import *

gpio61 = Pin(18, mode=Pin.IN, pull=Pin.PULL_UP)

swio_sm = rp2.StateMachine(4, singlewire_pio.singlewire_pio, freq=12_000_000,
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

def enter_debug_mode():
    send_write(WCH_DM_SHDWCFGR, OUTSTA)
    send_write(WCH_DM_CFGR, OUTSTA) ## OUTSTA: 0: The debug slave has output function.
    ## guarantee halt
    send_write(DM_CTRL, 0x80000001) ## 1: Debug module works properly 
    send_write(DM_CTRL, 0x80000003) ## 1: Debug module works properly 
    send_write(DM_CTRL, 0x80000001) ## 1: halt
    send_write(DM_CTRL, 0x80000001) ## 1: halt
    send_write(DM_CTRL, 0x80000001) ## 1: halt

def print_status_capabilities():
    status = send_read(DM_STATUS)
    print("status")
    b32(status)
    capabilities = send_read(WCH_DM_CPBR)
    print("capabilities")
    b32(capabilities)

## OK, now flash in the bootloader

def wait_for_done():
    is_busy = True
    while is_busy:
        abstract_control_status = send_read(DMABSTRACTCS)
        if (abstract_control_status & (7<<8)):
            raise Exception(f"error, bail out: abs_ctrl {hex(abstract_control_status)}")
        if (abstract_control_status & (1 << 12)) == 0:  ## abstract command busy bit
            is_busy = False

def write_word(address, data):
    send_write( DMABSTRACTAUTO, 0x00000000 )  #; // Disable Autoexec.
    
    send_write( DMDATA0, 0xe00000f4 )  #;   // DATA0's location in memory.
    send_write( DMCOMMAND, 0x00231008 )  #; // Copy data to x8
    send_write( DMDATA0, 0xe00000f8 )  #;   // DATA1's location in memory.
    send_write( DMCOMMAND, 0x00231009 )  #; // Copy address to x9

    send_write( DMDATA0, data )  #;
    send_write( DMDATA1, address )  #;
    
    send_write( DMPROGBUF0, 0x408c_4008 )  #  
    send_write( DMPROGBUF1, 0x9002_c188 )  #    
    
    send_write( DMCOMMAND, ((1 << 18) | (1<<21)) )  # execute program
    wait_for_done()

def read_word(address):
    send_write( DMABSTRACTAUTO, 0x00000000 )  #; // Disable Autoexec.
    
    send_write( DMDATA0, 0xe00000f4 )  #;   // DATA0's location in memory.
    send_write( DMCOMMAND, 0x00231008 )  #; // Copy data to x8
    send_write( DMDATA0, 0xe00000f8 )  #;   // DATA1's location in memory.
    send_write( DMCOMMAND, 0x00231009 )  #; // Copy address to x9

    send_write( DMDATA0, address )  # ;
    
    send_write( DMPROGBUF0, 0x4108_4008)   # lw x10 0(x10)   lw x10 0(x8) 
    send_write( DMPROGBUF1, 0x9002_c008)     # sw x10, 0(x8)
    # break 
    send_write( DMCOMMAND, ((1 << 18) | (1<<21)) )  # execute program
    wait_for_done()
    data = send_read(DMDATA0)
    return(data)

def wait_for_flash():
    ## add timeout
    for i in range(200):
        rw = read_word( 0x4002200C )  # FLASH_STATR => 0x4002200C
        if not (rw & 1):   # BSY flag 
            break
    write_word( 0x4002200C, 0 )  #;
    if( rw & FLASH_STATR_WRPRTERR ):
        raise Exception("Misc Flash error")

    if( rw & 1 ):
        raise Exception("Flash timed out")

def unlock_flash():
    rw = read_word( 0x40022010 )  # FLASH->CTLR = 0x40022010
    if( rw & 0x8080 ):
        write_word( 0x40022004, 0x45670123 )  #; // FLASH->KEYR = 0x40022004
        write_word( 0x40022004, 0xCDEF89AB )  #;
        write_word( 0x40022008, 0x45670123 )  #; // OBKEYR = 0x40022008
        write_word( 0x40022008, 0xCDEF89AB )  #;
        write_word( 0x40022024, 0x45670123 )  #; // MODEKEYR = 0x40022024
        write_word( 0x40022024, 0xCDEF89AB )  #;
        rw = read_word( 0x40022010 )  # FLASH->CTLR = 0x40022010
        if( rw & 0x8080 ):
            raise Exception("flash could not be unlocked")

def erase_chip():
    write_word( 0x40022010, 0 )  # FLASH->CTLR = 0x40022010
    write_word( 0x40022010, FLASH_CTLR_MER  )  #;
    write_word( 0x40022010, CR_STRT_Set|FLASH_CTLR_MER )  #;
    wait_for_flash()
    write_word( 0x40022010, 0 )  #  FLASH->CTLR = 0x40022010

def simple_64_byte_write(start_address, data):
    """start_address = MUST_BE_64_BYTE_ALIGNED;"""

    write_word( 0x40022010, CR_BUF_RST | CR_PAGE_PG )
    b32(read_word(0x40022010))
    wait_for_flash()
    
    for i in range(16): 
        addr = start_address+(i*4)
        value = int.from_bytes(data[(i*4):(i*4)+4])
        print(hex(addr), hex(value))
        write_word( addr, value )
        write_word( 0x40022010, CR_BUF_LOAD) # set FLASH->CTLR BUFLOAD bit to load buffer
        wait_for_flash()

    write_word( 0x40022014, start_address )  # ;
    write_word( 0x40022010, CR_STRT_Set ) #;  // R32_FLASH_CTLR
    wait_for_flash()


## reset and resume
def reset_and_resume():
    send_write( DM_CTRL, 0x80000001)  
    send_write( DM_CTRL, 0x80000001) 
    send_write( DM_CTRL, 0x00000001)  
    send_write( DM_CTRL, 0x40000001)

def flash_binary(filename):
    data = open(filename, "b").read()
    
    for i in range(len(data) // 64): 
        byte_block = data[i*64:(i+1)*64]
        simple_64_byte_write(0x0800_0000 + i*64, byte_block)
    if len(data) % 64:
        residual = bytearray([0xff] * 64) 
        for j, this_byte in enumerate(data[(i+1)*64:]):
            residual[j] = this_byte
        simple_64_byte_write(0x0800_0000 + (i+1)*64, residual)

enter_debug_mode()

#unlock_flash()
#erase_chip()
#flash_binary("blink2.bin")

for i in range(4096):
    print(i)
    print(hex(read_word(0x0800_0000+i*4)))

#reset_and_resume()



