import time
import json
import RPi.GPIO as GPIO

class YL_Read():
	""" Read Soil Moisture.
	    This gives 0 when in wet and 1 when dry
	"""

	def __init__(self, pin=21):
		self.moisture = None
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.IN)
		self.pin = pin

	def read(self):
		try:
			return GPIO.input(self.pin)
		except:
			print "Error in reading from Sensor"

	def readAvg(self, num=50):
		""" Does the average of (num) readings. Default: 50 Readings """
		
		avg = 0
		for i in range(num):
			avg = avg + self.read()
		if(avg >= num/2):
			 self.moisture = 1
		else: 
			 self.moisture = 0
		
		if(self.moisture is not None):
			
			json_file=json.dumps({"moisture": self.moisture, "time": time.time()})
			
			return json_file			

