#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define polling tasks and EventTask class
"""

from tornado import gen

from main_app.extensions import executor, db
from main_app.models import Numbers


import uuid 
import os
import json
import pickle
from pathlib import Path
import subprocess

############# EventTask class ################
class EventTask():
      """Class to store main elts for event/request tasks."""

      def __init__(self, task_id) :
        self._task_id = task_id
        self._status = "not started"
        self._result = None

      @property
      def result(self) :
        return self._result

      @result.setter 
      def result(self, response) :
        self._result = response

      @property
      def status(self) :
        return self._status

      @status.setter 
      def status(self, status) :
        self._status = status

        
############# Polling tasks ################
@gen.coroutine
def small_loop():
      while True:
            yield print('in small loop!\n')
            yield gen.sleep(10)
            
            yield print('numbers in small loop : ' + str(session.query(Numbers).count()))


# python scripts
def python_script(script, inputArg):
      subprocess.Popen(['python', script, inputArg])
    
# Sum
@gen.coroutine
def sum_task():
      # Infinite loop 
      while True:

            yield gen.sleep(10)
      
            # Generate a task_id with uuid
            currentTaskId = uuid.uuid1()

            
            try :
                  # Create a session
                  session = db.sessionmaker()

                  # Select into Numbers table, number with sum to do
                  numbers_to_sum = session.query(Numbers).filter_by(jobToDo="sum").all()

                  print("Number of sum : " + str(len(numbers_to_sum)))

                  # Check number to sum (must be > 0)
                  if len(numbers_to_sum) > 0:
                        # Write numbers into a file
                        inputJson = {}
                        inputJson['numbers_id'] = []
                        inputJson['numbers'] = []

                        for i in range(0,len(numbers_to_sum)):
                              # Extract id and numbers information
                              inputJson['numbers_id'].append(numbers_to_sum[i].id)
                              inputJson['numbers'].append(numbers_to_sum[i].numbers)

                              # Update jobToDo with Doing
                              numbers_to_sum[i].jobToDo = "sum_Doing"

                        # Commit changes into our DB
                        session.commit()
                        
            except Exception as exc :
                  response = "Error INTO SUM during post request : "
                  print(response + str(type(exc)))

                  
                  # Write the json file
                  JSON_PATH = os.path.join(Path(__file__).parent.parent, 'processings/input_files/')
                  JSON_NAME = os.path.join(JSON_PATH, str(currentTaskId) + '.json')


                  with open(JSON_NAME, 'w') as f:
                        json.dump(inputJson, f)

                  # Launch sum processing with a SubProcess
                  SCRIPT_PATH = os.path.join(Path(__file__).parent.parent, 'processings/sum.py')
                  python_script(SCRIPT_PATH, JSON_NAME)

                  print('Hi! from sum_task')
              

# Mul
@gen.coroutine
def mul_task():
      # Infinite loop 
      while True:

            yield gen.sleep(10)
      
            # Generate a task_id with uuid
            currentTaskId = uuid.uuid1()

            try :
                  # Create a session
                  session = db.sessionmaker()

                  # Select into Numbers table, number with mul to do
                  numbers_to_mul = session.query(Numbers).filter_by(jobToDo="mul").all()

                  print("Number of mul : " + str(len(numbers_to_mul)))

                  # Check number to mul (must be > 0)
                  if len(numbers_to_mul) > 0:
                        # Write numbers into a file
                        inputJson = {}
                        inputJson['numbers_id'] = []
                        inputJson['numbers'] = []

                        for i in range(0,len(numbers_to_mul)):
                              # Extract id and numbers information
                              inputJson['numbers_id'].append(numbers_to_mul[i].id)
                              inputJson['numbers'].append(numbers_to_mul[i].numbers)

                              # Update jobToDo with Doing
                              numbers_to_mul[i].jobToDo = "mul_Doing"

                        # Commit changes into our DB
                        session.commit()
                        
            except Exception as exc :
                  response = "Error INTO MUL during post request : "
                  print(response + str(type(exc)))
                        
                  # Write the json file
                  JSON_PATH = os.path.join(Path(__file__).parent.parent, 'processings/input_files/')
                  JSON_NAME = os.path.join(JSON_PATH, str(currentTaskId) + '.json')


                  with open(JSON_NAME, 'w') as f:
                        json.dump(inputJson, f)

                  # Launch mul processing with a SubProcess
                  SCRIPT_PATH = os.path.join(Path(__file__).parent.parent, 'processings/mul.py')
                  python_script(SCRIPT_PATH, JSON_NAME)

                  print('Hi! from mul_task')
              
