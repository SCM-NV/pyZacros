# -*- PLT@NLeSC(2020) -*- 
"""
Main class triggering the run of the engine.   

  :type engine: str, required.
"""

import logging
import subprocess
import os


from pyzacros.utils.io_utils import read_input_data, write_kmc_input_files
#from scm.plams import * 

logger = logging.getLogger(__name__)
      
class KmcSimulation():
    def __init__(self, engine: str,
                 electronic_package: str = None, 
                 path: str = None ):
        """
        For a given engine, the input files will be searched in the current
        working directory unless additional path_to_inputs is provided
        (optional). Then, input files will be read in the following hierarchy
        of prevalence:

        - A .yaml .yml file containing KMC-like dictionaries (see manual).
        - Ab-initio results will be read.
        - Standard engine input files will be read.
 
        That is, .yaml/.yml data will prevail to ab-initio and standar inputs.

        :parm engine: Name of the engine (i.e. C++ or Fortran code to be
          executed).
        :type engine: str, required.
        :parm read_results_from: Name of the engine from which ab-initio data
          will be read.
        :type read_results_from: str, optional.
 #       TODO :: insert the optional path.
        :parm path_to_inputs: Additional path to find the input files. Default
         is the runnig_directory.
        :type path_to_inputs: str, optional.
        """
        print("Hello world!", engine, electronic_package, path)
        read_input_data( engine, electronic_package, path) 
        write_kmc_input_files(engine )
         

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
   """
   Hello function
   """
   print("Hello world!")

def sayhi2():
   """
   Hello function
   """