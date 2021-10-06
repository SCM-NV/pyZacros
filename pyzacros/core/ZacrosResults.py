"""Module containing the ZacrosResults class."""

import os
import stat

import scm.plams

from .Lattice import *
from .SpeciesList import *
from .ClusterExpansion import *
from .Mechanism import *
from .LatticeState import *
from .Settings import *

__all__ = ['ZacrosResults']

class ZacrosResults( scm.plams.Results ):
    """
    A Class for handling Zacros Results.
    """
    _filenames = {
        'general': 'general_output.txt',
        'history': 'history_output.txt',
        'lattice': 'lattice_output.txt',
        'procstat': 'procstat_output.txt',
        'specnum': 'specnum_output.txt',
        'err': 'std.err',
        'out': 'std.out'}


    def get_zacros_version(self):
        """
        Return the zacros's version from the 'general_output.txt' file.
        """
        lines = self.grep_file(self._filenames['general'], pattern='ZACROS')
        zversion = lines[0].split()[2]
        return float(zversion)


    def get_reaction_network(self):
        """
        Return the reactions from the 'general_output.txt' file.
        """
        lines = self.get_file_chunk(self._filenames['general'], begin="Reaction network:", end="Finished reading mechanism input.")

        reaction_network = {}
        for line in lines:
            if( not line.strip() or line.find("A(Tini)") == -1 ): continue
            reaction_network[ line.split()[1].replace(':','') ] = line[line.find("Reaction:")+len("Reaction:"):].strip().replace('  ',' ')

        return reaction_network


    def provided_quantities(self):
        """
        Return the provided quantities from the 'specnum_output.txt' file in a form of a dictionary.
        """
        lines = self.awk_file(self._filenames['specnum'],script='(NR==1){print $0}')
        names = lines[0].split()

        quantities = {}
        for name in names:
            quantities[name] = []

        lines = self.awk_file(self._filenames['specnum'],script='(NR>1){print $0}')

        for line in lines:
            for i,token in enumerate(line.split()):
                # Specific conversion rules
                cases = {
                    "Time"        : lambda sv: float(sv),
                    "Temperature" : lambda sv: float(sv),
                    "Energy"      : lambda sv: float(sv)
                }

                # Notice that by default values are considered integers
                value = cases.get( names[i], lambda sv: int(sv) )( token.strip() )
                quantities[ names[i] ].append( value )

        return quantities


    def number_of_lattice_sites(self):
        """
        Return the number of lattice sites from the 'general_output.txt' file.
        """
        zversion = self.get_zacros_version()

        if( zversion >= 2.0 and zversion < 3.0 ):
            lines = self.grep_file(self._filenames['general'], pattern='Number of lattice sites:')
            nsites = lines[0][ lines[0].find('Number of lattice sites:')+len("Number of lattice sites:"): ]
        elif( zversion >= 3.0 ):
            lines = self.grep_file(self._filenames['general'], pattern='Total number of lattice sites:')
            nsites = lines[0][ lines[0].find('Total number of lattice sites:')+len("Total number of lattice sites:"): ]
        else:
            raise Exception( "Error: Zacros version "+str(zversion)+" not supported!" )

        return int(nsites)


    def gas_species_names(self):
        """
        Return the gas species names from the 'general_output.txt' file.
        """
        lines = self.grep_file(self._filenames['general'], pattern='Gas species names:')
        return lines[0][ lines[0].find('Gas species names:')+len("Gas species names:"): ].split()


    def surface_species_names(self):
        """
        Return the surface species names from the 'general_output.txt' file.
        """
        lines = self.grep_file(self._filenames['general'], pattern='Surface species names:')
        return lines[0][ lines[0].find('Surface species names:')+len("Surface species names:"): ].split()


    def site_type_names(self):
        """
        Return the site types from the 'general_output.txt' file.
        """
        zversion = self.get_zacros_version()

        if( zversion >= 2.0 and zversion < 3.0 ):
            lines = self.get_file_chunk(self._filenames['general'], begin="Site type names and number of sites of that type:",
                                            end='Maximum coordination number:')
        elif( zversion >= 3.0 ):
            lines = self.get_file_chunk(self._filenames['general'], begin="Site type names and total number of sites of that type:",
                                            end='Maximum coordination number:')
        else:
            raise Exception( "Error: Zacros version "+str(zversion)+" not supported!" )

        site_types = []
        for line in lines:
            if( not line.strip() ): continue
            site_types.append( line.split()[0] )

        return site_types


    def number_of_configurations(self):
        """
        Return the number of configurations from the 'history_output.txt' file.
        """
        lines = self.grep_file(self._filenames['history'], pattern='configuration')
        return len(lines)


    def lattice_states(self):
        """
        Return the configurations from the 'history_output.txt' file.
        """
        output = []

        number_of_configurations = self.number_of_configurations()
        number_of_lattice_sites = self.number_of_lattice_sites()

        lines = self.grep_file(self._filenames['history'], pattern='Gas_Species:')
        gas_species_names = lines[0][ lines[0].find('Gas_Species:')+len("Gas_Species:"): ].split()

        gas_species = len(gas_species_names)*[None]
        for i,sname in enumerate(gas_species_names):
            for sp in self.job.mechanism.gas_species():
                if( sname == sp.symbol ):
                    gas_species[i] = sp
        gas_species = SpeciesList( gas_species )

        assert gas_species_names == self.gas_species_names(), "Warning: Inconsistent gas species between "+ \
            self._filenames['history']+" and "+self._filenames['general']

        lines = self.grep_file(self._filenames['history'], pattern='Surface_Species:')
        surface_species_names = lines[0][ lines[0].find('Surface_Species:')+len("Surface_Species:"): ].split()

        surface_species = len(surface_species_names)*[None]
        for i,sname in enumerate(surface_species_names):
            for sp in self.job.mechanism.surface_species():
                if( sname == sp.symbol ):
                    surface_species[i] = sp
        surface_species = SpeciesList( surface_species )

        assert surface_species_names == self.surface_species_names(), "Warning: Inconsistent surface species between "+ \
            self._filenames['history']+" and "+self._filenames['general']

        lines = self.get_file_chunk(self._filenames['history'], begin="configuration", end="Finished reading mechanism input.")

        for nconf in range(number_of_configurations):
            lines = self.grep_file(self._filenames['history'], pattern='configuration', options="-A"+str(number_of_lattice_sites)+" -m"+str(nconf+1))
            lines = lines[-number_of_lattice_sites-1:] # Equivalent to tail -n $number_of_lattice_sites+1

            lattice_state = None
            pos = 0
            for nline,line in enumerate(lines):
                tokens = line.split()

                if( nline==0 ):
                    assert tokens[0] == "configuration"

                    configuration_number = int(tokens[1])
                    number_of_events = int(tokens[2])
                    time = float(tokens[3])
                    temperature = float(tokens[4])
                    energy = float(tokens[5])

                    add_info = {"number_of_events":number_of_events, "time":time,
                                "temperature":temperature, "energy":energy}
                    lattice_state = LatticeState( self.job.lattice, surface_species, add_info=add_info )
                else:
                    site_number = int(tokens[0])-1 # Zacros uses arrays indexed from 1
                    adsorbate_number = int(tokens[1])
                    species_number = int(tokens[2])-1 # Zacros uses arrays indexed from 1
                    dentation = int(tokens[3])

                    if( species_number > -1 ): # In zacros -1 means empty site (0 for Zacros)
                        lattice_state.fill_site( site_number, surface_species[species_number] )

                    pos += 1

            output.append( lattice_state )

        return output

        #id
        #nevents
        #time
        #temperature
        #energy
        #site_number
        #entity_id
        #species_number
        #dentation
        #ngas_molecules


    def plot_lattice_states(self, pause=-1, show=True, ax=None, close=False):
        """
        Plots the lattice states as an animation
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        plt.rcParams["figure.autolayout"] = True
        for i,ls in enumerate(self.lattice_states()):
            ax.cla()
            ls.plot( show=True, pause=0.5, ax=ax )

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")


    def plot_molecule_numbers(self, species_name, pause=-1, show=True, ax=None, close=False):
        """
        Plots the Molecule Numbers as a function of time
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        provided_quantities = self.provided_quantities()

        COLORS = ['r', 'g', 'b', 'm']

        ax.set_xlabel('t (s)')
        ax.set_ylabel('Molecule Numbers')

        for i,spn in enumerate(species_name):
            ax.step(provided_quantities["Time"], provided_quantities[spn], where='post', color=COLORS[i], label=spn)

        ax.legend(loc='best')

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")


    def get_process_statistics(self):
        """
        Return the statistics from the 'specnum_output.txt' file.
        """
        output = []

        lines = self.grep_file(self._filenames['procstat'], pattern='Overall')
        elementary_steps_names = lines[0][ lines[0].find('Overall')+len("Overall"): ].split()

        lines = self.grep_file(self._filenames['procstat'], pattern='configuration')
        number_of_configurations = len(lines)

        for nconf in range(number_of_configurations):
            lines = self.grep_file(self._filenames['procstat'], pattern='configuration', options="-A2 -m"+str(nconf+1))
            lines = lines[-2-1:] # Equivalent to tail -n $number_of_lattice_sites+1

            procstat_state = {}
            pos = 0
            for nline,line in enumerate(lines):
                tokens = line.split()

                if( nline==0 ):
                    assert tokens[0] == "configuration"

                    configuration_number = int(tokens[1])
                    total_number_of_events = int(tokens[2])
                    time = float(tokens[3])

                    procstat_state["configuration_number"] = configuration_number
                    procstat_state["total_number_of_events"] = total_number_of_events
                    procstat_state["time"] = time

                elif( nline==1 ):
                    assert len(tokens)-1 == len(elementary_steps_names)

                    average_waiting_time = {}
                    for i,k in enumerate(elementary_steps_names):
                        average_waiting_time[k] = float(tokens[i+1])

                    procstat_state["average_waiting_time"] = average_waiting_time

                elif( nline==2 ):
                    assert len(tokens)-1 == len(elementary_steps_names)

                    number_of_events = {}
                    occurence_frequency = {}
                    for i,k in enumerate(elementary_steps_names):
                        number_of_events[k] = int(tokens[i+1])

                        if( procstat_state["time"] > 0.0 ):
                            occurence_frequency[k] = number_of_events[k]/procstat_state["time"]
                        else:
                            occurence_frequency[k] = 0.0

                    procstat_state["number_of_events"] = number_of_events
                    procstat_state["occurence_frequency"] = occurence_frequency

                else:
                    raise( "Error: Wrong format in file specnum_output.txt" )

                pos += 1

            output.append( procstat_state )


        return output


    def plot_process_statistics(self, data, key, log_scale=False, pause=-1, show=True, ax=None, close=False):
        """
        Plots data as a histogram
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        plt.rcParams["figure.autolayout"] = True

        provided_quantities = self.provided_quantities()

        ax.set_title('t $\in$ [0.000,{:.3f}] s'.format(data["time"]))
        ax.set_xlabel(key)

        keys = list(data[key].keys())
        y_pos = len(keys)*[None]
        j = 0
        for i in range(len(keys)):
            if( i==0 ):
                y_pos[i] = j
            else:
                if( keys[i].replace('_fwd','').replace('_rev','') != keys[i-1].replace('_fwd','').replace('_rev','') ):
                    j += 1

                y_pos[i] = j

        COLORS = ['r', 'b', 'g', 'm']
        color = len(y_pos)*[COLORS[0]]

        j = 0
        for i in range(1,len(y_pos)):
            if( y_pos[i] == y_pos[i-1] ):
                y_pos[i] += 0.15
                y_pos[i-1] -= 0.15
                color[i] = COLORS[j]
                color[i-1] = COLORS[j+1]

        ax.barh(y_pos, data[key].values(), align='center', height=0.25, color=color)

        if( log_scale ):
            ax.set_xlim((1e0,1.2*max(data[key].values())))
            plt.xscale("log")

        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_yticks(y_pos)
        ax.set_yticklabels(keys)
        plt.tight_layout()

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")


    def get_TOFs(self, npoints=None):
        """
        Return the TOF calculated with the last ```npoints```
        """
        values = {}
        errors = {}

        try:
            import math
            import scipy.optimize
        except ImportError as e:
            return values,errors # module doesn't exist, deal with it.

        def line(x, a, b):
            return a * x + b

        gas_species_names = self.gas_species_names()
        provided_quantities = self.provided_quantities()

        if( npoints is None ):
            tVec = provided_quantities["Time"]
        else:
            tVec = provided_quantities["Time"][-npoints:]

        for sn in gas_species_names:

            if( npoints is None ):
                nMolsVec = provided_quantities[sn]
            else:
                nMolsVec = provided_quantities[sn][-npoints:]

            popt,pcov = scipy.optimize.curve_fit(line, tVec, nMolsVec)

            values[sn] = popt[0]
            errors[sn] = math.sqrt(pcov[0,0])

        return values,errors
