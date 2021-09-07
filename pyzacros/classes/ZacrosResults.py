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


    def get_reaction_network(self):
        """
        Return the reactions from the 'general_output.txt' file.
        """
        lines = self.get_file_chunk(self._filenames['general'], begin="Reaction network:", end="Finished reading mechanism input.")

        reaction_network = {}
        for line in lines:
            if( not line.strip() ): continue
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
        lines = self.grep_file(self._filenames['general'], pattern='Number of lattice sites:')
        nsites = lines[0][ lines[0].find('Number of lattice sites:')+len("Number of lattice sites:"): ]
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
        lines = self.get_file_chunk(self._filenames['general'], begin="Site type names and number of sites of that type:",
                                        end='Maximum coordination number:')

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
                    assert tokens[0]=="configuration"

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
                        lattice_state.fillSite( site_number, surface_species[species_number] )

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


    def get_process_statistics(self):
        """
        Return the configurations from the 'history_output.txt' file.
        """
        output = []


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
            return output # module doesn't exist, deal with it.

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
