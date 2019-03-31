import cherrypy
import json

class Catalog():

    exposed = True

    def GET(self,*uri,**params):

        # Read the setup file and handle the error in case error
        try:
            file = open("setup.json", "r")
            json_str = file.read()
            file.close()
        except:
            raise cherrypy.HTTPError(500, "Error in reading Setup File")

        json_dic = json.loads(json_str)

        for i in uri:
            if (i in json_dic):
                json_dic = json_dic[i]
            else:
                raise cherrypy.HTTPError(404,  "Please check that your request is correct")

        requested_data = json.dumps(json_dic)
        return requested_data

    def POST(self,*uri,**params):

        try:
            file = open("setup.json", "r")
            json_str = file.read()
            file.close()
        except:
            raise cherrypy.HTTPError(500, "Error in reading Setup File")
        json_dic = json.loads(json_str)

        # Add user to user list
        if uri[0] == "telegram":
            if uri[1] == "users":
                user = cherrypy.request.body.read()
                user=json.loads(user)
                userList = json_dic["telegram"]["users"]
                userList.append(user)
                json_dic["telegram"]["users"] = userList

        # Add new zone or update current existing zone

        if uri[0] == "zones":

            zoneData = cherrypy.request.body.read()
            zoneData=json.loads(zoneData)
            key=zoneData.keys()
            key=key[0]
            zones=json_dic["zones"]
            zones[key]=zoneData[key]

            json_dic["zones"]=zones

        # Rewrite JSON
        jsonText = json.dumps(json_dic)
        try:
            file = open("setup.json", "w")
            file.write(jsonText)
            file.close()
        except:
            raise KeyError("Error in writing Setup File")

    def PUT(self, *uri, **params):

        # Read the setup file and handle the error in case error
        try:
            file = open("setup.json", "r")
            json_str = file.read()
            file.close()
        except:
            raise cherrypy.HTTPError(500, "Error in reading Setup File")

        json_dic = json.loads(json_str)

        # Change user emergency status
        if uri[0] == "telegram":
            if uri[1] == "users":
                userList=json_dic["telegram"]["users"]
                for counter, i in enumerate(userList):
                    if int(params["chat_id"])==i["chat_id"]:
                        userList[counter]["emergency"]= not(userList[counter]["emergency"])
                        stat = userList[counter]
                        break
                json_dic["telegram"]["users"]=userList


        # Rewrite JSON
        jsonText = json.dumps(json_dic)
        try:
            file = open("setup.json", "w")
            file.write(jsonText)
            file.close()
        except:
            raise KeyError("Error in writing Setup File")

    def DELETE(self,*uri,**params):

        try:
            file = open("setup.json", "r")
            json_str = file.read()
            file.close()
        except:
            raise cherrypy.HTTPError(500, "Error in reading Setup File")
        json_dic = json.loads(json_str)

        # Remove User
        if uri[0] == "telegram":
            if uri[1] == "users":
                userList=json_dic["telegram"]["users"]

                for counter,i in enumerate(userList):
                    if int(params["chat_id"])==i["chat_id"]:
                        userList.pop(counter)
                        break
                json_dic["telegram"]["users"]=userList

        # Remove Zone
        if uri[0] == "zones":
            zones=json_dic["zones"]
            try:
                del zones[params["zone"]]
            except:
                raise cherrypy.HTTPError(404,"Zone already not defined")
            json_dic['zones']=zones


        # Rewrite JSON
        jsonText=json.dumps(json_dic)
        try:
            file = open("setup.json", "w")
            file.write(jsonText)
            file.close()
        except:
            raise KeyError("Error in writing Setup File")

if __name__ == '__main__':
    # read the config file to set the url and the port to expose the data on it
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(Catalog(), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
