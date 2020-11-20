#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main script (define and run our Tornado application)
"""

from tornado.httpserver import HTTPServer
from tornado import ioloop
from tornado import process
from tornado.options import define, options
from tornado.web import Application

from main_app.views import HelloWorld, NumberRequest, Update_NumberRequest
from main_app.tasks import small_loop, sum_task, mul_task
from main_app.extensions import Base, db_engine, executor

import time, signal

define('port', default=8889, help='port to listen on')


_SHUTDOWN_TIMEOUT = 2

def make_safely_shutdown(server):
    io_loop = ioloop.IOLoop.instance()
    print(io_loop)
    def stop_handler(*args, **keywords):
        #print("Hello Stop Handler!")
        def shutdown():
            print("Hello shutdown!")
            # Stop http_server => if connection request after this stop will
            # receive a Connection refused
            # However all current connection (into handlers function even on ThreadPoolExecutor)
            # will continue and will finish
            server.stop() # this may still disconnection backlogs at a low probability
            deadline = time.time() + _SHUTDOWN_TIMEOUT
            def stop_loop():
                print("Hello stop_loop!")
                now = time.time()
                if now < deadline:
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    print("Stop IOLoop")
                    io_loop.stop()
            stop_loop()
        # Add a callback to our io_loop. This callback comes after current callbacks
        # (ex : mul/sum_task). If sum/mul_task are running, it will finish before launching
        # shutdown callback
        io_loop.add_callback_from_signal(shutdown)
        
    # if catch signal => stop IOLoop
    signal.signal(signal.SIGQUIT, stop_handler) # SIGQUIT is send by our supervisord to stop this server.
    signal.signal(signal.SIGTERM, stop_handler) # SIGTERM is send by Ctrl+C or supervisord's default.
    signal.signal(signal.SIGINT, stop_handler)

def main() :
    """Construct and serve the tornado application."""
    app = Application([
        ('/', HelloWorld),  ('/number_request', NumberRequest),
        ('/update_request', Update_NumberRequest)])

    Base.metadata.create_all(db_engine)

    http_server = HTTPServer(app)
    http_server.listen(options.port)

    # To launch several tornado process app in //
    #http_server.start(0)   # Processes = number of CPUs
    # assign background tasks
    # if process.task_id() == 0:
    #     ioloop.IOLoop.instance().spawn_callback(sum_task)
    #     ioloop.IOLoop.instance().spawn_callback(mul_task)

    ioloop.IOLoop.instance().spawn_callback(sum_task)
    ioloop.IOLoop.instance().spawn_callback(mul_task)
    
    print('Listening on http://localhost:%i' % options.port)

    make_safely_shutdown(http_server)    
    ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
