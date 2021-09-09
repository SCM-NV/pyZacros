"""Module containing the ZacrosJob class."""

import os
import stat

import scm.plams

from .ZacrosResults import *
from .SpeciesList import *
from .Lattice import *
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
        It should generate the Zacros input file. But Zacros has several
        input files. So, we discourage using this function.
        On the other side, this function is also used as a hash to
        represent the job univocally. Because of that, we just return
        its string representation which contains all input files concatenated.
        """
        return str(self)


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
            output += "gas_molar_fracs   " + ''.join([" %9s"%str(elem) for elem in molar_frac_list]) + "\n\n"
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


    def check(self):
        """
        Look for the normal termination signal in output. Note, that does not mean your calculation was successful!
        """
        lines = self.results.grep_file(self.results._filenames['general'], pattern='> Normal termination <')
        return len(lines) > 0


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
            ret += ' >"{}"'.format(ZacrosJob._filenames['out'])
        ret += '\n'

        return ret


    def _get_ready(self):
        """
        Create inputs and runscript files in the job folder.
        Filenames correspond to entries in the `_filenames` attribute
        """
        simulation = os.path.join(self.path, ZacrosJob._filenames['simulation'])
        lattice = os.path.join(self.path, ZacrosJob._filenames['lattice'])
        energetics = os.path.join(self.path, ZacrosJob._filenames['energetics'])
        mechanism = os.path.join(self.path, ZacrosJob._filenames['mechanism'])
        state = os.path.join(self.path, ZacrosJob._filenames['state'])

        runfile = os.path.join(self.path, ZacrosJob._filenames['run'])
        #err = os.path.join(self.path, ZacrosJob._filenames['err'])
        #out = os.path.join(self.path, ZacrosJob._filenames['out'])

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
        output += ZacrosJob._filenames['simulation']+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_simulation_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += ZacrosJob._filenames['lattice']+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_lattice_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += ZacrosJob._filenames['energetics']+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_energetics_input()

        output += "\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += ZacrosJob._filenames['mechanism']+"\n"
        output += "---------------------------------------------------------------------"+"\n"
        output += self.get_mechanism_input()

        if(self.initialState is not None):
            output += "\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += ZacrosJob._filenames['state']+"\n"
            output += "---------------------------------------------------------------------"+"\n"
            output += self.get_initial_state_input()

        return output


    @staticmethod
    def __recreate_simulation_input( path ):
        """
        Recreates the simulation input for the corresponding job based on file 'simulation_input.dat' present in the job folder.
        This method is used by |load_external|.
        Returns a |Settings| object.
        """
        sett = Settings()

        with open( path+"/"+ZacrosJob._filenames['simulation'], "r" ) as inp:
            file_content = inp.readlines()
        file_content = [line for line in file_content if line.strip()] # Removes empty lines

        for line in file_content:
            tokens = line.split()

            if( len(tokens)<2 ): continue

            # Specific conversion rules
            cases = {
                "random_seed" : lambda sv: sett.setdefault("random_seed", int(sv[0])),
                "temperature" : lambda sv: sett.setdefault("temperature", float(sv[0])),
                "pressure" : lambda sv: sett.setdefault("pressure", float(sv[0])),

                "n_gas_species" : lambda sv: sett.setdefault("n_gas_species", int(sv[0])),
                "gas_specs_names" : lambda sv: sett.setdefault("gas_specs_names", sv),
                "gas_energies" : lambda sv: sett.setdefault("gas_energies", [float(a) for a in sv]),
                "gas_molec_weights" : lambda sv: sett.setdefault("gas_molec_weights", [float(a) for a in sv]),
                "gas_molar_fracs" : lambda sv: sett.setdefault("gas_molar_fracs", [float(a) for a in sv]),

                "n_surf_species" : lambda sv: sett.setdefault("n_surf_species", int(sv[0])),
                "surf_specs_names" : lambda sv: sett.setdefault("surf_specs_names", sv),
                "surf_specs_dent" : lambda sv: sett.setdefault("surf_specs_dent", [int(a) for a in sv]),

                "snapshots" : lambda sv: sett.setdefault("snapshots", ( sv[1],float(sv[2]) ) ),
                "process_statistics" : lambda sv: sett.setdefault("process_statistics", ( sv[1],float(sv[2]) )),
                "species_numbers" : lambda sv: sett.setdefault("species_numbers", ( sv[1],float(sv[2]) )),
                "event_report" : lambda sv: sett.setdefault("event_report", sv),
                "max_steps" : lambda sv: sett.setdefault("max_steps", sv[0] if sv[0]=='infinity' else int(sv[0])),
                "max_time" : lambda sv: sett.setdefault("max_time", float(sv[0])),
                "wall_time" : lambda sv: sett.setdefault("wall_time", int(sv[0]))
            }

            value = cases.get( tokens[0], lambda sv: None )( tokens[1:] )

            if( value is None ):
                raise Exception( "Error: Keyword "+tokens[0]+" in file "+ZacrosJob._filenames['simulation']+" is not supported!" )

        return sett


    @staticmethod
    def __recreate_lattice_input( path ):
        """
        Recreates the lattice input for the corresponding job based on file 'lattice_input.dat' present in the job folder.
        This method is used by |load_external|.
        Returns a |Lattice| object.
        """
        lattice = None

        with open( path+"/"+ZacrosJob._filenames['lattice'], "r" ) as inp:
            file_content = inp.readlines()
        file_content = [line for line in file_content if line.strip()] # Removes empty lines

        print("---")
        for line in file_content:
            print(line[:-1])
        print("---")

        nline = 0
        while( nline < len(file_content) ):
            tokens = file_content[nline].split()

            if( tokens[0].lower() == "lattice" and tokens[1].lower() == "default_choice" ):
                nline += 1
                tokens = file_content[nline].split()

                if( len(tokens) < 4 ):
                    raise Exception( "Format Error in line "+str(nline)+" of file "+ZacrosJob._filenames['lattice'] )

                cases = {
                    "triangular_periodic" : Lattice.TRIANGULAR,
                    "rectangular_periodic" : Lattice.RECTANGULAR,
                    "hexagonal_periodic" : Lattice.HEXAGONAL
                }

                lattice_type = cases.get( tokens[0].lower(), None )

                if( lattice_type is None ):
                    raise Exception( "Error: Keyword "+tokens[0]+" in file "+ZacrosJob._filenames['lattice']+" is not supported!" )

                lattice_constant = float(tokens[1])
                repeat_cell = ( int(tokens[2]), int(tokens[3]) )

                lattice = Lattice( lattice_type=lattice_type, lattice_constant=lattice_constant, repeat_cell=repeat_cell )

            if( tokens[0] == "lattice" and tokens[1] == "periodic_cell" ):
                raise Exception("Error: Lattice periodic_cell is not implemented yet!")
            if( tokens[0] == "lattice" and tokens[1] == "explicit" ):
                raise Exception("Error: Lattice periodic_cell is not implemented yet!")

            nline += 1

        return lattice


    @staticmethod
    def __recreate_energetics_input():
        """
        Recreates the energetics input for the corresponding job based on file 'energetics_input.dat' present in the job folder.
        This method is used by |load_external|.
        Returns a list of |Cluster| objects.
        """
        cluster_expansion = []
        return cluster_expansion


    @staticmethod
    def __recreate_mechanism_input():
        """
        Recreates the mechanism input for the corresponding job based on file 'mechanism_input.dat' present in the job folder.
        This method is used by |load_external|.
        Returns a list of |ElementaryReaction| objects.
        """
        mechanism = []
        return mechanism


    @staticmethod
    def __recreate_initial_state_input( lattice ):
        """
        Recreates the initial state input for the corresponding job based on file 'initial_state_input.dat' present in the job folder.
        This method is used by |load_external|.
        Returns a |LatticeState| object
        """
        lattice_state = LatticeState()
        return lattice_state


    @classmethod
    def load_external(cls, path, settings=None, molecule=None, finalize=False):
        """
        Load an external job from *path*.
        """
        if( not os.path.isdir(path) ):
            raise FileError('Path {} does not exist, cannot load from it.'.format(path))

        path = os.path.abspath(path)
        jobname = os.path.basename(path)

        sett = ZacrosJob.__recreate_simulation_input( path )
        lattice = ZacrosJob.__recreate_lattice_input( path )
        print(">")
        print(">")
        #print(sett)
        print(lattice)
        exit(0)

        #job = cls( name=jobname )
        #job.path = path
        ##job.status = 'copied'
        ##job.results.collect()

        #job.settings  = settings or job.results.recreate_settings() or config.job.copy()
        #job.molecule  = molecule or job.results.recreate_molecule()

        #job = super(ZacrosJob, cls).load_external( path, settings, molecule, finalize)
        #return job

