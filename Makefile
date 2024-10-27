all: test_transmit

%: %.py
	mpremote a1 run $^

