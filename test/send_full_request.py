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

  
def main(nb, ip):

    # Use requests module with ip to reach tornado server
    BASE_URL = "http://" + ip + ":8888/"
        
    #### request POST on http://ip:8888/number_request #### 
    print("\nFirst Step : Send a post request ")

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
        print("numbers : " +  str(dataRequest["numbers"][0:10]))
        print("jobtodo : " + str(dataRequest["jobtodo"][0:10]))
    else :
        print("numbers : " +  str(dataRequest["numbers"]))
        print("jobtodo : " + str(dataRequest["jobtodo"]))
        
    # Req is directy a response (not a Future) => sync
    reqPost = requests.post(BASE_URL + "number_request",
                            data=json.dumps(dataRequest),
                            headers=headers)
    
    # Check status code (must be 200 or 201)
    if reqPost.status_code != 200 and reqPost.status_code != 201 :
        print("status code sended by http shows a error : " + str(reqPost.status_code))
        quit()
        
    # Get the task_id (inside reqPost)
    reqPostDict = json.loads(reqPost.text)
    

    if 'task_id' not in reqPostDict :
        print("task_id not into post response")
        quit()

    
    #### request GET on http://ip:8888/number_request and wait to et result (if not into db yet) #### 
    print("\nSecond Step : Send a get request (wait until status and processed is done)")
    
    while True :
        # Get status/response
        reqGet = requests.get(BASE_URL + "number_request",
                              data=reqPostDict,
                              headers=headers)

        # Check status code (must be 200 or 201)
        if reqGet.status_code != 200 and reqGet.status_code != 201 :
            print("status code sended by http shows a error : " + str(reqGet.status_code))
            quit()

        reqGetDict = json.loads(reqGet.text)
                

        print("Get status : " + str(reqGetDict['status']))
    
        # If status done : request into our db and processed == True => get the results
        if reqGetDict['status'].startswith("done") :
            if reqGetDict['processed'] :
                print("\nGet result : ")

                if 'numbers' in reqGetDict:
                    if len(reqGetDict["numbers"]) > 10:
                        print("Number too large => display only the first ones (10)")
                        print("numbers : " +  str(reqGetDict["numbers"][0:10]))
                        print("jobtodo : " + str(reqGetDict["jobtodo"][0:10]))
                        print("results : " + str(reqGetDict["results"][0:10]))
                    else :
                        print("numbers : " +  str(reqGetDict["numbers"]))
                        print("jobtodo : " + str(reqGetDict["jobtodo"]))
                        print("results : " + str(reqGetDict["results"]))
            
                break # Get out of the while

        time.sleep(2) # sleep 2s


# Main Program
if __name__ == "__main__":
    
    ###### Get arguments : mode and request id ######
    # Check arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("nb", help="input number")
    parser.add_argument("--ip", help="ip to reach our tornado server (by default 127.0.0.1)",
                        default="127.0.0.1")

    args = parser.parse_args()

    main(args.nb,args.ip)
