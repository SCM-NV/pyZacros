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


    def get_reactions(self):
        """
        Return the reactions from the 'general_output.txt' file.
        """
        lines = self.get_file_chunk(self._filenames['general'], begin="Reaction network:", end="Finished reading mechanism input.")

        reactions = []
        for line in lines:
            if( not line.strip() ): continue
            reactions.append( line[line.find("Reaction:")+len("Reaction:"):].strip().replace('  ',' ') )

        return reactions


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

                # Note that by default values are considered integers
                value = cases.get( names[i], lambda sv: int(sv) )( token.strip() )
                quantities[ names[i] ].append( value )

        return quantities


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


    #def addlayer_configurations(self):
        #"""
        #Return the site types from the 'general_output.txt' file.
        #"""
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
