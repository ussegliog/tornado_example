#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define polling tasks and EventTask class
"""

from tornado import gen

from main_app.extensions import executor


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

