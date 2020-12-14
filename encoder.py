###########################################################################
#
# encoder.py
# Author:  Jonathan Lee
# Date:    2019-09-25
# Repository:
# https://github.com/jglee72/encoder-dac.git
# Description: Read an incremental encoder into two digital inputs of an RPI
#	Translte rotations from encoder to an analog output chip external to RPI
# 	Use a momentary button (integral in encoder) to enable/dis-able functionality
#	Pass enable/dis-able output to GSS API for its enabling functionality.
#	When disabled, output 2.5V from the ADC; Ignored by GSS API when disabled
# Hardware: Use of Adafruit MCP4725 12-bit ADC
#	Use a Bourns Mechanical or CUI Inc. optical quadrature (grey code)
#	encoder.
# Drivers: Install Adafruit_MCP4725 driver based on Adafruits archived
#	repository at https://github.com/adafruit/Adafruit_Python_MCP4725.git
#
#
# 2019-09-27 - JGL
#	- Remove ADC self check; done in ADC Class 
#
# 2019-09-30 - JGL
#	- Attempt command line options for seperate BCM pin definition
#	- Add list of BCM Pins, and method for checking validity
#
# 2019-10-02 - JGL
#	- Add new argument categories: {encoder resolution, encoder delays,
#	encoder bouncetime, button bouncetime}
#	- Add new output for a)triggering enable on micro computer and
#	b) to light an LED; add argument to change output pin 
#	- add try/exception for KeyBoardInterrupt to GPIO.cleanup() the io pins
# 2019-10-03 - JGL
#	- Set Led Default out to False (LO), clear false True (HI) on power up
#
# 2019-10-16 - JGL
#	- Add new argument categories: {encoder_led, encoder_en}
#	- Add new OP encoder_en; parallel to encoder_led for triggering GSS code
#	- Add different encoding for Optical Encoders which are different than
#		Mechanical encoders; 
#	- Add new argument for setting MECH_ENC with -m
# 
###########################################################################
import RPi.GPIO as GPIO
import time
import Adafruit_MCP4725
# for command line arguments
import sys
import argparse
# Globals
DEBUG = False
MECH_ENC = False
RPI_INPUT = set([0,1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
	22,23,24,25,26,27])

class encoder (object):
	''' Class for encdoder functions.  Expansion for multiple rotary encoders
		Addressed by i/o pin definition.
	'''
	def __init__(self, ip_a=5, ip_b=6, ip_pb=23, op_led=17, op_en=18 ,enc_bounce=30,btn_bounce=300,enc_resolution=10):
		self.input_a = ip_a
		self.input_b = ip_b
		self.input_pb = ip_pb
		self.enc_bouncetime = enc_bounce
		self.btn_bouncetime = btn_bounce
		self.rotation = 2048
		self.encoder_enabled = False
		self.enc_res = enc_resolution
		self.output_led = op_led
		self.output_en = op_en
		#Setup the IO
		self.setup_io()

		# Use callbacks to enable GPIO interrupts.
		# https://medium.com/@rxseger/interrupt-driven-i-o-on-raspberry-pi-3-with
		# -leds-and-pushbuttons-rising-falling-edge-detection-36c14e640fef
		# Note: Mechanical and Optical Encoders output differently:
		#	- Optical outputs are steady state - i.e. stay HI or LO until next indent
		#		It takes 4 indent clicks to go through cycle as stated in datasheet
		#	- Mechanical outputs momentary waveforms - i.e. always returns to LO
		if MECH_ENC:
			GPIO.add_event_detect(self.input_a,GPIO.FALLING, self.encoder_interrupt, self.enc_bouncetime)
			GPIO.add_event_detect(self.input_pb,GPIO.FALLING, self.enable_encoder, self.btn_bouncetime)
		else:
			GPIO.add_event_detect(self.input_a,GPIO.BOTH, self.encoder_interrupt, self.enc_bouncetime)
			GPIO.add_event_detect(self.input_b,GPIO.BOTH, self.encoder_interrupt, self.enc_bouncetime)
			GPIO.add_event_detect(self.input_pb,GPIO.FALLING, self.enable_encoder, self.btn_bouncetime)
	def read_encoder(self,pin):
		''' Simple function to return rpi gpio pin
		'''
		return GPIO.input(pin)

	def setup_io(self):
		''' Each encoder has a different set of pins for input
		'''
		if DEBUG:
			print("setting up IO...")
			print("Encoder inputs A, B, Pushbutton:",self.input_a, self.input_b, self.input_pb)
			print("Resolution, encoder debounce, button debounce:", self.enc_res, self.enc_bouncetime, self.btn_bouncetime)
		# BCM Mode uses Broadcom based definitions; not header pin numbering
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.input_a, GPIO.IN)
		GPIO.setup(self.input_b, GPIO.IN)
		GPIO.setup(self.input_pb, GPIO.IN)
		GPIO.setup(self.output_led, GPIO.OUT)
		GPIO.output(self.output_led, False)
		GPIO.setup(self.output_en, GPIO.OUT)
		GPIO.output(self.output_en, False)

	def pulse_trim_enable(self):
		GPIO.output(self.output_en, True)
		time.sleep(0.2)
		GPIO.output(self.output_en, False)

	def enable_encoder(self, pin):
		''' This function will toggle the encoder enable status when called
			and change output led, and/or send output to other micro-controller
		'''
		if DEBUG:
			print("toggled pin",pin)
			print("en1",self.encoder_enabled)
		self.rotation = 2048
		print ("rotation = ",self.rotation)
		self.encoder_enabled = not(self.encoder_enabled)
		if DEBUG:
			print("en2",self.encoder_enabled)
		if self.encoder_enabled == True:
			GPIO.output(self.output_led, True)
#			GPIO.output(self.output_en, True)
			self.pulse_trim_enable()
		else:
			GPIO.output(self.output_led, False)
#			GPIO.output(self.output_en, False)
			self.pulse_trim_enable()

	def encoder_interrupt(self,pin):
		''' Interrupt function called on 'pin' changes; see above for criteria
		'''
		if DEBUG:
			print ("up/down/ENABLE pin/enabled?:",pin, self.encoder_enabled)
		if self.encoder_enabled == False:
			if DEBUG:
				print("encoder disabled...push button to enable")
			return
		if MECH_ENC:
			# Limit detection taken care of in ADC class (0-4095 count)
			if (self.read_encoder(self.input_b) == 1):
				self.rotation += self.enc_res
			else:
				self.rotation -= self.enc_res
		else:
			# A has triggered interrupt
			if pin==5:
				if (self.read_encoder(self.input_a) == self.read_encoder(self.input_b)):
					self.rotation -= self.enc_res
				else:
					self.rotation += self.enc_res
			# B has triggered interrupt
			if pin==6:
				if (self.read_encoder(self.input_a) == self.read_encoder(self.input_b)):
					self.rotation += self.enc_res
				else:
					self.rotation -= self.enc_res
		if DEBUG:
			print ("rotation = ", self.rotation)

def check_input(args):
	''' Encoder require 3 inputs on the RPI, Check they are valid
	'''
	# Check for no arguments; quantity check done inline
	if DEBUG:
		print("Checking inputs inline argumnets: ", args)
	if args == None:
		if DEBUG:
			print(" Too many input arguments or None")
		return False
	# convert args to integers to test against a large integer set
	l_inputs = []
	for i in range(len(args)):
		l_inputs.append(int(args[i]))
	s_inputs = set(l_inputs)
	# check against RPI pins
	if s_inputs <= RPI_INPUT:
		if DEBUG:
			print("yes", set(args), RPI_INPUT,l_inputs,s_inputs)
		return True
	print("Input pins not valid")
	return False

def check_resolution(args):
	''' Encdoer resolution check.
	'''
	# Check for no arguments
	if DEBUG:
		print("Checking resolution inline argumnets: ", args)
	if (args == None or int(args) < 0 or int(args) >200):
		if DEBUG:
			print ("Resolution out of range (0-200), or None")
		return False
	else:
		return True

def check_button_bounce(args):
	''' Button Bouncetime check
	'''
	# Check for no arguments
	if DEBUG:
		print("Checking button bounce inline argumnets: ", args)
	if (args == None or int(args) < 0 or int(args) >1000):
		if DEBUG:
			print ("Button Bounce out or range (0-1000), or None")
		return False
	else:
		return True

def check_encoder_bounce(args):
	''' Encoder bouncetime check
	'''
	# Check for no arguments
	if DEBUG:
		print("Checking encoder bounce inline argumnets: ", args)
	if (args == None or int(args) < 0 or int(args) >100):
		if DEBUG:
			print ("Button Bounce out or range (0-100), or None")
		return False
	else:
		return True

def main():
	# Need global reference to change global constant
	global DEBUG
	global MECH_ENC
	# Contruct the argument parser and parse the arguments
	ap = argparse.ArgumentParser(description='Take incremental encoders to output analog voltage via ADC')
	ap.add_argument("-d", "--debug", action='store_true', required=False,
		help="Output inline debug comments")
	ap.add_argument("-i", "--input", nargs = 3, required=False,
		help="change main encoder pins A B and PB associated RPI pins (BCM numbering), eg -i 5 6 13. Expects 3 arguments ")
	ap.add_argument("-o", "--output", nargs = 2, required=False,
		help="change main encoder pins LED and EN  associated RPI pins (BCM numbering), eg -o 18 17. Expects 2 arguments ")
	ap.add_argument("-r", "--resolution", required=False,
		help="Resolution of main encoder (range 0-200). Resolution/4096 x 5V (Default 10= [12mV/enc detent])")
	ap.add_argument("-b", "--button", required=False,
		help="Button Bouncetime in mS (range 0-1000). Ignores noise and button bounce (default: 300)")
	ap.add_argument("-e", "--encoder", required=False,
		help="Encoder Bouncetime in mS (range 0-100). Ignores noise and encoder errors (default: 30)")
	ap.add_argument("-m", "--mech", action='store_true', required=False,
		help="Encoder Type, use -m for a mechanical encoder (default: optical encoder)")
	args = vars(ap.parse_args())

	if (args["debug"]==True):
		DEBUG=True
		print ("DEBUG Enabled...", DEBUG)
		print ("Argparse arguments:", args)
		print ("sys.argv: number of arguments:", len(sys.argv))
		print ("sys.argv: argument list:", str(sys.argv))

	if (args["mech"]==True):
		MECH_ENC=True
		print ("MECHANICAL ENCODER is Enabled...", MECH_ENC)

	# raspberry pi/project functionality to GPIO numbers (not pin numbers)

	# Encoder 1 (main encoder) hardware pinout
	if DEBUG:
		print("args:", args)
	if (check_input(args["input"]) == True):
		# do thses need int(args[n])?
		encoder_1_a = int(args["input"][0])
		encoder_1_b = int(args["input"][1])
		encoder_1_pb = int(args["input"][2])
	else:
		print("..using default i/o pins")
		encoder_1_a = 5
		encoder_1_b = 6
		encoder_1_pb = 23
	if (check_input(args["output"]) == True):
		encoder_1_led = int(args["output"][0])
		encoder_1_en = int(args["output"][1])
	else:
		print("..using default i/o pins")
		encoder_1_led = 17
		encoder_1_en = 18

	# Encoder 1 (main encoder) resolution settings
	if (check_resolution(args["resolution"])== True):
		encoder_1_res = int(args["resolution"])
	else:
		print("...using default resolution")
		encoder_1_res = 10;

	# Encoder 1 (main encoder) bounce settings
	if (check_encoder_bounce(args["encoder"])== True):
		encoder_1_bounce = int(args["encoder"])
	else:
		print("...using default encoder bouncetime")
		encoder_1_bounce = 30;

	# Button 1 (usually main encoder) bounce settings
	if (check_button_bounce(args["button"])== True):
		button_1_bounce = int(args["button"])
	else:
		print("...using default button bouncetime")
		button_1_bounce = 300;

	# DAC 1 hardware address
	dac_1_address = 0x62
	# RPI I2C may always be bus 1
	bus_num = 1

	trim_encoder_1  = encoder(encoder_1_a, encoder_1_b, encoder_1_pb,
		encoder_1_led, encoder_1_en, enc_bounce=encoder_1_bounce,
		btn_bounce=button_1_bounce, enc_resolution=encoder_1_res)
	dac1 = Adafruit_MCP4725.MCP4725(address=dac_1_address, busnum=bus_num)

	try:
		while(1):
			dac1.set_voltage(trim_encoder_1.rotation)
			# Delay required to set CPU useage to approx 3%
			time.sleep(0.01)
	except KeyboardInterrupt:
		print("end it!")
		GPIO.cleanup()

if __name__=='__main__':
	main()
