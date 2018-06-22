import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os
from string import Template
import wave
import time


HOSTNAME = 'example.ngrok.io' #Change to the hostname of your server

def convert():
    f = wave.open('static/audio.wav', 'wb')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    with open('static/audio.raw', 'rb') as src:
        f.writeframes(src.read())
    f.close()

def timestamps(d):
    p = d[0]
    output = []
    for ts in d:
        td = ts-p
        output.append(td*1000)
        p=ts
    with open('static/timestamps.json', "w") as f:
        f.write(json.dumps(output))


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        with open('static/index.html') as f:
            file = f.read()
        self.content_type = 'text/html'
        self.write(file)
        self.finish()

		
class CallHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        data={}
        data['hostname'] = HOSTNAME
        filein = open('ncco.json')
        src = Template(filein.read())
        filein.close()
        ncco = json.loads(src.substitute(data))
        self.write(json.dumps(ncco))
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.finish()


class EventHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        print(self.request.body)
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()
			

class WSHandler(tornado.websocket.WebSocketHandler):
    buffer = b''
    ts = []
    def check_origin(self, origin):
        return True
    def open(self):
        print("Websocket Call Connected")
    def on_message(self, message):
        self.ts.append(time.time())
        if type(message) != str:
            self.buffer += message
        else:
            print(message)
    def on_close(self):
        print("Websocket Call Disconnected")
        with open('static/audio.raw', 'wb') as f:
            f.write(self.buffer)
        convert()
        timestamps(self.ts)



def main():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    application = tornado.web.Application([(r"/", MainHandler),
                                            (r"/event", EventHandler),
                                            (r"/ncco", CallHandler),
                                            (r"/socket", WSHandler),
                                            (r'/s/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
                                        ])
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 8004))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
	
	

