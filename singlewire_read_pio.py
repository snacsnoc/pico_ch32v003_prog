import rp2

## Implement the WH32 single-wire protocol in a PIO

## Normal mode:
## 1    = low 1T to  4T, high 1T to 16T
## 0    = low 6T to 64T, high 1T to 16T
## Stop = high 18T
## If T = 125 ns
## Normal mode:
## 1    = low 125ns to  500ns, high 125ns to 2000ns
## 0    = low 750ns to 8000ns, high 125ns to 2000ns
## Stop = high 2250 ns


@rp2.asm_pio(set_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, autopush=True)  
def singlewire_read_pio():

    wrap_target()

    label("start")
    set(pindirs, 1)           .side(1)[0]
    pull()                    .side(1)[0] # Pull the address from the fifo, waiting if fifo empty
    out(y, 24)                .side(0)[1] # Move the block count to Y, leaving the address in O
    nop()                     .side(1)[1]

    label("addr_loop")
    out(x,1)                  .side(0)[0]
    jmp(not_x, "addr_zero")   .side(0)[0]
    nop()                     .side(0)[3]

    label("addr_zero")
    jmp(not_osre, "addr_loop").side(1)[1]

    label("read_repeat")
    set(x, 31)                .side(1)[1]

    label("read_loop")
    set(pindirs, 1)           .side(0)[1] ## 000 ns -- start pulse
    set(pindirs, 0)           .side(0)[1] ## 250 ns -- release start pulse and wait
    in_(pins, 1)              .side(0)[1]  ## 500 ns read and wait
    jmp(x_dec, "read_loop")   .side(0)[1] # 750 ns target should release pin

    nop()                     .side(1)[14]  ## long delay
    irq(1)                    .side(1)[14]
    jmp("start")              .side(1)[14]

    wrap()

