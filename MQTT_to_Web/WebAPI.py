import cherrypy
import json
import time
class Catalog():

    exposed = True

    def GET(self,*uri,**params):
        # Read the setup file and handle the error in case error
        try:
            file = open("data.json", "r")
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
        return

    def PUT(self, *uri, **params):
        return

    def DELETE(self,*uri,**params):
        return

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
    cherrypy.config.update({'server.socket_port': 9090})
    cherrypy.engine.start()
    cherrypy.engine.block()
