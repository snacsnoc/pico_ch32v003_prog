from machine import Pin
import time

@rp2.asm_pio(set_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, sideset_init=rp2.PIO.OUT_LOW)
def dut():
    set(pins, 0)
    wrap_target()
    nop() .side(1)
    in_(pins, 1)
    nop() .side(0)
    in_(pins, 1)
    nop() .side(1)
    in_(pins, 1)
    nop() .side(0)
    in_(pins, 1)
    push()
    wrap()

gpio61 = Pin(18, Pin.IN, pull=Pin.PULL_UP)

sm = rp2.StateMachine(0, dut, freq=10_000, in_base=gpio61, out_base=gpio61, set_base=gpio61, sideset_base=gpio61)

SIDE_PINDIR  = const(29)
PIO0_BASE    = const(0x50200000)
SM0_EXECCTRL = const(PIO0_BASE + 0x0cc)  # p 375
## Set side-set to control pindire on machine 0
machine.mem32[SM0_EXECCTRL] = machine.mem32[SM0_EXECCTRL]  | (1 << SIDE_PINDIR)

sm.restart()
sm.active(1)
time.sleep_ms(100)
print(bin(sm.get()))
sm.active(0)






