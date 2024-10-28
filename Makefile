all: test_sideset_pindirs
#all: test_pindirs

%: %.py
	mpremote a1 run $^

