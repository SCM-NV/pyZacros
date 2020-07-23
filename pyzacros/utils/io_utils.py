# -*- PLT@NLeSC(2020) -*-
"""
Module containing utilities to read/write data.
"""


def read_input_data(engine: str,
                    electronic_package: str = None,
                    path: str = None):
    """
    Function to search input files. In increasing herarchical order:
    - Read engine standard input.
    - Read ab-initio output input.
    - Read formatted yaml or hdf5 files.

    :return: instantiation of PLAMS-like settings according for the input
             files read.
    """
    # 1. find engine standard files:
    #   list=find_input_files(enigne)                      ### find_utils.py
    #   map_settings(input_file_list, engine)              ### setting_utils.py

    # 2. if results from ab-initio code:
    #   find_input_files(electronic_pacakge)               ### find_utils.py
    #   map_settings(input_file_list, electronic_package)  ### setting_utils.py

    # 3. Always:
    #   find_input_files(yaml)                             ### find_utils.py
    #   map_settings(input_file_list, formatted_input)     ### setting_utils.py


def write_kmc_input_files( engine: str):
    """
    Function to write KMC input files.

    :parm engine: Name of the engine
    :type engine: str, required.
    """
    # TODO Search yaml files or standard input files according to engine. 
    inputfile_list = []
    return inputfile_list
