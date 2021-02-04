"""Module containing the KMCJob class."""

from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.InitialState import InitialState
from pyzacros.utils.setting_utils import check_settings
from pyzacros.utils.setting_utils import get_species, get_gas_species
from pyzacros.utils.find_utils import find_working_path, find_engine_path
from pyzacros.utils.io_utils import write_file_input
from typing import List
from subprocess import Popen, PIPE


class KMCJob:
    """Main KMC class."""

    def __init__(self, settings: KMCSettings = None,
                 lattice: Lattice = None,
                 mechanism: List[ElementaryReaction] = None,
                 cluster_expansions: List[Cluster] = None,
                 initialState: InitialState = None):
        """
        Create a new KMCJob object.

        Arguments are set by default to None because they can be read from
        standard Zacros input files.

        :parm settings: KMCSettings containing the parameters of the Zacros
                        calculation.
        :parm mechanism: Mechanism containing the mechanisms involved in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        :parm initialState: Initial state of the system. By default a KMC
                       simulation in Zacros is initialized with an empty
                       lattice.
        """
        # Initialize the dictionary of Zacros input files:
        dict_of_inputs = init_dict_of_inputs()

        # Attributes:
        if settings:
            # We need to check that both settings and mechanism
            # arguments have been passed on. Both are needed to
            # write the simulation_input.dat
            if not mechanism:
                msg = "### ERROR ### __init__ in KMCJob.py.\n"
                msg += "            KMCJob object instantiated\n"
                msg += "            with Settings but without Mechanism."
                raise NameError(msg)

            self.settings = settings
            # Find the working directory:
            self.working_path = find_working_path(self.settings)
            self.path_to_engine = find_engine_path(settings=self.settings)

        else:
            dict_of_inputs["simulation_input.dat"] = False  # Don't write file.
            print("### WARNING ### No working_path and path_to_engine set,"
                  " using the current folder.")
            self.working_path = './'
            self.path_to_engine = './zacros.x'

        if lattice:
            self.lattice = lattice
        else:
            dict_of_inputs["lattice_input.dat"] = False  # Don't write file.

        if mechanism:
            # We need to check that both settings and mechanism
            # arguments have been passed on. Both are needed to
            # write the simulation_input.dat
            if not settings:
                msg = "### ERROR ### __init__ in KMCJob.py.\n"
                msg += "            KMCJob object instantiated\n"
                msg += "            with Mechanism but without Settings."
                raise NameError(msg)

            self.mechanism = mechanism
        else:
            dict_of_inputs["mechanism_input.dat"] = False  # Don't write file.

        if cluster_expansions:
            self.clusters = cluster_expansions
        else:
            dict_of_inputs["energetics_input.dat"] = False  # Don't write file.

        if initialState:
            self.initialState = initialState
        else:
            dict_of_inputs["state_input.dat"] = False

        # Check KMCSettings content:
        if settings and mechanism:
            check_settings(self.settings,
                           get_gas_species(get_species(self.mechanism)))

        # Write input files:
        self.writeInputFiles(directory=self.working_path, dict=dict_of_inputs)

    def run(self):
        """Execute the KMC engine."""
        print("Running engine ...")
        p = Popen(self.path_to_engine, cwd=self.working_path,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        print("End running engine.")
        return

    def writeInputFiles(self, directory: str, dict: dict):
        """
        Write KMC inputs files to disk.

        :parm directory: Directory where the Zacros will be printed.
        :parm dict: Dictionary containing the names of the Zacros
                    input files needed to run the engine, and whether
                    they will have to be printed in the directory.
        """
        # If the boolean is True, the file will be printed.
        if dict["simulation_input.dat"] is True:
            with open(directory+"/simulation_input.dat", "w") as f:
                f.write(write_file_input(settings=self.settings,
                                         mechanism=self.mechanism))
        if dict["lattice_input.dat"] is True:
            with open(directory+"/lattice_input.dat", "w") as f:
                f.write(write_file_input(lattice=self.lattice))
        if dict["mechanism_input.dat"] is True:
            with open(directory+"/mechanism_input.dat", "w") as f:
                f.write(write_file_input(mechanism=self.mechanism))
        if dict["energetics_input.dat"] is True:
            with open(directory+"/energetics_input.dat", "w") as f:
                f.write(write_file_input(cluster_expansions=self.clusters))
        if dict["state_input.dat"] is True:
            with open(directory+"/state_input.dat", "w") as f:
                f.write(write_file_input(initial_state=self.initialState))
        return


def init_dict_of_inputs() -> dict:
    """
    Initialize the dictionary of input files.

    :return dict_of_inputs: {Name_of_input_file.dat : bool}
                            Dictionary containing the name of the default
                            Zacros input files names and a boolean set to
                            .True. meaning that the files will have to be
                            written in the working_directory.
    """
    dict_of_inputs = {
               "simulation_input.dat": True,
               "lattice_input.dat": True,
               "mechanism_input.dat": True,
               "energetics_input.dat": True,
               "state_input.dat": True
               }
    return(dict_of_inputs)
