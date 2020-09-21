#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Instanciate a global DB and executor to be available for all elements : views and models
"""

from tornado import concurrent
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config.settings import SQLALCHEMY_DATABASE_URI


# thread pool for async background tasks
executor = concurrent.futures.ThreadPoolExecutor(8)
# Database
db_engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Base = declarative_base()
