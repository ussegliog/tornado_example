#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Instanciate a global DB to be available for all elements : views, tasks and models
"""

from tornado_sqlalchemy import SQLAlchemy
from config.settings import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(url=SQLALCHEMY_DATABASE_URI)

