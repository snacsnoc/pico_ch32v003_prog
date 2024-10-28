# all: test_sideset_pindirs
#all: test_singlewire_read_pio

all: test_debug_mode

copy_pio: 
	mpremote a1 cp singlewire_pio.py :

%: %.py
	mpremote a1 run $^

