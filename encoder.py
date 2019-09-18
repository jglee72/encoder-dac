import RPi.GPIO as GPIO
import time
import Adafruit_MCP4725

#input output definitions if needed
DEBUG = False
#DEBUG = True


class encoder (object):
	def __init__(self, ip_a, ip_b, ip_pb):
		self.input_a = ip_a
		self.input_b = ip_b
		self.input_pb = ip_pb
		self.setup_io(self.input_a, input)
		enc_bouncetime = 30
		btn_bouncetime = 300
		self.rotation = 2040
		self.encoder_enabled = False
		self.rot_delta = 10

		GPIO.add_event_detect(self.input_a,GPIO.FALLING, self.encoder, enc_bouncetime)
		GPIO.add_event_detect(self.input_pb,GPIO.FALLING, self.toggle_encoder, btn_bouncetime)

	def read_encoder(self,pin):
		return GPIO.input(pin)

	def setup_io(self, io_pin, input_output):
		if DEBUG:
			print("setting up IO...")
		# BCM Mode uses Broadcom based definitions; not header pin numbering
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.input_a, GPIO.IN)
		GPIO.setup(self.input_b, GPIO.IN)
		GPIO.setup(self.input_pb, GPIO.IN)


	def toggle_encoder(self, pin):
		if DEBUG:
			print("toggled pin",pin)
			print("en1",self.encoder_enabled)
		self.rotation = 2048
		print ("rotation = ",self.rotation)
		self.encoder_enabled = not(self.encoder_enabled)
		if DEBUG:
			print("en2",self.encoder_enabled)

	def encoder(self,pin):
		if DEBUG:
			print ("up/down/ENABLE",pin, self.encoder_enabled)
		if self.encoder_enabled == False:
			if DEBUG:
				print("encoder disabled...push button to enable")
			return
		if (self.read_encoder(self.input_b) == 1):
			self.rotation += self.rot_delta
			if self.rotation > 4096: self.rotation=4096
		else:
			self.rotation -= self.rot_delta
			if self.rotation < 0: self.rotation=0

		print ("rotation = ",self.rotation)

def main():
	#raspberry pi/project functionality to GPIO numbers (not pin numbers)
	io_pin_a = 5
	io_pin_b = 6
	io_pin_pb = 13
	dac1_address = 0x62
	bus_num = 1
	trim_encoder_1  = encoder(io_pin_a, io_pin_b, io_pin_pb)
	dac1 = Adafruit_MCP4725.MCP4725(address=dac1_address, busnum=bus_num)
	while(1):
		dac1.set_voltage(trim_encoder_1.rotation)
		time.sleep(0.01)
if __name__=='__main__':
	main()



