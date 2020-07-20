# -*- PLT@NLeSC(2020) -*- 
"""
Module containing utility functions to find files.  
"""
import os
from pathlib import Path

def find_input_files( engine: str, electronic_package: str = None, path: str = None ) -> list:
    """
    Function to search enigne.yml or engine.yaml input files.
    If none, engine standard input files will be searched. 
    :return: A list of input files.
    :rtype : list. 
    """
    # TODO Search yaml files or standard input files according to engine. 
    inputfile_list = []

    working_path=Path.cwd()
    print("Pablo resolves", working_path.resolve())
    folders = []
    files = []
    for item in os.scandir(working_path):
       print("there is file!")
    for entry in os.scandir(working_path):
        print(entry)
#        if entry.is_file():
#            print(entry.name)
#    if entry.is_dir():
#        folders.append(entry)
#    elif entry.is_file():
#        files.append(entry)

    print("Folders - {}".format(folders))
    print("Files - {}".format(files))
#   if name in os.walk(working_path.absolute):
#       print("I have found it!")
#   if read_results_from:
#            input_path=Path(str(path))
#            print(input_path.resolve()) 
#            print(working_path.resolve())
    return inputfile_list