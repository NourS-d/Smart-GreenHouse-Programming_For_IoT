import Adafruit_DHT
import time
import json

class DHT_Read():
	""" Read Temperature and Humidity """

	def __init__(self,pin=17):
		self.humidity = None
		self.temp     = None
		self.sensor   = Adafruit_DHT.DHT11
		self.pin=pin
	def read(self):
		try:
			self.humidity, self.temp = Adafruit_DHT.read_retry(self.sensor,self.pin)
		except:
			print "Error in reading from Sensor"

		if(self.humidity is not None and self.temp is not None):
			data={}
			data["temperature"]= self.temp
			data["humidity"]= self.humidity
			data["time"] = time.time()
			json_file=json.dumps(data)
			
			return json_file			
	
