#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define all available views/handlers for our Tornado Application
"""

from tornado.web import RequestHandler
from tornado import gen
from tornado import concurrent
from tornado import process
from tornado import locks

import sqlalchemy
import json
import pickle
import uuid 
import time

from main_app.models import Requests
from main_app.models import Numbers
from main_app.models import Link
from main_app.extensions import executor
from main_app.tasks import EventTask, make_session

# list of tasks to store future and get result/status : Global
tasks = dict()
lock_tasks = locks.Lock()


# First Handler : Helloworld
class HelloWorld(RequestHandler):
    """Print 'Hello, world!' as the response body."""

    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def get(self):
        """Handle a GET request for saying Hello World!."""
        self.write("Hello, world!")
        
# Main Handler : NumberRequest
class NumberRequest(RequestHandler):
    """Handle request and main transactions into the request table of the DB."""

    """Allow GET and POST requests."""
    SUPPORTED_METHODS = ("GET", "POST",)

    # Executor to run post request in //
    executor = executor

    # Use the global dict (work only with one process for tornado app) :
    # only one process to listen on input port (otherwise this can't work)
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
    @gen.coroutine
    def done(self, fn):
        global tasks
        global lock_tasks

        with (yield lock_tasks.acquire()):
            if fn.cancelled():
                tasks[fn.arg].status = "cancelled"
                print('{}: canceled'.format(fn.arg))
            elif fn.done():
                tasks[fn.arg].status = "done (request into our db)"
                tasks[fn.arg].result = fn.result()
                print('{}: done'.format(fn.arg))
        
            
    # Handle post (on one thread)
    @concurrent.run_on_executor    
    def handle_post(self, form_data) :
        response = "OK"
          
        number_list=pickle.dumps(form_data['numbers'])
        jobtodo_list=pickle.dumps(form_data['jobtodo'])
        request_id = form_data['rid']

        #time.sleep(10)
        
        # Put the request into our DB : into request and number tables
        try :
            # First into request table (make_session from tasks.py)
            with make_session() as session:
                my_request = Requests(request_id=request_id,
                                      processed=False) # init results with input numbers and processed to False
                
                
                
                # Second into number table
                # Loop on number_list and jobtodo_list to store one by one number into number table
                for i in range(0, len(form_data['numbers'])):
                    my_number = Numbers(number=form_data['numbers'][i],
                                        jobToDo=form_data['jobtodo'][i],
                                        result_number=form_data['numbers'][i])
                    
                    # Link request to my_number
                    my_number.requests.append(my_request)
                    #my_request.numbers.append(my_number)
                    
                    session.add(my_number)

                session.add(my_request)

            # Save chgts into our DB : At the end of context manager (same "everywhere")

        except sqlalchemy.exc.IntegrityError :
            # Adapt response if exception (usually if rid is already into request table)
            response = "Error during DB transaction : Please Check the request" 
            print(response + " (rid must already be registered into DB) ")
        except :
            response = "Error during post request"

    
    # Get Results into our db for a given rid
    def queryDb_withRid(self, rid):
        jsonDict = {}
        # make_session from tasks.py
        with make_session() as session:

            request_id = rid

            # Query into request table thanks to request_id
            required_request = session.query(Requests).filter_by(request_id=request_id).first()

            # Transform elt to have input request format
            jsonDict['rid'] = request_id
            jsonDict['processed'] = required_request.processed
            jsonDict['numbers'] = []
            jsonDict['jobtodo'] = []
            jsonDict['results'] = []

            # All query to retrieve all numbers for a specific request_id
            for x in session.query(Numbers).join(Link).filter(Link.request_id==request_id).all():
                jsonDict['numbers'].append(x.number)
                jsonDict['jobtodo'].append(x.jobToDo)
                jsonDict['results'].append(x.result_number)
                

        return jsonDict
        
    # Async GET
    @gen.coroutine
    def get(self):
        """Handle a GET request and get input data."""

        # Two kind of get : one for checking if task_id is done and the other to get rid elt
        if 'rid' in self.form_data :
            jsonRes = self.queryDb_withRid(self.form_data['rid'])
            
            if len(jsonRes) > 0 : 
                # if dict not empty
                self.send_response(jsonRes, 201)
            else :
                self.send_response("rid not found into our db ", 200)

        elif 'task_id' in self.form_data :
            # Search inside the global dictionary the required task_id
            response = "task id not found into the global dictionary"
            
            if self.form_data['task_id'] in tasks :
                # Get status and results (if done)
                status = tasks[self.form_data['task_id']].status
                rid = tasks[self.form_data['task_id']].rid

                if status.startswith("done") :
                    # rid into Db => Get numbers, jobtodo and result_numbers
                    jsonRes = self.queryDb_withRid(rid)

                    if len(jsonRes) > 0 : 
                        # if dict not empty
                        # Add status into jsonRes
                        jsonRes['status'] = status 
                        self.send_response(jsonRes, 201)
                    else :
                        self.send_response("rid not found into our db ", 200)
                else :
                    self.send_response({'status': status}, 201)
            else :
                self.send_response({'status': response}, 201)

        else :
            self.send_response("Wrong get request", 400)
            
    # Async POST
    @gen.coroutine
    def post(self):
        """Handle a POST request and insert input data into our db."""
        
        response = "OK"

        global tasks
        global lock_tasks
        
        # Generate a task_id with uuid
        task_id = uuid.uuid1()

        # Create a EventTask
        task = EventTask(task_id, self.form_data['rid'])
        
        # Store the task inside the dictionary
        with (yield lock_tasks.acquire()):
            tasks[str(task_id)] = task
            print("Add from NumberRequest a tasks into our global dict (size : " + str(len(tasks)) + " ) ")
            
            
        task.status = "started (put request into our db)"

        # If yield => wait and retrun a response if not yield => future
        #concurent_Future = executor.submit(self.handle_post, form_data=self.form_data)
        concurent_Future = self.handle_post(form_data=self.form_data)
        # Adapt future to store and get result later
        concurent_Future.arg = str(task_id)
        concurent_Future.add_done_callback(self.done)
        
        # post response : task_id
        self.send_response(json.dumps({'task_id': str(task_id)}), 201)


# Handler : Update_NumberRequest
class Update_NumberRequest(NumberRequest):
    """Update tables of the DB."""

    """Allow only POST requests."""
    SUPPORTED_METHODS = ("POST")
 
    
    # Use the global dict (work only with one process for tornado app) :
    # only one process to listen on input port (otherwise this can't work)
    global tasks
    
    
    # Handle post (on one thread)
    @concurrent.run_on_executor    
    def update_post(self, Ntable_id, N_list, JTD_list, res_list) :
 
        # List to store request_id for each number
        rId_list = []

        # Put the request into our DB : into request and number tables
        try :
            # First into request table (make_session from tasks.py)
            with make_session() as session:

                # Update first, Numbers Table and store request id
                for i in range(0, len(Ntable_id)):
                    my_number = session.query(Numbers).get(Ntable_id[i])
                    # Update my number
                    my_number.jobToDo = JTD_list[i]
                    my_number.result_number = res_list[i]

                    # Store rid for current number
                    for x in session.query(Requests).join(Link).filter(Link.number_id == Ntable_id[i]).all():
                        rId_list.append(x.request_id)

                # Udpate then, Request_Table
                # Get unique rid into our list
                rid_unique = set(rId_list)

                # Loop on each unique rid
                for rid in rid_unique:

                    # Check if request is totally processed
                    jobToDo_for_current_rid = []
                    for x in session.query(Numbers).join(Link).filter(Link.request_id == rid).all():
                        jobToDo_for_current_rid.append(x.jobToDo)

                    if not ("sum" in jobToDo_for_current_rid or "mul" in jobToDo_for_current_rid) :
                        my_request = session.query(Requests).get(rid)
                        # Change to processed = True
                        my_request.processed = True
                  
            
        except Exception as exc :
            response = "Error INTO update_post during post request : "
            print(response + str(type(exc)))

        response = "OK"

        
    
     # Async POST
    @gen.coroutine
    def post(self):
        """Handle a POST request and update input data into our db."""

        global tasks
        global lock_tasks
                
        response = "OK"

        # Generate a task_id with uuid
        task_id = uuid.uuid1()

        # Create a EventTask
        task = EventTask(task_id)
        
        # Store the task inside the dictionary
        with (yield lock_tasks.acquire()):
            tasks[str(task_id)] = task
            print("Add from UpdateNumberRequest a tasks into our global dict (size : " + str(len(tasks)) + " ) ")
            
        
        task.status = "started"

        # Get data from request
        number_table_id = self.form_data['numbers_id'] # list of id inside Numbers table
        numbers_intoRequest = self.form_data['numbers'] # list of numbers
        jobToDo_new_intoRequest = self.form_data['jobtodo_new'] # list of string
        res_intoRequest = self.form_data['result'] # list of results

        # If yield => wait and retrun a response if not yield => future
        concurent_Future = self.update_post(Ntable_id=number_table_id,
                                            N_list=numbers_intoRequest,
                                            JTD_list=jobToDo_new_intoRequest,
                                            res_list=res_intoRequest)
        # Adapt future to store and get result later
        concurent_Future.arg = str(task_id)
        concurent_Future.add_done_callback(self.done)
        
        # post response : task_id
        self.send_response(json.dumps({'task_id': str(task_id)}), 201)
