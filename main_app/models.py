#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define tables as models with SQLAlchemy.
Two tables in this example:
_ One to store request and to have a direct interface with views (user APis)
_ Another one to store number and job_to_do. Uses by processing. 
"""

from sqlalchemy import Column, Boolean, BigInteger, Integer, String, PickleType
from main_app.extensions import db

# Request table
class Request(db.Model):
    __tablename__ = "Request"
    
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, unique=True, nullable=False)
    number_list = Column(PickleType, unique=False, nullable=False)
    jobToDo_list = Column(PickleType, unique=False, nullable=False)
    result_list = Column(PickleType, unique=False, nullable=False)
    processed = Column(Boolean, unique=False, nullable=False)

    def __repr__(self):
        return '<Request %r>' % self.request_id

# Number table 
class Numbers(db.Model):
    __tablename__ = "Numbers"
    
    id = Column(Integer, primary_key=True)
    numbers = Column(Integer, unique=False, nullable=False)
    jobToDo = Column(String(80), unique=False, nullable=False)
    request_id = Column(Integer, unique=False, nullable=False)
    result_numbers = Column(Integer, unique=False, nullable=True)
    
    def __repr__(self):
        return '<Numbers %r>' % self.id
