import RPi.GPIO as GPIO
import time
import Adafruit_MCP4725

#input output definitions if needed
DEBUG = False
#DEBUG = True

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
# Drivers: Install Adafruit_MCP4725 driver based on Adafruits archived
#	repository at https://github.com/adafruit/Adafruit_Python_MCP4725.git
#
###########################################################################

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
		# Limit ouput of ADC to 0 and 5V (4096 count)
		if (self.read_encoder(self.input_b) == 1):
			self.rotation += self.rot_delta
			if self.rotation > 4096: self.rotation=4096
		else:
			self.rotation -= self.rot_delta
			if self.rotation < 0: self.rotation=0
		print ("rotation = ",self.rotation)

def main():
	# raspberry pi/project functionality to GPIO numbers (not pin numbers)
	# Encoder 1 hardware pinout 
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



