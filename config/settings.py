#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Global settings 
"""

# DEV settings.py
import os
from pathlib import Path
import threading

from tornado.ioloop import PeriodicCallback

DEBUG = True

# Secret key
SECRET_KEY = os.urandom(24)

# Database Path
DB_PATH = os.path.join(Path(__file__).parent.parent, 'database.db')

# SQL Alchemy Database URI
SQLALCHEMY_DATABASE_URI = f"sqlite:////{DB_PATH}"


############# Singleton class #############
class Singleton(type):
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


############# ServerState with Singleton as metaclass #############
class ServerState(metaclass=Singleton) :
    """
        Handle and check state for dependancies (ie : GPFS, PBS, HPSS or DB).
        This class is a singleton in order to provide same information into views or tasks 
    """
    def __init__(self) :
        """
        Constructor to set all states to True
        """
        # Init states
        self._GPFS_ok = True
        self._DB_ok = True
        self._PBS_ok = True
        self._HPSS_ok = True

        # Sub-states
        self._GPFSLantency_ok = True
        self._GPFSMount_ok = True

        print("self._PBS_ok : " + str(self._PBS_ok))

        # Instanciate a lock (only one for all states)
        self.lock_states = threading.Lock()
        # Bool to run only one check in //
        self.lock_running = threading.Lock()

        # Default Timer
        self.timer_ForPeriodic = 60000 # 1 min => 60 000 ms

        # Init a dict of PeriodicCallback instances (each key matches with a check functions as callbacks)
        # Several keys can correpond to a smae state (ex GPFS lancenty or pb mount => self.GPFS_ok to False)
        self.dict_Periodics = {"GPFS_latency" : None, "GPFS_mount" : None, "PBS_qsub" : None}



    ### getters ####
    @property
    def GPFS_ok(self) :
        self.lock_states.acquire()
        gpfs_ok = self._GPFS_ok
        self.lock_states.release()
        
        return gpfs_ok

    @property
    def DB_ok(self) :
        self.lock_states.acquire()
        db_ok = self._DB_ok
        self.lock_states.release()
        
        return db_ok

    @property
    def PBS_ok(self) :
        self.lock_states.acquire()
        pbs_ok = self._PBS_ok
        self.lock_states.release()
        
        print("pbs_ok : " + str(pbs_ok))

        return pbs_ok

    @property
    def HPSS_ok(self) :
        self.lock_states.acquire()
        hpss_ok = self._HPSS_ok
        self.lock_states.release()
        
        return hpss_ok


    #### check functions for each dependancies/problems ###
    def check_gpfs_latency(self) :
        """
        Check on gpfs (latency)
        """
        # Do a check (a real one)
        status_toChange = False
        print("Pouet GPFS latency")
        status_toChange = True # depends on "real test"

        check_ok = True

        # Change status according to the previous check
        if status_toChange :
            self.lock_states.acquire()
            self._GPFSLatency_ok = not self._GPFSLatency_ok
            check_ok = self._GPFSLatency_ok
            self._GPFS_ok = self._GPFSLantency_ok and self._GPFSMount_ok 
            self.lock_states.release()
            
            # If GPFS return OK => Stop the PeriodicCallback
            if  self._GPFSLatency_ok :
                self.lock_running.acquire()
                # Get instance into our dict, stop the PeriodicCallback and forget instance 
                self.dict_Periodics["GPFS_latency"].stop()
                self.dict_Periodics["GPFS_latency"] = None
                self.lock_running.release()


        return check_ok

    
    def check_gpfs_mount(self) :
        """
        Check on gpfs (mount space)
        """
        # Do a check (a real one)
        status_toChange = False
        print("Pouet GPFS mount ServerState")
        status_toChange = True # depends on "real test"

        check_ok = True

        # Change status according to the previous check
        if status_toChange :
            self.lock_states.acquire()
            self._GPFSMount_ok = not self._GPFSMount_ok
            check_ok = self._GPFSMount_ok
            self._GPFS_ok = self._GPFSLantency_ok and self._GPFSMount_ok 
            self.lock_states.release()
            
            # If GPFS return OK => Stop the PeriodicCallback
            if self._GPFSMount_ok :
                self.lock_running.acquire()
                # Get instance into our dict, stop the PeriodicCallback and forget instance 
                self.dict_Periodics["GPFS_mount"].stop()
                self.dict_Periodics["GPFS_mount"] = None
                self.lock_running.release()


        return check_ok


    def check_pbs_qsub(self) :
        """
        Check on pbs (submition)
        """
        # Do a check (a real one)
        status_toChange = False
        print("Pouet PBS Check")
        status_toChange = True # depends on "real test"

        check_ok = True

        # Change status according to the previous check
        if status_toChange :
            self.lock_states.acquire()
            self._PBS_ok = not self._PBS_ok
            check_ok = self._PBS_ok
            self.lock_states.release()

            # If PBS return OK => Stop the PeriodicCallback
            if self._PBS_ok :
                self.lock_running.acquire()
                # Get instance into our dict, stop the PeriodicCallback and forget instance 
                self.dict_Periodics["PBS_qsub"].stop()
                self.dict_Periodics["PBS_qsub"] = None
                self.lock_running.release()
    

        return check_ok


    ###### Launch checks (with PeriodicCallback) ####
    def launch_checks(self, suspect="gpfs") :
        """
        Run some checks according to suspects (can be called by all server : views, tasks ..)
        """
        print("Into launch_checks")
        
        
        # Launch a first check (directly call to check functions)
        # Then, if ko : instanciate/start a or several PeriodicCallback following the "suspect"
        if suspect == "gpfs" :
            
            # Call checks 
            check_latency = self.check_gpfs_latency()
            check_mount = self.check_gpfs_mount()

            self.lock_running.acquire()
            # For gpfs : Two kinds of problems : latency or mount => two PeriodicCallback
            # Latency KO and None into our dict (do not override a existing/running instance)
            # => Instanciate and start a PeriodicCallback to check reguraly
            if not check_latency and not self.dict_Periodics["GPFS_latency"]: 
                periodic_gpfs_latency = PeriodicCallback(self.check_gpfs_latency, 
                                                         self.timer_ForPeriodic)
                periodic_gpfs_latency.start()
                self.dict_Periodics["GPFS_latency"] = periodic_gpfs_latency

            # Mount KO and None into our dict (do not override a existing/running instance)
            # => Instanciate and start a PeriodicCallback to check reguraly
            if not check_mount and not self.dict_Periodics["GPFS_mount"]:
                periodic_gpfs_mount = PeriodicCallback(self.check_gpfs_mount, 
                                                       self.timer_ForPeriodic)
                periodic_gpfs_mount.start()
                self.dict_Periodics["GPFS_mount"] = periodic_gpfs_mount

            self.lock_running.release()
            
        if suspect == "pbs" :
            # Call checks 
            check_pbs = self.check_pbs_qsub()

            self.lock_running.acquire()
            # PBS KO and None into our dict (do not override a existing/running instance)
            # => Instanciate and start a PeriodicCallback to check reguraly
            if not check_pbs and not self.dict_Periodics["PBS_qsub"] :
                # For pbs : qsub problems
                periodic_pbs_qsub = PeriodicCallback(self.check_pbs_qsub, 
                                                     self.timer_ForPeriodic)

                periodic_pbs_qsub.start()

                # Store instance into our dict
                self.dict_Periodics["PBS_qsub"] = periodic_pbs_qsub

            self.lock_running.release()
            
        # Others suspects .....

        



# Instanciate a ServerState
server_state = ServerState()
