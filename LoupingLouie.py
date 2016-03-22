from time import sleep
from random import randrange
import RPi.GPIO as io
io.setmode(io.BCM)

in1_pin = 4	# direction +
in2_pin = 17	# direction -
in3_pin = 23	# change direction
in4_pin = 24	# faster
in5_pin = 25	# slower
in6_pin = 22	# switch program
in7_pin = 7	# led program 1
in8_pin = 8	# led program 2
in9_pin = 9	# led program 3

bool1 = False
bool2 = False
stoped = False
speed= 50
program = 1 # 1 = self 2 = random speed 3 = random speed + direction
oldprogram = 1
time_passed = 0
time_till_next_speed_change = 4 # for program 2
PLAY = True

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)
io.setup(in3_pin, io.IN)
io.setup(in4_pin, io.IN)
io.setup(in5_pin, io.IN)
io.setup(in6_pin, io.IN)
io.setup(in7_pin, io.OUT)
io.setup(in8_pin, io.OUT)
io.setup(in9_pin, io.OUT)

def set(property, value):
	try:
		f = open("/sys/class/rpi-pwm/pwm0/" + property, 'w')
		f.write(value)
		f.close()
	except:
		print("Error writing to: " + str(property) + " value " + str(value))

set("delayed", "immediate")
set("mode", "pwm")
set("frequency", "500")
set("active", "1")

def clockwise():
	global bool1
	global bool2
	bool1 = True
	bool2 = False
	apply_changes()
	#io.output(in1_pin, True)
	#io.output(in2_pin, False)

def counter_clockwise():
	global bool1
	global bool2
	bool1 = False
	bool2 = True
	apply_changes()
	#io.output(in1_pin, False)
	#io.output(in2_pin, True)
    
def change_direction():
    global bool1
    global bool2
    helpbool = bool1
    bool1 = bool2
    bool2 = helpbool
    apply_changes()

def stop_start():
	global stoped
	if stoped:
		apply_changes()
		stoped = False
	else:
		io.output(in1_pin, False)
		io.output(in2_pin, False)
		stoped = True

def faster():
	global speed
	if speed == 0:
		speed = 20
		stop_start()
	else:
		if speed < 100:
			speed += 10
		apply_changes()

def slower():
	global speed
	if speed > 20:
		speed -= 10
		apply_changes()
	else:
		if (speed > 0):
			speed = 0
			stop_start()

def apply_changes():
	io.output(in1_pin, bool1)
	io.output(in2_pin, bool2)
	set("duty", str(speed))
	print("Applied bool1: " + str(bool1) + " bool2: " + str(bool2) + " speed: " + str(speed))

def apply_program():
	if program == 1:
		io.output(in7_pin, io.LOW)
		io.output(in8_pin, io.HIGH)
		io.output(in9_pin, io.HIGH)
	elif program == 2:
		io.output(in7_pin, io.HIGH)
		io.output(in8_pin, io.LOW)
		io.output(in9_pin, io.HIGH)
	elif program == 3:
		io.output(in7_pin, io.HIGH)
		io.output(in8_pin, io.LOW)
		io.output(in9_pin, io.LOW)
	else:
		io.output(in7_pin, io.LOW)
		io.output(in8_pin, io.LOW)
		io.output(in9_pin, io.LOW)

clockwise()
apply_program()

while PLAY:
	if program == 1:
		print("round and round")

		if (io.input(in3_pin) == False):
			change_direction()

		if (io.input(in4_pin) == False and io.input(in5_pin) == True):
			faster()

		if (io.input(in5_pin) == False and io.input(in4_pin) == True):
			slower()

	elif (program == 2 or program == 3):
		print ("Time till next speed change: " + str(time_till_next_speed_change - time_passed % time_till_next_speed_change))
		
		if ((time_passed % time_till_next_speed_change) == 0):
			time_till_next_speed_change = randrange(1,4)
			speed = (randrange(20,100,10))
			print("changing speed to " + str(speed))
			if (speed < 30):
				if stoped:
					time_till_next_speed_change = 0.5
				else:
					stop_start()
			else:
				if stoped:
					stop_start()
				else:
					apply_changes()
	if (program == 3):
		if ((time_passed % 2) == 0):
			randombool = randrange(8)
			if (randombool == 0):
				counter_clockwise()
			else:
				clockwise()

	if (io.input(in6_pin) == False):
		if (program < 3):
			program += 1
		else:
			program = 1
		print("changed program to " + str(program))
		apply_program()

	if (io.input(in4_pin) == False and io.input(in5_pin) == False and io.input(in3_pin) == True):
		if program == 0:
			program = oldprogram
		else:
			oldprogram = program
			program = 0
		stop_start()
		apply_program()

	if (io.input(in4_pin) == False and io.input(in5_pin) == False and io.input(in3_pin) == False):
		PLAY = False

	sleep(0.5)
	time_passed += 0.5
