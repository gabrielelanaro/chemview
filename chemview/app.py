"""Tornado webapp for indipendent trajectory viewer"""
import os
import sys

from zmq.eventloop import ioloop
ioloop.install()
import tornado.web
import tornado.ioloop

from tornado.template import Template

from jupyter_client.ioloop.manager import IOLoopKernelManager

BASE_PATH = os.path.dirname(__file__)

km = IOLoopKernelManager()
kc = km.client()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        template_string = open(sys.argv[1]).read()
        self.finish(Template(template_string).generate(**self.get_template_namespace()))


# TODO: add a websocket that forwards the message to the right channel
        
application = tornado.web.Application([
        (r'/', MainHandler),
    ],
    template_path=os.path.join(BASE_PATH, "templates"),
    static_path=os.path.join(BASE_PATH, "static"))

PORT = 8819
application.listen(PORT)
import webbrowser
webbrowser.open('http://localhost:%d'%PORT)

tornado.ioloop.IOLoop.current().start()
