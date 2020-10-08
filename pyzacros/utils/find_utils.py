# -*- PLT@NLeSC(2020) -*-
"""Module containing utility functions to find files."""

import os
import shutil
from os import path
from pyzacros.classes.KMCSettings import KMCSettings


def find_file(name, path_to_search):
    """Find a given name file."""
    for root, dirs, files in os.walk(path_to_search):
        if name in files:
            return os.path.join(root, name)


def find_path_to_engine(settings: KMCSettings) -> tuple:
    """
    Find the path to the KMC engine using the sett.KMCEngine.path.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    :type settings: KMCSettings, required.
    :return path_to_engine: The path to the engine.
    :rtype path_to_engine: str
    """
    # 1. Set path_to_engine:
    #   If the engine is Zacros(default):
    if str(settings.get_nested(('KMCEngine', 'name'))).lower() == 'zacros':
        print("The selected KMC engine is Zacros.")

        # First tries to find 'zacros.x' in the directories listed in 'path'
        path_to_engine = shutil.which( 'zacros.x' )
        if path_to_engine is None:
            # Check if there is a given path to the executable:
            if settings.get_nested(('KMCEngine', 'path')):
                # Does it exist?
                path_to_engine = settings.get_nested(('KMCEngine', 'path'))
                # Then search:
                if path.exists(path_to_engine):
                    path_to_engine = find_file('zacros.x',
                                            path_to_search=path_to_engine)
                else:
                    msg = "### ERROR ### check_settings\n"
                    msg += "Path to KMCEngine does not exist.\n"
                    raise FileNotFoundError(msg)
            else:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "sett.KMCEngine.path is not defined or the Zacros executable is not in the path.\n"
                raise NameError(msg)

        print("Using Zacros executable:\n", path_to_engine)
    else:
        # Otherwise rise an error:
        # FIXME to add more KMCengines.
        msg = "### ERROR ### check_settings\n"
        msg += "KMC engine not implemented.\n"
        raise NotImplementedError(msg)

    return path_to_engine


def find_input_files(engine: str,
                     electronic_package: str = None,
                     path: str = None) -> list:
    """
    Search enigne.yml or engine.yaml input files.

    If none, engine standard input files will be searched.
    :return: A list of input files.
    :rtype : list.
    """
    # TODO Search yaml files or standard input files according to engine.
    inputfile_list = []

    working_path = Path.cwd()
    print("Pablo resolves", working_path.resolve())
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
