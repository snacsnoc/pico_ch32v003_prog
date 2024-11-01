# all: test_sideset_pindirs
#all: test_singlewire_read_pio

MPREMOTE:=mpremote

all: copy_pio test_debug_mode_new

copy_pio: 
	${MPREMOTE} cp singlewire_pio.py :

%: %.py
	${MPREMOTE} run $^

