
# test if I can use the pindirs + pullup/down to signal
# then could keep it always in input mode, just toggle?

from machine import Pin
import time

    # ## glitch replaces
    # nop() .side(0)[2] # rising
    
    # with

    # set(pins, 1).side(1)[0] ## glitch up
    # set(pins, 0).side(0)[0] ## undo glitch, and go high-z
    # nop().side(0)[0]



@rp2.asm_pio(set_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, sideset_init=rp2.PIO.OUT_LOW)
def dut():
    set(pins, 0)
    wrap_target()

    nop() .side(1)[4] #falling
    in_(pins, 1)
    
    set(pins, 1).side(1)[0] ## glitch up
    set(pins, 0).side(0)[0] ## undo glitch, and go high-z
    nop() .side(0)[2] # rising
    in_(pins, 1)
    
    nop() .side(1)[4] # falling 
    in_(pins, 1)
   
    set(pins, 1).side(1)[0] ## glitch up, hold high?
    set(pins, 0).side(0)[0] ## undo glitch, and go high-z
    nop() .side(0)[1] # rising
    in_(pins, 1)
    push()
    
    wrap()




#     set(pins, 1)[0]
#     set(pindirs, 0)[2]
#     set(pins, 0)[0]  ## and clean up


gpio61 = Pin(18, Pin.IN, pull=Pin.PULL_UP)
time.sleep_ms(1)
mosheen2 = rp2.StateMachine(0, dut, freq=10_000_000, in_base=gpio61, out_base=gpio61, set_base=gpio61, sideset_base=gpio61)
# gpio61 = Pin(18, Pin.OPEN_DRAIN)

## add sideset pin action
SIDE_PINDIR  = const(29)
PIO0_BASE    = const(0x50200000)
SM0_EXECCTRL = const(PIO0_BASE + 0x0cc)  # p 375
## Set side-set to control pindire on machine 0
machine.mem32[SM0_EXECCTRL] = machine.mem32[SM0_EXECCTRL]  | (1 << SIDE_PINDIR)


mosheen2.restart()
mosheen2.active(1)
time.sleep_ms(100)
mosheen2.active(0)



