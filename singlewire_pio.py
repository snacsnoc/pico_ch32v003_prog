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


#@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH)  
@rp2.asm_pio(set_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, sideset_init=rp2.PIO.OUT_LOW)
def singlewire_pio(autopush=True):

    wrap_target()
    label("start")

    pull()                     .side(0)[2]  #  Pull the address from the fifo and let the bus pull high for 300 ns
    out(y, 24)                 .side(1)[1]  #  Move high 24 bits of the address to y and send the start bit
    nop()                      .side(0)[2]  #  end start bit, pull up for 2T

    label("addr_loop")
    out(x, 1)                  .side(1)[0]  # short pulse 200 ns
    jmp(not_x, "addr_zero")    .side(1)[0]
    nop()                      .side(1)[5]  # long pulse 800ns

    label("addr_zero")
    jmp(not_osre, "addr_loop") .side(0)[2]  # end bit, pull up 300 ns

    jmp(not_x, "op_write")     .side(0)[0]  # Read/write bit
    jmp("op_read")             .side(0)[0]

    label("op_read")
    set(x, 31)                 .side(0)[0]
    
    label("read_loop")
    nop()                      .side(1)[1]  #  000 ns - Start pulse. Target will drive pin low starting immediately and continue for ~800 ns to signal 0.
#    set(pins, 1).side(1)[0]                 ## pull up hard, driven value to 1
#    set(pins, 0).side(1)[0]                 ## reset to high-z, with driven value 0 
    nop()                      .side(0)[2]  #  200 ns - Release start pulse, wait for pin to rise if target isn't driving it
    in_(pins, 1)               .side(0)[2]  #  500 ns - Read pin and then wait for target to release it.
    jmp(x_dec, "read_loop")    .side(0)[2]  #  800 ns - Pin should be going high by now.
    nop()                      .side(0)[6]
    jmp("start")               .side(0)[10]

    label("op_write")
    pull()                     .side(0)[1]

    label("write_loop")
    out(x,1)                   .side(1)[0]
    jmp(not_x, "data_zero")    .side(1)[0]
    nop()                      .side(1)[5]

    label("data_zero")
    jmp(not_osre, "write_loop").side(0)[2] # end bit and pull up for 300 ns
    nop()                      .side(0)[6]
    jmp("start")               .side(0)[10]
    
    wrap()




