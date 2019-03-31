import paho.mqtt.client as PahoMQTT
import json
import requests
import time


class GetData():

    def __init__(self, url, clientID, broker, port=1883):
        # Define some stuff
        self.clientID = clientID
        self.sub = PahoMQTT.Client(clientID+"_Sub", False)
        self.pub = PahoMQTT.Client(clientID+"_Pub", False)
        self.broker = broker
        self.port = port
        self.topic = []
        self.url = url
        self.publish = PublishData(self.pub,url)

        # Register the callbacks
        self.sub.on_connect = self.OnConnectSub
        self.pub.on_connect = self.OnConnectPub
        self.sub.on_message = self.OnMessageReceived
        self.pub.on_publish = self.OnPublish

    def start(self):
        # Manage connection to broker
        self.sub.connect(self.broker, self.port)
        self.sub.loop_start()

        self.pub.connect(self.broker, self.port)
        self.pub.loop_start()

    def OnConnectSub(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        self.sub.subscribe([("/+/temperature", 2),("/+/humidity", 2)])

    def OnConnectPub(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def OnMessageReceived(self, paho_mqtt, userdata, msg):
        print "Message Recieved"
        branches = msg.topic.split("/")
        zone = branches[1]
        type = branches[2]
        json_dic = json.loads(msg.payload)
        print str(json_dic)
        self.publish.SanityCheck(type, zone, json_dic[type])

    def OnPublish(self, paho_mqtt, userdata, flags, rc):
        print "Published"



class PublishData():

    def __init__(self, client,url):
        self.PrevVals = {}
        self.client = client
        self.url = url
        zones = requests.get(self.url + "/zones")
        zones = zones.json()
        for zone in zones:
            self.PrevVals[zone] = {}
            self.PrevVals[zone]["heater"] = False
            self.PrevVals[zone]["cooler"] = False
            self.PrevVals[zone]["humidifier"] = False
            self.PrevVals[zone]["fan"] = False

    def SanityCheck(self, type, zone, value):
        zones = requests.get(self.url + "/zones")
        zones = zones.json()

        if zone in zones:
            dataZ = zones[zone]
            data = {}

            # Temperature Rule Based Control
            if type == "temperature":

                # Low Temperature
                if value <= int(dataZ["minimum_Temp"]):
                    print "temp too low"
                    # Activate heater
                    data["heater"] = True
                    data["cooler"] = False

                    msg="Temperature of " +zone+" is below the minimum allowable value. Activating heater. "

                # High Temperature
                elif value >= int(dataZ["maximum_Temp"]):

                    print "temp too high"
                    # Activate cooler
                    data["cooler"] = True
                    data["heater"] = False

                    msg="It's too hot in " + zone +". Turning on cooler."
                else:
                    msg="Temperature in " + zone + " is back to the normal range. Turning off auxiliary regulation systems."

                    data["heater"] = False
                    data["cooler"] = False


                if self.PrevVals[zone]["heater"]==True or self.PrevVals[zone]["cooler"]==True:
                        #Waits until temperature is in average value
                        if abs(value -0.5*(dataZ["maximum_Temp"]+dataZ["minimum_Temp"]))>dataZ["temp_margin"]:
                            data["heater"] = self.PrevVals[zone]["heater"]
                            data["cooler"] = self.PrevVals[zone]["cooler"]
                        else:
                            data["heater"] = False
                            data["cooler"] = False

                if data["heater"] != self.PrevVals[zone]["heater"]:
                    print "here"
                    userList = requests.get(self.url + "/telegram/users").json()
                    token = requests.get(self.url + "/telegram/token").json()
                    for i in userList:
                        if i["emergency"] == True:
                            url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                  + "&text=" + msg
                            requests.post(url)
                    self.PrevVals[zone]["heater"] = data["heater"]
                    msgJson = {}
                    msgJson["heater"] = data["heater"]
                    self.client.publish("/" + zone + "/heater", json.dumps(msgJson))
                    msgJson = {}
                    msgJson["cooler"] = data["cooler"]
                    self.client.publish("/" + zone + "/cooler", json.dumps(msgJson))

                    del msgJson

                if data["cooler"] != self.PrevVals[zone]["cooler"]:
                        print "here"
                        userList = requests.get(self.url + "/telegram/users").json()
                        token = requests.get(self.url + "/telegram/token").json()
                        for i in userList:
                            if i["emergency"] == True:
                                url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                      + "&text="+msg
                                requests.post(url)
                        self.PrevVals[zone]["cooler"] = data["cooler"]
                        msgJson = {}
                        msgJson["cooler"] = data["cooler"]
                        self.client.publish("/" + zone + "/cooler", json.dumps(msgJson))
                        msgJson = {}
                        msgJson["heater"] = data["heater"]
                        self.client.publish("/" + zone + "/heater", json.dumps(msgJson))
                        del msgJson

            # Humidity Rule Based Control
            if type == "humidity":
                if value <= int(dataZ["minimum_Humidity"]):
                    print "hum too low"
                    # Activate heater
                    data["humidifier"] = True
                    data["fan"] = False

                    msg="Humidity in " +zone+" is below the minimum allowable value. Activating humidifier. "
                elif value >= int(dataZ["maximum_Humidity"]):

                    print "hum too high"
                    # Activate cooler
                    data["fan"] = True
                    data["humidifier"] = False


                    msg="High humidity levels in " + zone +". Turning on ventilator."
                else:
                    msg="Humidity in " + zone + " is back to the normal range. Turning off auxiliary regulation systems."

                    data["fan"] = False
                    data["humidifier"] = False

                if self.PrevVals[zone]["fan"]==True or self.PrevVals[zone]["humidifier"]==True:
                        #Waits until humidity is atleast average value
                        if abs(value - 0.5*(dataZ["maximum_Humidity"]+dataZ["minimum_Humidity"])) > dataZ["hum_margin"] :
                            data["fan"] = self.PrevVals[zone]["fan"]
                            data["humidifier"] = self.PrevVals[zone]["humidifier"]
                        else:
                            data["fan"] = False
                            data["humidifier"] = False

                if data["fan"] != self.PrevVals[zone]["fan"]:
                    userList = requests.get(self.url + "/telegram/users").json()
                    token = requests.get(self.url + "/telegram/token").json()
                    for i in userList:
                        if i["emergency"] == True:
                            url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                  + "&text=" + msg
                            requests.post(url)
                    self.PrevVals[zone]["fan"] = data["fan"]
                    msgJson = {}
                    msgJson["fan"] = data["fan"]
                    self.client.publish("/" + zone + "/fan", json.dumps(msgJson))
                    msgJson = {}
                    msgJson["humidifier"] = data["humidifier"]
                    self.client.publish("/" + zone + "/humidifier", json.dumps(msgJson))
                    del msgJson

                if data["humidifier"] != self.PrevVals[zone]["humidifier"]:
                    userList = requests.get(self.url + "/telegram/users").json()
                    token = requests.get(self.url + "/telegram/token").json()
                    for i in userList:
                        if i["emergency"] == True:
                            url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                  + "&text=" + msg
                            requests.post(url)
                    self.PrevVals[zone]["humidifier"] = data["humidifier"]
                    msgJson = {}
                    msgJson["humidifier"] = data["humidifier"]
                    self.client.publish("/" + zone + "/humidifier", json.dumps(msgJson))
                    msgJson = {}
                    msgJson["fan"] = data["fan"]
                    self.client.publish("/" + zone + "/fan", json.dumps(msgJson))
                    del msgJson


        else:
            print "Zone not registered"


if __name__ == "__main__":


    try:
        file = open("config.json", "r")
        json_str = file.read()
        file.close()
    except:
        raise KeyError("Error opening config file. Please check.")

    conf_json = json.loads(json_str)
    url = conf_json["catalog"]["url"]

    response = requests.get(url + "/broker")
    brokerData = response.json()

    broker = brokerData["IP"]
    port = brokerData["port"]

    del brokerData, response

    client = GetData(url, "AirControl", broker, port)

    # Connect to relevant data
    client.start()

    # Loop to keep program alive
    while True:
        time.sleep(0.5)
