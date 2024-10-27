from machine import Pin
import time

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW)
def dut():
    pull()
    set(pindirs, 1)
    set(x, 31)
    label("out")
    out(pins, 1) 
    jmp(x_dec, "out")


gpio61 = Pin(18, Pin.IN)#, pull=Pin.PULL_DOWN)
mosheen = rp2.StateMachine(0, dut, freq=10_000, out_base=gpio61)
mosheen.active(1)

mosheen.put(0xAAAAAAAA)
#print(mosheen.get())


time.sleep_ms(1)
# mosheen.active(0)

## take pin back?


