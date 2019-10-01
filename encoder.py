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
RPI_INPUT = set([0,1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
	22,23,24,25,26,27])

class encoder (object):
	''' Class for encdoder functions.  Expansion for multiple rotary encoders
		Addressed by i/o pin definition.
	'''
	def __init__(self, ip_a, ip_b, ip_pb):
		self.input_a = ip_a
		self.input_b = ip_b
		self.input_pb = ip_pb
		self.setup_io()
		self.enc_bouncetime = 30
		self.btn_bouncetime = 300
		self.rotation = 2040
		self.encoder_enabled = False
		self.rot_delta = 10

		# Use callbacks to enable GPIO interrupts.
		# https://medium.com/@rxseger/interrupt-driven-i-o-on-raspberry-pi-3-with
		# -leds-and-pushbuttons-rising-falling-edge-detection-36c14e640fef
		GPIO.add_event_detect(self.input_a,GPIO.FALLING, self.encoder_interrupt, self.enc_bouncetime)
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
		# BCM Mode uses Broadcom based definitions; not header pin numbering
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.input_a, GPIO.IN)
		GPIO.setup(self.input_b, GPIO.IN)
		GPIO.setup(self.input_pb, GPIO.IN)

	def enable_encoder(self, pin):
		''' This function will toggle the encoder enable status when called
		'''
		if DEBUG:
			print("toggled pin",pin)
			print("en1",self.encoder_enabled)
		self.rotation = 2048
		print ("rotation = ",self.rotation)
		self.encoder_enabled = not(self.encoder_enabled)
		if DEBUG:
			print("en2",self.encoder_enabled)

	def encoder_interrupt(self,pin):
		''' Interrupt function called on pin A (clk) changes
		'''
		if DEBUG:
			print ("up/down/ENABLE",pin, self.encoder_enabled)
		if self.encoder_enabled == False:
			if DEBUG:
				print("encoder disabled...push button to enable")
			return
		# Limit detection taken care of in ADC class (0-4095 count)
		if (self.read_encoder(self.input_b) == 1):
			self.rotation += self.rot_delta
		else:
			self.rotation -= self.rot_delta
		if DEBUG:
			print ("rotation = ", self.rotation)

def check_input(args):
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
	print("no input or not valid")
	return False

def main():
	# Need global reference to change global constant
	global DEBUG
	# Contruct the argument parser and parse the arguments
	ap = argparse.ArgumentParser(description='Take incremental encoders to output analog voltage via ADC')
	ap.add_argument("-d", "--debug", action='store_true', required=False,
		help="Output inline debug comments")
	ap.add_argument("-i", "--input", nargs = 3, required=False,
		help="change main encoder pins A B and PB associated RPI pins (BCM numbering)")
	args = vars(ap.parse_args())
	if (args["debug"]==True):
		DEBUG=True
		print ("DEBUG Enabled...", DEBUG)
		print ("Argparse arguments:", args)
		print ("sys.argv: number of arguments:", len(sys.argv))
		print ("sys.argv: argument list:", str(sys.argv))

	# raspberry pi/project functionality to GPIO numbers (not pin numbers)
	# Encoder 1 (main encoder) hardware pinout
	# has no len if empty...so what to trigger on?
	if DEBUG:
		print("args", args)
	if (check_input(args["input"]) == True):
		# do thses need int(args[n])?
		encoder_1_a = int(args["input"][0])
		encoder_1_b = int(args["input"][1])
		encoder_1_pb = int(args["input"][2])
	else:
		print("..using default i/o pins")
		encoder_1_a = 5
		encoder_1_b = 6
		encoder_1_pb = 13

	# DAC 1 hardware address
	dac_1_address = 0x62
	# RPI I2C may always be bus 1
	bus_num = 1

	trim_encoder_1  = encoder(encoder_1_a, encoder_1_b, encoder_1_pb)
	dac1 = Adafruit_MCP4725.MCP4725(address=dac_1_address, busnum=bus_num)


	while(1):
		dac1.set_voltage(trim_encoder_1.rotation)
		# Delay required to set CPU useage to approx 3%
		time.sleep(0.01)

if __name__=='__main__':
	main()



