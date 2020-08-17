#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main script (define and run our Tornado application)
"""

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import process
from tornado.options import define, options
from tornado.web import Application

from main_app.views import HelloWorld, NumberRequest, Update_NumberRequest
from main_app.tasks import small_loop, sum_task, mul_task
from main_app.extensions import db, executor

define('port', default=8888, help='port to listen on')

if __name__ == "__main__":
    """Construct and serve the tornado application."""
    app = Application([
        ('/', HelloWorld),  ('/number_request', NumberRequest),
        ('/update_request', Update_NumberRequest)
    ],
    db=db
    )

    db.create_all()

    http_server = HTTPServer(app)
    http_server.listen(options.port)

    # To launch several tornado process app in //
    #http_server.start(0)   # Processes = number of CPUs
    # assign background tasks
    # if process.task_id() == 0:
    #     IOLoop.instance().spawn_callback(sum_task)
    #     IOLoop.instance().spawn_callback(mul_task)

    IOLoop.instance().spawn_callback(sum_task)
    IOLoop.instance().spawn_callback(mul_task)
    
    print('Listening on http://localhost:%i' % options.port)
    IOLoop.current().start()
