# -*- PLT@NLeSC(2020) -*-
"""Module containing utility functions to find files."""

import os
from os import path
from pyzacros.classes.KMCSettings import KMCSettings


def find_file(name: str, path_to_search: str) -> path:
    """Find a given name file."""
    for root, dirs, files in os.walk(path_to_search):
        if name in files:
            return os.path.join(root, name)


def find_engine_path(settings: KMCSettings) -> str:
    """
    Find the path to the KMC engine using the sett.KMCEngine.path setting.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    :return path_to_engine: The path to the engine.
    """
    # Set path_to_engine:
    #   If the engine is Zacros(default):
    if str(settings.get_nested(('KMCEngine', 'name'))).lower() == 'zacros':
        print("The selected KMC engine is Zacros.")
        # Check if there is a given path to the executable:
        if settings.get_nested(('KMCEngine', 'path')):
            # Does it exist?
            path_to_engine = settings.get_nested(('KMCEngine', 'path'))
            # Then search:
            if path.exists(path_to_engine):
                path_to_engine = find_file('zacros.x',
                                           path_to_search=path_to_engine)
                print("Using Zacros executable:\n", path_to_engine)
            else:
                msg = "### ERROR ### check_settings\n"
                msg += "Path to KMCEngine does not exist.\n"
                raise FileNotFoundError(msg)
        else:
            msg = "### ERROR ### check_settings\n"
            msg += "sett.KMCEngine.path is not defined.\n"
            raise NameError(msg)
    else:
        # Otherwise rise an error:
        # FIXME to add more KMCengines.
        msg = "### ERROR ### check_settings\n"
        msg += "KMC engine not implemented.\n"
        raise NotImplementedError(msg)
    return path_to_engine


def find_working_path(settings: KMCSettings) -> str:
    """
    Find the path to the KMC working directory where outputs will be plotted.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    :return path_to_engine: The path of the working directory.
    """
    # Set path_to_output:
    if settings.get_nested(('KMCOutput', 'path')):
        working_path = settings.get_nested(('KMCOutput', 'path'))
    else:
        working_path = './'
    if not path.exists(working_path):
        print("KMCOutput does not exist, taking current ./ directory.")
        working_path = './'
    print("Working directory:\n", working_path)

    return working_path


def find_input_files(engine: str,
                     electronic_package: str = None,
                     path: str = None) -> list:
    """
    Search engine.yml or engine.yaml input files.

    If none, engine standard input files will be searched.
    :return: A list of input files.
    """
    # TODO Search yaml files or standard input files according to engine.
    inputfile_list = []

    working_path = Path.cwd()
    folders = []
    files = []
    for item in os.scandir(working_path):
        print("there is file!")
    for entry in os.scandir(working_path):
        print(entry)
#    if entry.is_file():
#        print(entry.name)
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
