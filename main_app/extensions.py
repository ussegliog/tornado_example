#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Instanciate a global DB and executor to be available for all elements : views and models
"""

from tornado import concurrent
from tornado_sqlalchemy import SQLAlchemy
from config.settings import SQLALCHEMY_DATABASE_URI


# thread pool for async background tasks
executor = concurrent.futures.ThreadPoolExecutor(8)
# Database
db = SQLAlchemy(url=SQLALCHEMY_DATABASE_URI)

