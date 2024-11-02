# all: test_sideset_pindirs
#all: test_singlewire_read_pio

MPREMOTE:=mpremote

all: flash_ch32v003

copy_pio: 
	${MPREMOTE} cp singlewire_pio.py :


.copied_constants :
	${MPREMOTE} cp constants.py : 
	touch .copied_constraints

copy_constants : .copied_constants

copy_blink: copy_constants
	${MPREMOTE} cp blink.bin : 

copy_blink2:
	${MPREMOTE} cp blink2.bin : 

%: %.py
	${MPREMOTE} run $^

