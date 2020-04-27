# tornado_example

Example of Tornado application

## Instructions

* Launch tornado application : **python tornado_app.py**

Two kind of corotines/tasks are available with polling tasks and event tasks. The Event corotines/tasks can be trigerred by POST or GET requests such as curl -X POST -d "data" http://127.0.0.1:8888/number_request. Two python scripts into test/ repository provide automatic requests and send its to the Web Server. The polling tasks are scheduled and directly sended.


## Technologies

A main technology is used inside the code : Tornado. Tornado is a Python web framework which allows asynchronous code. The module asyncio is included inside Tornado and the library tornado.gen and higher concurrence is available with the tornado.concurrent module.

A ORM (tornado-sqlalchemy) provides a generic API to make transactions with several kind of databases (PostGres, MySQL, Sqlite ...). For this code, a sqlite database is settled.

## Code organization

The Tornado application is put at the center with four directories to add specific features or tests/processings :
* *config/* : Define global path or configuration
* *test/* : Simulate user requests
* *processings/* : Define simple processings (python scripts)
* *main_app/* : Main diretory to handle incoming requests.
The main_app repository contains the heart of source files, with the following organization:






## Limitations
