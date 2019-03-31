from DHT import DHT_Read
import paho.mqtt.client as mqtt
import json
import requests
import time

class DHT_Pub:
	
	def __init__(self, clientID, broker, port = 1883):
		
		self.clientID = clientID
		self.port = port
		self.pub=mqtt.Client(self.clientID, port)
		self.broker = broker
	
	def start(self):

		self.pub.connect(broker)
		self.pub.loop_start()

	def stop(self):
		
		self.pub.loop_stop()
		self.pub.disconnect()
	
	def publish(self, topic, message):
		
		self.pub.publish(topic, message)

try:
        file=open("config.json", "r")
        json_str = file.read()
        file.close()
except:
        raise KeyError("Error opening config file. Please check.")

config_json = json.loads(json_str)
url = config_json["catalog"]["url"]
ID = config_json["zoneID"]


response = requests.get(url+"/broker")
brokerData=response.json()

broker = brokerData["IP"]
port = brokerData["port"]

del brokerData
del response

updateTime = 1

sensor = DHT_Read(17)


publisher = DHT_Pub("DHT11", broker, port)
publisher.start()

while True:

	val=sensor.read() 
	
	if val is not None:
		jsonDic=json.loads(val)
		print jsonDic
		
		#Publish Temperature
		temp='{"temperature": ' + str(jsonDic["temperature"])+', "time": '+str(jsonDic["time"])+'}'
		publisher.publish("/"+ID+"/temperature",temp) 
		
		#Publish Humidity
		hum='{"humidity": ' + str(jsonDic["humidity"])+', "time": '+str(jsonDic["time"])+'}'
		publisher.publish("/"+ID+"/humidity",hum) 
			
	else:
		print "Error reading from sensor"
	time.sleep(updateTime)
