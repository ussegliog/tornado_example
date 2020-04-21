#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define all available views/handlers for our Tornado Application
"""

from tornado.web import RequestHandler
from tornado_sqlalchemy import as_future, SessionMixin, SQLAlchemy
from tornado import gen
from tornado import concurrent
from tornado import process

import sqlalchemy
import json
import pickle
import uuid 

from main_app.models import Request
from main_app.models import Numbers
from main_app.extensions import executor
from main_app.tasks import EventTask

# list of tasks to store future and get result/status : Global 
tasks = dict()


# First Handler : Helloworld
class HelloWorld(RequestHandler):
    """Print 'Hello, world!' as the response body."""

    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def get(self):
        """Handle a GET request for saying Hello World!."""
        self.write("Hello, world!")
        
        
class NumberRequest(RequestHandler, SessionMixin):
    """Handle request and main transactions into the request table of the DB."""

    """Allow GET and POST requests."""
    SUPPORTED_METHODS = ("GET", "POST",)

    # Executor to run post request in //
    executor = executor

    # Use the global dict (does not work) : apparently problem with shared memory and cycle ref with tornado
    # I DON'T KNOW => AVOID SHARED MEMORY
    # HANDLE TASKS IS COMPLICATED HERE BECAUSE WE CAN'T STORE THE RESULT IN MEMORY AND THEN RETRIVE IT WITH A SEPARATE REQUEST
    global tasks
    
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

    # Callback function (called when a "event task" is done)
    def done(self, fn):
        if fn.cancelled():
            tasks[fn.arg].status = "cancelled"
            print('{}: canceled'.format(fn.arg))
        elif fn.done():
            tasks[fn.arg].status = "done"
            tasks[fn.arg].result = fn.result()
            print('{}: not canceled'.format(fn.arg))

        print(len(tasks))

    # Handle post (on one thread)
    @concurrent.run_on_executor    
    def handle_post(self, form_data) :
        response = "OK"

        #global tasks
        print("Executing on : " + str(process.task_id()))
        
        number_list=pickle.dumps(form_data['numbers'])
        jobtodo_list=pickle.dumps(form_data['jobtodo'])
        request_id = form_data['rid']

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

        except sqlalchemy.exc.IntegrityError :
            # Adapt response if exception (usually if rid is already into request table)
            response = "Error during DB transaction : Please Check the request" 
            
        except :
            response = "Error during post request"

        

        
    # Async GET
    @gen.coroutine
    def get(self):
        """Handle a GET request and get input data."""

        #global tasks
        # Two kind of get : one for checking if task_id is done and the other to get rid elt
        if 'rid' in self.form_data :
            print("GET for rid :" + str(self.form_data['rid']))
            count = 0
            with self.make_session() as session:
                count = session.query(Request).count()

            self.send_response(json.dumps({'count': count}), 201)
        elif 'task_id' in self.form_data :
            # Search inside the global dictionary the required task_id
            response = "not found"
            print(len(tasks))
            
            if self.form_data['task_id'] in tasks :
                # Get status and result (if done)
                status = tasks[self.form_data['task_id']].status
                result = "not yet"
                if status == "done" :
                    result = tasks[self.form_data['task_id']].result

                self.send_response(json.dumps({'status': status, 'result' : result}), 201)

            else :
                self.send_response(json.dumps({'status': response}), 201)

        else :
            self.send_response("Wrong get request", 400)
            
    # Async POST
    @gen.coroutine
    def post(self):
        """Handle a POST request and insert input data into our db."""
        
        print("POST for rid :" + str(self.form_data['rid']))
        
        response = "OK"

        #yield gen.sleep(5)

        # Generate a task_id with uuid
        task_id = uuid.uuid1()

        # Create a EventTask
        task = EventTask(task_id)
        # Store the task inside the dictionary
        tasks[str(task_id)] = task
        print(len(tasks))
        
        task.status = "started"
        
        # If yield => wait and retrun a response if not yield => future
        concurent_Future = self.handle_post(form_data=self.form_data)
        # Adapt future to store and get result later
        concurent_Future.arg = str(task_id)
        concurent_Future.add_done_callback(self.done)

        # post response : task_id
        self.send_response(json.dumps({'task_id': str(task_id)}), 201)
