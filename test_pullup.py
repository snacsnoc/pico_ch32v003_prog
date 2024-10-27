from machine import Pin
import time

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW)
def dut():
    pull()
    set(x, 31)
    label("out")
    out(pins, 1) 
    jmp(x_dec, "out")
    ## then read them in?

    

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW)
def inputs_pio():
    ## then read them in?
    set(pindirs, 1)
    pull()
    set(x, 31)
    label("out")
    out(pins, 1) 
    jmp(x_dec, "out")

    set(pindirs, 0)
    set(x, 31) [5]
    label("input_loop")
    in_(pins, 1) 
    jmp(x_dec, "input_loop")
    push()


# gpio61 = Pin(18, Pin.OUT)
# mosheen = rp2.StateMachine(0, dut, freq=10_000, out_base=gpio61)
# mosheen.active(1)
# mosheen.put(0xAA0AA0AA)
# time.sleep_ms(10)
# mosheen.active(0)

gpio61 = Pin(18, Pin.IN, pull=None)
mosheen2 = rp2.StateMachine(1, inputs_pio, freq=10_000, in_base=gpio61, out_base=gpio61)
mosheen2.active(1)
mosheen2.put(0xAA0AA0A1)
invalue = mosheen2.get()
print(invalue)
mosheen2.active(0)



## take pin back?


