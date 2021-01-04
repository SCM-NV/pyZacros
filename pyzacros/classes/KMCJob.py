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

    def __init__(self, settings: KMCSettings,
                 lattice: Lattice,
                 mechanism: List[ElementaryReaction],
                 cluster_expansions: List[Cluster],
                 initialState: InitialState = None):
        """
        Create a new KMCJob object.

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
        # Attributes:
        self.settings = settings
        self.lattice = lattice
        self.mechanism = mechanism
        self.clusters = cluster_expansions
        self.initialState = initialState

        # Check KMCSettings:
        check_settings(self.settings,
                       get_gas_species(get_species(self.mechanism)))

        # Find the working directory:
        self.working_path = find_working_path(self.settings)

        # Write input files:
        self.writeInputFiles(directory=self.working_path)

    def run(self):
        """Execute the KMC engine."""
        # Find path to engine:
        path_to_engine = find_engine_path(settings=self.settings)

        # Run engine:
        print("Running engine:")
        p = Popen(path_to_engine, cwd=self.working_path,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        print("End running engine.")
        return

    def writeInputFiles(self, directory: str):
        """
        Write KMC inputs files to disk.

        :parm directory: Directory where the Zacros will be printed.
        """
        # TODO here insert options to read standard Zacros inputs.
        # e.g. if there is no simulation_input.dat then:
        with open(directory+"/simulation_input.dat", "w") as f:
            f.write(write_file_input(settings=self.settings,
                                     mechanism=self.mechanism))
        with open(directory+"/lattice_input.dat", "w") as f:
            f.write(write_file_input(lattice=self.lattice))
        with open(directory+"/mechanism_input.dat", "w") as f:
            f.write(write_file_input(mechanism=self.mechanism))
        with open(directory+"/energetics_input.dat", "w") as f:
            f.write(write_file_input(cluster_expansions=self.clusters))
        if(self.initialState is not None):
            with open(directory+"/state_input.dat", "w") as f:
                f.write(initial_state=self.stateInput)
        return
