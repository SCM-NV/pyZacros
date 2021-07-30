"""Module containing the KMCJob class."""

import os
from subprocess import Popen, PIPE

from .Lattice import *
from .SpeciesList import *
from .ClusterExpansion import *
from .Mechanism import *
from .InitialState import *
from .KMCSettings import *
from pyzacros.utils.setting_utils import check_settings, get_molar_fractions
from pyzacros.utils.find_utils import find_path_to_engine

__all__ = ['KMCJob']

class KMCJob:
    """Job class that represents a chemical species."""


    def __init__(self, settings: KMCSettings, lattice: Lattice, mechanism: Mechanism,
                cluster_expansion: ClusterExpansion, initialState: InitialState = None, name: str = "results"):
        """
        Create a new Job object.

        :parm settings: KMCSettings containing the parameters of the Zacros
                        calculation.
        :parm mechanism: Mechanism containing the mechanisms involed in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        :parm initialState: Initial state of the system. By default a KMC
                       simulation in Zacros is initialized with an empty
                       lattice.
        """
        self.settings = settings
        self.lattice = lattice
        self.mechanism = mechanism
        self.cluster_expansion = cluster_expansion
        self.initialState = initialState
        self.name = name
        self.working_path = 'pyzacros_workdir/'+self.name

        # If directory already exists:
        if( os.path.isdir( self.working_path ) ):
            i=2
            while( True ):
                new_working_path = 'pyzacros_workdir'+"."+str("%03d"%i)+"/"+self.name
                if( not os.path.isdir( new_working_path ) ):
                    self.working_path = new_working_path
                    break
                i = i+1

        os.makedirs(self.working_path, exist_ok=True)
        print("Working directory:", self.working_path)

        # Check settings:
        check_settings(self.settings, self.mechanism.gas_species())

    def __str__(self) -> str:
        """Translate the object to a string."""
        output = ""

        output += "---------------------------------------------------------------------"+"\n"
        output += "simulation_input.dat"+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.simulationInput()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += "lattice_input.dat"+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.latticeInput()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += "energetics_input.dat"+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.energeticsInput()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += "mechanism_input.dat"+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.mechanismInput()

        if(self.initialState is not None):
            output += "\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += "state_input.dat"+"\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += self.stateInput()

        return output

    def run(self):
        """Execute the KMC engine."""
        path_to_engine = find_path_to_engine(self.settings)
        self.writeInputFiles(directory=self.working_path)
        print("Running engine:")
        p = Popen(path_to_engine, cwd=self.working_path,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        print("End running engine.")
        return

    def simulationInput(self) -> str:
        """Return a string with the content of simulation_input.dat ."""
        output = "random_seed\t" + \
                 str(self.settings.get(('random_seed')))+"\n"
        output += "temperature\t" + \
                  str(float(self.settings.get(('temperature'))))+"\n"
        output += "pressure\t" + \
                  str(float(self.settings.get(('pressure'))))+"\n\n"

        gasSpecies = self.mechanism.gas_species()

        if( len(gasSpecies) == 0 ):
            output += "n_gas_species "+str(len(gasSpecies))+"\n\n"
        else:
            output += str(gasSpecies)

        molar_frac_list = get_molar_fractions(self.settings, gasSpecies)

        if( len(molar_frac_list)>0 ):
            output += "gas_molar_fracs \t" + \
                    '\t '.join([str(elem) for elem in molar_frac_list]) \
                    + "\n\n"
        output += str(self.mechanism.species())+"\n\n"

        output += self.print_optional_sett(opt_sett='snapshots')
        output += self.print_optional_sett(opt_sett='process_statistics')
        output += self.print_optional_sett(opt_sett='species_numbers')

        output += "event_report\t" + \
                  str(self.settings.get(('event_report')))+"\n"
        output += "max_steps\t" + \
                  str(self.settings.get(('max_steps')))+"\n"
        output += "max_time\t" + \
                  str(self.settings.get(('max_time')))+"\n"
        output += "wall_time\t" + \
                  str(self.settings.get(('wall_time')))+"\n"
        output += "\nfinish"
        return output

    def print_optional_sett(self, opt_sett: str) -> str:
        """Give back the printing of an time/event/logtime setting."""
        dictionary = self.settings.as_dict()

        if 'time' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on time \t" + \
                     str(float(dictionary[opt_sett][1])) + "\n"
        if 'event' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on event\n"
        # becuase the order, it will overwrite time:
        if 'logtime' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on logtime\t" + \
                    str(float(dictionary[opt_sett][1])) + "\t" + \
                    str(float(dictionary[opt_sett][2])) + "\n"
        return output

    def latticeInput(self) -> str:
        """Return a string with the content of the lattice_input.dat file."""
        output = str(self.lattice)
        return output


    def energeticsInput(self) -> str:
        """Return a string with the content of the energetics_input.dat file."""
        output = str(self.cluster_expansion)
        return output


    def mechanismInput(self) -> str:
        """
        Returns a string with the content of the mechanism_input.dat file
        """
        output = str(self.mechanism)
        return output


    def stateInput(self) -> str:
        """
        Returns a string with the content of the state_input.dat file
        """
        output = ""
        if( self.initialState is not None ):
            output = str(self.initialState)
        return output


    def writeInputFiles(self, directory: str):
        """
        Write KMC inputs files to disk.

        :parm directory: Directory where the Zacros will be printed.
        :type directory: str, required.
        """
        with open(directory+"/simulation_input.dat", "w") as f:
            f.write(self.simulationInput())
        with open(directory+"/lattice_input.dat", "w") as f:
            f.write(self.latticeInput())
        with open(directory+"/energetics_input.dat", "w") as f:
            f.write(self.energeticsInput())
        with open(directory+"/mechanism_input.dat", "w") as f:
            f.write(self.mechanismInput())
        if(self.initialState is not None):
            with open(directory+"/state_input.dat", "w") as f:
                f.write(self.stateInput())
