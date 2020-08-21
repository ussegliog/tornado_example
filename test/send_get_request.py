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
def main(task_id, ip):
    
    # Use requests module with ip to reach tornado server
    BASE_URL = "http://" + ip + ":8888/"
    
    # Build data with only task_id
    dataRequest = {}
    dataRequest["task_id"] = task_id
    
    #### request GET on http://ip:8888/number_request ####
    # Get status/response
    req = requests.get(BASE_URL + "number_request",
                        data=json.dumps(dataRequest),
                        headers=headers)

    reqDict = json.loads(req.text)
    
    print("status : " + str(reqDict['status']))
    
    if 'numbers' in reqDict:
        if len(reqDict["numbers"]) > 10:
            print("Number too large => display only the first ones (10)")
            print("numbers : " +  str(reqDict["numbers"][0:10]))
            print("jobtodo : " + str(reqDict["jobtodo"][0:10]))
        else :
            print("numbers : " +  str(reqDict["numbers"]))
            print("jobtodo : " + str(reqDict["jobtodo"]))
  

# Main Program
if __name__ == "__main__":
    
    ###### Get arguments : mode and request id ######
    # Check arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", type=str, help="task id to get some intel")
    parser.add_argument("--ip", help="ip to reach our tornado server (by default 127.0.0.1)",
                        default="127.0.0.1")
    args = parser.parse_args()

    main(args.task_id, args.ip)
