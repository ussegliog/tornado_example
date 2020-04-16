#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main script (define and run our Tornado application)
"""

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from main_app.views import HelloWorld, NumberRequest
from main_app.extensions import db

define('port', default=8888, help='port to listen on')

if __name__ == "__main__":
    """Construct and serve the tornado application."""
    app = Application([
        ('/', HelloWorld),  ('/number_request', NumberRequest)
    ],
    db=db
    )

    db.create_all()

    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print('Listening on http://localhost:%i' % options.port)
    IOLoop.current().start()
