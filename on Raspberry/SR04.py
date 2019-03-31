import time
import json
import RPi.GPIO as GPIO

class SR_Read():
	""" Read distance. This is used to see if tank level in percentage
	"""

	def __init__(self, trig=18, echo=24):
		
		self.level = None
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(trig, GPIO.OUT)
		GPIO.setup(echo, GPIO.IN)
		self.trig = trig
		self.echo = echo

	def measure(self):

		GPIO.output(self.trig,True)
		time.sleep(0.00001)
		GPIO.output(self.trig,False)

		Start = time.time()
		Stop = time.time()+10

		while GPIO.input(self.echo) == 0:
			Start=time.time()

		while GPIO.input(self.echo) == 1:
			Stop=time.time()

		diff = Stop - Start

		dist= (diff * 34300)/2

		# Tank Level Range
		if dist >= 200: dist = 150
		if dist <= 5:	dist = 0
		level = ((150-dist)/150)*100

		return abs(int(level))

	def read(self):
		
		try:
			self.level = self.measure()	
		except:
			print "Error in reading from Sensor"
		
		if(self.level is not None):
			
			json_file=json.dumps({"level": self.level, "time": time.time()})
			
			return json_file			

