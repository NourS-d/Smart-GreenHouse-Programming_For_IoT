import paho.mqtt.client as mqtt
import json
import time
import requests


class Setup_Pub:

    def __init__(self, clientID, broker, port=1883):
        self.clientID = clientID
        self.port = port
        self.pub = mqtt.Client(self.clientID, port)
        self.broker = broker

    def start(self):
        self.pub.connect(broker)
        self.pub.loop_start()

    def stop(self):
        self.pub.loop_stop()
        self.pub.disconnect()

    def publish(self, topic, message,qos=2):
        self.pub.publish(topic, message,qos=qos)

try:
    file = open("config.json", "r")
    json_str = file.read()
    file.close()
except:
    raise KeyError("Error opening config file. Please check.")

config_json = json.loads(json_str)
url = config_json["catalog"]["url"]
ID = config_json["zoneID"]

response = requests.get(url + "/broker")
brokerData = response.json()

broker = brokerData["IP"]
port = brokerData["port"]

del brokerData
del response


name=ID+"_setup"
publisher = Setup_Pub(name, broker, port)
publisher.start()
publisher.publish("/setup/"+ID,"")
time.sleep(5)
publisher.stop()

