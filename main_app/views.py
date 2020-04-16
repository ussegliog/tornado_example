#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define all available views/handlers for our Tornado Application
"""

from tornado.web import RequestHandler
import json

# First Handler : Helloworld
class HelloWorld(RequestHandler):
    """Print 'Hello, world!' as the response body."""

    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def get(self):
        """Handle a GET request for saying Hello World!."""
        self.write("Hello, world!")
        


        
class NumberRequest(RequestHandler):
    """PHandle request and main transactions into the request table of the DB."""

    """Allow GET and POST requests."""
    SUPPORTED_METHODS = ("GET", "POST",)

    # Override prepare function to get request argument 
    def prepare(self):
        self.form_data = json.loads(self.request.body)
       
    # define json as default header
    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    # Override send_response 
    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        self.set_status(status)
        self.write(json.dumps(data))


    def get(self):
        """Handle a GET request and repeat input data."""
        self.send_response(self.form_data, 201)

    def post(self):
        """Handle a POST request and repeat input data."""
        #self.write(self.form_data)
        self.send_response(self.form_data, 201)
