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

    def OnPublish(self):
        print "Published"

    def start(self):
        # Manage connection to broker
        self.sub.connect(self.broker, self.port)
        self.sub.loop_start()
        self.pub.connect(self.broker, self.port)
        self.pub.loop_start()

    def OnConnectSub(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        self.sub.subscribe([("/+/water", 0), ("/+/moisture", 0)])

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


class PublishData():
    def __init__(self, client,url):
        self.PrevVals = {}
        self.client = client
        self.url = url
        zones = requests.get(self.url + "/zones")
        zones = zones.json()
        for zone in zones:
            self.PrevVals[zone] = {}
            self.PrevVals[zone]["pump"] = False
            self.PrevVals[zone]["sprinklers"] = False


    def SanityCheck(self, type, zone, value):

        zones = requests.get(self.url + "/zones")
        zones = zones.json()

        if zone in zones:
            dataZ = zones[zone]
            print dataZ["water_level"]

            if type == "water":
                print self.PrevVals[zone]["pump"]
                if value <= int(dataZ["water_level"]):
                    # Activate pump
                    # Send Telegram Data
                    print "pump on"
                    data = {}
                    data["pump"] = True
                else:
                    data = {}
                    data["pump"] = False

                    if self.PrevVals[zone]["pump"]==True:
                        if value <=90:
                            print "pump still on"
                            data["pump"] = True
                        else:
                            data={}
                            print "pump off"
                            data["pump"] = False
                    else:
                        print "pump off"

                if data["pump"] != self.PrevVals[zone]["pump"]:
                    userList = requests.get(self.url + "/telegram/users").json()
                    token = requests.get(self.url + "/telegram/token").json()

                    for i in userList:
                        if data["pump"]==True:
                            msg= "Low water levels in " +zone+". Turning on pumps"
                        else:

                            msg= "Tank in " +zone+" is full. Turning off pumps"
                        if i["emergency"] == True:
                            url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                  + "&text="+msg
                            requests.post(url)
                    msgJson = {}
                    msgJson["pump"] = data["pump"]

                    self.client.publish("/" + zone + "/pump", json.dumps(msgJson))
                    self.PrevVals[zone]["pump"] = data["pump"]
                print data["pump"]

            if type == "moisture":

                userList = requests.get (self.url + "/telegram/users").json()
                token = requests.get(self.url + "/telegram/token").json()

                if value == 1:
                    msg = "Soil in " + zone + " is dry. Activating sprinklers."
                    msgJson={}
                    msgJson["sprinklers"]=True

                else:
                    msg = "Turning off sprinklers"
                    msgJson={}
                    msgJson["sprinklers"] = False

                if  msgJson["sprinklers"] != self.PrevVals[zone]["sprinklers"]:
                    self.client.publish("/" + zone + "/sprinklers", json.dumps(msgJson))

                    for i in userList:
                        print i
                        if i["emergency"] == True:
                            url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + str(i['chat_id']) \
                                  + "&text=" + msg
                            requests.post(url)
                    self.PrevVals[zone]["sprinklers"]=msgJson["sprinklers"]


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

    client = GetData(url, "WaterControl", broker, port)

    # Connect to relevant data
    client.start()

    # Loop to keep program alive
    while True:
        time.sleep(0.5)
