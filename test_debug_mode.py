
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
capabilities = send_read(WCH_DM_CPBR)
b32(status)
b32(capabilities)

## OK, now flash in the bootloader
## Some debug-mode constants
DMDATA0 = const(0x04)
DMDATA1 = const(0x05)
DMCONTROL = const(0x10)
DMSTATUS = const(0x11)
DMHARTINFO = const(0x12)
DMABSTRACTCS = const(0x16)
DMCOMMAND = const(0x17)
DMABSTRACTAUTO = const(0x18)

FLASH_STATR_WRPRTERR = const(0x10)
CR_PAGE_PG           = const(0x00010000)
CR_BUF_LOAD          = const(0x00040000)
FLASH_CTLR_MER       = const(0x0004)   #  /* Mass Erase */)
CR_STRT_Set          = const(0x00000040)
CR_PAGE_ER           = const(0x00020000)
CR_BUF_RST           = const(0x00080000)

DMPROGBUF0 = const(0x20)
DMPROGBUF1 = const(0x21)
DMPROGBUF2 = const(0x22)
DMPROGBUF3 = const(0x23)
DMPROGBUF4 = const(0x24)
DMPROGBUF5 = const(0x25)
DMPROGBUF6 = const(0x26)
DMPROGBUF7 = const(0x27)

def wait_for_done():
    is_busy = True
    while is_busy:
        abstract_control_status = send_read(DMABSTRACTCS)
        if (abstract_control_status & (1 << 12)) == 0:  ## abstract command busy bit
            is_busy = False

def setup_flash(data, address):
    send_write( DMABSTRACTAUTO, 0x00000000 )  #; // Disable Autoexec.
    ## Program loads up data, writes it into memory, adds 4 to address, and stores it back
    send_write( DMPROGBUF0, 0xc0804184 )  #  c.sw x8, 0(x9)  c.lw x9, 0(x11)
    ## loads address from x11 into x9, writes x8 into mem[x9]
    send_write( DMPROGBUF1, 0xc1840491 )  #  c.sw x9, 0(x11) c.addi x9, 4
    ## adds 4 to address in x9, writes it back out to x11 for next round
    send_write( DMPROGBUF2, 0x9002c214 )  # c.sw x13,0(x12) // Acknowledge the page write. c.ebreak
    ## copies the PG/BUF_LOAD flags into flash controller
    
    send_write( DMDATA0, 0xe00000f4 )  #;   // DATA0's location in memory.
    send_write( DMCOMMAND, 0x0023100a )  #; // Copy data to x10
    send_write( DMDATA0, 0xe00000f8 )  #;   // DATA1's location in memory.
    send_write( DMCOMMAND, 0x0023100b )  #; // Copy data to x11
    send_write( DMDATA0, 0x40022010 )  #; // FLASH->CTLR
    send_write( DMCOMMAND, 0x0023100c )  #; // Copy data to x12
    send_write( DMDATA0, CR_PAGE_PG|CR_BUF_LOAD)  #;
    send_write( DMCOMMAND, 0x0023100d )  #; // Copy data to x13

    send_write( DMDATA1, address )  #;
    send_write( DMDATA0, data )  #;

    send_write( DMCOMMAND, 0x00271008 )  #; // Copy data0 to x8, and execute program.
    send_write( DMABSTRACTAUTO, 1 )  #; // Enable Autoexec.
    wait_for_done()

def write_word(data, address):
    send_write( DMDATA1, address )  #;
    send_write( DMDATA0, data )  # load data into DMDATA0;
    wait_for_done()

def flash_bin(filename):
    binary_image = open(filename, "b").read()
    if len(binary_image) % 4 != 0:
        raise BaseException("Binary not even word length, handle me!")

    address = 0x08000000 
    first_time = True
    for wordstart in range(0, len(binary_image), 4):
        word = binary_image[wordstart:(wordstart+4)]
        print(word.hex())
        word_value = int(word[0] << 24) + int(word[1] << 16) + int(word[2] << 8) + int(word[3])
        if first_time:
            setup_flash(word_value, address)
            first_time = False
        else:
            write_word(word_value, address)
        address = address + 4

# flash_bin("blink.bin")

print("unlocking flash")
flash_ctrler = send_read(0x40022010)
b32(flash_ctrler)


send_write( 0x40022004, 0x45670123 )  #; // FLASH->KEYR = 0x40022004
send_write( 0x40022004, 0xCDEF89AB )  #;
send_write( 0x40022008, 0x45670123 )  #; // OBKEYR = 0x40022008
send_write( 0x40022008, 0xCDEF89AB )  #;
send_write( 0x40022024, 0x45670123 )  #; // MODEKEYR = 0x40022024
send_write( 0x40022024, 0xCDEF89AB )  #;

flash_ctrler = send_read(0x40022010)
b32(flash_ctrler)


## reset and resume
if True:
    status = send_read(DM_STATUS)
    b32(status)
    send_write( DM_CTRL, 0x80000001)  
    send_write( DM_CTRL, 0x80000001) 
    send_write( DM_CTRL, 0x00000001)  
    send_write( DM_CTRL, 0x40000001)
    time.sleep_us(30)
    status = send_read(DM_STATUS)
    b32(status)






    

