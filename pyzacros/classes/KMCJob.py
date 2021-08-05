"""Module containing the KMCJob class."""

import os
from subprocess import Popen, PIPE

from .Lattice import *
from .SpeciesList import *
from .ClusterExpansion import *
from .Mechanism import *
from .InitialState import *
from .KMCSettings import *
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
        if( type(mechanism) == list ): self.mechanism = Mechanism(mechanism)
        self.cluster_expansion = cluster_expansion
        if( type(cluster_expansion) == list ): self.cluster_expansion = ClusterExpansion(cluster_expansion)
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
        KMCJob.check_settings(self.settings, self.mechanism.gas_species())


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
        output  = "random_seed     " + "%10s"%self.settings.get('random_seed')+"\n"
        output += "temperature     " + "%10s"%self.settings.get('temperature')+"\n"
        output += "pressure        " + "%10s"%self.settings.get('pressure')+"\n\n"

        gasSpecies = self.mechanism.gas_species()

        if( len(gasSpecies) == 0 ):
            output += "n_gas_species    "+str(len(gasSpecies))+"\n\n"
        else:
            output += str(gasSpecies)

        molar_frac_list = KMCJob.get_molar_fractions(self.settings, gasSpecies)

        if( len(molar_frac_list)>0 ):
            output += "gas_molar_fracs   " + ''.join(["%10s"%str(elem) for elem in molar_frac_list]) + "\n\n"
        output += str(self.mechanism.species())+"\n\n"

        output += self.print_optional_sett(opt_sett='snapshots')
        output += self.print_optional_sett(opt_sett='process_statistics')
        output += self.print_optional_sett(opt_sett='species_numbers')

        output += "event_report      " + str(self.settings.get(('event_report')))+"\n"
        output += "max_steps         " + str(self.settings.get(('max_steps')))+"\n"
        output += "max_time          " + str(self.settings.get(('max_time')))+"\n"
        output += "wall_time         " + str(self.settings.get(('wall_time')))+"\n"
        output += "\nfinish"
        return output


    def print_optional_sett(self, opt_sett: str) -> str:
        """Give back the printing of an time/event/logtime setting."""
        dictionary = self.settings.as_dict()

        if 'time' in str(dictionary[opt_sett]):
            output = "%-20s"%opt_sett + "      " + "on time       " + str(float(dictionary[opt_sett][1])) + "\n"
        if 'event' in str(dictionary[opt_sett]):
            output = "%-20s"%opt_sett + "      " + "on event\n"
        # because the order, it will overwrite time:
        if 'logtime' in str(dictionary[opt_sett]):
            output = "%-20s"%opt_sett + "      " + "on logtime      " + str(float(dictionary[opt_sett][1])) + "      " + \
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


    @staticmethod
    def check_settings(settings=KMCSettings, species_list=SpeciesList):
        """
        Check KMCSettings, load defaults if necessary.

        :parm settings: KMCSettings object with the main settings of the
                        KMC calculation.
        """
        # This list contains the defaults for KMCSettings, please modify
        # them as you wish.
        # They will NOT overwrite settings provided by user.
        KMCJob.check_molar_fraction(settings, species_list)
        tmp = KMCSettings(
            {'KMCEngine': {'name': 'Zacros'},
            'snapshots': ('time', 0.0005),
            'process_statistics': ('time', 0.0005),
            'species_numbers': ('time', 0.0005),
            'event_report': 'off',
            'max_steps': 'infinity',
            'max_time': 250.0,
            'wall_time': 10})
        # Soft merge of the settings:
        settings.soft_update(tmp)


    @staticmethod
    def check_molar_fraction(settings=KMCSettings,
                            species_list=SpeciesList):
        """
        Check if molar_fraction labels are compatible with Species labels.

        It also sets defaults molar_fractions 0.000.

        :parm settings: KMCSettings object with the main settings of the
                        KMC calculation.
        """
        list_of_species = [ sp.symbol for sp in species_list.gas_species() ]
        sett_keys = settings.as_dict()

        if( "molar_fraction" in sett_keys ):
            sett_keys = list(sett_keys["molar_fraction"])
            # Check if the molar fraction is assigned to a gas species:
            for i in sett_keys:
                if i not in list_of_species:
                    msg = "### ERROR ### check_molar_fraction_labels.\n"
                    msg += "molar fraction defined for a non-gas species."
                    raise NameError(msg)
            # Set default molar_fraction = 0.00 to the rest of gas species.
            for i in list_of_species:
                if i not in sett_keys:
                    tmp = KMCSettings({'molar_fraction': {i: 0.000}})
                    # Soft merge of the settings:
                    settings.soft_update(tmp)
        else:
            for i in list_of_species:
                tmp = KMCSettings({'molar_fraction': {i: 0.000}})
                # Soft merge of the settings:
                settings.soft_update(tmp)

    @staticmethod
    def get_molar_fractions(settings=KMCSettings,
                            species_list=SpeciesList) -> list:
        """
        Get molar fractions using the correct order of list_gas_species.

        :parm settings: KMCSettings object with the main settings of the
                        KMC calculation.

        :parm species_list: SpeciesList object containing the species
                                information.

        :rparm list_of_molar_fractions: Simple list of molar fracions.
        """
        # We must be sure that the order of return list is the same as
        # the order of the labels printed by SpeciesList.
        # For that:

        # 1- Generate a total_list of tuples with (atomic label,
        #    molar_fraciton):
        list_of_labels = []
        list_of_molar_fractions = []
        dic_test = settings.as_dict()
        for i, j in dic_test.items():
            if i == "molar_fraction":
                for key in sorted(j.keys()):
                    list_of_labels.append(key)
                    list_of_molar_fractions.append(j[key])
        total_list = list(zip(list_of_labels, list_of_molar_fractions))

        # 2- Match the tota_tuple to the "good" ordering of the
        # species_list:
        list_of_molar_fractions.clear()
        tuple_tmp = [i[0] for i in total_list]
        molar_tmp = [i[1] for i in total_list]
        for i in [ sp.symbol for sp in species_list.gas_species() ]:
            for j, k in enumerate(tuple_tmp):
                if i == k:
                    list_of_molar_fractions.append(molar_tmp[j])
        return list_of_molar_fractions
