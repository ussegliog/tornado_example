#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define polling tasks 
"""

from tornado import gen

from main_app.extensions import executor

@gen.coroutine
def small_loop():
  while True:
    yield print('in small loop!\n')
    yield gen.sleep(10)

