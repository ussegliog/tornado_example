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
headers = {"Content-type": "application/json"}
processings = ["sum", "mul"]

# Synchronous requests    
def main(nb, ip):
    
    # Use requests module with ip to reach tornado server
    BASE_URL = "http://" + ip + ":8888/"
        
    #### request POST on http://ip:8888/number_request #### 
    # Build data
    dataRequest = {}
    dataRequest["numbers"] = []
    dataRequest["jobtodo"] = []
    
    for n in range(0,int(nb)):
        dataRequest["rid"] = random.randint(0, 100000)
        dataRequest["numbers"].append(random.randint(0, 100000))
        dataRequest["jobtodo"].append(random.choice(processings))

    if (int(nb) > 10) :
        print("Number too large => display only the first ones (10)")
        print(dataRequest["numbers"][0:10])
        print(dataRequest["jobtodo"][0:10])
    else :
        print(dataRequest)
        
    # Req is directy a response (not a Future) => sync
    req = requests.post(BASE_URL + "number_request",
                        data=json.dumps(dataRequest),
                        headers=headers)
    
    # Check status code (must be 200 or 201)
    if req.status_code != 200 and req.status_code != 201 :
        print("status code sended by http shows a error : " + str(req.status_code))
        quit()


    print("Response Post :" + req.text)

    

# Main Program
if __name__ == "__main__":
    
    ###### Get arguments : mode and request id ######
    # Check arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("nb", help="input number")
    parser.add_argument("--ip", help="ip to reach our tornado server (by default 127.0.0.1)",
                        default="127.0.0.1")
    
    args = parser.parse_args()
    
    main(args.nb, args.ip)
