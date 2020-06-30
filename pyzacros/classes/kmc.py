# -*- PLT@NLeSC(2020) -*- 
"""
Module containing main classes.
"""

from pathlib import Path
from pyzacros.utils.find_utils import find_input_files 

import logging
import subprocess

logger = logging.getLogger(__name__)

class KmcSimulation():
   """
   Main class triggering the run of the engine.   
   """
   def __init__(self, engine: str):
#      TODO :: insert the optional path. 
      """
      For a given engine, the input files are checked in the running_directory.  
      Optionally, a path containing the input files can be provided. 
      :parm engine: Name of the engine (i.e. C++ or Fortran code to be executed). 
      :type engine: str, required.
      :parm path_to_inputs: Additional path to find the input files. Default is the runnig_directory. 
      :type engine: str, optional. 
      """
      input_list = find_input_files( engine)
      
       
   def run(self): 
      print("Hello world!")
#    def __init__(self, name, age):
#  	  self.name = name
#  	  self.age = age
#
#def run_command(cmd: str, workdir: str, expected_output: dict = None):
#    """
#   Run a bash command using subprocess
#   """
#    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, cwd=workdir.as_posix()) as p:
#        rs = p.communicate()
# 
#    logger.info("RUNNING COMMAND: {}".format(cmd))
#    logger.info("COMMAND OUTPUT: {}".format(rs[0].decode()))
#    logger.error("COMMAND ERROR: {}".format(rs[1].decode()))
# 
#    if expected_output is None:
#        return None
#    else:
#        return expected_output     

def sayhi():
   print("Hello world!")