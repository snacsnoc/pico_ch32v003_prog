## OK, here goes!
import singlewire_pio
from machine import Pin

gpio61 = Pin(18, Pin.OUT)

#foobar = rp2.StateMachine(2, singlewire_pio.foo, freq=10000, sideset_base=gpio61)
#foobar.active(1)


mosheen = rp2.StateMachine(1, singlewire_pio.singlewire_pio, freq=10_000_000,
                                   sideset_base=gpio61)
mosheen.active(1)

gpio61.value(1)
mosheen.put(0x0ABC)
gpio61.value(1)
mosheen.put(0x1234)
gpio61.value(1)

