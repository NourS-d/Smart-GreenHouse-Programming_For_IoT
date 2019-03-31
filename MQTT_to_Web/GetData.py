import paho.mqtt.client as PahoMQTT
import time
import json
import requests

class GetData():


    def __init__(self, url, clientID, broker, port = 1883):
        # Define some stuff
        self.clientID = clientID
        self.sub = PahoMQTT.Client(clientID, False)
        self.broker = broker
        self.port = port
        self.topic=[]
        self.url=url

        # Register the callbacks
        self.sub.on_connect = self.OnConnect
        self.sub.on_message = self.OnMessageReceived

    def start(self, topic, qos=2):
        # Manage connection to broker
        self.sub.connect(self.broker, self.port)
        self.sub.loop_start()

        self.topic = topic

        # subscribe for a topic
        self.sub.subscribe(self.topic, qos)

    def OnConnect(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def OnMessageReceived(self, paho_mqtt , userdata, msg):
        print ("Topic:'" + msg.topic + "', QoS: '" + str(msg.qos) + "' Message: '" + str(msg.payload) + "'")
        branches = msg.topic.split("/")

        # If received setup then add zone
        if branches[1]=="setup":

            data={}
            data[branches[2]]={}
            data[branches[2]]["plant"] = "Undefined"
            data[branches[2]]["water_level"] =  100
            data[branches[2]]["temp_margin"] = 0
            data[branches[2]]["hum_margin"] = 0
            data[branches[2]]["minimum_Temp"] = -100
            data[branches[2]]["maximum_Humidity"] = 100
            data[branches[2]]["maximum_Temp"] = 150
            data[branches[2]]["minimum_Humidity"] = 0
            requests.post(self.url+"/zones",json.dumps(data))

            data = {}
            data[branches[2]] = {}
            data[branches[2]]["heater"] = False
            data[branches[2]]["temperature"] = 20
            data[branches[2]]["humidity"] = 50
            data[branches[2]]["water"] = 100
            data[branches[2]]["pump"] = False
            data[branches[2]]["fan"] = False
            data[branches[2]]["moisture"] = True
            data[branches[2]]["sprinklers"] = False
            data[branches[2]]["cooler"] = False

            dats=data[branches[2]]
            print str(dats)
            for keys,vals in dats.items():
                updateData(branches[2],keys,vals)

        elif branches[1]=="disconnect":
            print "here"
            requests.delete(self.url+"/zones?zone="+branches[2])
            try:
                file = open("data.json", 'r')
                json_str = file.read()
                file.close()
            except:
                raise KeyError("Unable to open data file.")

            jsn = json.loads(json_str)
            del jsn[branches[2]]

            json_str=json.dumps(jsn)
            try:
                file = open("data.json", 'w')
                file.write(json_str)
                file.close()
            except:
                raise KeyError("Unable to open data file.")


        else:
            zone = branches[1]
            type = branches[2]
            json_dic=json.loads(msg.payload)

            val=json_dic[type]
            # Check if zone exists
            a=requests.get(self.url + "/zones")
            a=a.json()

            if zone in a.keys():
                updateData(zone,type,val)
            else:
                print "zone not available"

def updateData(zone, type, update):

        try:
            file= open("data.json",'r')
            json_str=file.read()
            file.close()
        except:
            raise KeyError("Unable to open data file.")

        jsn=json.loads(json_str)
        if zone not in jsn.keys():
            jsn[zone]={}

        jsn[zone][type]={}
        jsn[zone][type]["value"]=update
        json_str=json.dumps(jsn)
        try:
            file = open("data.json", 'w')
            file.write(json_str)
            file.close()
        except:
            raise KeyError("Unable to open data file.")



if __name__ == "__main__":

    try:
        file=open("config.json","r")
        json_str = file.read()
        file.close()
    except:
        raise KeyError("Error opening config file. Please check.")

    conf_json = json.loads(json_str)
    url = conf_json["catalog"]["url"]

    response = requests.get(url+"/broker")
    brokerData = response.json()

    broker = brokerData["IP"]
    port = brokerData["port"]

    del brokerData, response

    client=GetData(url,"Real",broker,port)
    client.start("#")

    while True:
        time.sleep(0.5)
