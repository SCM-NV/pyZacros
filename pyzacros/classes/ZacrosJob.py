"""Module containing the ZacrosJob class."""

import os
import stat

import scm.plams

from .ZacrosResults import *
from .SpeciesList import *
from .ClusterExpansion import *
from .Mechanism import *
from .Settings import *

__all__ = ['ZacrosJob']

class ZacrosJob( scm.plams.SingleJob ):
    """
    A class representing a single computational job with Zacros
    """
    _command = 'zacros.x'
    _result_type = ZacrosResults
    _filenames = {
        'simulation': 'simulation_input.dat',
        'lattice': 'lattice_input.dat',
        'energetics': 'energetics_input.dat',
        'mechanism': 'mechanism_input.dat',
        'state': 'state_input.dat',
        'run': 'slurm.run',
        'err': 'std.err',
        'out': 'std.out'}


    def __init__(self, lattice, mechanism, cluster_expansion, initialState= None, **kwargs):
        """
        Create a new ZacrosJob object.

        :parm settings: Settings containing the parameters of the Zacros
                        calculation.
        :parm mechanism: Mechanism containing the mechanisms involed in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        :parm initialState: Initial state of the system. By default a KMC
                       simulation in Zacros is initialized with an empty
                       lattice.
        """
        def check_molar_fraction(settings=Settings, species_list=SpeciesList):
            """
            Check if molar_fraction labels are compatible with Species labels.

            It also sets defaults molar_fractions 0.000.

            :parm settings: Settings object with the main settings of the
                            KMC calculation.
            """
            list_of_species = [ sp.symbol for sp in species_list.gas_species() ]
            section = settings.molar_fraction

            if( "molar_fraction" in settings ):

                # Check if the molar fraction is assigned to a gas species:
                for key in settings.molar_fraction.keys():
                    if key not in list_of_species:
                        msg = "### ERROR ### check_molar_fraction_labels.\n"
                        msg += "molar fraction defined for a non-gas species."
                        raise NameError(msg)

                # Set default molar_fraction = 0.00 to the rest of gas species.
                for key in list_of_species:
                    if key not in settings.keys():
                        section += {key: 0.000}
            else:
                for key in list_of_species:
                    section += {key: 0.000}

        if( 'molecule' in kwargs ):
            print("Warning: parameter 'molecule' is not used by the ZacrosJob constructor'")
            del kwargs['molecule']

        scm.plams.SingleJob.__init__(self, molecule=None, **kwargs)

        self.lattice = lattice
        self.mechanism = mechanism
        if( type(mechanism) == list ): self.mechanism = Mechanism(mechanism)
        self.cluster_expansion = cluster_expansion
        if( type(cluster_expansion) == list ): self.cluster_expansion = ClusterExpansion(cluster_expansion)
        self.initialState = initialState

        check_molar_fraction(self.settings, self.mechanism.gas_species())

        defaults = Settings({'snapshots': ('time', 0.0005),
                             'process_statistics': ('time', 0.0005),
                             'species_numbers': ('time', 0.0005),
                             'event_report': 'off',
                             'max_steps': 'infinity',
                             'max_time': 250.0,
                             'wall_time': 10})

        self.settings += defaults


    def get_input(self):
        """
        It should generate the Zagros input file. But Zagros has several input files,
        so we don't use this function. Instead, we made the equivalent function for
        every input file. See below.
        """
        pass


    def get_simulation_input(self):
        """
        Return a string with the content of simulation_input.dat.
        """

        def print_optional_sett(self, opt_sett):
            """
            Give back the printing of an time/event/logtime setting.
            """
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

        def get_molar_fractions(settings=Settings,species_list=SpeciesList):
            """
            Get molar fractions using the correct order of list_gas_species.

            :parm settings: Settings object with the main settings of the
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

        output  = "random_seed     " + "%10s"%self.settings.get('random_seed')+"\n"
        output += "temperature     " + "%10s"%self.settings.get('temperature')+"\n"
        output += "pressure        " + "%10s"%self.settings.get('pressure')+"\n\n"

        gasSpecies = self.mechanism.gas_species()

        if( len(gasSpecies) == 0 ):
            output += "n_gas_species    "+str(len(gasSpecies))+"\n\n"
        else:
            output += str(gasSpecies)

        molar_frac_list = get_molar_fractions(self.settings, gasSpecies)

        if( len(molar_frac_list)>0 ):
            output += "gas_molar_fracs   " + ''.join(["%10s"%str(elem) for elem in molar_frac_list]) + "\n\n"
        output += str(self.mechanism.species())+"\n\n"

        output += print_optional_sett(self,opt_sett='snapshots')
        output += print_optional_sett(self,opt_sett='process_statistics')
        output += print_optional_sett(self,opt_sett='species_numbers')

        output += "event_report      " + str(self.settings.get(('event_report')))+"\n"
        output += "max_steps         " + str(self.settings.get(('max_steps')))+"\n"
        output += "max_time          " + str(self.settings.get(('max_time')))+"\n"
        output += "wall_time         " + str(self.settings.get(('wall_time')))+"\n"
        output += "\nfinish"
        return output


    def get_lattice_input(self):
        """
        Return a string with the content of the lattice_input.dat file.
        """
        return str(self.lattice)


    def get_energetics_input(self):
        """
        Return a string with the content of the energetics_input.dat file.
        """
        return str(self.cluster_expansion)


    def get_mechanism_input(self):
        """
        Returns a string with the content of the mechanism_input.dat file
        """
        return str(self.mechanism)


    def get_initial_state_input(self):
        """
        Returns a string with the content of the state_input.dat file
        """
        output = ""
        if( self.initialState is not None ):
            output = str(self.initialState)
        return output


    def get_runscript(self):
        """
        Generate a runscript for slurm

        ``name`` is taken from the class attribute ``_command``. ``-n`` flag is added if ``settings.runscript.nproc`` exists. ``[>jobname.out]`` is used based on ``settings.runscript.stdout_redirect``.
        """
        #path = find_path_to_engine(self.settings)

        s = self.settings.runscript

        ret = '#!/bin/bash\n'
        if 'nproc' in s:
            ret += '\n'
            ret += 'export OMP_NUM_THREADS='+str(s.nproc)
        ret += '\n'
        #ret += path
        ret += self._command

        if s.stdout_redirect:
            ret += ' >"{}"'.format(self._filename('out'))
        ret += '\n'

        return ret


    def _get_ready(self):
        """
        Create inputs and runscript files in the job folder.
        Filenames correspond to entries in the `_filenames` attribute"""
        simulation = os.path.join(self.path, self._filename('simulation'))
        lattice = os.path.join(self.path, self._filename('lattice'))
        energetics = os.path.join(self.path, self._filename('energetics'))
        mechanism = os.path.join(self.path, self._filename('mechanism'))
        state = os.path.join(self.path, self._filename('state'))

        runfile = os.path.join(self.path, self._filename('run'))
        #err = os.path.join(self.path, self._filename('err'))
        #out = os.path.join(self.path, self._filename('out'))

        with open(simulation, "w") as inp:
            inp.write(self.get_simulation_input())

        with open(lattice, "w") as inp:
            inp.write(self.get_lattice_input())

        with open(energetics, "w") as inp:
            inp.write(self.get_energetics_input())

        with open(mechanism, "w") as inp:
            inp.write(self.get_mechanism_input())

        if self.initialState is not None:
            with open(state, "w") as inp:
                inp.write(self.get_initial_state_input())

        with open(runfile, 'w') as run:
            run.write(self.get_runscript())

        os.chmod(runfile, os.stat(runfile).st_mode | stat.S_IEXEC)


    def __str__(self):
        """
        Translate the object to a string.
        """
        output = ""

        output += "---------------------------------------------------------------------"+"\n"
        output += self._filename('simulation')+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_simulation_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self._filename('lattice')+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_lattice_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self._filename('energetics')+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_energetics_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self._filename('mechanism')+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_mechanism_input()

        if(self.initialState is not None):
            output += "\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += self._filename('state')+"\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += self.get_initial_state_input()

        return output
