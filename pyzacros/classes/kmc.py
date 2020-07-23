# -*- PLT@NLeSC(2020) -*-
"""
Main class of the pyZacros, it triggers the run of the KMC engine.
"""

import logging
import subprocess

from pyzacros.utils.io_utils import read_input_data, write_kmc_input_files


class KmcSimulation():

    """
    Main class triggering the run of the engine.

      :parm engine: Name of the engine (i.e. C++ or Fortran code to be
                    executed).
      :type engine: str, required.

      :parm electronic_package: Name of the engine from which ab-initio data
       will be read.
      :type electronic_package: str, optional.

      :parm path: Additional path to find the input files. Default
       is the runnig_directory.
      :type path: str, optional.
    """

    def __init__(self, engine: str,
                 electronic_package: str = None,
                 path: str = None):

        logger = logging.getLogger(__name__)
        print("logger:", logger)
        print("Hello world!", engine, electronic_package, path)
        read_input_data(engine, electronic_package, path)
        write_kmc_input_files(engine)

    def run(self):
        """
        Runnig of the engine.
        """
        print("Hello world!")

#    def __init__(self, name, age):
#  	  self.name = name
#  	  self.age = age

#   def run_command(cmd: str, workdir: str, expected_output: dict = None):

#   """
#   Run a bash command using subprocess
#   """
#
#    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True,
#               cwd=workdir.as_posix()) as p:
#    rs = p.communicate()
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
