#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define tables as models with SQLAlchemy.
Two tables in this example:
_ One to store request and to have a direct interface with views (user APis)
_ Another one to store number and job_to_do. Uses by processing. 
"""

from sqlalchemy import Column, Boolean, BigInteger, Integer, String, PickleType, ForeignKey, Table
from sqlalchemy.orm import relationship
from main_app.extensions import Base



# Request table
class Requests(Base):
    __tablename__ = "request"
    
    #id = Column(Integer, primary_key=True)
    request_id = Column(Integer, primary_key=True)
    processed = Column(Boolean, unique=False, nullable=False)
    
    numbers = relationship('Numbers', secondary='link')

    def __repr__(self):
        return '<Request %r>' % self.request_id

# Number table 
class Numbers(Base):
    __tablename__ = "number"
    
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=False, nullable=False)
    jobToDo = Column(String(80), unique=False, nullable=False)
    result_number = Column(Integer, unique=False, nullable=True)
    
    requests = relationship('Requests', secondary='link')

    def __repr__(self):
        return '<Numbers %r>' % self.id


# Class for relationship : Many-To-Many
class Link(Base):
   __tablename__ = 'link'
   
   request_id = Column(Integer, ForeignKey('request.request_id'), primary_key = True)

   number_id = Column(Integer, ForeignKey('number.id'), primary_key = True)
