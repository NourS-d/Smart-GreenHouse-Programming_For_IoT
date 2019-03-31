import cherrypy
import json
import os.path
import requests
import os

class freeboard():
    exposed = True

    def GET(self,*uri,**params):

        # Loads Home Page
        if len(uri) == 0:
            s = """
            <html>
                <head><title>Greenhouse Management System</title></head>
                <body>
                <h3>Welcome to your Greenhouse Management System!</h3>
                
                <p>
                Your current available zones are:
                <br><br>
                """

            try:
                file = open("config.json", "r")
                json_str = file.read()
                file.close()
            except:
                raise cherrypy.HTTPError(500,"Error opening config file. Please check.")

            config_json = json.loads(json_str)
            url = config_json["catalog"]["url"]
            zoneList = requests.get("http://" + url + "/zones")
            zoneList = zoneList.json()

            for zoneName,zoneData in zoneList.items():
                s=s +"""
                <a href =" """+"/"+str(zoneName)+'">'+zoneData["plant"]+'</a> -- <a href = "' +"/"+str(zoneName)+'/settings">Settings </a><br>'
            s=s+"""
            </p></body></html>
            """
            return s
        # The user should user url/(zone name) where zone name could be zone1, zone2...
        # Is this zone is not in the zone list, then we cannot access it
        if len(uri)==1:
            try:
                file = open("config.json", "r")
                json_str = file.read()
                file.close()
            except:
                raise cherrypy.HTTPError(500,"Error opening config file. Please check.")

            config_json = json.loads(json_str)
            url = config_json["catalog"]["url"]
            api = str(requests.get("http://"+url+"/webapi/url").json())
            respond=requests.get("http://"+url+"/zones")
            respond=respond.json()
            if uri[0] in respond.keys():
                if not os.path.exists("./dashboard/"+uri[0]+".json"):
                    formatter = open("./dashboard/format.txt").read()
                    formatter=json.loads(formatter)
                    for counter,i in enumerate(formatter["datasources"]):
                        if i["name"] == "zoneData":
                            formatter["datasources"][counter]["settings"]["url"] = "http://" + api + "/" + uri[0]
                        if i["name"] == "zoneInfo":
                            formatter["datasources"][counter]["settings"]["url"] = "http://" + url + "/zones/" + uri[0]
                    newFile=open("./dashboard/"+uri[0]+".json","w")
                    newFile.write(json.dumps(formatter))
                    newFile.close()

                s1 = open("./index.html").read(82).format(test=uri[0])
                s2 = open("./index.html").read()
                s2 = s2[82:]
                s2 = s1 + s2
                return s2
            else:
                raise cherrypy.HTTPError(404,"The link you entered isn't a valid link")
            #return open("./index.html").read()

        if len(uri) ==2:
            if uri[1]=="settings":
                try:
                    file = open("config.json", "r")
                    json_str = file.read()
                    file.close()
                except:
                    raise cherrypy.HTTPError(500, "Error opening config file. Please check.")

                config_json = json.loads(json_str)
                url = config_json["catalog"]["url"]
                respond = requests.get("http://" + url + "/zones")
                respond = respond.json()
                if uri[0] in respond.keys():
                    zoneData=respond[uri[0]]
                    s= """
                    <html>
                    <head>
                    <title>""" + str(uri[0]) + """ Settings </title>
                    </head>
                    <body>
                        <h3> Settings </h3>
                        <form method="post" action="update">
                        """
                    s=s+'Plant Name<br><input type="text" value="'+zoneData["plant"]+'" name="plant" /><br><br>'
                    s=s+'Minimum Allowable Temperature<br><input type="number" value="'+str(zoneData["minimum_Temp"])+'" name="minimum_Temp" /><br><br>'
                    s=s+'Maximum Allowable Temperature<br><input type="number" value="' + str(zoneData["maximum_Temp"]) + '" name="maximum_Temp" /><br><br>'
                    s = s + 'Minimum Allowable Humidity<br><input type="number" value="' + str(zoneData[
                        "minimum_Humidity"]) + '" name="minimum_Humidity" /><br><br>'
                    s = s + 'Maximum Allowable Humidity<br><input type="number" value="' + str(zoneData[
                        "maximum_Humidity"]) + '" name="maximum_Humidity" /><br><br>'
                    s=s+'Minimum Water Tank Level<br><input type="number" value="'+str(zoneData["water_level"])+'" name="water_level" /><br><br>'
                    s=s+'Temperature Margin<br><input type="number" value="'+str(zoneData["temp_margin"])+'" name="temp_margin" /><br><br>'
                    s=s+'Humidity Margin<br><input type="number" value="'+str(zoneData["hum_margin"])+'" name="hum_margin" /><br><br>'
                    s=s+""" <button type="submit">Update</button>
                        </form>
                        
                    </body>
                    """
                    return s
                else:
                    raise cherrypy.HTTPError(404, "The link you entered isn't a valid link")
        else:
            raise cherrypy.HTTPError(404,"You must be lost!")

    def POST(self,*uri,**params):
        if len(uri)==1 and uri[0]=='saveDashboard':
            a = params['json_string']
            print a
            txt=open('./dashboard.json','w')
            txt.write(a)
            txt.close()
        elif len(uri)==2 and uri[1] == "update":
            dataJson={}
            dataJson=params
            for key,val in dataJson.items():
                if key != "plant":
                    dataJson[key]=int(val)
            zone={}
            zone[uri[0]]=dataJson

            try:
                file = open("config.json", "r")
                json_str = file.read()
                file.close()
            except:
                raise cherrypy.HTTPError(500,"Error opening config file. Please check.")

            config_json = json.loads(json_str)
            url = config_json["catalog"]["url"]

            requests.post("http://"+url+"/zones",json.dumps(zone))
            raise cherrypy.HTTPRedirect("/")

if __name__ == '__main__':

    path = os.path.abspath(os.path.dirname(__file__))

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())

        },
        '/static':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './'
        }
    }

    cherrypy.tree.mount(freeboard(), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 7070})
    cherrypy.engine.start()
    cherrypy.engine.block()