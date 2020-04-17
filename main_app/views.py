#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define all available views/handlers for our Tornado Application
"""

from tornado.web import RequestHandler
from tornado_sqlalchemy import as_future, SessionMixin, SQLAlchemy
from tornado import gen
import json
import pickle

from main_app.models import Request
from main_app.models import Numbers

# First Handler : Helloworld
class HelloWorld(RequestHandler):
    """Print 'Hello, world!' as the response body."""

    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def get(self):
        """Handle a GET request for saying Hello World!."""
        self.write("Hello, world!")
        


        
class NumberRequest(RequestHandler, SessionMixin):
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

    # Async GET
    @gen.coroutine
    def get(self):
        """Handle a GET request and get input data."""

        print("GET for rid :" + str(self.form_data['rid']))
        count = 0
        with self.make_session() as session:
            count = session.query(Request).count()

        self.send_response(json.dumps({'count :': count}), 201)

    # Async POST
    @gen.coroutine
    def post(self):
        """Handle a POST request and insert input data into our db."""

        print("POST for rid :" + str(self.form_data['rid']))
        
        response = "OK"

        number_list=pickle.dumps(self.form_data['numbers'])
        jobtodo_list=pickle.dumps(self.form_data['jobtodo'])
        request_id = self.form_data['rid']
        
        # Put the request into our DB : into request and number tables
        try :
            # First into request table
            with self.make_session() as session:
                my_request = Request(request_id=request_id,
                                     number_list=number_list,
                                     jobToDo_list=jobtodo_list)
                session.add(my_request)

            # Second into number table
            # Loop on number_list and jobtodo_list to store one by one number into number table
            for i in range(0, len(number_list)):
                my_number = Numbers(numbers=number_list[i], jobToDo=jobtodo_list[i],
                                    request_id=request_id)
                session.add(my_number)

            # Save chgts into our DB
            #db.session.commit()

        except Exception as exc :
            # Adapt response if exception (usually if rid is already into request table)
            response = "Error during DB transaction : Please Check the request"    

        self.send_response(response, 201)
