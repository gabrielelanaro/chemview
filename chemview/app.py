"""Tornado webapp for indipendent trajectory viewer"""
import os
from zmq.eventloop import ioloop
ioloop.install()
import tornado.web
import tornado.ioloop
from jupyter_client.ioloop.manager import IOLoopKernelManager
BASE_PATH = os.path.dirname(__file__)

km = IOLoopKernelManager()
kc = km.client()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# TODO: add a websocket that forwards the message to the right channel
        
application = tornado.web.Application([
        (r'/', MainHandler),
    ],
    template_path=os.path.join(BASE_PATH, "templates"),
    static_path=os.path.join(BASE_PATH, "static"))


application.listen(8819)
tornado.ioloop.IOLoop.current().start()
# main(argv=['--no-browser'])
# nbapp = NotebookApp()
# nbapp.allow_origin = '*'
# nbapp.open_browser = False
# nbapp.initialize()
# nbapp.start()
