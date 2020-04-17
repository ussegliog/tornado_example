#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
from tornado import httpclient
from tornado.ioloop import IOLoop
from tornado import gen
import functools
import time
import random

""" 
Script to simulate user requests
Two argument :  request_id and number of Numbers 
"""

# Global variables for requests
BASE_URL = "http://127.0.0.1:8888/"
headers = {"Content-type": "application/json"}
processings = ["sum", "mul"]

# Asynchronous requests
@gen.coroutine    
def main_async(rid, nb):

    # Use HTTP Client (asynchronous mode)
    # Async client 
    http_client = httpclient.AsyncHTTPClient()
       
    #### 1): request POST on http://127.0.0.1:8888/number_request #### 
    # Build data
    dataRequest = {}
    dataRequest["rid"] = rid
    dataRequest["numbers"] = []
    dataRequest["jobtodo"] = []
    
    for n in range(0,int(nb)):
        dataRequest["numbers"].append(random.randint(0, 1000))
        dataRequest["jobtodo"].append(random.choice(processings))

    response = ""

    request = httpclient.HTTPRequest(BASE_URL + "number_request",
                                     method="POST", headers=headers,
                                     body=json.dumps(dataRequest))

    try:
        # send the asynchronous request and get a Asyncio Future
        response = http_client.fetch(request)
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print("Error: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        print("Error: " + str(e))


    wait = True

    if wait :
        #### 2): Wait for SUCCESS or FAILURE with yield ####
        # Check if response if done or cancelled
        if not (response.cancelled() or response.done()):
            print("Not done yet ")
            # Wait (yield => execute/send the request : generate the coroutine)
            res = yield response
            # Re check
            if (response.cancelled() or response.done()):
                print("Done ")

        print("Response : " + response.result().body.decode("utf-8"))


        #### 3): request GET on http://127.0.0.1:8888/number_request #### 
        request_get = httpclient.HTTPRequest(BASE_URL + "number_request",
                                             method="GET", headers=headers,
                                             body=json.dumps(dataRequest),
                                             allow_nonstandard_methods=True)


        try:
            # send the asynchronous request and get a response (because of yield)
            response = yield http_client.fetch(request_get)
        except httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error: " + str(e))
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))

        print(response.body)

    
    http_client.close()

    
# Synchronous requests    
def main_sync(rid, nb):
    
    # Use requests module
    
    #### 1): request POST on http://127.0.0.1:8888/number_request #### 
    # Build data
    dataRequest = {}
    dataRequest["rid"] = rid
    dataRequest["numbers"] = []
    dataRequest["jobtodo"] = []
    
    for n in range(0,int(nb)):
        dataRequest["numbers"].append(random.randint(0, 1000))
        dataRequest["jobtodo"].append(random.choice(processings))

    # Req is directy a response (not a Future) => sync
    req = requests.post(BASE_URL + "number_request",
                        data=json.dumps(dataRequest),
                        headers=headers)
    
    # Check status code (must be 200 or 201)
    if req.status_code != 200 and req.status_code != 201 :
        print("status code sended by http shows a error : " + str(req.status_code))
        quit()


    print("At the end :" + req.text)
       
    #### 2): request GET on http://127.0.0.1:8888/number_request ####
    # Get status/response
    req = requests.get(BASE_URL + "number_request",
                        data=json.dumps(dataRequest),
                        headers=headers)

    print("At the end :" + req.text)
    

# Main Program
if __name__ == "__main__":
    
    ###### Get arguments : mode and request id ######
    # Check arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("rid", type=int, help="input request id")
    parser.add_argument("nb", help="input number")
    parser.add_argument("--mode", type=str, help="mode for request : async or sync",
                        default="async")
    args = parser.parse_args()

    if (args.mode == "async") :
        print("Asynchronous mode for client")
        # Event loop
        IOLoop.current().run_sync(functools.partial(main_async, args.rid, args.nb))
    else :
        print("Synchronous mode for client")
        main_sync(args.rid, args.nb)
